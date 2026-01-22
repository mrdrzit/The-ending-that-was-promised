import matplotlib.pyplot as plt
import seaborn as sns

def plot_distance_vs_angle_mad(
    df,
    hue="outcome_type",
    alpha=0.6,
    s=25,
):
    fig, ax = plt.subplots(figsize=(7, 6))

    sns.scatterplot(
        data=df,
        x="distance_reduction",
        y="angle_mad",
        hue=hue,
        ax=ax,
        alpha=alpha,
        s=s,
    )

    ax.set_xlabel("Distance reduction toward ROI")
    ax.set_ylabel("Mean absolute angular deviation (deg)")
    ax.set_title("Approach geometry predicts outcome")

    ax.legend(title="Outcome", frameon=False)
    ax.grid(alpha=0.3)

    return fig
