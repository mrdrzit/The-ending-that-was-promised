import pandas as pd
import numpy as np

def extract_retreat_events(df):
    df = df.copy()

    # Ensure correct ordering
    df = df.sort_values("frame").reset_index(drop=True)

    # Boolean mask for retreat frames
    is_retreat = df["interaction_state"] == "retreating"

    # Identify retreat blocks
    retreat_blocks = (
        is_retreat
        .ne(is_retreat.shift())
        .cumsum()
    )

    retreat_events = []
    retreat_id = 0

    for _, block in df[is_retreat].groupby(retreat_blocks):
        retreat_id += 1

        start_frame = block["frame"].iloc[0]
        end_frame = block["frame"].iloc[-1]
        duration_frames = end_frame - start_frame + 1

        start_distance = block["distance_to_roi"].iloc[0]
        max_distance = block["distance_to_roi"].max()
        distance_increase = max_distance - start_distance
        mean_distance = block["distance_to_roi"].mean()
        distance_variance = block["distance_to_roi"].var()

        mean_retreat_speed = block["delta distance"].mean()
        peak_retreat_speed = block["delta distance"].max()

        mean_angle = block["angle_to_roi"].mean()
        angle_variance = block["angle_to_roi"].var()

        mean_head_area = block["head_area"].mean()

        # Head area slope
        if len(block) > 1:
            x = np.arange(len(block))
            y = block["head_area"].values
            head_area_slope = np.polyfit(x, y, 1)[0]
        else:
            head_area_slope = np.nan

        retreat_events.append({
            "retreat_id": retreat_id,
            "roi_name": block["roi_name"].iloc[0],
            "start_frame": start_frame,
            "end_frame": end_frame,
            "duration_frames": duration_frames,
            "start_distance": start_distance,
            "max_distance": max_distance,
            "mean_distance": mean_distance,
            "distance_variance": distance_variance,
            "mean_angle_to_roi": mean_angle,
            "angle_variance": angle_variance,
            "distance_increase": distance_increase,
            "mean_retreat_speed": mean_retreat_speed,
            "peak_retreat_speed": peak_retreat_speed,
            "mean_head_area": mean_head_area,
            "head_area_slope": head_area_slope,
        })

    return pd.DataFrame(retreat_events)
