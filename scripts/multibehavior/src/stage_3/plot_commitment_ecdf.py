import numpy as np
import matplotlib.pyplot as plt

def plot_commitment_ecdf_by_session_and_context(
    df,
    session_order=("tra", "trb", "tta", "ttb"),
    contexts=("A", "B"),
    figsize=(8, 6),
):
    """
    ECDF of commitment index, stratified by session × context.
    """

    fig, ax = plt.subplots(figsize=figsize)

    for session in session_order:
        for context in contexts:
            sub = df[
                (df["group"] == session) &
                (df["context"] == context)
            ]["commitment_index"].dropna().values

            if len(sub) == 0:
                continue

            x = np.sort(sub)
            y = np.arange(1, len(x) + 1) / len(x)

            ax.plot(
                x,
                y,
                linewidth=2,
                label=f"{session.upper()} - {context}"
            )

    ax.set_xlabel("Commitment index")
    ax.set_ylabel("Cumulative fraction")
    ax.set_title("ECDF of approach commitment")

    ax.set_ylim(0, 1.01)
    ax.set_xlim(-6, 6)
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)

    return fig
