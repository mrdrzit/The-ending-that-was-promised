import numpy as np
import pandas as pd

def extract_approach_events(df):
    df = df.copy()

    # Ensure correct ordering
    df = df.sort_values("frame").reset_index(drop=True)

    # Boolean mask for approach frames
    is_approach = df["interaction_state"] == "approaching"

    # Identify approach start and end points
    approach_blocks = (
        is_approach
        .ne(is_approach.shift())
        .cumsum()
    )

    approach_events = []
    approach_id = 0

    for _, block in df[is_approach].groupby(approach_blocks):
        approach_id += 1

        start_frame = block["frame"].iloc[0]
        end_frame = block["frame"].iloc[-1]
        duration_frames = end_frame - start_frame + 1

        start_distance = block["distance_to_roi"].iloc[0]
        min_distance = block["distance_to_roi"].min()
        max_distance = block["distance_to_roi"].max()
        mean_distance = block["distance_to_roi"].mean()
        distance_variance = block["distance_to_roi"].var()

        distance_reduction = start_distance - min_distance

        mean_delta_distance = block["delta distance"].mean()
        peak_approach_speed = block["delta distance"].min()  # most negative

        mean_angle = block["angle_to_roi"].mean()
        angle_variance = block["angle_to_roi"].var()

        mean_head_area = block["head_area"].mean()

        # Simple head area slope (linear trend)
        if len(block) > 1:
            x = np.arange(len(block))
            y = block["head_area"].values
            head_area_slope = np.polyfit(x, y, 1)[0]
        else:
            head_area_slope = np.nan

        approach_events.append({
            "approach_id": approach_id,
            "roi_name": block["roi_name"].iloc[0],
            "start_frame": start_frame,
            "end_frame": end_frame,
            "duration_frames": duration_frames,
            "start_distance": start_distance,
            "min_distance": min_distance,
            "max_distance": max_distance,
            "distance_reduction": distance_reduction,
            "mean_delta_distance": mean_delta_distance,
            "peak_approach_speed": peak_approach_speed,
            "mean_angle_to_roi": mean_angle,
            "angle_variance": angle_variance,
            "mean_head_area": mean_head_area,
            "head_area_slope": head_area_slope,
        })

    return pd.DataFrame(approach_events)

