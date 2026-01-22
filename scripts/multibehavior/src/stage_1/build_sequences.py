import pandas as pd

def build_interaction_sequences(
    approach_events,
    collision_events,
    retreat_events,
    COLLISION_LINK_WINDOW=30,
    RETREAT_LINK_WINDOW=30
):
    sequences = []
    sequence_id = 0

    used_collisions = set()
    used_retreats = set()

    # Ensure ordering
    approach_events = approach_events.sort_values("start_frame")
    collision_events = collision_events.sort_values("start_frame")
    retreat_events = retreat_events.sort_values("start_frame")

    for _, approach in approach_events.iterrows():
        sequence_id += 1

        a_start = approach["start_frame"]
        a_end = approach["end_frame"]

        linked_collision = None
        linked_retreat = None

        # ---- Find collision ----
        candidate_collisions = collision_events[
            (~collision_events["collision_id"].isin(used_collisions)) &
            (collision_events["start_frame"] > a_start) &
            (collision_events["start_frame"] <= a_end + COLLISION_LINK_WINDOW)
        ]

        if not candidate_collisions.empty:
            linked_collision = candidate_collisions.iloc[0]
            used_collisions.add(linked_collision["collision_id"])

        # ---- Find retreat ----
        if linked_collision is not None:
            ref_end = linked_collision["end_frame"]
        else:
            ref_end = a_end

        candidate_retreats = retreat_events[
            (~retreat_events["retreat_id"].isin(used_retreats)) &
            (retreat_events["start_frame"] > ref_end) &
            (retreat_events["start_frame"] <= ref_end + RETREAT_LINK_WINDOW)
        ]

        if not candidate_retreats.empty:
            linked_retreat = candidate_retreats.iloc[0]
            used_retreats.add(linked_retreat["retreat_id"])

        # ---- Outcome ----
        if linked_collision is not None:
            outcome = "collision"
        elif linked_retreat is not None:
            outcome = "abortive_retreat"
        else:
            outcome = "approach_only"

        # ---- Timing ----
        if linked_collision is not None:
            approach_to_collision_latency = (
                linked_collision["start_frame"] - a_start
            )
        else:
            approach_to_collision_latency = None

        if linked_retreat is not None:
            approach_to_retreat_latency = (
                linked_retreat["start_frame"] - a_start
            )
        else:
            approach_to_retreat_latency = None

        if linked_collision is not None and linked_retreat is not None:
            collision_to_retreat_latency = (
                linked_retreat["start_frame"] -
                linked_collision["end_frame"]
            )
        else:
            collision_to_retreat_latency = None

        end_frame = (
            linked_retreat["end_frame"]
            if linked_retreat is not None
            else (
                linked_collision["end_frame"]
                if linked_collision is not None
                else a_end
            )
        )

        total_duration = end_frame - a_start + 1

        sequences.append({
            "animal_name": approach["animal_name"],
            "sequence_id": sequence_id,
            "roi_name": approach["roi_name"],
            "approach_id": approach["approach_id"],
            "collision_id": (
                linked_collision["collision_id"]
                if linked_collision is not None else None
            ),
            "retreat_id": (
                linked_retreat["retreat_id"]
                if linked_retreat is not None else None
            ),
            "outcome_type": outcome,
            "approach_start_frame": a_start,
            "approach_end_frame": a_end,
            "collision_start_frame": (
                linked_collision["start_frame"]
                if linked_collision is not None else None
            ),
            "retreat_start_frame": (
                linked_retreat["start_frame"]
                if linked_retreat is not None else None
            ),
            "total_sequence_duration": total_duration,
            "approach_to_collision_latency": approach_to_collision_latency,
            "approach_to_retreat_latency": approach_to_retreat_latency,
            "collision_to_retreat_latency": collision_to_retreat_latency,
        })

    return pd.DataFrame(sequences)
