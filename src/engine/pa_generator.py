"""Plate appearance outcome generator."""

import numpy as np
from typing import Optional
from src.models.player import Player


class PAOutcomeGenerator:
    """Generates plate appearance outcomes based on player probabilities."""
    
    def __init__(self, random_state: Optional[int] = None):
        """Initialize the generator.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.rng = np.random.RandomState(random_state)
    
    def generate_outcome(self, player: Player, game_state: Optional[dict] = None) -> str:
        """Generate a plate appearance outcome for a player.
        
        Args:
            player: Player object with calculated probabilities
            game_state: Optional game state (unused for now, for future enhancement)
            
        Returns:
            Outcome string: 'OUT', 'WALK', 'SINGLE', 'DOUBLE', 'TRIPLE', or 'HR'
        """
        # Get probabilities from player
        probs = player.pa_probs
        
        # Create cumulative probability distribution
        outcomes = ['OUT', 'WALK', 'SINGLE', 'DOUBLE', 'TRIPLE', 'HR']
        cum_probs = np.cumsum([probs[outcome] for outcome in outcomes])
        
        # Generate random number and find outcome
        rand = self.rng.random()
        
        for i, cum_prob in enumerate(cum_probs):
            if rand < cum_prob:
                return outcomes[i]
        
        # Should never reach here if probabilities sum to 1.0
        return 'OUT'
    
    def set_seed(self, seed: int):
        """Reset random seed.
        
        Args:
            seed: New random seed
        """
        self.rng = np.random.RandomState(seed)


if __name__ == "__main__":
    # Test PA outcome generator
    import sys
    sys.path.insert(0, '.')
    
    print("=== Testing PA Outcome Generator ===\n")
    
    # Create test player
    from src.models.probability import decompose_slash_line
    
    ba, obp, slg = 0.280, 0.350, 0.450
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)
    
    player = Player(
        name="Test Player",
        ba=ba,
        obp=obp,
        slg=slg,
        iso=slg-ba,
        pa=500,
        pa_probs=pa_probs,
        hit_dist=hit_dist
    )
    
    print(f"Player: {player.name}")
    print(f"Slash: {ba:.3f}/{obp:.3f}/{slg:.3f}")
    print("\nExpected probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")
    
    # Generate many outcomes and check distribution
    print("\n--- Testing 10,000 PAs ---")
    generator = PAOutcomeGenerator(random_state=42)
    
    outcomes_count = {
        'OUT': 0,
        'WALK': 0,
        'SINGLE': 0,
        'DOUBLE': 0,
        'TRIPLE': 0,
        'HR': 0
    }
    
    n_trials = 10000
    for _ in range(n_trials):
        outcome = generator.generate_outcome(player)
        outcomes_count[outcome] += 1
    
    print("\nObserved frequencies:")
    for outcome, count in outcomes_count.items():
        observed_pct = count / n_trials
        expected_pct = pa_probs[outcome]
        diff = abs(observed_pct - expected_pct)
        print(f"  {outcome}: {count:5d} ({observed_pct:.4f}) - Expected: {expected_pct:.4f} - Diff: {diff:.4f}")
    
    # Check if observed is close to expected (within 1%)
    max_diff = max(abs(outcomes_count[o]/n_trials - pa_probs[o]) for o in outcomes_count.keys())
    print(f"\nMax difference: {max_diff:.4f}")
    
    if max_diff < 0.01:
        print("✓ Distribution matches expected probabilities")
    else:
        print("⚠ Distribution differs from expected (may need more trials)")
    
    # Test reproducibility
    print("\n--- Testing Reproducibility ---")
    gen1 = PAOutcomeGenerator(random_state=42)
    gen2 = PAOutcomeGenerator(random_state=42)
    
    outcomes1 = [gen1.generate_outcome(player) for _ in range(10)]
    outcomes2 = [gen2.generate_outcome(player) for _ in range(10)]
    
    if outcomes1 == outcomes2:
        print("✓ Reproducibility verified (same seed produces same sequence)")
    else:
        print("✗ Reproducibility failed")
    
    print("\n" + "="*60)
    print("✓ PA Outcome Generator tests complete")
