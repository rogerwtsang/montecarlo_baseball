# ============================================================================
# main.py
# ============================================================================
"""Main entry point for baseball Monte Carlo simulation."""

import config
from src.data.scraper import get_team_batting_stats
from src.data.processor import prepare_lineup
from src.simulation.batch import run_simulations


def main():
    """Run simulation for configured team."""
    print(f"Loading {config.CURRENT_SEASON} {config.TARGET_TEAM} data...")

    # TODO: Load data
    # TODO: Prepare lineup
    # TODO: Run simulations
    # TODO: Display results

    print("Simulation complete!")


if __name__ == "__main__":
    main()
