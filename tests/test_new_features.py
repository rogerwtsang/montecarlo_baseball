"""Test script for sacrifice flies and probabilistic base-running."""

from src.data.scraper import load_data
from src.data.processor import prepare_lineup
from src.simulation.batch import run_simulations, print_simulation_results
import config

print("=== Testing New Features ===\n")

# Display config settings
print("Configuration:")
print(f"  ENABLE_STOLEN_BASES: {config.ENABLE_STOLEN_BASES}")
print(f"  ENABLE_SACRIFICE_FLIES: {config.ENABLE_SACRIFICE_FLIES}")
print(f"  ENABLE_PROBABILISTIC_BASERUNNING: {config.ENABLE_PROBABILISTIC_BASERUNNING}")
print(f"  FLYOUT_PERCENTAGE: {config.FLYOUT_PERCENTAGE}")
print(f"  Baserunning aggression:")
print(f"    Single 1st→3rd: {config.BASERUNNING_AGGRESSION['single_1st_to_3rd']}")
print(f"    Double 1st scores: {config.BASERUNNING_AGGRESSION['double_1st_scores']}")
print(f"    Double 2nd scores: {config.BASERUNNING_AGGRESSION['double_2nd_scores']}")

# Load 2025 Blue Jays
df = load_data('blue_jays_2025_prepared.csv', 'processed')
df_sorted = df.sort_values('pa', ascending=False)
lineup = prepare_lineup(df_sorted.reset_index(drop=True), order=list(range(9)))

print("\nLineup:")
for i, p in enumerate(lineup, 1):
    print(f"  {i}. {p.name}: {p.ba:.3f}/{p.obp:.3f}/{p.slg:.3f}")

# Run simulation
print("\n" + "="*80)
print("Running 10,000 simulations with all features enabled...")
print("="*80 + "\n")

results = run_simulations(lineup, n_iterations=10000, verbose=1)
print_simulation_results(results)

# Compare to actual
actual_runs = 798
simulated_runs = results['summary']['runs']['mean']
improvement = simulated_runs - 540.4  # Previous baseline
gap = actual_runs - simulated_runs

print("\n" + "="*80)
print("COMPARISON TO ACTUAL 2025 SEASON")
print("="*80)
print(f"  Actual 2025 runs:     {actual_runs}")
print(f"  Simulated (previous): 540.4 runs (gap: 257.6)")
print(f"  Simulated (current):  {simulated_runs:.1f} runs (gap: {gap:.1f})")
print(f"  Improvement:          +{improvement:.1f} runs")
print(f"  Remaining gap:        {(gap/actual_runs)*100:.1f}%")

# Feature contribution estimates
summary = results['summary']
if 'stolen_bases' in summary:
    sb_contribution = summary['stolen_bases']['mean'] * 0.17  # ~0.17 runs per SB
    cs_cost = summary['caught_stealing']['mean'] * 0.5  # ~0.5 runs per CS
    sb_net = sb_contribution - cs_cost
    print(f"\nStolen bases net contribution: ~{sb_net:.1f} runs")

if 'sacrifice_flies' in summary:
    sf_contribution = summary['sacrifice_flies']['mean'] * 1.0  # Each SF = 1 run
    print(f"Sacrifice flies contribution: ~{sf_contribution:.1f} runs")

# Estimate probabilistic baserunning contribution
# This is harder to isolate, but we can estimate from improvement
other_improvement = improvement - sb_net - sf_contribution if 'stolen_bases' in summary and 'sacrifice_flies' in summary else improvement
print(f"Probabilistic baserunning (estimated): ~{other_improvement:.1f} runs")

print("\n" + "="*80)
