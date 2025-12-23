# ============================================================================
# src/models/probability.py
# ============================================================================
"""Probability calculations for PA outcomes."""

from typing import Dict, Tuple
import numpy as np
import config


def calculate_hit_distribution(iso: float) -> Dict[str, float]:
    """Calculate hit type distribution based on ISO using parametric model.

    Uses linear interpolation between predefined hitter profiles based on ISO.

    Args:
        iso: Isolated power (SLG - BA)

    Returns:
        Dictionary with probabilities for each hit type given a hit occurred.
        Keys: '1B', '2B', '3B', 'HR'
    """
    iso_low = config.ISO_THRESHOLDS['low']
    iso_med = config.ISO_THRESHOLDS['medium']

    singles_profile = config.HIT_DISTRIBUTIONS['singles_hitter']
    balanced_profile = config.HIT_DISTRIBUTIONS['balanced']
    power_profile = config.HIT_DISTRIBUTIONS['power_hitter']

    if iso < iso_low:
        # Singles hitter - use singles profile
        return singles_profile.copy()

    elif iso < iso_med:
        # Interpolate between singles and balanced
        # Weight: 0 at iso_low (pure singles), 1 at iso_med (pure balanced)
        weight = (iso - iso_low) / (iso_med - iso_low)

        return {
            '1B': singles_profile['1B'] * (1 - weight) + balanced_profile['1B'] * weight,
            '2B': singles_profile['2B'] * (1 - weight) + balanced_profile['2B'] * weight,
            '3B': singles_profile['3B'] * (1 - weight) + balanced_profile['3B'] * weight,
            'HR': singles_profile['HR'] * (1 - weight) + balanced_profile['HR'] * weight
        }

    else:
        # Interpolate between balanced and power
        # Weight: 0 at iso_med (pure balanced), 1 at iso_med+0.200 (pure power)
        # Cap weight at 1.0 for very high ISO
        weight = min(1.0, (iso - iso_med) / 0.200)

        return {
            '1B': balanced_profile['1B'] * (1 - weight) + power_profile['1B'] * weight,
            '2B': balanced_profile['2B'] * (1 - weight) + power_profile['2B'] * weight,
            '3B': balanced_profile['3B'] * (1 - weight) + power_profile['3B'] * weight,
            'HR': balanced_profile['HR'] * (1 - weight) + power_profile['HR'] * weight
        }


def decompose_slash_line(ba: float, obp: float, slg: float) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Convert slash line statistics to PA outcome probabilities.

    Args:
        ba: Batting average
        obp: On-base percentage
        slg: Slugging percentage

    Returns:
        Tuple of (pa_probs, hit_dist) where:
        - pa_probs: Dict with keys 'OUT', 'WALK', 'SINGLE', 'DOUBLE', 'TRIPLE', 'HR'
        - hit_dist: Dict with keys '1B', '2B', '3B', 'HR' (conditional on hit)
    """
    # Calculate ISO
    iso = slg - ba

    # Get hit type distribution based on ISO
    hit_dist = calculate_hit_distribution(iso)

    # Basic PA outcome probabilities
    p_out = 1.0 - obp
    p_walk = obp - ba
    p_hit = ba

    # Distribute hits into specific types
    pa_probs = {
        'OUT': p_out,
        'WALK': p_walk,
        'SINGLE': p_hit * hit_dist['1B'],
        'DOUBLE': p_hit * hit_dist['2B'],
        'TRIPLE': p_hit * hit_dist['3B'],
        'HR': p_hit * hit_dist['HR']
    }

    # Validate
    validate_probabilities(pa_probs)
    validate_probabilities(hit_dist)

    return pa_probs, hit_dist


def validate_probabilities(probs: Dict[str, float], tolerance: float = 1e-6) -> bool:
    """Validate that probabilities sum to 1.0 and are non-negative.

    Args:
        probs: Dictionary of probabilities
        tolerance: Acceptable deviation from 1.0

    Returns:
        True if valid, raises ValueError otherwise
    """
    # Check for negative probabilities
    for key, prob in probs.items():
        if prob < 0:
            raise ValueError(f"Negative probability for {key}: {prob}")

    # Check sum
    total = sum(probs.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"Probabilities sum to {total:.6f}, expected 1.0 (tolerance: {tolerance})")

    return True


def calculate_expected_bases_per_hit(hit_dist: Dict[str, float]) -> float:
    """Calculate expected total bases per hit given a hit distribution.

    Useful for validating that hit distribution matches observed SLG/BA ratio.

    Args:
        hit_dist: Dictionary with keys '1B', '2B', '3B', 'HR'

    Returns:
        Expected bases per hit
    """
    return (
        1 * hit_dist['1B'] +
        2 * hit_dist['2B'] +
        3 * hit_dist['3B'] +
        4 * hit_dist['HR']
    )


def compare_to_observed(ba: float, slg: float, hit_dist: Dict[str, float]) -> Dict[str, float]:
    """Compare calculated hit distribution to observed SLG/BA ratio.

    Args:
        ba: Observed batting average
        slg: Observed slugging percentage
        hit_dist: Calculated hit distribution

    Returns:
        Dictionary with comparison metrics
    """
    observed_bases_per_hit = slg / ba if ba > 0 else 0
    expected_bases_per_hit = calculate_expected_bases_per_hit(hit_dist)

    error = expected_bases_per_hit - observed_bases_per_hit
    error_pct = (error / observed_bases_per_hit * 100) if observed_bases_per_hit > 0 else 0

    return {
        'observed_bases_per_hit': observed_bases_per_hit,
        'expected_bases_per_hit': expected_bases_per_hit,
        'absolute_error': error,
        'error_pct': error_pct
    }


if __name__ == "__main__":
    # Add project root to path for standalone testing
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    import config

    # Test the probability calculations
    print("=== Testing Probability Calculations ===\n")

    # Test case 1: Singles hitter
    print("Test 1: Singles Hitter (BA: .280, OBP: .340, SLG: .360)")
    ba, obp, slg = 0.280, 0.340, 0.360
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)

    print(f"ISO: {slg - ba:.3f}")
    print("\nPA Outcome Probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")

    print("\nHit Distribution (given a hit):")
    for hit_type, prob in hit_dist.items():
        print(f"  {hit_type}: {prob:.4f} ({prob*100:.2f}%)")

    comparison = compare_to_observed(ba, slg, hit_dist)
    print(f"\nBases/hit - Observed: {comparison['observed_bases_per_hit']:.3f}, Expected: {comparison['expected_bases_per_hit']:.3f}")
    print(f"Error: {comparison['error_pct']:.2f}%")

    # Test case 2: Balanced hitter
    print("\n" + "="*60 + "\n")
    print("Test 2: Balanced Hitter (BA: .270, OBP: .340, SLG: .450)")
    ba, obp, slg = 0.270, 0.340, 0.450
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)

    print(f"ISO: {slg - ba:.3f}")
    print("\nPA Outcome Probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")

    print("\nHit Distribution (given a hit):")
    for hit_type, prob in hit_dist.items():
        print(f"  {hit_type}: {prob:.4f} ({prob*100:.2f}%)")

    comparison = compare_to_observed(ba, slg, hit_dist)
    print(f"\nBases/hit - Observed: {comparison['observed_bases_per_hit']:.3f}, Expected: {comparison['expected_bases_per_hit']:.3f}")
    print(f"Error: {comparison['error_pct']:.2f}%")

    # Test case 3: Power hitter
    print("\n" + "="*60 + "\n")
    print("Test 3: Power Hitter (BA: .250, OBP: .330, SLG: .520)")
    ba, obp, slg = 0.250, 0.330, 0.520
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)

    print(f"ISO: {slg - ba:.3f}")
    print("\nPA Outcome Probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")

    print("\nHit Distribution (given a hit):")
    for hit_type, prob in hit_dist.items():
        print(f"  {hit_type}: {prob:.4f} ({prob*100:.2f}%)")

    comparison = compare_to_observed(ba, slg, hit_dist)
    print(f"\nBases/hit - Observed: {comparison['observed_bases_per_hit']:.3f}, Expected: {comparison['expected_bases_per_hit']:.3f}")
    print(f"Error: {comparison['error_pct']:.2f}%")

    # Test case 4: 2025 Blue Jays team average
    print("\n" + "="*60 + "\n")
    print("Test 4: 2025 Blue Jays Team Average (BA: .261, OBP: .331, SLG: .424)")
    ba, obp, slg = 0.261, 0.331, 0.424
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)

    print(f"ISO: {slg - ba:.3f}")
    print("\nPA Outcome Probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")

    print("\nHit Distribution (given a hit):")
    for hit_type, prob in hit_dist.items():
        print(f"  {hit_type}: {prob:.4f} ({prob*100:.2f}%)")

    comparison = compare_to_observed(ba, slg, hit_dist)
    print(f"\nBases/hit - Observed: {comparison['observed_bases_per_hit']:.3f}, Expected: {comparison['expected_bases_per_hit']:.3f}")
    print(f"Error: {comparison['error_pct']:.2f}%")

    print("\n" + "="*60)
    print("✓ All tests passed - probabilities valid")
