import pandas as pd
from config.paths import EVENTS

def load_events(event_type):
    files = sorted((EVENTS / event_type).glob("*.parquet"))
    dfs = [pd.read_parquet(f) for f in files]
    return pd.concat(dfs, ignore_index=True)