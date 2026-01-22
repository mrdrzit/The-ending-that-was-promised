import numpy as np
import matplotlib.pyplot as plt


def _setup_polar_ax(ax):
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)


def plot_polar_separate_by_phase_context(
    approach,
    collision,
    retreat,
    bins=36,
    with_mean_vector=False,
):
    """
    Create one figure per (phase, context),
    with 3 rows: approach / collision / retreat.
    """

    dfs = {
        "approach": approach,
        "collision": collision,
        "retreat": retreat,
    }

    combos = (
        approach[["phase", "context"]]
        .drop_duplicates()
        .sort_values(["phase", "context"])
    )

    figures = {}

    for _, row in combos.iterrows():
        phase = row["phase"]
        context = row["context"]

        fig, axes = plt.subplots(
            3,
            1,
            subplot_kw={"projection": "polar"},
            figsize=(6, 12),
            constrained_layout=True,
        )

        for ax, (label, df) in zip(axes, dfs.items()):
            sub = df[
                (df["phase"] == phase) &
                (df["context"] == context)
            ]

            angles = np.deg2rad(sub["mean_angle_to_roi"].dropna().values)

            if len(angles) > 0:
                ax.hist(angles, bins=bins, density=True)

                if with_mean_vector:
                    mean_sin = np.mean(np.sin(angles))
                    mean_cos = np.mean(np.cos(angles))
                    R = np.sqrt(mean_sin**2 + mean_cos**2)
                    theta = np.arctan2(mean_sin, mean_cos)

                    ax.arrow(
                        theta, 0,
                        0, R,
                        width=0.02,
                        length_includes_head=True,
                        head_width=0.08,
                        head_length=0.08,
                    )

                    title = (
                        f"{label.capitalize()} | "
                        f"Mean: {np.rad2deg(theta):.1f}° | R={R:.2f}"
                    )
                else:
                    title = label.capitalize()
            else:
                title = f"{label.capitalize()} (no data)"

            ax.set_title(title)
            _setup_polar_ax(ax)

        fig.suptitle(f"Phase: {phase} | Context: {context}", fontsize=14)
        figures[(phase, context)] = fig

    return figures