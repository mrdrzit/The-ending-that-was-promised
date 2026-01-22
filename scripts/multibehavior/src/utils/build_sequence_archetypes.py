
def build_sequence_archetype_table(sequences):
    """
    Build normalized outcome proportions per session × context.

    Output columns:
        group
        phase
        context
        outcome_type
        proportion
    """

    counts = (
        sequences
        .groupby(["group", "phase", "context", "outcome_type"])
        .size()
        .reset_index(name="count")
    )

    totals = (
        counts
        .groupby(["group", "phase", "context"])["count"]
        .sum()
        .reset_index(name="total")
    )

    merged = counts.merge(
        totals,
        on=["group", "phase", "context"],
        how="left"
    )

    merged["proportion"] = merged["count"] / merged["total"]

    return merged
