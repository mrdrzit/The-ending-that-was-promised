import numpy as np
import pandas as pd
from src.utils.normalize_collisions import normalize_collision_positions

def extract_collision_events(df):
    df = df.copy()

    # Ensure correct ordering
    df = df.sort_values("frame").reset_index(drop=True)

    # Boolean mask for collision frames
    is_collision = df["collision_flag"] == 1

    # Identify collision blocks
    collision_blocks = (
        is_collision
        .ne(is_collision.shift())
        .cumsum()
    )

    collision_events = []
    collision_id = 0

    for _, block in df[is_collision].groupby(collision_blocks):
        collision_id += 1

        start_frame = block["frame"].iloc[0]
        end_frame = block["frame"].iloc[-1]
        duration_frames = end_frame - start_frame + 1

        mean_distance = block["distance_to_roi"].mean()
        distance_variance = block["distance_to_roi"].var()

        mean_angle = block["angle_to_roi"].mean()
        angle_variance = block["angle_to_roi"].var()

        mean_head_area = block["head_area"].mean()
        head_area_variance = block["head_area"].var()

        # Collision position variance
        # positions = [
        #     p for p in block["collision_pos"] if p is not None
        # ]

        all_points = []

        for cp in block["collision_pos"]:
            all_points.extend(normalize_collision_positions(cp))

        if len(all_points) > 1:
            positions = np.array(all_points)  # shape (N, 2)
            collision_position_variance = (
                np.var(positions[:, 0]) +
                np.var(positions[:, 1])
            )
        else:
            collision_position_variance = np.nan

        collision_events.append({
            "collision_id": collision_id,
            "roi_name": block["roi_name"].iloc[0],
            "start_frame": start_frame,
            "end_frame": end_frame,
            "duration_frames": duration_frames,
            "mean_distance": mean_distance,
            "distance_variance": distance_variance,
            "mean_angle_to_roi": mean_angle,
            "angle_variance": angle_variance,
            "mean_head_area": mean_head_area,
            "head_area_variance": head_area_variance,
            "collision_position_variance": collision_position_variance,
        })


    return pd.DataFrame(collision_events)
