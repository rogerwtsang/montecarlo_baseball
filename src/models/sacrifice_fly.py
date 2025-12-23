# ============================================================================
# src/models/sacrifice_fly.py
# ============================================================================
"""Sacrifice fly logic."""

from typing import Tuple
import numpy as np
from src.models.player import Player
from src.models.baserunning import BasesState
import config


def check_sacrifice_fly(
    bases: BasesState,
    outs: int,
    rng: np.random.RandomState
) -> Tuple[BasesState, int, bool]:
    """Check if an out results in a sacrifice fly.
    
    A sacrifice fly occurs when:
    - Batter hits a fly ball (caught for out)
    - Runner on 3rd base
    - Less than 2 outs
    - Runner tags up and scores
    
    Args:
        bases: Current bases state
        outs: Current number of outs
        rng: Random number generator
        
    Returns:
        Tuple of (bases_after, runs_scored, was_sac_fly)
    """
    if not config.ENABLE_SACRIFICE_FLIES:
        return bases, 0, False
    
    # Can't sacrifice fly with 2 outs (runner wouldn't try)
    if outs >= 2:
        return bases, 0, False
    
    # Need runner on 3rd
    if bases['third'] is None:
        return bases, 0, False
    
    # Determine if this out is a fly ball
    # config.FLYOUT_PERCENTAGE of outs are fly balls
    is_flyout = rng.random() < config.FLYOUT_PERCENTAGE
    
    if not is_flyout:
        return bases, 0, False
    
    # Sacrifice fly! Runner from 3rd scores
    bases_after = bases.copy()
    bases_after['third'] = None
    
    return bases_after, 1, True


if __name__ == "__main__":
    # Test sacrifice fly logic
    import sys
    sys.path.insert(0, '.')
    
    print("=== Testing Sacrifice Fly Logic ===\n")
    
    # Create test player
    from src.models.player import Player
    runner = Player("Test Runner", 0.280, 0.350, 0.450, 0.170, 500)
    
    rng = np.random.RandomState(42)
    
    # Test 1: No runner on 3rd
    print("Test 1: No runner on 3rd")
    bases = {'first': None, 'second': None, 'third': None}
    bases_after, runs, is_sf = check_sacrifice_fly(bases, 1, rng)
    print(f"  Result: runs={runs}, is_sac_fly={is_sf}")
    assert runs == 0 and not is_sf
    print("  ✓ Passed\n")
    
    # Test 2: Runner on 3rd, 2 outs (shouldn't sac fly)
    print("Test 2: Runner on 3rd, 2 outs")
    bases = {'first': None, 'second': None, 'third': runner}
    bases_after, runs, is_sf = check_sacrifice_fly(bases, 2, rng)
    print(f"  Result: runs={runs}, is_sac_fly={is_sf}")
    assert runs == 0 and not is_sf
    print("  ✓ Passed\n")
    
    # Test 3: Multiple trials with runner on 3rd
    print("Test 3: 1000 outs with runner on 3rd, 1 out")
    bases = {'first': None, 'second': None, 'third': runner}
    
    sac_flies = 0
    for _ in range(1000):
        _, runs, is_sf = check_sacrifice_fly(bases, 1, rng)
        if is_sf:
            sac_flies += 1
    
    expected_rate = config.FLYOUT_PERCENTAGE
    observed_rate = sac_flies / 1000
    
    print(f"  Expected ~{expected_rate*100:.0f}% sac flies")
    print(f"  Observed: {sac_flies}/1000 ({observed_rate*100:.1f}%)")
    
    if abs(observed_rate - expected_rate) < 0.05:
        print("  ✓ Within expected range\n")
    else:
        print("  ⚠ Outside expected range\n")
    
    print("="*60)
    print("✓ Sacrifice fly tests complete")
