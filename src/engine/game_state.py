# ============================================================================
# src/engine/game_state.py
# ============================================================================
"""Game state representation."""

from dataclasses import dataclass
from typing import List, Optional
from src.models.player import Player
from src.models.baserunning import BasesState


@dataclass
class GameState:
    """Represents the current state of a baseball game.

    Attributes:
        inning: Current inning (1-9+)
        half: 'top' or 'bottom'
        outs: Number of outs in current half-inning (0-2)
        bases: Current runners on base
        score_away: Away team score
        score_home: Home team score
        batter_idx: Current batter index in lineup (0-8)
        lineup: List of 9 Player objects in batting order
    """
    inning: int
    half: str  # 'top' or 'bottom'
    outs: int
    bases: BasesState
    score_away: int
    score_home: int
    batter_idx: int
    lineup: List[Player]
