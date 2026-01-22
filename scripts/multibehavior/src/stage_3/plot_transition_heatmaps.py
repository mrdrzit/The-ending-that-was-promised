import matplotlib.pyplot as plt
import seaborn as sns

def plot_transition_heatmap_by_context(df):
    """
    Heatmap of P(outcome | approach) for each context.
    """

    outcomes = ["collision", "abortive_retreat", "approach_only"]
    contexts = sorted(df["context"].unique())

    fig, axes = plt.subplots(
        1,
        len(contexts),
        figsize=(8, 3),
        sharey=True,
        constrained_layout=True
    )

    if len(contexts) == 1:
        axes = [axes]

    vmax = df["probability"].max()

    for ax, context in zip(axes, contexts):
        sub = df[df["context"] == context]

        mat = (
            sub
            .set_index("outcome_type")
            .reindex(outcomes)
            [["probability"]]
        )

        sns.heatmap(
            mat,
            ax=ax,
            annot=True,
            fmt=".2f",
            cmap="viridis",
            vmin=0,
            vmax=vmax,
            cbar=ax is axes[-1]
        )

        ax.set_title(f"Context {context}")
        ax.set_xlabel("")
        ax.set_ylabel("Outcome" if ax is axes[0] else "")

    return fig

def plot_transition_heatmap_by_phase(df):
    outcomes = ["collision", "abortive_retreat", "approach_only"]
    phases = ["treino", "teste"]
    contexts = ["A", "B"]

    fig, axes = plt.subplots(
        2, 2, figsize=(8, 6),
        sharex=True, sharey=True,
        constrained_layout=True
    )

    vmax = df["probability"].max()

    for i, phase in enumerate(phases):
        for j, context in enumerate(contexts):
            ax = axes[i][j]

            sub = (
                df[(df["phase"] == phase) & (df["context"] == context)]
                .set_index("outcome_type")
                .reindex(outcomes)
            )

            sns.heatmap(
                sub[["probability"]],
                annot=True,
                fmt=".2f",
                cmap="viridis",
                vmin=0,
                vmax=vmax,
                cbar=(i == 0 and j == 1),
                ax=ax
            )

            ax.set_title(f"{phase.capitalize()} – Context {context}")

    axes[0][0].set_ylabel("Outcome")
    axes[1][0].set_ylabel("Outcome")

    return fig
