import os
import pandas as pd

from config.paths import DERIVED
from src.stage_3.plot_latency_ecdf import plot_latency_ecdf_by_session_and_context
from src.stage_3.plot_polar_angles import plot_polar_separate_by_phase_context
from src.stage_3.plot_approach_geometry import plot_distance_vs_angle_mad
from src.stage_3.plot_sequence_archetypes import plot_sequence_archetypes_stacked
from src.stage_3.plot_transition_heatmaps import plot_transition_heatmap_by_phase, plot_transition_heatmap_by_context
from src.stage_3.plot_commitment_ecdf import plot_commitment_ecdf_by_session_and_context
from src.stage_3.plot_commitment_hesitation_space import (
    plot_commitment_vs_hesitation, 
    plot_commitment_vs_hesitation_by_phase_context, 
    plot_ci_hi_single_outcome,
    plot_ci_hi_single_outcome_by_phase_context,
    plot_ci_hi_single_outcome_by_context
)

from src.stage_3.plot_hesitation_ecdf import plot_hesitation_ecdf_by_session_and_context

from src.utils.load_events import load_events

def main():
    print("Stage 3 — figures ----------------------------------------------")

    # --------------------------------------------------
    # Latency ECDF plots
    # --------------------------------------------------
    print("Loading latency table...")
    latency_path = os.path.join(DERIVED, "approach_latency_table.parquet")
    latency_df = pd.read_parquet(latency_path)

    for outcome in ["collision", "abortive_retreat"]:
        print(f"Plotting ECDF for outcome: {outcome}")
        fig = plot_latency_ecdf_by_session_and_context(latency_df, outcome=outcome)
        out_path = os.path.join(DERIVED, f"latency_ecdf_{outcome}.png")
        fig.savefig(out_path, dpi=300, bbox_inches="tight")

    # --------------------------------------------------
    # Approach geometry plot
    # --------------------------------------------------
    print("Loading approach geometry table...")
    geom_path = os.path.join(DERIVED, "approach_geometry_table.parquet")
    geom_df = pd.read_parquet(geom_path)

    print("Generating Figure 5...")
    fig = plot_distance_vs_angle_mad(geom_df)

    out_path = os.path.join(DERIVED, "Approach_geometry.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")

    # --------------------------------------------------
    # Polar angle plots
    # --------------------------------------------------
    print("Loading event tables...")
    approach = load_events("approach")
    collision = load_events("collision")
    retreat = load_events("retreat")

    out_dir = os.path.join(DERIVED, "polar_plots")
    os.makedirs(out_dir, exist_ok=True)

    print("Generating polar plots...")
    figures = plot_polar_separate_by_phase_context(approach, collision, retreat, bins=36, with_mean_vector=True)
    for (phase, context), fig in figures.items():
        fname = f"polar_angles_phase_{phase}_context_{context}.png"
        path = os.path.join(out_dir, fname)
        fig.savefig(path, dpi=300, bbox_inches="tight")

    print("Loading sequence archetypes...")
    seq_path = os.path.join(DERIVED, "sequence_archetypes.parquet")
    seq_df = pd.read_parquet(seq_path)

    print("Generating Figure 8...")
    fig = plot_sequence_archetypes_stacked(seq_df)
    out_path = os.path.join(DERIVED, "sequence_archetypes.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")

    print("Loading transition matrices...")
    transition_matrix_by_context = pd.read_parquet(os.path.join(DERIVED, "transition_matrix_by_context.parquet"))
    transition_matrix_by_phase = pd.read_parquet(os.path.join(DERIVED, "transition_matrix_by_phase.parquet"))

    print("Plotting transition heatmaps...")
    fig_main = plot_transition_heatmap_by_context(transition_matrix_by_context)
    fig_supp = plot_transition_heatmap_by_phase(transition_matrix_by_phase)
    fig_main.savefig(os.path.join(DERIVED, "figure_transition_heatmap.png"), dpi=300, bbox_inches="tight")
    fig_supp.savefig(os.path.join(DERIVED, "figure_S_transition_heatmap_phase.png"), dpi=300, bbox_inches="tight")
    print("Saved transition heatmaps")

    print("Loading commitment index table...")
    commitment_df = pd.read_parquet(os.path.join(DERIVED, "approach_commitment_index.parquet"))
    
    print("Plotting ECDF of commitment index...")
    fig = plot_commitment_ecdf_by_session_and_context(commitment_df)
    out_path = os.path.join(DERIVED, "commitment_index_ecdf.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")

    print("Loading CI/HI table...")
    latent_df = pd.read_parquet(os.path.join(DERIVED, "approach_latent_indices.parquet"))

    # ----------------------------------
    # CI vs HI scatter
    # ----------------------------------
    print("Plotting CI vs HI...")
    fig, _ = plot_commitment_vs_hesitation(latent_df)
    out_path = os.path.join(DERIVED, "figure_commitment_vs_hesitation.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")

    # ----------------------------------
    # HI ECDF
    # ----------------------------------
    print("Plotting ECDF of hesitation index...")
    fig = plot_hesitation_ecdf_by_session_and_context(latent_df)
    out_path = os.path.join(DERIVED, "hesitation_index_ecdf.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    latent_df = pd.read_parquet(os.path.join(DERIVED, "approach_latent_indices.parquet"))

    # ------------------------
    # Main figure
    # ------------------------
    fig, _ = plot_commitment_vs_hesitation(latent_df)
    fig.savefig(os.path.join(DERIVED, "figure_commitment_vs_hesitation.png"), dpi=300, bbox_inches="tight")

    # ------------------------
    # Phase × Context figures
    # ------------------------
    figures = plot_commitment_vs_hesitation_by_phase_context(latent_df)
    out_dir = os.path.join(DERIVED, "commitment_hesitation_by_phase_context")
    os.makedirs(out_dir, exist_ok=True)

    for (phase, context), fig in figures.items():
        fname = f"CI_HI_{phase}_context_{context}.png"
        fig.savefig(os.path.join(out_dir, fname), dpi=300, bbox_inches="tight")

    # ------------------------
    # Single outcome figures

    latent_df = pd.read_parquet(os.path.join(DERIVED, "approach_latent_indices.parquet"))

    outcomes = ["collision", "approach_only", "abortive_retreat"]
    out_dir = os.path.join(DERIVED, "CI_HI_by_outcome")
    os.makedirs(out_dir, exist_ok=True)

    for outcome in outcomes:
        # -------------------------
        # Pooled plot (ALL sessions, ALL contexts)
        # -------------------------
        fig = plot_ci_hi_single_outcome(latent_df, outcome)
        fig.savefig(os.path.join(out_dir, f"CI_HI_{outcome}.png"), dpi=300, bbox_inches="tight")

        # -------------------------
        # Phase × context plots (ALL combinations)
        # -------------------------
        figs = plot_ci_hi_single_outcome_by_phase_context(latent_df, outcome)

        subdir = os.path.join(out_dir, outcome)
        os.makedirs(subdir, exist_ok=True)

        for (phase, context), fig in figs.items():
            fname = f"CI_HI_{outcome}_{phase}_context_{context}.png"
            fig.savefig(os.path.join(subdir, fname), dpi=300, bbox_inches="tight")

    print("Plotting CI vs HI by context (sessions pooled)...")
    latent_df = pd.read_parquet(os.path.join(DERIVED, "approach_latent_indices.parquet") )
    outcomes = ["collision", "approach_only", "abortive_retreat"]
    out_dir = os.path.join(DERIVED, "CI_HI_by_outcome_context")
    os.makedirs(out_dir, exist_ok=True)

    for outcome in outcomes:
        fig = plot_ci_hi_single_outcome_by_context(latent_df, outcome)
        out_path = os.path.join(out_dir, f"CI_HI_{outcome}_context_comparison.png")
        fig.savefig(out_path, dpi=300, bbox_inches="tight")

    print("Stage 3 complete.")

if __name__ == "__main__":
    main()