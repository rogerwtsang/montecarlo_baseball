"""Stolen base logic and calculations."""

from typing import Optional, Tuple
import numpy as np
from src.models.player import Player
from src.models.baserunning import BasesState
import config


def calculate_sb_rate(player: Player, team_avg_rate: float = 0.05) -> Tuple[float, float]:
    """Calculate stolen base attempt rate and success rate for a player.
    
    Args:
        player: Player object with SB/CS statistics
        team_avg_rate: Team average SB attempt rate (fallback)
        
    Returns:
        Tuple of (attempt_rate, success_rate)
        - attempt_rate: Probability of SB attempt when on base per PA
        - success_rate: Probability of successful steal given attempt
    """
    if player.sb is None or player.cs is None:
        # No data - use team average
        return team_avg_rate, 0.75  # MLB average ~75% success rate
    
    total_attempts = player.sb + player.cs
    
    if total_attempts < config.MIN_SB_ATTEMPTS_FOR_RATE:
        # Too few attempts - use team average attempt rate, but player success rate
        success_rate = player.sb / total_attempts if total_attempts > 0 else 0.75
        return team_avg_rate, success_rate
    
    # Calculate from player data
    # Attempt rate = total attempts per time on base
    # Approximate times on base = hits + walks (ignoring HBP, errors)
    times_on_base = player.ba * player.pa + (player.obp - player.ba) * player.pa
    
    if times_on_base > 0:
        attempt_rate = total_attempts / times_on_base
    else:
        attempt_rate = team_avg_rate
    
    success_rate = player.sb / total_attempts if total_attempts > 0 else 0.75
    
    # Apply scaling factor from config
    attempt_rate *= config.SB_ATTEMPT_SCALE
    
    return attempt_rate, success_rate


def should_attempt_steal(
    runner: Player,
    base: str,
    outs: int,
    rng: np.random.RandomState,
    team_avg_rate: float = 0.05
) -> bool:
    """Determine if a runner should attempt to steal.
    
    Args:
        runner: Player object currently on base
        base: Current base ('first' or 'second')
        outs: Current number of outs (0-2)
        rng: Random number generator
        team_avg_rate: Team average SB attempt rate
        
    Returns:
        True if steal should be attempted
    """
    # Don't steal with 2 outs (too risky in simulation)
    if outs >= 2:
        return False
    
    # Only steal from first or second
    if base not in ['first', 'second']:
        return False
    
    # Calculate attempt probability
    attempt_rate, _ = calculate_sb_rate(runner, team_avg_rate)
    
    # Random check
    return rng.random() < attempt_rate


def attempt_stolen_base(
    runner: Player,
    from_base: str,
    bases_before: BasesState,
    rng: np.random.RandomState,
    team_avg_rate: float = 0.05
) -> Tuple[BasesState, bool, bool]:
    """Attempt a stolen base.
    
    Args:
        runner: Player attempting to steal
        from_base: Base stealing from ('first' or 'second')
        bases_before: Current bases state
        rng: Random number generator
        team_avg_rate: Team average SB attempt rate
        
    Returns:
        Tuple of (bases_after, successful, caught_stealing)
        - bases_after: Updated bases state
        - successful: True if steal successful
        - caught_stealing: True if runner caught stealing
    """
    _, success_rate = calculate_sb_rate(runner, team_avg_rate)
    
    # Determine outcome
    successful = rng.random() < success_rate
    
    bases_after = bases_before.copy()
    
    if successful:
        # Successful steal
        if from_base == 'first':
            bases_after['first'] = None
            bases_after['second'] = runner
        elif from_base == 'second':
            bases_after['second'] = None
            bases_after['third'] = runner
        
        return bases_after, True, False
    else:
        # Caught stealing - runner out
        if from_base == 'first':
            bases_after['first'] = None
        elif from_base == 'second':
            bases_after['second'] = None
        
        return bases_after, False, True


def check_steal_opportunities(
    bases: BasesState,
    outs: int,
    rng: np.random.RandomState,
    team_avg_rate: float = 0.05
) -> Tuple[BasesState, int]:
    """Check for and execute stolen base attempts.
    
    Called between plate appearances to simulate SB attempts.
    
    Args:
        bases: Current bases state
        outs: Current number of outs
        rng: Random number generator
        team_avg_rate: Team average SB attempt rate
        
    Returns:
        Tuple of (bases_after, additional_outs)
        - bases_after: Updated bases state
        - additional_outs: Number of outs from caught stealing (0 or 1)
    """
    if not config.ENABLE_STOLEN_BASES:
        return bases, 0
    
    # Check each base for steal attempts (first, then second)
    # Only one steal attempt per between-PA period
    
    bases_after = bases.copy()
    additional_outs = 0
    
    # Check second base first (more valuable)
    if bases['second'] is not None and bases['third'] is None:
        runner = bases['second']
        if should_attempt_steal(runner, 'second', outs, rng, team_avg_rate):
            bases_after, success, caught = attempt_stolen_base(
                runner, 'second', bases_after, rng, team_avg_rate
            )
            if caught:
                additional_outs = 1
            return bases_after, additional_outs
    
    # Check first base
    if bases['first'] is not None and bases['second'] is None:
        runner = bases['first']
        if should_attempt_steal(runner, 'first', outs, rng, team_avg_rate):
            bases_after, success, caught = attempt_stolen_base(
                runner, 'first', bases_after, rng, team_avg_rate
            )
            if caught:
                additional_outs = 1
            return bases_after, additional_outs
    
    return bases_after, additional_outs


if __name__ == "__main__":
    # Test stolen base calculations
    import sys
    sys.path.insert(0, '.')
    
    print("=== Testing Stolen Base Module ===\n")
    
    # Create test players with different SB profiles
    speedster = Player(
        name="Speedster",
        ba=0.260, obp=0.330, slg=0.380, iso=0.120, pa=500,
        sb=30, cs=5
    )
    
    average_runner = Player(
        name="Average Runner",
        ba=0.280, obp=0.350, slg=0.450, iso=0.170, pa=500,
        sb=10, cs=5
    )
    
    slow_player = Player(
        name="Slow Player",
        ba=0.290, obp=0.360, slg=0.500, iso=0.210, pa=500,
        sb=2, cs=3
    )
    
    no_sb_data = Player(
        name="No SB Data",
        ba=0.270, obp=0.340, slg=0.440, iso=0.170, pa=500
    )
    
    # Test rate calculations
    print("--- SB Rate Calculations ---\n")
    
    for player in [speedster, average_runner, slow_player, no_sb_data]:
        attempt_rate, success_rate = calculate_sb_rate(player)
        print(f"{player.name}:")
        print(f"  SB: {player.sb}, CS: {player.cs}")
        print(f"  Attempt rate: {attempt_rate:.4f} ({attempt_rate*100:.2f}%)")
        print(f"  Success rate: {success_rate:.4f} ({success_rate*100:.2f}%)")
        print()
    
    # Test steal attempts
    print("--- Simulating 1000 Steal Opportunities ---\n")
    
    rng = np.random.RandomState(42)
    
    for player in [speedster, average_runner, slow_player]:
        attempts = 0
        successes = 0
        
        for _ in range(1000):
            if should_attempt_steal(player, 'first', 1, rng):
                attempts += 1
                _, success, caught = attempt_stolen_base(
                    player, 'first',
                    {'first': player, 'second': None, 'third': None},
                    rng
                )
                if success:
                    successes += 1
        
        expected_attempt_rate, expected_success_rate = calculate_sb_rate(player)
        observed_attempt_rate = attempts / 1000
        observed_success_rate = successes / attempts if attempts > 0 else 0
        
        print(f"{player.name}:")
        print(f"  Expected attempts: {expected_attempt_rate*1000:.1f}, Observed: {attempts}")
        print(f"  Expected success: {expected_success_rate:.3f}, Observed: {observed_success_rate:.3f}")
        print()
    
    # Test full steal opportunity check
    print("--- Testing check_steal_opportunities ---\n")
    
    bases = {
        'first': speedster,
        'second': None,
        'third': None
    }
    
    print("Initial: Runner on 1st (Speedster)")
    
    steals = 0
    caught = 0
    
    for _ in range(100):
        bases_after, outs = check_steal_opportunities(bases, 1, rng)
        
        if bases_after['second'] == speedster:
            steals += 1
        elif outs == 1:
            caught += 1
    
    print(f"  100 opportunities: {steals} successful steals, {caught} caught stealing")
    
    print("\n" + "="*60)
    print("✓ Stolen base module tests complete")
