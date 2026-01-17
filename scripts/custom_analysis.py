import os
import re
import pickle as pkl
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def sort_behavior_videos(file_list):
    """
    Sorts a list of file paths based on behavioral groups 
    (tra, trb, tta, ttb) and then chronologically by filename.
    """
    
    # Define the custom order priority
    priority_map = {
        'tra': 1,
        'trb': 2,
        'tta': 3,
        'ttb': 4
    }

    def _get_sort_key(path):
        # 1. Search for the group folder name inside the path
        # We look for \tra\, \trb\, etc. to ensure we match the folder
        match = re.search(r'\\(tra|trb|tta|ttb)\\', path, re.IGNORECASE)
        
        if match:
            group = match.group(1).lower()
            # Get priority from map, default to 5 if something weird happens
            priority = priority_map.get(group, 5)
        else:
            # If no group found, put it at the very end
            priority = 99
            
        # Return tuple: (Group Priority, Original Path)
        return (priority, path)

    # Return the sorted list
    return sorted(file_list, key=_get_sort_key)


data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
plots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'plots'))

groups_file = os.path.join(data_dir, 'all_exploration_bouts.pkl')
sorted_groups_file = os.path.join(data_dir, 'sorted_exploration_bouts.pkl')

if not os.path.exists(sorted_groups_file):
    print("Sorted exploration bouts file not found. Generating...")
    # First define the paths to the original directories that contain the groups information
    path_text_file = os.path.join(data_dir, 'original_paths.txt')
    full_paths = []
    with open(path_text_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            full_paths.append(line.strip())

    with open(os.path.join(data_dir, 'all_exploration_bouts.pkl'), 'rb') as fh:
        raw_results = pkl.load(fh)

    full_path_results = {}

    # iterate over a static list of keys to avoid modifying the dict during iteration
    for key in list(raw_results.keys()):
        for path in full_paths:
            if key in path:
                full_path_results[path] = raw_results.pop(key)
                break

    # Sort the dictionary based on the custom sorting function
    sorted_paths = sort_behavior_videos(list(full_path_results.keys()))
    sorted_results = {path: full_path_results[path] for path in sorted_paths}

    # Save the sorted results for future use
    with open(os.path.join(data_dir, 'sorted_exploration_bouts.pkl'), 'wb') as fh: pkl.dump(sorted_results, fh)
elif os.path.exists(sorted_groups_file):
    print("Loading sorted exploration bouts file...")
    with open(os.path.join(data_dir, 'sorted_exploration_bouts.pkl'), 'rb') as fh:
        sorted_results = pkl.load(fh)
else:
    raise FileNotFoundError("Required data files are missing.")

# Oganizing data
for key, data in sorted_results.items():
    # Calculate inter bout interval
    ibi = np.append(0, np.diff(data['start (s)']))
    sorted_results[key]['inter_bout_intervals'] = ibi

# Engagement analysis
engagement_data = {}
for key, data in sorted_results.items():
    latency_to_first_bout = data['start (s)'][0] if len(data['start (s)']) > 0 else np.nan
    number_of_bouts_in_first_minute = np.sum(data['start (s)'] < 60)
    fraction_of_time_exploring_first_minute = np.sum(data['duration (s)'][data['start (s)'] < 60]) / np.sum(data['duration (s)']) if np.sum(data['duration (s)']) > 0 else np.nan
    engagement_data[key] = {
        'latency to first bout (s)': latency_to_first_bout,
        'number of bouts in first minute': number_of_bouts_in_first_minute,
        'fraction of time exploring first minute (%)': fraction_of_time_exploring_first_minute * 100
    }

# Bout duration structure analysis
bout_duration_data = {}
for key, data in sorted_results.items():
    bout_durations = data['duration (s)']
    mean_bout_duration = np.mean(bout_durations) if len(bout_durations) > 0 else np.nan
    ninethy_fifth_percentile_duration = np.percentile(bout_durations, 95) if len(bout_durations) > 0 else np.nan
    short_bout_fraction = np.sum(bout_durations < 0.5) / len(bout_durations) if len(bout_durations) > 0 else np.nan
    bout_duration_data[key] = {
        'mean bout duration (s)': mean_bout_duration,
        '95th percentile duration (s)': ninethy_fifth_percentile_duration,
        'short bout fraction (%)': short_bout_fraction * 100
    }

# Inter-bout organization analysis
inter_bout_data = {}
for key, data in sorted_results.items():
    ibi = data['inter_bout_intervals']
    mean_ibi = np.mean(ibi[1:]) if len(ibi) > 1 else np.nan  # exclude the first zero
    iqr_ibi = np.percentile(ibi[1:], 75) - np.percentile(ibi[1:], 25) if len(ibi) > 1 else np.nan
    variability_ibi = np.std(ibi[1:]) if mean_ibi > 0 else np.nan
    inter_bout_data[key] = {
        'mean inter-bout interval (s)': mean_ibi,
        'iqr inter-bout interval (s)': iqr_ibi,
        'variability inter-bout interval': variability_ibi
    }

# Master dataframe creation
master_df = pd.DataFrame.from_dict(engagement_data, orient='index')
bout_duration_df = pd.DataFrame.from_dict(bout_duration_data, orient='index')
inter_bout_df = pd.DataFrame.from_dict(inter_bout_data, orient='index')
master_df = master_df.join(bout_duration_df).join(inter_bout_df)
master_df.reset_index(inplace=True)
master_df.rename(columns={'index': 'video_path'}, inplace=True)
master_df.to_excel(os.path.join(data_dir, 'exploration_bout_analysis_summary.xlsx'), index=False)
