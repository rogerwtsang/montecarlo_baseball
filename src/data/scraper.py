"""Data acquisition using pybaseball."""

import pandas as pd
from typing import Optional
import pybaseball as pyb
from pybaseball import batting_stats, team_batting


# Enable cache to avoid repeated API calls
pyb.cache.enable()


def get_team_batting_stats(team: str, season: int) -> pd.DataFrame:
    """Fetch batting statistics for a team's roster.

    Args:
        team: Team abbreviation (e.g., 'TOR')
        season: Season year

    Returns:
        DataFrame with player batting statistics
    """
    print(f"Fetching {season} batting stats for {team}...")

    # Get all batting stats for the season
    stats = batting_stats(season, qual=1)  # qual=1 gets all players with at least 1 PA

    # Filter for specific team
    team_stats = stats[stats['Team'] == team].copy()

    if team_stats.empty:
        raise ValueError(f"No data found for team {team} in {season}")

    print(f"Found {len(team_stats)} players for {team}")

    return team_stats


def get_league_batting_stats(season: int, min_pa: int = 100) -> pd.DataFrame:
    """Fetch league-wide batting statistics for calculating averages.

    Args:
        season: Season year
        min_pa: Minimum plate appearances for inclusion

    Returns:
        DataFrame with qualified league batting statistics
    """
    print(f"Fetching {season} league-wide batting stats...")

    # Get qualified hitters (default qual is typically 3.1 PA per team game)
    stats = batting_stats(season, qual=min_pa)

    print(f"Found {len(stats)} qualified players")

    return stats


def calculate_league_averages(season: int, min_pa: int = 300) -> dict:
    """Calculate league-average hit distributions.

    Args:
        season: Season year
        min_pa: Minimum PAs for inclusion in averages

    Returns:
        Dictionary with league average statistics
    """
    stats = get_league_batting_stats(season, min_pa)

    # Calculate totals
    total_hits = stats['H'].sum()
    total_doubles = stats['2B'].sum()
    total_triples = stats['3B'].sum()
    total_hr = stats['HR'].sum()

    # Singles = Hits - (2B + 3B + HR)
    total_singles = total_hits - (total_doubles + total_triples + total_hr)

    # Distribution of hit types (conditional on a hit occurring)
    hit_dist = {
        '1B': total_singles / total_hits,
        '2B': total_doubles / total_hits,
        '3B': total_triples / total_hits,
        'HR': total_hr / total_hits
    }

    # Overall slash line averages
    # pybaseball uses 'AVG' instead of 'BA'
    ba_col = 'AVG' if 'AVG' in stats.columns else 'BA'

    slash = {
        'BA': stats[ba_col].mean(),
        'OBP': stats['OBP'].mean(),
        'SLG': stats['SLG'].mean(),
        'ISO': stats['ISO'].mean() if 'ISO' in stats.columns else stats['SLG'].mean() - stats[ba_col].mean()
    }

    return {
        'hit_distribution': hit_dist,
        'slash_line': slash,
        'season': season,
        'n_players': len(stats),
        'total_hits': total_hits
    }


def prepare_player_stats(df: pd.DataFrame, min_pa: int = 100) -> pd.DataFrame:
    """Clean and prepare player statistics for simulation.

    Args:
        df: Raw DataFrame from pybaseball
        min_pa: Minimum plate appearances for inclusion

    Returns:
        Cleaned DataFrame with necessary columns
    """
    # Filter by minimum PAs
    df_clean = df[df['PA'] >= min_pa].copy()

    # Select and rename key columns
    columns_needed = {
        'Name': 'name',
        'PA': 'pa',
        'AVG': 'ba',  # pybaseball uses AVG instead of BA
        'OBP': 'obp',
        'SLG': 'slg',
        'H': 'hits',
        '2B': 'doubles',
        '3B': 'triples',
        'HR': 'hr',
        'SB': 'sb',
        'CS': 'cs'
    }

    # Check which columns exist
    available_cols = {k: v for k, v in columns_needed.items() if k in df.columns}

    df_clean = df_clean[list(available_cols.keys())].copy()
    df_clean.rename(columns=available_cols, inplace=True)

    # Calculate singles if we have the data
    if all(col in df_clean.columns for col in ['hits', 'doubles', 'triples', 'hr']):
        df_clean['singles'] = df_clean['hits'] - (df_clean['doubles'] + df_clean['triples'] + df_clean['hr'])

    # Calculate ISO if not present
    if 'iso' not in df_clean.columns and 'slg' in df_clean.columns and 'ba' in df_clean.columns:
        df_clean['iso'] = df_clean['slg'] - df_clean['ba']

    # Handle missing values
    df_clean = df_clean.dropna(subset=['ba', 'obp', 'slg'])

    print(f"Prepared stats for {len(df_clean)} players (min PA: {min_pa})")

    return df_clean


def save_data(df: pd.DataFrame, filename: str, data_type: str = 'raw'):
    """Save DataFrame to data directory.

    Args:
        df: DataFrame to save
        filename: Filename (without path)
        data_type: 'raw' or 'processed'
    """
    import os

    path = f"data/{data_type}/{filename}"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path, index=False)
    print(f"Saved data to {path}")


def load_data(filename: str, data_type: str = 'raw') -> pd.DataFrame:
    """Load DataFrame from data directory.

    Args:
        filename: Filename (without path)
        data_type: 'raw' or 'processed'

    Returns:
        Loaded DataFrame
    """
    path = f"data/{data_type}/{filename}"
    df = pd.read_csv(path)
    print(f"Loaded data from {path}")
    return df


if __name__ == "__main__":
    # Test the scraper
    import sys

    # Check for 2025 data availability
    try:
        print("\n=== Testing Data Scraper ===\n")

        # Try 2025 first
        tor_stats = get_team_batting_stats('TOR', 2025)
        print(f"\nColumns available: {list(tor_stats.columns)}")
        print(f"\nFirst few rows:\n{tor_stats.head()}")

        # Save raw data
        save_data(tor_stats, 'blue_jays_2025_raw.csv', 'raw')

        # Prepare stats
        prepared = prepare_player_stats(tor_stats)
        save_data(prepared, 'blue_jays_2025_prepared.csv', 'processed')

        print(f"\n=== Sample prepared data ===")
        print(prepared[['name', 'pa', 'ba', 'obp', 'slg', 'iso']].head())

        # Calculate league averages
        print("\n=== Calculating league averages ===")
        league_avg = calculate_league_averages(2025, min_pa=300)
        print(f"\nLeague average hit distribution: {league_avg['hit_distribution']}")
        print(f"League average slash line: {league_avg['slash_line']}")

    except Exception as e:
        print(f"\nError with 2025 data: {e}")
        print("\nTrying 2024 data as fallback...")

        try:
            tor_stats = get_team_batting_stats('TOR', 2024)
            print(f"\nUsing 2024 data: {len(tor_stats)} players found")
            save_data(tor_stats, 'blue_jays_2024_raw.csv', 'raw')

            prepared = prepare_player_stats(tor_stats)
            save_data(prepared, 'blue_jays_2024_prepared.csv', 'processed')

            print(f"\n=== Sample 2024 prepared data ===")
            print(prepared[['name', 'pa', 'ba', 'obp', 'slg', 'iso']].head())

        except Exception as e2:
            print(f"\nError with 2024 data: {e2}")
            sys.exit(1)
