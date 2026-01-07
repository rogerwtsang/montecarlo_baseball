"""Summary card widget for displaying lineup comparison summary."""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from datetime import datetime


class SummaryCard(ttk.Frame):
    """
    Widget displaying a summary card for a lineup in comparison view.

    Shows lineup name, timestamp, mean runs, and difference from baseline.
    """

    def __init__(self, parent, lineup_name: str, timestamp: datetime,
                 mean_runs: float, difference: Optional[float] = None,
                 is_baseline: bool = False, **kwargs):
        """
        Initialize summary card.

        Args:
            parent: Parent widget
            lineup_name: Name of the lineup
            timestamp: When the result was created
            mean_runs: Mean runs per season
            difference: Difference from baseline (None if this is baseline)
            is_baseline: Whether this is the baseline lineup
            **kwargs: Additional arguments passed to Frame
        """
        super().__init__(parent, **kwargs)

        self.lineup_name = lineup_name
        self.timestamp = timestamp
        self.mean_runs = mean_runs
        self.difference = difference
        self.is_baseline = is_baseline

        self._create_widgets()

    def _create_widgets(self):
        """Create card widgets."""
        # Configure card style with border
        self.config(relief=tk.RIDGE, borderwidth=2, padding=10)

        # Lineup name (bold, larger font)
        name_label = ttk.Label(
            self,
            text=self.lineup_name,
            font=('TkDefaultFont', 12, 'bold')
        )
        name_label.pack(anchor=tk.W)

        # Timestamp
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M")
        timestamp_label = ttk.Label(
            self,
            text=timestamp_str,
            font=('TkDefaultFont', 9),
            foreground='gray'
        )
        timestamp_label.pack(anchor=tk.W, pady=(2, 8))

        # Mean runs (large font)
        runs_frame = ttk.Frame(self)
        runs_frame.pack(fill=tk.X, pady=5)

        runs_label = ttk.Label(
            runs_frame,
            text=f"{self.mean_runs:.1f}",
            font=('TkDefaultFont', 24, 'bold')
        )
        runs_label.pack(side=tk.LEFT)

        units_label = ttk.Label(
            runs_frame,
            text=" runs/season",
            font=('TkDefaultFont', 10)
        )
        units_label.pack(side=tk.LEFT, padx=(5, 0), anchor=tk.S, pady=(0, 4))

        # Difference from baseline (if not baseline)
        if self.is_baseline:
            baseline_label = ttk.Label(
                self,
                text="(Baseline)",
                font=('TkDefaultFont', 9, 'italic'),
                foreground='blue'
            )
            baseline_label.pack(anchor=tk.W)
        elif self.difference is not None:
            # Determine color based on positive/negative difference
            if self.difference > 0:
                color = 'green'
                prefix = '+'
            elif self.difference < 0:
                color = 'red'
                prefix = ''
            else:
                color = 'gray'
                prefix = ''

            diff_label = ttk.Label(
                self,
                text=f"{prefix}{self.difference:.1f} vs baseline",
                font=('TkDefaultFont', 10, 'bold'),
                foreground=color
            )
            diff_label.pack(anchor=tk.W, pady=(5, 0))


if __name__ == "__main__":
    # Test the SummaryCard widget
    root = tk.Tk()
    root.title("SummaryCard Test")
    root.geometry("800x300")

    # Create test frame
    test_frame = ttk.Frame(root, padding=20)
    test_frame.pack(fill=tk.BOTH, expand=True)

    # Test data
    now = datetime.now()

    # Create baseline card
    card1 = SummaryCard(
        test_frame,
        lineup_name="Optimal Lineup A",
        timestamp=now,
        mean_runs=785.3,
        is_baseline=True
    )
    card1.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    # Create comparison card with positive difference
    card2 = SummaryCard(
        test_frame,
        lineup_name="Speed-Focused Lineup",
        timestamp=now,
        mean_runs=802.7,
        difference=17.4
    )
    card2.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

    # Create comparison card with negative difference
    card3 = SummaryCard(
        test_frame,
        lineup_name="Power Lineup B",
        timestamp=now,
        mean_runs=761.2,
        difference=-24.1
    )
    card3.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')

    # Configure grid weights
    test_frame.columnconfigure(0, weight=1)
    test_frame.columnconfigure(1, weight=1)
    test_frame.columnconfigure(2, weight=1)

    root.mainloop()
