import pandas as pd

def build_animal_bout_outcomes(approach, collision, retreat, sequences):
    rows = []

    animals = approach["animal_name"].unique()

    for animal in animals:
        a = approach[approach["animal_name"] == animal]
        c = collision[collision["animal_name"] == animal]
        r = retreat[retreat["animal_name"] == animal]
        s = sequences[sequences["animal_name"] == animal]

        meta = a.iloc[0][["group", "phase", "context"]].to_dict()

        approach_count = len(a)
        collision_count = len(c)
        retreat_count = len(r)

        n_collision_outcomes = (s["outcome_type"] == "collision").sum()
        n_abortive_retreats = (s["outcome_type"] == "abortive_retreat").sum()
        n_approach_only = (s["outcome_type"] == "approach_only").sum()

        if approach_count == 0:
            success_rate = float("nan")
            abortive_rate = float("nan")
            failure_rate = float("nan")
        else:
            success_rate = n_collision_outcomes / approach_count
            abortive_rate = n_abortive_retreats / approach_count
            failure_rate = (n_abortive_retreats + n_approach_only) / approach_count

        rows.append({
            "animal_name": animal,
            **meta,
            "n_approach_bouts": approach_count,
            "n_collision_bouts": collision_count,
            "n_retreat_bouts": retreat_count,
            "n_collision_outcomes": n_collision_outcomes,
            "n_abortive_retreats": n_abortive_retreats,
            "n_approach_only": n_approach_only,
            "success_rate": success_rate,
            "abortive_rate": abortive_rate,
            "failure_rate": failure_rate,
        })

    return pd.DataFrame(rows)