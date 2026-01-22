def build_approach_duration_table(approach, fps=30):
    """
    Build approach duration table from approach event dataframe.

    Output columns:
        animal_name
        group
        phase
        context
        duration_sec
    """

    df = approach.copy()
    df["duration_sec"] = df["duration_frames"] / fps

    return df[["animal_name", "approach_id", "group", "phase", "context", "duration_sec"]]

def summarize_approach_durations(duration_table):
    """
    Per-animal summary of approach durations.
    """

    duration_table = duration_table.copy()
    group_by_duration_table = duration_table.groupby(["animal_name", "group", "phase", "context"], as_index=False)
    agg_duration_table = group_by_duration_table.agg(mean_duration_sec=("duration_sec", "mean"), std_duration_sec=("duration_sec", "std"), n_approaches=("duration_sec", "count"))
    
    return agg_duration_table