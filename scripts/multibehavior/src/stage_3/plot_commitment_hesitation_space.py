import matplotlib.pyplot as plt
import seaborn as sns

def split_by_outcome(df, outcome_col="outcome_type"):
    """
    Split dataframe by outcome.
    Returns dict: outcome -> dataframe
    """
    out = {"all": df}

    for outcome, g in df.groupby(outcome_col):
        out[outcome] = g

    return out

def plot_commitment_vs_hesitation(
    df,
    hue="outcome_type",
    alpha=0.6,
    s=25,
):
    """
    Plot CI vs HI scatter and return outcome-separated data.
    """

    # --------------------
    # Split outcomes
    # --------------------
    outcome_dfs = {"all": df}
    for outcome, g in df.groupby(hue):
        outcome_dfs[outcome] = g

    # --------------------
    # Main combined figure
    # --------------------
    fig, ax = plt.subplots(figsize=(6.5, 6))

    sns.scatterplot(
        data=df,
        x="commitment_index",
        y="hesitation_index",
        hue=hue,
        alpha=alpha,
        s=s,
        ax=ax,
    )

    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.axvline(0, color="gray", linestyle="--", linewidth=1)

    ax.set_xlabel("Commitment index")
    ax.set_ylabel("Hesitation index")
    ax.set_title("Approach behavior decision space")

    ax.legend(title="Outcome", frameon=False)
    ax.grid(alpha=0.3)

    return fig, outcome_dfs

def plot_commitment_vs_hesitation_by_phase_context(
    df,
    hue="outcome_type",
    alpha=0.6,
    s=20,
):
    """
    Generate CI vs HI plots for each phase × context combination.

    Returns:
        dict[(phase, context)] -> fig
    """

    figures = {}

    combos = (
        df[["phase", "context"]]
        .drop_duplicates()
        .sort_values(["phase", "context"])
    )

    for _, row in combos.iterrows():
        phase = row["phase"]
        context = row["context"]

        sub = df[
            (df["phase"] == phase) &
            (df["context"] == context)
        ]

        if len(sub) == 0:
            continue

        fig, ax = plt.subplots(figsize=(6, 6))

        sns.scatterplot(
            data=sub,
            x="commitment_index",
            y="hesitation_index",
            hue=hue,
            alpha=alpha,
            s=s,
            ax=ax,
        )

        ax.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax.axvline(0, color="gray", linestyle="--", linewidth=1)

        ax.set_title(f"{phase.capitalize()} – Context {context}")
        ax.set_xlabel("Commitment index")
        ax.set_ylabel("Hesitation index")

        ax.legend(title="Outcome", frameon=False)
        ax.grid(alpha=0.3)

        figures[(phase, context)] = fig

    return figures

def plot_ci_hi_single_outcome(
    df,
    outcome,
    alpha=0.6,
    s=25,
):
    """
    Plot CI vs HI for a single outcome only.
    """

    sub = df[df["outcome_type"] == outcome]

    fig, ax = plt.subplots(figsize=(6, 6))

    sns.scatterplot(
        data=sub,
        x="commitment_index",
        y="hesitation_index",
        alpha=alpha,
        s=s,
        ax=ax,
    )

    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.axvline(0, color="gray", linestyle="--", linewidth=1)

    ax.set_xlabel("Commitment index")
    ax.set_ylabel("Hesitation index")
    ax.set_title(f"Approach decision space — {outcome.replace('_', ' ')}")

    ax.grid(alpha=0.3)

    return fig

def plot_ci_hi_single_outcome_by_phase_context(
    df,
    outcome,
    alpha=0.6,
    s=20,
):
    """
    Plot CI vs HI for a single outcome, split by phase × context.

    Returns:
        dict[(phase, context)] -> fig
    """

    figures = {}

    sub = df[df["outcome_type"] == outcome]

    combos = (
        sub[["phase", "context"]]
        .drop_duplicates()
        .sort_values(["phase", "context"])
    )

    for _, row in combos.iterrows():
        phase = row["phase"]
        context = row["context"]

        g = sub[
            (sub["phase"] == phase) &
            (sub["context"] == context)
        ]

        if len(g) == 0:
            continue

        fig, ax = plt.subplots(figsize=(6, 6))

        sns.scatterplot(
            data=g,
            x="commitment_index",
            y="hesitation_index",
            alpha=alpha,
            s=s,
            ax=ax,
        )

        ax.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax.axvline(0, color="gray", linestyle="--", linewidth=1)

        ax.set_title(
            f"{outcome.replace('_', ' ')}\n"
            f"{phase.capitalize()} – Context {context}"
        )
        ax.set_xlabel("Commitment index")
        ax.set_ylabel("Hesitation index")

        ax.grid(alpha=0.3)

        figures[(phase, context)] = fig

    return figures


def plot_ci_hi_single_outcome_by_context(
    df,
    outcome,
    alpha=0.6,
    s=25,
):
    """
    Plot CI vs HI for a single outcome,
    comparing Context A vs B (sessions pooled).
    """

    sub = df[df["outcome_type"] == outcome]

    fig, ax = plt.subplots(figsize=(6.5, 6))

    sns.scatterplot(
        data=sub,
        x="commitment_index",
        y="hesitation_index",
        hue="context",
        palette={"A": "#1f77b4", "B": "#d62728"},
        alpha=alpha,
        s=s,
        ax=ax,
    )

    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.axvline(0, color="gray", linestyle="--", linewidth=1)

    ax.set_xlabel("Commitment index")
    ax.set_ylabel("Hesitation index")
    ax.set_title(
        f"{outcome.replace('_', ' ')}\nContext comparison (sessions pooled)"
    )

    ax.legend(title="Context", frameon=False)
    ax.grid(alpha=0.3)

    return fig