import pandas as pd
import os
from matplotlib import pyplot as plt

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
plots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'plots'))

if not os.path.exists(plots_dir):
    exit("Plots directory does not exist.")
if not os.path.exists(data_dir):
    exit("Data directory does not exist.")

data_file = os.path.join(data_dir, 'behaviors.tsv')

data_df = pd.read_csv(data_file, sep='\t')
data_df.columns = [col.strip() for col in data_df.columns]
clean_data_df = data_df.drop(columns=['Observation date', 'Description', 'Observation type', 'Source', 'Time offset (s)', 'Coding duration', 'Media duration (s)', 'FPS (frame/s)', 'Subject', 'Behavioral category', 'Behavior type', 'Observation duration by subject by observation', 'Media file name', 'Image file path start', 'Image file path stop', 'Comment start', 'Comment stop'])

for col in ['Behavior', 'Image index start', 'Image index stop', 'Duration (s)']:
    clean_data_df[col] = clean_data_df[col].astype(str).str.strip()

# Inspect the cleaned data
clean_data_df.to_clipboard()

# I want to drop evey row that has Image index start above 9000
clean_data_df = clean_data_df[clean_data_df['Image index start'].astype(int) <= 9099]


grouped_df = clean_data_df.groupby(['Observation id']).agg({
    'Behavior': lambda x: list(x),
    'Start (s)': lambda x: list(x.astype(float)),
    'Stop (s)': lambda x: list(x.astype(float)),
    'Duration (s)': lambda x: list(x.astype(float))
    }).reset_index()

behavior_counts_sum = grouped_df['Behavior'].apply(lambda behaviors: pd.Series(behaviors).value_counts()).fillna(0)

# If two consecutive rows describe the same behavior and the gap between them is tiny, merge them into one continuous state.
MAX_GAP = 1.0

# Sort
sorted_df = clean_data_df.sort_values(by=["Observation id", "Behavior", "Start (s)"]).reset_index(drop=True)

# Compute gap 
sorted_df["prev_stop"] = sorted_df.groupby(["Observation id", "Behavior"])["Stop (s)"].shift(1)
sorted_df["gap"] = sorted_df["Start (s)"] - sorted_df["prev_stop"]

# Identify bouts
sorted_df["new_bout"] = (sorted_df["gap"].isna() | (sorted_df["gap"] > MAX_GAP))

# Assign bout IDs
sorted_df["bout_id"] = sorted_df.groupby(["Observation id", "Behavior"])["new_bout"].cumsum()

# Merge bouts
merged = (
    sorted_df.groupby(
        ["Observation id", "Behavior", "bout_id"],
        as_index=False
    )
    .agg(
        Start_s=("Start (s)", "min"),
        Stop_s=("Stop (s)", "max")
    )
)
merged["Duration_s"] = merged["Stop_s"] - merged["Start_s"]

# Aggregate on animal level 
bout_stats = (
    merged
    .groupby(["Observation id", "Behavior"])
    .agg(
        n_bouts=("bout_id", "count"),
        total_time_s=("Duration_s", "sum")
    )
    .reset_index()
)

bout_table = (
    bout_stats
    .pivot(
        index="Observation id",
        columns="Behavior",
        values=["n_bouts", "total_time_s"]
    )
    .fillna(0)
)

bout_table.to_excel(os.path.join(data_dir, 'bout_table.xlsx'))