import pandas as pd

def organize_table(table):
    order = ["tra", "trb", "tta", "ttb"]

    animal_name_format = ["animal_name", "animal", "session"]

    for name in animal_name_format:
        if name in table.columns:
            table.copy()

            # make sure we preserve only those groups, in this order
            table["group"] = pd.Categorical(table["group"], categories=order, ordered=True)
            table = table.sort_values(["group", name]).reset_index(drop=True)
            return table
    return table