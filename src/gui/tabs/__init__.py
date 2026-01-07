"""GUI tabs package."""

from .setup_tab import SetupTab
from .lineup_tab import LineupTab
from .baserunning_tab import BaserunningTab
from .errors_tab import ErrorsTab
from .distribution_tab import DistributionTab
from .validation_tab import ValidationTab
from .output_tab import OutputTab
from .run_tab import RunTab
from .compare_tab import CompareTab

__all__ = [
    'SetupTab',
    'LineupTab',
    'BaserunningTab',
    'ErrorsTab',
    'DistributionTab',
    'ValidationTab',
    'OutputTab',
    'RunTab',
    'CompareTab',
]
