# ============================================================================
# src/simulation/season.py
# ============================================================================
"""Season simulation."""

from typing import List, Dict
from src.models.player import Player
from src.engine.game import simulate_game
from src.engine.pa_generator import PAOutcomeGenerator
import config


def simulate_season(
    lineup: List[Player],
    pa_generator: PAOutcomeGenerator,
    n_games: int = config.N_GAMES_PER_SEASON
) -> Dict:
    """Simulate a full season of games.

    Args:
        lineup: List of 9 Player objects in batting order
        pa_generator: PAOutcomeGenerator instance
        n_games: Number of games in season (default: 162)

    Returns:
        Dictionary with season results
    """
    total_runs = 0
    total_hits = 0
    total_walks = 0
    total_lob = 0
    total_sb = 0
    total_cs = 0
    total_sf = 0

    game_results = []

    for game_num in range(1, n_games + 1):
        game_result = simulate_game(lineup, pa_generator, n_innings=9)

        total_runs += game_result['total_runs']
        total_hits += game_result['total_hits']
        total_walks += game_result['total_walks']
        total_lob += game_result['total_lob']
        total_sb += game_result.get('total_sb', 0)
        total_cs += game_result.get('total_cs', 0)
        total_sf += game_result.get('total_sf', 0)

        game_results.append({
            'game_num': game_num,
            'runs': game_result['total_runs'],
            'hits': game_result['total_hits'],
            'walks': game_result['total_walks']
        })

    return {
        'total_runs': total_runs,
        'total_hits': total_hits,
        'total_walks': total_walks,
        'total_lob': total_lob,
        'total_sb': total_sb,
        'total_cs': total_cs,
        'total_sf': total_sf,
        'games_played': n_games,
        'avg_runs_per_game': total_runs / n_games,
        'game_results': game_results
    }


if __name__ == "__main__":
    # Test season simulation
    import sys
    sys.path.insert(0, '.')
    from src.data.scraper import load_data
    from src.data.processor import prepare_lineup

    print("=== Testing Season Simulation ===\n")

    # Load test data
    try:
        df = load_data('blue_jays_2025_prepared.csv', 'processed')
    except:
        df = load_data('blue_jays_2024_prepared.csv', 'processed')

    # Create lineup
    lineup = prepare_lineup(df)
    print(f"Created lineup with {len(lineup)} players")
    print(f"Top 3 hitters:")
    for i in range(3):
        p = lineup[i]
        print(f"  {i+1}. {p.name}: {p.ba:.3f}/{p.obp:.3f}/{p.slg:.3f}")

    # Create PA generator
    pa_gen = PAOutcomeGenerator(random_state=42)

    # Simulate one season
    print(f"\n--- Simulating {config.N_GAMES_PER_SEASON}-game season ---")
    result = simulate_season(lineup, pa_gen, n_games=config.N_GAMES_PER_SEASON)

    print(f"\nSeason Results:")
    print(f"  Total runs: {result['total_runs']}")
    print(f"  Total hits: {result['total_hits']}")
    print(f"  Total walks: {result['total_walks']}")
    print(f"  Games played: {result['games_played']}")
    print(f"  Runs per game: {result['avg_runs_per_game']:.2f}")

    # Show first 10 games
    print(f"\nFirst 10 games:")
    for game in result['game_results'][:10]:
        print(f"  Game {game['game_num']}: {game['runs']} runs, {game['hits']} hits")

    # Sanity checks
    print("\n--- Sanity Checks ---")

    if 400 <= result['total_runs'] <= 1000:
        print(f"✓ Total runs reasonable ({result['total_runs']})")
    else:
        print(f"⚠ Total runs unusual ({result['total_runs']})")

    if 3.0 <= result['avg_runs_per_game'] <= 6.0:
        print(f"✓ Average runs per game reasonable ({result['avg_runs_per_game']:.2f})")
    else:
        print(f"⚠ Average runs per game unusual ({result['avg_runs_per_game']:.2f})")

    print("\n" + "="*60)
    print("✓ Season simulation test complete")
