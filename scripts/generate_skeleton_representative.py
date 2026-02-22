import matplotlib.pyplot as plt
import numpy as np
import cv2
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from dlc_helper_functions import *
import matplotlib
matplotlib.use("Qt5Agg")
# ==========================
# CONFIG
# ==========================
FRAME_IDX = 5          # escolha um frame bonito
LIKELIHOOD_TH = 0.8
DPI = 300
POINT_SIZE = 10
LINE_WIDTH = 0.5
LABEL_OFFSET = 15

# ==========================
# LOAD ROI
# ==========================
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Select ROI file",
    filetypes=[("CSV files", "*.csv")]
)
roi = pd.read_csv(file_path)
roi.columns = roi.columns.str.lower()

roi_x = roi["x"][0]
roi_y = roi["y"][0]
roi_d = roi["width"][0]

# ==========================
# LOAD VIDEO
# ==========================
root = tk.Tk()
root.withdraw()
video_path = filedialog.askopenfilename(
    title="Select video file",
    filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
)

# ==========================
# LOAD DLC DATA
# ==========================
data = DataFiles()
animals = []
get_files([], data, animals)

animal = animals[0]
dimensions = animal.exp_dimensions()
VIDEO_H, VIDEO_W, _ = dimensions

# ==========================
# BODY PART CONFIG
# ==========================
bodyparts = {
    "focinho": {
        "color": "#fe8081",
        "size": 3,
        "alpha": 0.8,
        "label": True,
        "label_size": 4,
        "label_dx": -85,
        "label_dy": 20
    },
    "orelhae": {
        "color": "#fe8081",
        "size": 3,
        "alpha": 0.8,
        "label": True,
        "label_size": 4,
        "label_dx": 0,
        "label_dy": 25
    },
    "orelhad": {
        "color": "#fe8081",
        "size": 3,
        "alpha": 0.8,
        "label": True,
        "label_size": 4,
        "label_dx": -90,
        "label_dy": -15
    },
    "centro": {
        "color": "#fe8081",
        "size": 3,
        "alpha": 0.8,
        "label": True,
        "label_size": 4,
        "label_dx": -35,
        "label_dy": -10
    },
    "rabo": {
        "color": "#fe8081",
        "size": 3,
        "alpha": 0.8,
        "label": True,
        "label_size": 4,
        "label_dx": 0,
        "label_dy": -10
    }
}

# skeleton connections
skeleton = [
    ("focinho", "orelhae"),
    ("focinho", "orelhad"),
    ("orelhae", "orelhad"),
    ("orelhad", "centro"),
    ("orelhae", "centro"),
    ("centro", "rabo")
]

# Dict to correct partname 
partname_corrections = {
    "focinho": "Focinho",
    "orelhae": "Orelha E",
    "orelhad": "Orelha D",
    "centro": "Centro",
    "rabo": "Rabo"
}

# ==========================
# READ FRAME
# ==========================
cap = cv2.VideoCapture(video_path)

cap.set(cv2.CAP_PROP_POS_FRAMES, FRAME_IDX)
ret, frame = cap.read()
cap.release()

if not ret:
    raise RuntimeError(f"Could not read frame {FRAME_IDX}")

# OpenCV -> matplotlib (BGR → RGB)
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# ==========================
# FIGURE
# ==========================
fig, ax = plt.subplots(figsize=(VIDEO_W / DPI, VIDEO_H / DPI), dpi=DPI)
ax.axis("off")
ax.imshow(frame_rgb)
ax.set_facecolor((0, 0, 0, 0))
fig.patch.set_alpha(0)


# ==========================
# ROI
# ==========================
cup = plt.Circle(
    (roi_x, roi_y),
    roi_d / 2,
    edgecolor="#fe8081",
    facecolor="none",
    linewidth=0.5
)
ax.add_patch(cup)

# ==========================
# PLOT KEYPOINTS
# ==========================
coords = {}

for bp, cfg in bodyparts.items():
    if bp not in animal.bodyparts:
        continue

    x = animal.bodyparts[bp]["x"][FRAME_IDX]
    y = animal.bodyparts[bp]["y"][FRAME_IDX]
    p = animal.bodyparts[bp]["likelihood"][FRAME_IDX]

    if p < LIKELIHOOD_TH:
        continue

    coords[bp] = (x, y)

    ax.scatter(
        x, y,
        s=cfg.get("size", 8),
        color=cfg.get("color", "white"),
        alpha=cfg.get("alpha", 1.0),
        zorder=3
    )

    if cfg.get("label", False):
        ax.text(
            x + cfg.get("label_dx", 0),
            y + cfg.get("label_dy", 0),
            bp if bp not in partname_corrections else partname_corrections[bp],
            fontsize=cfg.get("label_size", 2),
            color="white",
            fontname="Helvetica",
            zorder=4
        )

# ==========================
# PLOT SKELETON
# ==========================
for a, b in skeleton:
    if a in coords and b in coords:
        xa, ya = coords[a]
        xb, yb = coords[b]

        ax.plot(
            [xa, xb],
            [ya, yb],
            color="white",
            linewidth=0.2,
            zorder=2
        )

# ==========================
# SAVE
# ==========================
out = "C:\\Users\\uzuna\\Desktop\\representativa_pose\\representativa_pose.png"
plt.savefig(out, dpi=DPI, bbox_inches="tight", pad_inches=0)
plt.close()

print(f"Saved: {out}")
