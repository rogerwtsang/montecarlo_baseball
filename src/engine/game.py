# ============================================================================
# src/engine/game.py
# ============================================================================
"""Full game simulation."""

from typing import List, Dict
from src.models.player import Player
from src.engine.inning import simulate_half_inning
from src.engine.pa_generator import PAOutcomeGenerator


def simulate_game(
    lineup: List[Player],
    pa_generator: PAOutcomeGenerator,
    n_innings: int = 9
) -> Dict:
    """Simulate a complete baseball game (offensive side only).

    For now, simulates only the team's offense across 9 innings.
    Does not simulate opponent or track wins/losses.

    Args:
        lineup: List of 9 Player objects in batting order
        pa_generator: PAOutcomeGenerator instance
        n_innings: Number of innings (9 for regulation)

    Returns:
        Dictionary with game results
    """
    total_runs = 0
    total_hits = 0
    total_walks = 0
    total_lob = 0
    total_sb = 0
    total_cs = 0
    total_sf = 0

    batter_idx = 0  # Start with leadoff batter
    inning_results = []

    for inning in range(1, n_innings + 1):
        runs, next_batter, stats = simulate_half_inning(lineup, batter_idx, pa_generator)

        total_runs += runs
        total_hits += stats['hits']
        total_walks += stats['walks']
        total_lob += stats['lob']
        total_sb += stats.get('sb_success', 0)
        total_cs += (stats.get('sb_attempts', 0) - stats.get('sb_success', 0))
        total_sf += stats.get('sac_flies', 0)

        inning_results.append({
            'inning': inning,
            'runs': runs,
            'hits': stats['hits'],
            'walks': stats['walks'],
            'lob': stats['lob']
        })

        batter_idx = next_batter

    return {
        'total_runs': total_runs,
        'total_hits': total_hits,
        'total_walks': total_walks,
        'total_lob': total_lob,
        'total_sb': total_sb,
        'total_cs': total_cs,
        'total_sf': total_sf,
        'innings_played': n_innings,
        'inning_results': inning_results
    }


def simulate_game_with_opponent(
    home_lineup: List[Player],
    away_lineup: List[Player],
    pa_generator: PAOutcomeGenerator,
    max_innings: int = 9
) -> Dict:
    """Simulate a complete baseball game with both teams (with extra innings).

    Args:
        home_lineup: Home team lineup (9 players)
        away_lineup: Away team lineup (9 players)
        pa_generator: PAOutcomeGenerator instance
        max_innings: Minimum innings (9 for regulation, plays extra if tied)

    Returns:
        Dictionary with game results for both teams
    """
    home_score = 0
    away_score = 0

    home_batter_idx = 0
    away_batter_idx = 0

    home_innings = []
    away_innings = []

    inning = 1

    while inning <= max_innings or home_score == away_score:
        # Top of inning (away team bats)
        runs, away_batter_idx, stats = simulate_half_inning(
            away_lineup, away_batter_idx, pa_generator
        )
        away_score += runs
        away_innings.append({
            'inning': inning,
            'runs': runs,
            'hits': stats['hits']
        })

        # Bottom of inning (home team bats)
        # Walk-off: if home team leads after batting in bottom of 9th+, game ends
        if inning >= max_innings and home_score > away_score:
            break

        runs, home_batter_idx, stats = simulate_half_inning(
            home_lineup, home_batter_idx, pa_generator
        )
        home_score += runs
        home_innings.append({
            'inning': inning,
            'runs': runs,
            'hits': stats['hits']
        })

        # Walk-off check
        if inning >= max_innings and home_score > away_score:
            break

        inning += 1

    return {
        'home_score': home_score,
        'away_score': away_score,
        'innings_played': inning,
        'winner': 'home' if home_score > away_score else 'away',
        'home_innings': home_innings,
        'away_innings': away_innings
    }


if __name__ == "__main__":
    # Test game simulation
    import sys
    sys.path.insert(0, '.')
    from src.data.scraper import load_data
    from src.data.processor import prepare_lineup

    print("=== Testing Game Simulation ===\n")

    # Load test data
    try:
        df = load_data('blue_jays_2025_prepared.csv', 'processed')
    except:
        df = load_data('blue_jays_2024_prepared.csv', 'processed')

    # Create lineup
    lineup = prepare_lineup(df)
    print(f"Created lineup with {len(lineup)} players")

    # Create PA generator
    pa_gen = PAOutcomeGenerator(random_state=42)

    # Test 1: Single game (offense only)
    print("\n--- Test 1: Single game (offense only) ---")
    result = simulate_game(lineup, pa_gen, n_innings=9)

    print(f"\nGame Result:")
    print(f"  Total runs: {result['total_runs']}")
    print(f"  Total hits: {result['total_hits']}")
    print(f"  Total walks: {result['total_walks']}")
    print(f"  Total LOB: {result['total_lob']}")
    print(f"  Innings: {result['innings_played']}")

    print(f"\nInning-by-inning:")
    for inning_stat in result['inning_results']:
        print(f"  Inning {inning_stat['inning']}: {inning_stat['runs']} runs, "
              f"{inning_stat['hits']} hits")

    # Test 2: Multiple games to get averages
    print("\n--- Test 2: Simulating 162 games ---")
    pa_gen.set_seed(42)

    total_season_runs = 0
    games_played = 162
    min_game_runs = float('inf')
    max_game_runs = 0

    for _ in range(games_played):
        result = simulate_game(lineup, pa_gen, n_innings=9)
        total_season_runs += result['total_runs']
        min_game_runs = min(min_game_runs, result['total_runs'])
        max_game_runs = max(max_game_runs, result['total_runs'])

    avg_runs_per_game = total_season_runs / games_played

    print(f"\nSeason Results ({games_played} games):")
    print(f"  Total runs: {total_season_runs}")
    print(f"  Average runs per game: {avg_runs_per_game:.2f}")
    print(f"  Run range: {min_game_runs} to {max_game_runs}")

    # Test 3: Game with opponent and extra innings
    print("\n--- Test 3: Game with opponent (extra innings possible) ---")
    pa_gen.set_seed(100)

    result = simulate_game_with_opponent(lineup, lineup, pa_gen, max_innings=9)

    print(f"\nGame Result:")
    print(f"  Home: {result['home_score']}")
    print(f"  Away: {result['away_score']}")
    print(f"  Winner: {result['winner']}")
    print(f"  Innings played: {result['innings_played']}")

    if result['innings_played'] > 9:
        print(f"  ⚠ Game went to extra innings!")

    # Sanity checks
    print("\n--- Sanity Checks ---")

    if 3.0 <= avg_runs_per_game <= 6.0:
        print(f"✓ Average runs per game reasonable ({avg_runs_per_game:.2f})")
    else:
        print(f"⚠ Average runs per game unusual ({avg_runs_per_game:.2f})")

    if 400 <= total_season_runs <= 1000:
        print(f"✓ Season run total reasonable ({total_season_runs})")
    else:
        print(f"⚠ Season run total unusual ({total_season_runs})")

    print("\n" + "="*60)
    print("✓ Game simulation tests complete")
