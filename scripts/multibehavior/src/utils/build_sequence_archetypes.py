
import pandas as pd

def build_sequence_archetype_table(sequences, return_prism=False, subject_col="animal_name"):
    """
    Build normalized outcome proportions per session x context (original output),
    and optionally also per-subject (animal) proportions for Prism ANOVA.

    Original output columns (unchanged):
        group, phase, context, outcome_type, count, total, proportion

    Prism output columns (long format; per animal):
        group, phase, context, animal_name, outcome_type, count, total, proportion
    """

    # ----------------------------
    # Original (pooled) output
    # ----------------------------
    pooled_counts = (
        sequences
        .groupby(["group", "phase", "context", "outcome_type"])
        .size()
        .reset_index(name="count")
    )

    pooled_totals = (
        pooled_counts
        .groupby(["group", "phase", "context"])["count"]
        .sum()
        .reset_index(name="total")
    )

    merged = pooled_counts.merge(
        pooled_totals,
        on=["group", "phase", "context"],
        how="left"
    )

    merged["proportion"] = merged["count"] / merged["total"]

    if not return_prism:
        return merged  # <-- EXACT SAME behavior as before

    # ----------------------------
    # Prism-ready (per-animal) long table
    # ----------------------------
    if subject_col not in sequences.columns:
        raise ValueError(f"'{subject_col}' column not found in sequences. Available: {list(sequences.columns)}")

    prism_counts = (
        sequences
        .groupby(["group", "phase", "context", subject_col, "outcome_type"])
        .size()
        .reset_index(name="count")
        .rename(columns={subject_col: "animal_name"})
    )

    prism_totals = (
        prism_counts
        .groupby(["group", "phase", "context", "animal_name"])["count"]
        .sum()
        .reset_index(name="total")
    )

    prism_long = prism_counts.merge(
        prism_totals,
        on=["group", "phase", "context", "animal_name"],
        how="left"
    )

    prism_long["proportion"] = prism_long["count"] / prism_long["total"]

    return merged, prism_long


def prism_grouped_from_long(
    df_long: pd.DataFrame,
    outcome_type: str,
    value_col: str = "proportion",
    phase_order=("treino", "teste"),
    context_order=("A", "B"),
    animal_col="animal_name",
):
    """
    Convert long per-animal outcome table into a Prism 'Grouped' paste table.

    Input df_long must have:
      phase, context, animal_name, outcome_type, and value_col (e.g., proportion or count)

    Output:
      index = phase (rows in Prism)
      columns = A_1..A_nmax, B_1..B_nmax (subcolumns for each context)
      values = replicates (animals), sorted by animal_name within each cell
    """

    # Filter to one outcome
    d = df_long.loc[df_long["outcome_type"] == outcome_type, ["phase", "context", animal_col, value_col]].copy()

    # Collect replicate lists per (phase, context)
    vals = {}
    nmax = 0
    for ph in phase_order:
        for cx in context_order:
            v = (
                d.loc[(d["phase"] == ph) & (d["context"] == cx)]
                .sort_values(animal_col)[value_col]
                .tolist()
            )
            vals[(ph, cx)] = v
            nmax = max(nmax, len(v))

    # Build output columns Prism likes to paste (subcolumns)
    cols = [f"{context_order[0]}_{i+1}" for i in range(nmax)] + [f"{context_order[1]}_{i+1}" for i in range(nmax)]
    out = pd.DataFrame(index=list(phase_order), columns=cols, dtype=float)
    out.index.name = "phase"

    # Fill each phase row with A replicates then B replicates (pad with NA)
    for ph in phase_order:
        a = vals[(ph, context_order[0])] + [pd.NA] * (nmax - len(vals[(ph, context_order[0])]))
        b = vals[(ph, context_order[1])] + [pd.NA] * (nmax - len(vals[(ph, context_order[1])]))
        out.loc[ph, :] = a + b

    return out