import pandas as pd

def build_latent_indices_table(geometry_df, duration_df):
    """
    Build a unified table with Commitment Index (CI) and Hesitation Index (HI)
    per approach bout.
    """

    organized_table = pd.DataFrame()
    
    df = geometry_df.merge(
        duration_df[
            ["animal_name", "approach_id", "duration_sec"]
        ],
        on=["animal_name", "approach_id"],
        how="left"
    )

    # -------------------------
    # Z-score normalization
    # -------------------------
    df["z_distance"] = (
        df["distance_reduction"] - df["distance_reduction"].mean()
    ) / df["distance_reduction"].std()

    df["z_angle_mad"] = (
        df["angle_mad"] - df["angle_mad"].mean()
    ) / df["angle_mad"].std()

    df["z_duration"] = (
        df["duration_sec"] - df["duration_sec"].mean()
    ) / df["duration_sec"].std()

    # -------------------------
    # Indices
    # -------------------------
    df["commitment_index"] = df["z_distance"] - df["z_angle_mad"]
    df["hesitation_index"] = df["z_angle_mad"] + df["z_duration"]

    organized_table = df.groupby("animal_name").agg(
        {
            "distance_reduction": "mean", 
            "mean_angle_to_roi": "mean", 
            "angle_variance": "mean", 
            "angle_mad": "mean",
            "duration_sec": "mean",
            "commitment_index": "mean",
            "hesitation_index": "mean"
        })

    ## add metadata columns back
    organized_table = organized_table.reset_index()
    organized_table["group"] = df.groupby("animal_name")["group"].first().values
    organized_table["phase"] = df.groupby("animal_name")["phase"].first().values
    organized_table["context"] = df.groupby("animal_name")["context"].first().values

    return df, organized_table