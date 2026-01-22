def build_transition_matrix_by_context(sequences):
    """
    P(outcome | approach, context) — pooled across phases
    """

    counts = (
        sequences
        .groupby(["context", "outcome_type"])
        .size()
        .reset_index(name="count")
    )

    totals = (
        counts
        .groupby("context")["count"]
        .sum()
        .reset_index(name="total")
    )

    df = counts.merge(totals, on="context")
    df["probability"] = df["count"] / df["total"]

    return df[["context", "outcome_type", "probability"]]

def build_transition_matrix_by_phase(sequences):
    """
    P(outcome | approach, context, phase)
    """

    counts = (
        sequences
        .groupby(["phase", "context", "outcome_type"])
        .size()
        .reset_index(name="count")
    )

    totals = (
        counts
        .groupby(["phase", "context"])["count"]
        .sum()
        .reset_index(name="total")
    )

    df = counts.merge(totals, on=["phase", "context"])
    df["probability"] = df["count"] / df["total"]

    return df[["phase", "context", "outcome_type", "probability"]]