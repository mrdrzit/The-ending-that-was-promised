import re
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import re
import matplotlib as mpl
import matplotlib.lines as mlines
from pathlib import Path
from tkinter import filedialog
from matplotlib import colors as mcolors
from dlc_helper_functions import *

plt.ioff()

INTERACTIVE = True
save_fig = True
if INTERACTIVE:
    file_explorer = tk.Tk()
    file_explorer.withdraw()
    file_explorer.call("wm", "attributes", ".", "-topmost", True)
    figures_folder = str(Path(filedialog.askdirectory(title="Select the folder to save the plots", mustexist=True)))

data = DataFiles()
animals = []
all_results = {}
get_files([], data, animals)


for animal in animals:
    collision_data = []
    dimensions = animal.exp_dimensions()
    focinho_x = animal.bodyparts["focinho"]["x"]
    focinho_y = animal.bodyparts["focinho"]["y"]
    orelha_esq_x = animal.bodyparts["orelhae"]["x"]
    orelha_esq_y = animal.bodyparts["orelhae"]["y"]
    orelha_dir_x = animal.bodyparts["orelhad"]["x"]
    orelha_dir_y = animal.bodyparts["orelhad"]["y"]
    centro_x = animal.bodyparts["centro"]["x"]
    centro_y = animal.bodyparts["centro"]["y"]
    roi_X = []
    roi_Y = []
    roi_D = []
    roi_NAME = []
    roi_regex = re.compile(r"\\([^\\]+)\.")
    number_of_filled_rois = sum(1 for roi in animal.rois if roi["x"])
    for i in range(number_of_filled_rois):
        # Finds the name of the roi in the file name
        roi_name = Path(animal.rois[i]["file"]).stem.split("_")[0]
        roi_NAME.append(roi_name)
        roi_X.append(animal.rois[i]["x"])
        roi_Y.append(animal.rois[i]["y"])
        roi_D.append((animal.rois[i]["width"] + animal.rois[i]["height"]) / 2)
    # ---------------------------------------------------------------

    # General data
    arena_width = 30
    arena_height = 30
    frames_per_second = 30
    max_analysis_time = 300
    threshold = 0.0267
    # Maximum video height set by user
    # (height is stored in the first element of the list and is converted to int beacuse it comes as a string)
    max_video_height = 1920
    max_video_width = 1080
    plot_options = True
    trim_amount = 0
    video_height, video_width, _ = dimensions
    factor_width = arena_width / video_width
    factor_height = arena_height / video_height
    number_of_frames = animal.exp_length()
    bin_size = 10
    # ----------------------------------------------------------------------------------------------------------

    runtime = range(int(max_analysis_time * frames_per_second))

    # Try to clean the animal name from the date and time timestamp
    clean_animal_name = None
    date_time_timestamp_regex = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}")
    try:
        date_time_timestamp = date_time_timestamp_regex.search(animal.name).group(0)
        # Replace the date and time timestamp with the an empty string
        # Replace all remaining underscores, spcaces and dashes with a single underscore
        new_key = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}", "", animal.name)
        new_key = re.sub(r"[_\s-]+", "_", new_key)
        clean_animal_name = new_key
    except:
        print(f"Could not find the date and time timestamp for the animal {animal.name}")
        print("Using the complete animal name instead.")
        clean_animal_name = animal.name

    for i in runtime:
        # Calculate the area of the mice's head
        Side1 = np.sqrt(((orelha_esq_x[i] - focinho_x[i]) ** 2) + ((orelha_esq_y[i] - focinho_y[i]) ** 2))
        Side2 = np.sqrt(((orelha_dir_x[i] - orelha_esq_x[i]) ** 2) + ((orelha_dir_y[i] - orelha_esq_y[i]) ** 2))
        Side3 = np.sqrt(((focinho_x[i] - orelha_dir_x[i]) ** 2) + ((focinho_y[i] - orelha_dir_y[i]) ** 2))
        S = (Side1 + Side2 + Side3) / 2
        mice_head_area = np.sqrt(S * (S - Side1) * (S - Side2) * (S - Side3))
        # ------------------------------------------------------------------------------------------------------

        # Calculate the exploration threshold in front of the mice's nose
        A = np.array([focinho_x[i], focinho_y[i]])
        B = np.array([orelha_esq_x[i], orelha_esq_y[i]])
        C = np.array([orelha_dir_x[i], orelha_dir_y[i]])
        P, Q = line_trough_triangle_vertex(A, B, C)
        # ------------------------------------------------------------------------------------------------------

        # Calculate the collisions between the ROI and the mice's nose
        for ii in range(number_of_filled_rois):
            collision = detect_collision([Q[0], Q[1]], [P[0], P[1]], [roi_X[ii], roi_Y[ii]], roi_D[ii] / 2)
            if collision:
                collision_data.append([1, collision, mice_head_area, roi_NAME[ii]])
            else:
                collision_data.append([0, None, mice_head_area, None])

    # ----------------------------------------------------------------------------------------------------------
    corrected_runtime_last_frame = runtime[-1] + 1
    corrected_first_frame = runtime[1] - 1
    ANALYSIS_RANGE = [corrected_first_frame, corrected_runtime_last_frame]
    # ----------------------------------------------------------------------------------------------------------
    ## TODO: #43 If there is no collision, the collision_data will be empty and the code will break. Throw an error and print a message to the user explaining what is a collision.
    collisions = pd.DataFrame(collision_data)
    xy_data = collisions[1].dropna()

    # The following line substitutes these lines:
    #   t = xy_data.to_list()
    #   t = [item for sublist in t for item in sublist]
    #   x, y = zip(*t)
    # Meaning that it flattens the list and then separates the x and y coordinates
    try:
        x_collision_data, y_collision_data = zip(*[item for sublist in xy_data.to_list() for item in sublist])
    except ValueError:
        x_collision_data, y_collision_data = np.zeros(len(runtime)), np.zeros(len(runtime))  # If there is no collision, the x and y collision data will be 0
        print("\n")
        print(f"---------------------- WARNING FOR ANIMAL {animal.name} ----------------------")
        print(f"Something went wrong with the animal's {animal.name} exploration data.\nThere are no exploration data in the video for this animal.")
        print(f"Please check the video for this animal: {animal.name}")
        print("-------------------------------------------------------------------------------\n")

    # ----------------------------------------------------------------------------------------------------------

    # Calculate the total exploration time
    exploration_mask = collisions[0] > 0
    exploration_mask = exploration_mask.astype(int)
    exploration_time = np.sum(exploration_mask) * (1 / frames_per_second)

    # get sections
    exploration_bouts = find_sections(collisions, frames_per_second)
    exploration_bouts = exploration_bouts[exploration_bouts["duration"] > (1 / frames_per_second) * 2].reset_index(drop=True)

    # Save excel file with the exploration bouts
    exploration_bouts_sec = exploration_bouts.copy(deep=True)
    exploration_bouts_sec["start"] = exploration_bouts_sec["start"] / frames_per_second
    exploration_bouts_sec["end"] = exploration_bouts_sec["end"] / frames_per_second
    exploration_bouts_sec = exploration_bouts_sec.astype(float).round(2)
    exploration_bouts_sec = exploration_bouts_sec.rename(columns={"start": "start (s)", "end": "end (s)", "duration": "duration (s)"})
    print(f"Saving the exploration bouts data for {clean_animal_name}...")
    exploration_bouts_sec.to_excel(os.path.join(figures_folder, f"{clean_animal_name}_exploration_bouts.xlsx"))
    durations = np.array(exploration_bouts["duration"])

    # Normalize durations and map to colors
    cmap = plt.get_cmap("afmhot")
    half_cmap = mcolors.LinearSegmentedColormap.from_list(f"half_{cmap.name}", cmap(np.linspace(0.1, 0.5, 256)))
    vmin = durations.min()
    vmax = durations.max()
    tick_values = np.floor(np.linspace(vmin, vmax, num=6))
    vmin, vmax = tick_values[0], tick_values[-1]
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=half_cmap)
    colors = [mapper.to_rgba(duration) for duration in durations]
    x_positions = np.linspace(0, len(runtime) / frames_per_second, len(runtime))

    mpl.rcParams['font.family'] = 'Palatino Linotype'

    fig, ax = plt.subplots(figsize=(15.0, 2.88))
    plt.subplots_adjust(wspace=0.1, hspace=1)

    # Calculate the center positions for each line
    mid_points = [(start + end) / 2 for start, end in zip(exploration_bouts["start"], exploration_bouts["end"])]
    total_minutes = int(np.floor(len(runtime) / frames_per_second / 60))
    x_ticks_positions_mins = np.arange(60, (total_minutes + 1) * 60, 60)

    # Create horizontal event lines at y positions [0, 1, 2, ..., len(durations)-1]
    y_offset = 0
    positions = np.zeros(len(durations)) + y_offset
    lengths = np.array(durations)[:, np.newaxis]
    transposed_positions = (np.array(positions)[:, np.newaxis]) / frames_per_second
    transposed_mid_points = np.array(mid_points)[:, np.newaxis] / frames_per_second
    x_points_sec = len(x_positions) / frames_per_second

    # Plot event lines
    ax.eventplot(transposed_mid_points, orientation="horizontal", colors=colors, lineoffsets=transposed_positions, linelengths=max(durations), linewidths=durations)
    ax.set_xlim(0, x_points_sec)
    ax.set_ylim(y_offset - max(durations), y_offset + max(durations))
    ax.set_ylabel("Exploration bouts")

    orange_line = mlines.Line2D([], [], color='orange', linewidth=2, label='Exploration bouts')
    ax.legend(handles=[orange_line], loc="upper right")
    ax.set_title(f"Duration mapped by color and linewidth")
    tick_values = np.floor(np.linspace(vmin, vmax, num=6))
    cbar = fig.colorbar(mapper, ax=ax, orientation='vertical', fraction=0.02, pad=0.04)
    cbar.set_ticks(tick_values)
    cbar.set_label("Duration (s)")
    ax.set_yticks([])
    ax.set_xticks(x_ticks_positions_mins)
    ax.set_xticklabels([str(i) for i in range(1, total_minutes + 1)])
    ax.set_xlabel("Time (min)")
    for x in x_ticks_positions_mins:
        ax.axvline(x=x, color='gray', linestyle='-.', linewidth=1, alpha=0.7)
    fig.tight_layout()
    if save_fig:
        print(f"Saving the exploration bouts comparison figure for {animal.name}...")
        fig.savefig(os.path.join(figures_folder, f"{clean_animal_name}_exploration_bouts.png"))

    plt.close("all")
    all_results[animal.name] = exploration_bouts_sec

import matplotlib.font_manager
print([f.name for f in matplotlib.font_manager.fontManager.ttflist if "hel" in f.name])

cleaned_results = {}
for key in all_results.keys():
    date_time_timestamp_regex = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}")
    try:
        date_time_timestamp = date_time_timestamp_regex.search(key).group(0)
        # Replace the date and time timestamp with the an empty string
        # Replace all remaining underscores, spcaces and dashes with a single underscore
        new_key = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}", "", key)
        new_key = re.sub(r"[_\s-]+", "_", new_key)
        cleaned_results[new_key] = all_results[key]
    except AttributeError:
        print(f"Could not find the date and time timestamp for the animal {key}")
        print("Using the complete animal name instead.")
        cleaned_results[key] = key

with pd.ExcelWriter(os.path.join(figures_folder, "Combined_results_by_sheet.xlsx"), engine="openpyxl") as writer:
    for animal_name, animal_df in cleaned_results.items():
        animal_df.to_excel(writer, sheet_name=animal_name, index=False)