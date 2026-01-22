import pandas as pd
import numpy as np

def build_latency_table(sequences, fps=30):
    """
    Build latency table from interaction sequences.

    Output columns:
        animal_name
        group
        phase
        context
        outcome
        latency_sec
    """

    rows = []

    for _, row in sequences.iterrows():
        outcome = row["outcome_type"]

        if outcome == "collision":
            latency = row["approach_to_collision_latency"]
        elif outcome == "abortive_retreat":
            latency = row["approach_to_retreat_latency"]
        else:
            continue  # approach_only excluded

        if pd.isna(latency):
            continue

        rows.append({
            "animal_name": row["animal_name"],
            "group": row["group"],
            "phase": row["phase"],
            "context": row["context"],
            "outcome": outcome,
            "latency_sec": latency / fps,
        })

    return pd.DataFrame(rows)