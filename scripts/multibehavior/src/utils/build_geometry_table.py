import pandas as pd
import numpy as np

def build_approach_geometry_table(approach, sequences):
    """
    One row per approach bout:
        - distance_reduction
        - mean absolute angular deviation (MAD)
        - outcome_type
    """

    organized_table = pd.DataFrame()

    # Keep only columns we need
    approach_cols = [
        "animal_name",
        "approach_id",
        "group",
        "phase",
        "context",
        "distance_reduction",
        "mean_angle_to_roi",
        "angle_variance",
    ]

    a = approach[approach_cols].copy()

    # ---- Mean absolute angular deviation ----
    # Reconstruct MAD from per-bout angle samples
    # NOTE: angle_variance is not used; MAD is more interpretable

    if "angle_samples" in approach.columns:
        # (only if you ever store samples explicitly)
        def mad(x):
            mu = np.mean(x)
            return np.mean(np.abs(x - mu))

        a["angle_mad"] = approach["angle_samples"].apply(mad)

    else:
        # Fallback: approximate MAD from variance (robust enough)
        # MAD ≈ sqrt(variance) * sqrt(2 / π)
        a["angle_mad"] = np.sqrt(a["angle_variance"]) * np.sqrt(2 / np.pi)

    # ---- Attach outcome from sequences ----
    s = sequences[
        ["animal_name", "approach_id", "outcome_type"]
    ].copy()

    out = a.merge(
        s,
        on=["animal_name", "approach_id"],
        how="left"
    )

    organized_table = out.groupby("animal_name").agg({"distance_reduction": "mean", "mean_angle_to_roi": "mean", "angle_variance": "mean", "angle_mad": "mean"})

    ## add metadata columns back
    organized_table = organized_table.reset_index()
    organized_table["group"] = approach.groupby("animal_name")["group"].first().values
    organized_table["phase"] = approach.groupby("animal_name")["phase"].first().values
    organized_table["context"] = approach.groupby("animal_name")["context"].first().values




    return out, organized_table