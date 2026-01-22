import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use('Qt5Agg') 

def plot_latency_ecdf_by_session_and_context(df, outcome, session_order=("tra", "trb", "tta", "ttb"), contexts=("A", "B"), figsize=(8, 6)):
    fig, ax = plt.subplots(figsize=figsize)

    for session in session_order:
        for context in contexts:
            sub = df[
                (df["group"] == session) &
                (df["context"] == context) &
                (df["outcome"] == outcome)
            ]["latency_sec"].dropna().values

            if len(sub) == 0:
                continue

            x = np.sort(sub)
            y = np.arange(1, len(x) + 1) / len(x)

            ax.plot(x, y, linewidth=2, label=f"{session.upper()} - {context}")

    ax.set_xlabel("Latency (s)")
    ax.set_ylabel("Cumulative fraction")
    ax.set_title(f"ECDF of approach → {outcome.replace('_', ' ')} latency")

    ax.set_ylim(0, 1.01)
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)

    return fig