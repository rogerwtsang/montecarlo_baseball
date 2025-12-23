# ============================================================================
# src/engine/inning.py
# ============================================================================
"""Half-inning simulation."""

from typing import List, Dict, Tuple
from src.models.player import Player
from src.models.baserunning import create_empty_bases, advance_runners
from src.models.stolen_bases import check_steal_opportunities
from src.models.sacrifice_fly import check_sacrifice_fly
from src.engine.pa_generator import PAOutcomeGenerator
import config


def simulate_half_inning(
    lineup: List[Player],
    starting_batter_idx: int,
    pa_generator: PAOutcomeGenerator
) -> Tuple[int, int, Dict]:
    """Simulate a half-inning of baseball.

    Args:
        lineup: List of 9 Player objects in batting order
        starting_batter_idx: Index of first batter (0-8)
        pa_generator: PAOutcomeGenerator instance

    Returns:
        Tuple of (runs, next_batter_idx, inning_stats)
        - runs: Total runs scored in half-inning
        - next_batter_idx: Index of next batter (for next inning)
        - inning_stats: Dictionary with detailed statistics
    """
    if len(lineup) != 9:
        raise ValueError(f"Lineup must have exactly 9 batters, got {len(lineup)}")

    # Initialize state
    outs = 0
    bases = create_empty_bases()
    runs = 0
    batter_idx = starting_batter_idx

    # Track stats
    pa_count = 0
    hits = 0
    walks = 0
    lob = 0  # Left on base (will calculate at end)
    sb_attempts = 0
    sb_success = 0
    sac_flies = 0

    while outs < 3:
        # Check for stolen base attempts BEFORE the PA
        if config.ENABLE_STOLEN_BASES:
            bases_after_sb, sb_outs = check_steal_opportunities(
                bases, outs, pa_generator.rng
            )

            # Track if there was a steal attempt
            if bases_after_sb != bases:
                sb_attempts += 1
                if sb_outs == 0:  # Successful
                    sb_success += 1

            bases = bases_after_sb
            outs += sb_outs

            # If caught stealing resulted in 3rd out, inning over
            if outs >= 3:
                break

        # Get current batter
        batter = lineup[batter_idx]

        # Generate PA outcome
        outcome = pa_generator.generate_outcome(batter)
        pa_count += 1

        # Handle outcome
        if outcome == 'OUT':
            # Check for sacrifice fly
            bases_after_sf, sf_runs, is_sf = check_sacrifice_fly(bases, outs, pa_generator.rng)

            if is_sf:
                sac_flies += 1
                runs += sf_runs
                bases = bases_after_sf

            outs += 1

        else:
            # Hit or walk - advance runners
            bases_after, runs_scored = advance_runners(outcome, bases, batter, pa_generator.rng)
            bases = bases_after
            runs += runs_scored

            # Track stats
            if outcome == 'WALK':
                walks += 1
            else:
                hits += 1

        # Advance to next batter (cycle through lineup)
        batter_idx = (batter_idx + 1) % 9

    # Calculate LOB (runners stranded)
    lob = sum(1 for runner in bases.values() if runner is not None)

    inning_stats = {
        'runs': runs,
        'hits': hits,
        'walks': walks,
        'pa_count': pa_count,
        'lob': lob,
        'sb_attempts': sb_attempts,
        'sb_success': sb_success,
        'sac_flies': sac_flies
    }

    return runs, batter_idx, inning_stats


if __name__ == "__main__":
    # Test half-inning simulation
    import sys
    sys.path.insert(0, '.')
    from src.data.scraper import load_data
    from src.data.processor import prepare_lineup

    print("=== Testing Half-Inning Simulation ===\n")

    # Load test data
    try:
        df = load_data('blue_jays_2025_prepared.csv', 'processed')
    except:
        df = load_data('blue_jays_2024_prepared.csv', 'processed')

    # Create lineup
    lineup = prepare_lineup(df)
    print(f"Created lineup with {len(lineup)} players")
    print(f"Leadoff: {lineup[0].name} ({lineup[0].ba:.3f}/{lineup[0].obp:.3f}/{lineup[0].slg:.3f})")

    # Create PA generator
    pa_gen = PAOutcomeGenerator(random_state=42)

    # Simulate one half-inning
    print("\n--- Simulating one half-inning ---")
    runs, next_batter, stats = simulate_half_inning(lineup, 0, pa_gen)

    print(f"\nResults:")
    print(f"  Runs: {runs}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Walks: {stats['walks']}")
    print(f"  PAs: {stats['pa_count']}")
    print(f"  LOB: {stats['lob']}")
    print(f"  Next batter: #{next_batter + 1} ({lineup[next_batter].name})")

    # Simulate multiple half-innings to get averages
    print("\n--- Simulating 1,000 half-innings ---")
    pa_gen.set_seed(42)

    total_runs = 0
    total_hits = 0
    total_pas = 0
    min_runs = float('inf')
    max_runs = 0

    n_innings = 1000
    batter_idx = 0

    for i in range(n_innings):
        runs, batter_idx, stats = simulate_half_inning(lineup, batter_idx, pa_gen)
        total_runs += runs
        total_hits += stats['hits']
        total_pas += stats['pa_count']
        min_runs = min(min_runs, runs)
        max_runs = max(max_runs, runs)

    avg_runs = total_runs / n_innings
    avg_hits = total_hits / n_innings
    avg_pas = total_pas / n_innings

    print(f"\nAverages over {n_innings} innings:")
    print(f"  Runs per inning: {avg_runs:.3f}")
    print(f"  Hits per inning: {avg_hits:.3f}")
    print(f"  PAs per inning: {avg_pas:.3f}")
    print(f"  Run range: {min_runs} to {max_runs}")

    # Sanity checks
    print("\n--- Sanity Checks ---")
    if 0.3 <= avg_runs <= 0.8:
        print(f"✓ Average runs per inning reasonable ({avg_runs:.3f})")
    else:
        print(f"⚠ Average runs per inning unusual ({avg_runs:.3f})")

    if 0.7 <= avg_hits <= 1.3:
        print(f"✓ Average hits per inning reasonable ({avg_hits:.3f})")
    else:
        print(f"⚠ Average hits per inning unusual ({avg_hits:.3f})")

    if 3.0 <= avg_pas <= 5.0:
        print(f"✓ Average PAs per inning reasonable ({avg_pas:.3f})")
    else:
        print(f"⚠ Average PAs per inning unusual ({avg_pas:.3f})")

    print("\n" + "="*60)
    print("✓ Half-inning simulation tests complete")
