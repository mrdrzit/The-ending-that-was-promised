def attach_group_metadata(df, animal_name, session_group_map):
    meta = session_group_map[animal_name]

    df = df.copy()
    df["animal_name"] = animal_name
    df["group"] = meta["group"]
    df["phase"] = meta["phase"]
    df["context"] = meta["context"]

    return df
