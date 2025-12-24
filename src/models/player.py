# ============================================================================
# src/models/player.py
# ============================================================================
"""Player data representation."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Player:
    """Represents a baseball player with their statistics and calculated probabilities.

    Attributes:
        name: Player name
        ba: Batting average
        obp: On-base percentage
        slg: Slugging percentage
        iso: Isolated power (SLG - BA)
        pa: Plate appearances
        singles: Number of singles (if available)
        doubles: Number of doubles (if available)
        triples: Number of triples (if available)
        hr: Number of home runs (if available)
        sb: Stolen bases (if available)
        cs: Caught stealing (if available)
        position: Defensive position (if available)
        pa_probs: Calculated probabilities for each PA outcome
        hit_dist: Distribution of hit types given a hit occurred
    """
    name: str
    ba: float
    obp: float
    slg: float
    iso: float
    pa: int

    # Raw counts (optional, for future Bayesian upgrade)
    singles: Optional[int] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    hr: Optional[int] = None

    # Stolen base data
    sb: Optional[int] = None
    cs: Optional[int] = None

    # Position
    position: Optional[str] = None

    # Calculated probabilities
    pa_probs: Optional[Dict[str, float]] = None
    hit_dist: Optional[Dict[str, float]] = None

    def __post_init__(self):
        """Calculate ISO if not provided."""
        if self.iso is None:
            self.iso = self.slg - self.ba
