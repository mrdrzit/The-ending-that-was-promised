from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"

RAW = DATA / "raw"
EVENTS = DATA / "events"
DERIVED = DATA / "derived"
EXCEL = DATA / "exports" / "excel"

GROUP_JSON = RAW / "original_paths_dict.json"

RAW_ANALYSIS_PKL = RAW / "raw_analysis_data.pkl"
RAW_COLLISION_PKL = RAW / "raw_collision_data.pkl"
