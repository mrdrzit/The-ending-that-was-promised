import pandas as pd

def build_animal_bout_counts(approach, collision, retreat):
    rows = []

    for animal, g in approach.groupby("animal_name"):
        meta = g.iloc[0][["group", "phase", "context"]].to_dict()

        rows.append({
            "animal_name": animal,
            **meta,
            "n_approach_bouts": len(g),
            "n_collision_bouts": len(collision[collision["animal_name"] == animal]),
            "n_retreat_bouts": len(retreat[retreat["animal_name"] == animal]),
        })

    return pd.DataFrame(rows)