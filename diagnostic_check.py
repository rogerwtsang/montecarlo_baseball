from src.data.scraper import load_data
from src.data.processor import prepare_lineup
from src.simulation.batch import run_simulations, print_simulation_results

df = load_data('blue_jays_2025_prepared.csv', 'processed')
df_sorted = df.sort_values('pa', ascending=False)
lineup = prepare_lineup(df_sorted.reset_index(drop=True), order=list(range(9)))

results = run_simulations(lineup, n_iterations=10000, verbose=1)
print_simulation_results(results)

print(f"\nActual 2025: 798 runs")
print(f"With SB module: {results['summary']['runs']['mean']:.1f} runs")
