# ============================================================================
# src/models/baserunning.py
# ============================================================================
"""Base-running logic for runner advancement."""

from typing import Dict, Optional, Tuple
import numpy as np
from src.models.player import Player
import config


BasesState = Dict[str, Optional[Player]]


def create_empty_bases() -> BasesState:
    """Create an empty bases state.

    Returns:
        Dictionary with all bases empty
    """
    return {
        'first': None,
        'second': None,
        'third': None
    }


def advance_runners(
    hit_type: str,
    bases_before: BasesState,
    batter: Player,
    rng: Optional[np.random.RandomState] = None
) -> Tuple[BasesState, int]:
    """Advance runners based on hit type using deterministic or probabilistic rules.

    Conservative deterministic rules (defaultJ):
    - Walk: forced advancement only
    - Single: everyone advances 1 base
    - Double: batter to 2nd, runner from 1st to 3rd, runners from 2nd/3rd score
    - Triple: batter to 3rd, all runners score
    - Home Run: everyone scores

    Probabilistic rules (if ENABLE_PROBABILISTIC_BASERUNNING=True):
    - Single: runner from 1st sometimes goes to 3rd
    - Double: runner from 1st sometimes scores (not just stops at 3rd)

    Args:
        hit_type: One of 'OUT', 'WALK', 'SINGLE', 'DOUBLE', 'TRIPLE', 'HR'
        bases_before: Dict with keys 'first', 'second', 'third' (Player or None)
        batter: Player object for the batter
        rng: Random number generator (required if probabilistic enabled)

    Returns:
        Tuple of (bases_after, runs_scored)
        - bases_after: Updated bases state
        - runs_scored: Number of runs that scored on this play
    """
    runs_scored = 0
    bases_after = create_empty_bases()

    # Check if we need RNG for probabilistic baserunning
    use_probabilistic = config.ENABLE_PROBABILISTIC_BASERUNNING
    if use_probabilistic and rng is None:
        raise ValueError("RNG required when ENABLE_PROBABILISTIC_BASERUNNING is True")

    if hit_type == 'OUT':
        # No advancement, runners stay
        bases_after = bases_before.copy()

    elif hit_type == 'WALK':
        # Forced advancement only
        # If bases loaded, runner from 3rd scores
        if (bases_before['first'] is not None and
            bases_before['second'] is not None and
            bases_before['third'] is not None):
            runs_scored = 1

        # Advance runners if forced
        if bases_before['second'] is not None and bases_before['first'] is not None:
            bases_after['third'] = bases_before['second']
        elif bases_before['third'] is not None:
            bases_after['third'] = bases_before['third']

        if bases_before['first'] is not None:
            bases_after['second'] = bases_before['first']

        # Batter always goes to first
        bases_after['first'] = batter

    elif hit_type == 'SINGLE':
        # Batter to first
        # Runner from 3rd scores
        if bases_before['third'] is not None:
            runs_scored += 1

        # Runner from 2nd advances to 3rd
        bases_after['third'] = bases_before['second']

        # Runner from 1st: deterministic=2nd, probabilistic=sometimes 3rd
        if bases_before['first'] is not None:
            if use_probabilistic and rng.random() < config.BASERUNNING_AGGRESSION['single_1st_to_3rd']:
                # Aggressive: 1st to 3rd
                if bases_after['third'] is None: # Only if 3rd is open
                    bases_after['third'] = bases_before['first']
                else:
                    bases_after['second'] = bases_before['first']
            else:
                # Conservative: 1st to 2nd
                bases_after['second'] = bases_before['first']

        bases_after['first'] = batter

    elif hit_type == 'DOUBLE':
        # Batter to second
        # Runner from 3rd scores
        if bases_before['third'] is not None:
            runs_scored += 1

        # Runner from 2nd: almost always scores
        if bases_before['second'] is not None:
            if use_probabilistic:
                if rng.random() < config.BASERUNNING_AGGRESSION['double_2nd_scores']:
                    runs_scored += 1
                else:
                    bases_after['third'] = bases_before['second']
            else:
                runs_scored += 1

        # Runner from 1st: deterministic=3rd, probabilistic=sometimes scores
        if bases_before['first'] is not None:
            if use_probabilistic and rng.random() < config.BASERUNNING_AGGRESSION['double_1st_scores']:
                # Aggressive: scores from 1st
                runs_scored += 1
            else:
                # Conservative: 1st to 3rd
                bases_after['third'] = bases_before['first']

        bases_after['second'] = batter

    elif hit_type == 'TRIPLE':
        # Batter to third
        # All runners score
        if bases_before['first'] is not None:
            runs_scored += 1
        if bases_before['second'] is not None:
            runs_scored += 1
        if bases_before['third'] is not None:
            runs_scored += 1

        bases_after['third'] = batter

    elif hit_type == 'HR':
        # Everyone scores including batter
        runs_scored = 1  # Batter
        if bases_before['first'] is not None:
            runs_scored += 1
        if bases_before['second'] is not None:
            runs_scored += 1
        if bases_before['third'] is not None:
            runs_scored += 1
        # All bases empty after HR

    else:
        raise ValueError(f"Unknown hit type: {hit_type}")

    return bases_after, runs_scored


def count_runners_on_base(bases: BasesState) -> int:
    """Count number of runners on base.

    Args:
        bases: Bases state dictionary

    Returns:
        Number of runners (0-3)
    """
    return sum(1 for runner in bases.values() if runner is not None)


def bases_to_string(bases: BasesState) -> str:
    """Convert bases state to readable string.

    Args:
        bases: Bases state dictionary

    Returns:
        String representation like "1st, 3rd" or "Bases empty"
    """
    occupied = []
    if bases['first'] is not None:
        occupied.append('1st')
    if bases['second'] is not None:
        occupied.append('2nd')
    if bases['third'] is not None:
        occupied.append('3rd')

    if not occupied:
        return "Bases empty"
    return ", ".join(occupied)


if __name__ == "__main__":
    # Test base-running logic
    import sys
    sys.path.insert(0, '.')

    print("=== Testing Base-Running Logic ===\n")

    # Create test players
    batter = Player("Test Batter", 0.280, 0.350, 0.450, 0.170, 500)
    runner1 = Player("Runner 1", 0.250, 0.320, 0.400, 0.150, 400)
    runner2 = Player("Runner 2", 0.260, 0.330, 0.410, 0.150, 450)
    runner3 = Player("Runner 3", 0.270, 0.340, 0.420, 0.150, 500)

    # Create RNG for probabilistic tests
    rng = np.random.RandomState(42)

    # Test 1: Walk with bases empty
    print("Test 1: Walk with bases empty")
    bases_before = create_empty_bases()
    bases_after, runs = advance_runners('WALK', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['first'] == batter
    assert bases_after['second'] is None
    assert bases_after['third'] is None
    assert runs == 0
    print("  ✓ Passed\n")

    # Test 2: Walk with bases loaded
    print("Test 2: Walk with bases loaded")
    bases_before = {
        'first': runner1,
        'second': runner2,
        'third': runner3
    }
    bases_after, runs = advance_runners('WALK', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['first'] == batter
    assert bases_after['second'] == runner1
    assert bases_after['third'] == runner2
    assert runs == 1
    print("  ✓ Passed\n")

    # Test 3: Single with runner on first
    print("Test 3: Single with runner on first")
    bases_before = {
        'first': runner1,
        'second': None,
        'third': None
    }
    bases_after, runs = advance_runners('SINGLE', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['first'] == batter
    # Runner could be on 2nd or 3rd depending on probabilistic
    assert runs == 0
    print("  ✓ Passed\n")

    # Test 4: Single with runner on third
    print("Test 4: Single with runner on third")
    bases_before = {
        'first': None,
        'second': None,
        'third': runner3
    }
    bases_after, runs = advance_runners('SINGLE', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['first'] == batter
    assert bases_after['second'] is None
    assert bases_after['third'] is None
    assert runs == 1
    print("  ✓ Passed\n")

    # Test 5: Double with runner on second
    print("Test 5: Double with runner on second")
    bases_before = {
        'first': None,
        'second': runner2,
        'third': None
    }
    bases_after, runs = advance_runners('DOUBLE', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['second'] == batter
    # Runner from 2nd almost always scores with probabilistic
    assert runs >= 1
    print("  ✓ Passed\n")

    # Test 6: Double with runners on first and second
    print("Test 6: Double with runners on first and second")
    bases_before = {
        'first': runner1,
        'second': runner2,
        'third': None
    }
    bases_after, runs = advance_runners('DOUBLE', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['second'] == batter
    # At least 1 run should score
    assert runs >= 1
    print("  ✓ Passed\n")

    # Test 7: Triple with bases loaded
    print("Test 7: Triple with bases loaded")
    bases_before = {
        'first': runner1,
        'second': runner2,
        'third': runner3
    }
    bases_after, runs = advance_runners('TRIPLE', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['first'] is None
    assert bases_after['second'] is None
    assert bases_after['third'] == batter
    assert runs == 3
    print("  ✓ Passed\n")

    # Test 8: Home run with bases loaded (grand slam)
    print("Test 8: Home run with bases loaded")
    bases_before = {
        'first': runner1,
        'second': runner2,
        'third': runner3
    }
    bases_after, runs = advance_runners('HR', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['first'] is None
    assert bases_after['second'] is None
    assert bases_after['third'] is None
    assert runs == 4
    print("  ✓ Passed\n")

    # Test 9: Out doesn't advance runners
    print("Test 9: Out with runners on base")
    bases_before = {
        'first': runner1,
        'second': runner2,
        'third': None
    }
    bases_after, runs = advance_runners('OUT', bases_before, batter, rng)
    print(f"  Before: {bases_to_string(bases_before)}")
    print(f"  After:  {bases_to_string(bases_after)}")
    print(f"  Runs:   {runs}")
    assert bases_after['first'] == runner1
    assert bases_after['second'] == runner2
    assert bases_after['third'] is None
    assert runs == 0
    print("  ✓ Passed\n")

    print("="*60)
    print("✓ All base-running tests passed")
