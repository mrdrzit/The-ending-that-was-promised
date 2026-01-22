import os
import pandas as pd

from config.paths import EVENTS, DERIVED, EXCEL
from src.utils.organize_tables import organize_table
from src.utils.build_bout_outcomes import build_animal_bout_outcomes
from src.utils.build_bout_counts import build_animal_bout_counts
from src.utils.build_latency_table import build_latency_table
from src.utils.build_duration_table import build_approach_duration_table, summarize_approach_durations
from src.utils.build_geometry_table import build_approach_geometry_table
from src.utils.build_sequence_archetypes import build_sequence_archetype_table
from src.utils.build_latent_indices import build_latent_indices_table
from src.utils.build_transition_matrices import build_transition_matrix_by_phase, build_transition_matrix_by_context

def load_events(event_type):
    files = sorted((EVENTS / event_type).glob("*.parquet"))
    dfs = [pd.read_parquet(f) for f in files]
    return pd.concat(dfs, ignore_index=True)

def main():
    print("Stage 2 — aggregating event tables --------------------------------")

    DERIVED.mkdir(exist_ok=True)
    print("Table output directory ensured")

    approach = load_events("approach")
    collision = load_events("collision")
    retreat = load_events("retreat")
    sequences = load_events("sequences")
    print("Loaded event tables")

    sequence_archetypes = build_sequence_archetype_table(sequences)
    sequence_archetypes.to_parquet(os.path.join(DERIVED, "sequence_archetypes.parquet"))
    sequence_archetypes.to_excel(os.path.join(EXCEL, "sequence_archetypes.xlsx"), index=False)
    print("Saved sequence archetype table")

    bout_counts = build_animal_bout_counts(approach, collision, retreat)
    bout_counts = organize_table(bout_counts)
    bout_counts.to_parquet(os.path.join(DERIVED, "animal_bout_counts.parquet"))
    bout_counts.to_excel(os.path.join(EXCEL, "animal_bout_counts.xlsx"), index=False)
    print("Saved animal bout counts")

    bout_outcomes = build_animal_bout_outcomes(approach, collision, retreat, sequences)
    bout_outcomes = organize_table(bout_outcomes)
    bout_outcomes.to_parquet(os.path.join(DERIVED, "animal_bout_outcomes.parquet"))
    bout_outcomes.to_excel(os.path.join(EXCEL, "animal_bout_outcomes.xlsx"), index=False)
    print("Saved animal bout outcomes and rates")

    latency_table = build_latency_table(sequences)
    latency_table = organize_table(latency_table)
    latency_table.to_parquet(os.path.join(DERIVED, "approach_latency_table.parquet"))
    latency_table.to_excel(os.path.join(EXCEL, "approach_latency_table.xlsx"),index=False)
    print("Saved latency table")

    approach_duration_table = build_approach_duration_table(approach)
    approach_duration_table.to_parquet(os.path.join(DERIVED, "approach_duration_table.parquet"))
    approach_duration_table.to_excel(os.path.join(EXCEL, "approach_duration_table.xlsx"),index=False)
    print("Saved approach duration table")

    approach_duration_summary = summarize_approach_durations(approach_duration_table)
    approach_duration_summary = organize_table(approach_duration_summary)
    approach_duration_summary.to_parquet(os.path.join(DERIVED, "approach_duration_summary.parquet"))
    approach_duration_summary.to_excel(os.path.join(EXCEL, "approach_duration_summary.xlsx"), index=False)
    print("Saved summarized approach duration table")

    approach_geometry, organized_approach_geometry = build_approach_geometry_table(approach, sequences)
    approach_geometry = organize_table(approach_geometry)
    organized_approach_geometry = organize_table(organized_approach_geometry)
    approach_geometry.to_parquet(os.path.join(DERIVED, "approach_geometry_table.parquet"))
    organized_approach_geometry.to_excel(os.path.join(EXCEL, "approach_geometry_table_organized.xlsx"), index=False)
    approach_geometry.to_excel(os.path.join(EXCEL, "approach_geometry_table.xlsx"), index=False)
    print("Saved approach geometry table")

    print("Building transition matrices by context...")
    transition_df = build_transition_matrix_by_context(sequences)
    transition_df.to_parquet(os.path.join(DERIVED, "transition_matrix_by_context.parquet"))
    transition_df.to_excel(os.path.join(EXCEL, "transition_matrix_by_context.xlsx"),index=False)
    print("Saved transition matrix table")

    print("Building transition matrices by phase...")
    transition_df_phase = build_transition_matrix_by_phase(sequences)
    transition_df_phase.to_parquet(os.path.join(DERIVED, "transition_matrix_by_phase.parquet"))
    transition_df_phase.to_excel(os.path.join(EXCEL, "transition_matrix_by_phase.xlsx"),index=False)
    print("Saved transition matrix by phase table")

    print("Building latent indices table...")
    geometry_df = pd.read_parquet(os.path.join(DERIVED, "approach_geometry_table.parquet"))
    duration_df = pd.read_parquet(os.path.join(DERIVED, "approach_duration_table.parquet"))
    latent_df, organized_approach_geometry = build_latent_indices_table(geometry_df, duration_df)
    latent_df.to_parquet(os.path.join(DERIVED, "approach_latent_indices.parquet"))
    latent_df.to_excel(os.path.join(EXCEL, "approach_latent_indices.xlsx"), index=False)
    organized_approach_geometry = organize_table(organized_approach_geometry)
    organized_approach_geometry.to_excel(os.path.join(EXCEL, "approach_latent_indices_table_organized.xlsx"), index=False)
    print("Saved latent indices table")

if __name__ == "__main__":
    main()