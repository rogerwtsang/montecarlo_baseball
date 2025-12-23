# ============================================================================
# config.py
# ============================================================================
"""Configuration constants and parameters for baseball Monte Carlo simulation."""

from typing import Dict

# Simulation parameters
N_SIMULATIONS = 10000
N_GAMES_PER_SEASON = 162
RANDOM_SEED = 42

# Base-running configuration
CONSERVATIVE_BASERUNNING = True  # Toggle for future probabilistic advancement
ENABLE_STOLEN_BASES = True # Toggle stolen base attempts
ENABLE_SACRIFICE_FLIES = True
ENABLE_PROBABILISTIC_BASERUNNING = True

# Stolen base parameters
MIN_SB_ATTEMPTS_FOR_RATE = 5
SB_ATTEMPT_SCALE = 1.0

# Sacrifice fly parameters
FLYOUT_PERCENTAGE = 0.35 # Percentage of outs that are fly balls (vs ground outs, strikeouts)

# Probabilistic base-running parameters
# Probability that runner advances extra base on hits
BASERUNNING_AGGRESSION = {
    'single_1st_to_3rd': 0.28,  # Runner on 1st → 3rd on single
    'double_1st_scores': 0.60,   # Runner on 1st scores on double
    'double_2nd_scores': 0.98,   # Runner on 2nd scores on double
}

# ISO-based hit distribution thresholds
# Maps ISO ranges to hit type probabilities
ISO_THRESHOLDS = {
    'low': 0.100,      # Below this = singles hitter
    'medium': 0.200,   # Between low and medium = balanced
    # Above medium = power hitter
}

# Hit distribution by hitter type (P(1B|hit), P(2B|hit), P(3B|hit), P(HR|hit))
HIT_DISTRIBUTIONS: Dict[str, Dict[str, float]] = {
    'singles_hitter': {
        '1B': 0.80,
        '2B': 0.15,
        '3B': 0.02,
        'HR': 0.03
    },
    'balanced': {
        '1B': 0.70,
        '2B': 0.20,
        '3B': 0.02,
        'HR': 0.08
    },
    'power_hitter': {
        '1B': 0.60,
        '2B': 0.20,
        '3B': 0.01,
        'HR': 0.19
    }
}

# League averages (fallback when player data unavailable)
# Update these based on actual league data
LEAGUE_AVG_HIT_DISTRIBUTION = {
    '1B': 0.75,
    '2B': 0.18,
    '3B': 0.02,
    'HR': 0.05
}

# Data source configuration
CURRENT_SEASON = 2025
TARGET_TEAM = 'TOR'  # Toronto Blue Jays

# Validation thresholds
VALIDATION_TOLERANCE_PCT = 0.05  # 5% difference acceptable
MIN_PA_FOR_INCLUSION = 100  # Minimum PAs to use player stats

# Output configuration
VERBOSITY = 1  # 0=silent, 1=progress, 2=debug

FLYOUT_PERCENTAGE = 0.35  # 35% of outs are fly balls

