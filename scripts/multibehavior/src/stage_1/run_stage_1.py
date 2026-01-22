import pickle
import gc
import os

from config.paths import RAW_ANALYSIS_PKL, EVENTS, GROUP_JSON
from config.constants import MIN_EVENT_FRAMES

from src.stage_1.extract_approach import extract_approach_events
from src.stage_1.extract_collision import extract_collision_events
from src.stage_1.extract_retreat import extract_retreat_events
from src.stage_1.build_sequences import build_interaction_sequences

from src.utils.io import load_session_groups
from src.utils.metadata import attach_group_metadata

def main():
    print("Stage 1 — extracting events from raw data")

    print("Loading session group mappings...")
    session_group_map = load_session_groups(GROUP_JSON)

    print("Creating event directories...")
    EVENTS.mkdir(exist_ok=True)
    for sub in ["approach", "collision", "retreat", "sequences"]:
        (EVENTS / sub).mkdir(parents=True, exist_ok=True)

    print("Loading raw analysis data...")
    with open(RAW_ANALYSIS_PKL, "rb") as f:
        analysis_results_raw = pickle.load(f)

    print("Extracting events...")
    for animal, session_data in analysis_results_raw.items():
        print(f"Processing {animal}")

        raw_df = session_data["raw_collision_data"]
        approach = extract_approach_events(raw_df)
        collision = extract_collision_events(raw_df)
        retreat = extract_retreat_events(raw_df)
        print("Extracted events: " \
        f"{len(approach)} approaches, " \
        f"{len(collision)} collisions, "
        f"{len(retreat)} retreats")

        print(f"Filtering short events (<{MIN_EVENT_FRAMES} frames) and assigning IDs...")
        approach = approach[approach["duration_frames"] >= MIN_EVENT_FRAMES].reset_index(drop=True)
        approach["approach_id"] = range(1, len(approach) + 1)

        collision = collision[collision["duration_frames"] >= MIN_EVENT_FRAMES].reset_index(drop=True)
        collision["collision_id"] = range(1, len(collision) + 1)

        retreat = retreat[retreat["duration_frames"] >= MIN_EVENT_FRAMES].reset_index(drop=True)
        retreat["retreat_id"] = range(1, len(retreat) + 1)

        print("Attaching group metadata...")
        approach = attach_group_metadata(approach, animal, session_group_map)
        collision = attach_group_metadata(collision, animal, session_group_map)
        retreat = attach_group_metadata(retreat, animal, session_group_map)

        print("Building interaction sequences...")
        sequences = build_interaction_sequences(approach, collision, retreat)
        sequences = attach_group_metadata(sequences, animal, session_group_map)

        print("Saving extracted events...")
        approach.to_parquet(os.path.join(EVENTS, "approach", f"{animal}.parquet"))
        collision.to_parquet(os.path.join(EVENTS, "collision", f"{animal}.parquet"))
        retreat.to_parquet(os.path.join(EVENTS, "retreat", f"{animal}.parquet"))
        sequences.to_parquet(os.path.join(EVENTS, "sequences", f"{animal}.parquet"))
        
        print(
            f"  saved: "
            f"{len(approach)} approaches, "
            f"{len(collision)} collisions, "
            f"{len(retreat)} retreats, "
            f"{len(sequences)} sequences"
        )

        del raw_df, approach, collision, retreat, sequences
        gc.collect()

if __name__ == "__main__":
    main()