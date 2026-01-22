import matplotlib.pyplot as plt

def plot_sequence_archetypes_stacked(df):
    """
    Create stacked bar plots of outcome proportions.
    One panel per context.
    """

    contexts = sorted(df["context"].unique())
    sessions = ["tra", "trb", "tta", "ttb"]
    outcomes = ["collision", "abortive_retreat", "approach_only"]

    fig, axes = plt.subplots(
        1,
        len(contexts),
        figsize=(10, 4),
        sharey=True,
        constrained_layout=True
    )

    if len(contexts) == 1:
        axes = [axes]

    for ax, context in zip(axes, contexts):
        sub = df[df["context"] == context]

        bottom = {s: 0 for s in sessions}

        for outcome in outcomes:
            vals = []
            for s in sessions:
                v = sub[
                    (sub["group"] == s) &
                    (sub["outcome_type"] == outcome)
                ]["proportion"]

                vals.append(v.iloc[0] if len(v) else 0)

            ax.bar(
                sessions,
                vals,
                bottom=[bottom[s] for s in sessions],
                label=outcome
            )

            for i, s in enumerate(sessions):
                bottom[s] += vals[i]

        ax.set_title(f"Context {context}")
        ax.set_xlabel("Session")
        ax.set_ylim(0, 1)

    axes[0].set_ylabel("Proportion of approaches")
    axes[0].legend(frameon=False)

    return fig
