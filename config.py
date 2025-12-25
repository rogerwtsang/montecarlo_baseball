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

# Hit distribution Bayesian smoothing parameters
MIN_HITS_FOR_ACTUAL_DIST = 100  # Minimum hits to use player's actual distribution without smoothing
BAYESIAN_PRIOR_WEIGHT = 100  # Equivalent sample size for league average prior

# Errors and wild pitches
ENABLE_ERRORS_WILD_PITCHES = True
ERROR_RATE_PER_PA = 0.015  # ~1.5% of PAs result in error/WP/PB that advances runners

# ============================================================================
# Lineup Optimization Configuration
# ============================================================================

# Optimization method selection
OPT_EXHAUSTIVE_THRESHOLD = 10  # Use exhaustive search if roster <= this many players
# Above threshold, use genetic algorithm

# Genetic Algorithm parameters
OPT_GA_POPULATION_SIZE = 50     # Number of lineups in each generation
OPT_GA_GENERATIONS = 100        # Maximum number of generations
OPT_GA_MUTATION_RATE = 0.1      # Probability of swapping two positions (0.0-1.0)
OPT_GA_TOURNAMENT_SIZE = 3      # Number of candidates in tournament selection
OPT_GA_ELITISM_RATE = 0.10      # Percentage of top lineups to preserve (0.0-1.0)
OPT_GA_NO_IMPROVEMENT_STOP = 20 # Stop after this many generations with no improvement

# Simulation budget for optimization
OPT_DEFAULT_SIMS_PER_LINEUP = 1000  # Default number of simulations per lineup candidate
OPT_EXHAUSTIVE_SIMS = 100           # Simulations per lineup for exhaustive search (faster)
OPT_GA_SIMS_INITIAL = 1000          # Simulations per lineup in early GA generations
OPT_GA_SIMS_FINAL = 5000            # Simulations per lineup in final GA generation

# Optimization objectives
OPT_PRIMARY_OBJECTIVE = 'mean_runs'  # Options: 'mean_runs', 'median_runs', 'percentile_95'
OPT_SECONDARY_OBJECTIVE = None       # Options: None, 'min_variance', 'max_percentile_95', 'max_median'
OPT_SECONDARY_WEIGHT = 0.3           # Weight for secondary objective (0.0-1.0)

# Caching
OPT_ENABLE_CACHE = True              # Cache simulation results for identical lineups
OPT_MAX_CACHE_SIZE = 10000           # Maximum number of cached lineup evaluations
