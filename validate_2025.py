from src.data.scraper import load_data
from src.data.processor import prepare_lineup
from src.simulation.batch import run_simulations
from src.engine.pa_generator import PAOutcomeGenerator

# from src.data.scraper import get_team_batting_stats, prepare_player_stats, save_data
#
# tor_2025 = get_team_batting_stats('TOR',2025)
# prepared = prepare_player_stats(tor_2025, min_pa=100)
# save_data(prepared, 'blue_jays_2025_prepared.csv','processed')

# Load data
df = load_data('blue_jays_2025_prepared.csv', 'processed')

# Get top 9 by PA
df_sorted = df.sort_values('pa', ascending=False)
top_9_indices = list(range(9))

# Create lineup
lineup = prepare_lineup(df_sorted.reset_index(drop=True), order=top_9_indices)

# Print lineup
print("Actual 2025 Blue Jays Lineup (by PA):")
for i, p in enumerate(lineup, 1):
    print(f"  {i}. {p.name}: {p.ba:.3f}/{p.obp:.3f}/{p.slg:.3f}")

# Run simulation
results = run_simulations(lineup, n_iterations=10000, verbose=1)

print(f"\nActual 2025: 798 runs")
print(f"Simulated:   {results['summary']['runs']['mean']:.1f} runs")
print(f"Difference:  {798 - results['summary']['runs']['mean']:.1f} runs")
