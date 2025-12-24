"""Data processing to create Player objects with calculated probabilities."""

import pandas as pd
from typing import List, Optional
from src.models.player import Player
from src.models.probability import decompose_slash_line
import config


def create_player_from_stats(row: pd.Series) -> Player:
    """Create a Player object from a DataFrame row with statistics.
    
    Args:
        row: pandas Series with player statistics
        
    Returns:
        Player object with calculated probabilities
    """
    # Extract basic stats
    name = row['name']
    ba = row['ba']
    obp = row['obp']
    slg = row['slg']
    iso = row['iso']
    pa = int(row['pa'])

    # Extract stolen base counts if available
    sb = int(row['sb']) if 'sb' in row and pd.notna(row['sb']) else None
    cs = int(row['cs']) if 'cs' in row and pd.notna(row['cs']) else None
    
    # Extract hit counts if available
    singles = int(row['singles']) if 'singles' in row and pd.notna(row['singles']) else None
    doubles = int(row['doubles']) if 'doubles' in row and pd.notna(row['doubles']) else None
    triples = int(row['triples']) if 'triples' in row and pd.notna(row['triples']) else None
    hr = int(row['hr']) if 'hr' in row and pd.notna(row['hr']) else None
    position = row['position'] if 'position' in row and pd.notna(row['position']) else None

    # Create player object first (without probabilities)
    player = Player(
        name=name,
        ba=ba,
        obp=obp,
        slg=slg,
        iso=iso,
        pa=pa,
        singles=singles,
        doubles=doubles,
        triples=triples,
        hr=hr,
        sb=sb,
        cs=cs,
        position=position
    )

    # Calculate probabilities (now passing player object)
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg, player)

    # Update player with probabilities
    player.pa_probs = pa_probs
    player.hit_dist = hit_dist

    return player


def prepare_lineup(df: pd.DataFrame, order: Optional[List[int]] = None) -> List[Player]:
    """Create a lineup of Player objects from DataFrame.
    
    Args:
        df: DataFrame with player statistics (already prepared/cleaned)
        order: Optional list of indices specifying batting order.
               If None, uses DataFrame order (first 9 players)
        
    Returns:
        List of 9 Player objects in batting order
    """
    if order is None:
        # Use first 9 players by default
        if len(df) < 9:
            raise ValueError(f"Need at least 9 players, found {len(df)}")
        order = list(range(9))
    
    if len(order) != 9:
        raise ValueError(f"Lineup must have exactly 9 batters, got {len(order)}")
    
    # Create player objects in specified order
    lineup = []
    for idx in order:
        if idx >= len(df):
            raise ValueError(f"Index {idx} out of range for {len(df)} players")
        player = create_player_from_stats(df.iloc[idx])
        lineup.append(player)
    
    return lineup


def prepare_roster(df: pd.DataFrame) -> List[Player]:
    """Create Player objects for entire roster.
    
    Args:
        df: DataFrame with player statistics
        
    Returns:
        List of all Player objects
    """
    roster = []
    for _, row in df.iterrows():
        player = create_player_from_stats(row)
        roster.append(player)
    
    return roster


def get_lineup_by_stat(df: pd.DataFrame, stat: str = 'ops', ascending: bool = False) -> List[Player]:
    """Create lineup ordered by a specific statistic.
    
    Args:
        df: DataFrame with player statistics
        stat: Statistic to sort by ('ops', 'obp', 'slg', 'ba', 'iso')
        ascending: If True, sort ascending (worst to best), else descending
        
    Returns:
        List of 9 Player objects ordered by specified stat
    """
    df_copy = df.copy()
    
    # Calculate OPS if sorting by it
    if stat == 'ops' and 'ops' not in df_copy.columns:
        df_copy['ops'] = df_copy['obp'] + df_copy['slg']
    
    if stat not in df_copy.columns:
        raise ValueError(f"Stat '{stat}' not found in DataFrame columns")
    
    # Sort and take top 9
    df_sorted = df_copy.sort_values(stat, ascending=ascending).head(9)
    
    # Create lineup
    lineup = []
    for _, row in df_sorted.iterrows():
        player = create_player_from_stats(row)
        lineup.append(player)
    
    return lineup


def print_lineup(lineup: List[Player]):
    """Print lineup information in readable format.
    
    Args:
        lineup: List of Player objects
    """
    print("\n" + "="*80)
    print("LINEUP")
    print("="*80)
    print(f"{'Pos':<4} {'Name':<25} {'BA':>6} {'OBP':>6} {'SLG':>6} {'ISO':>6} {'PA':>5}")
    print("-"*80)
    
    for i, player in enumerate(lineup, 1):
        print(f"{i:<4} {player.name:<25} {player.ba:>6.3f} {player.obp:>6.3f} "
              f"{player.slg:>6.3f} {player.iso:>6.3f} {player.pa:>5}")
    
    # Team totals
    avg_ba = sum(p.ba for p in lineup) / len(lineup)
    avg_obp = sum(p.obp for p in lineup) / len(lineup)
    avg_slg = sum(p.slg for p in lineup) / len(lineup)
    
    print("-"*80)
    print(f"{'AVG':<4} {'':<25} {avg_ba:>6.3f} {avg_obp:>6.3f} {avg_slg:>6.3f}")
    print("="*80)


if __name__ == "__main__":
    # Test with 2025 Blue Jays data
    import sys
    sys.path.append('..')
    from src.data.scraper import load_data
    
    print("=== Testing Data Processor ===\n")
    
    # Load prepared data
    try:
        df = load_data('blue_jays_2025_prepared.csv', 'processed')
    except:
        print("Could not find 2025 data, trying 2024...")
        df = load_data('blue_jays_2024_prepared.csv', 'processed')
    
    print(f"Loaded {len(df)} players")
    
    # Test 1: Create lineup from first 9 players
    print("\n--- Test 1: Default lineup (first 9 players) ---")
    lineup = prepare_lineup(df)
    print_lineup(lineup)
    
    # Verify probabilities
    print("\nSample player probabilities:")
    sample = lineup[0]
    print(f"\n{sample.name}:")
    print("PA Outcomes:")
    for outcome, prob in sample.pa_probs.items():
        print(f"  {outcome}: {prob:.4f}")
    print("Hit Distribution:")
    for hit_type, prob in sample.hit_dist.items():
        print(f"  {hit_type}: {prob:.4f}")
    
    # Test 2: Create lineup by OPS
    print("\n\n--- Test 2: Lineup by OPS (descending) ---")
    lineup_ops = get_lineup_by_stat(df, 'ops', ascending=False)
    print_lineup(lineup_ops)
    
    # Test 3: Create full roster
    print("\n\n--- Test 3: Full roster ---")
    roster = prepare_roster(df)
    print(f"\nCreated {len(roster)} player objects")
    print(f"Sample: {roster[0].name} - BA: {roster[0].ba:.3f}, Probs calculated: {roster[0].pa_probs is not None}")
    
    print("\n✓ All processor tests passed")
