"""Comparison table widget for displaying side-by-side statistics."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional


class ComparisonTable(ttk.Frame):
    """
    Widget displaying a comparison table with statistics for multiple lineups.

    Uses ttk.Treeview to show stats in rows with lineup values in columns.
    Highlights best (green) and worst (red) values in each row.
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize comparison table.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to Frame
        """
        super().__init__(parent, **kwargs)

        self.tree = None
        self.lineup_names = []
        self._create_widgets()

    def _create_widgets(self):
        """Create table widgets."""
        # Create Treeview with scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            self,
            columns=[],
            show='tree headings',
            yscrollcommand=scrollbar.set,
            selectmode='none'
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Configure tag colors for highlighting
        self.tree.tag_configure('best', background='#E8F5E9')  # Light green
        self.tree.tag_configure('worst', background='#FFEBEE')  # Light red
        self.tree.tag_configure('normal', background='white')
        self.tree.tag_configure('header', font=('TkDefaultFont', 10, 'bold'))

    def setup_columns(self, lineup_names: List[str]):
        """
        Set up table columns for the given lineups.

        Args:
            lineup_names: List of 2-4 lineup names for columns
        """
        self.lineup_names = lineup_names
        num_lineups = len(lineup_names)

        # Define columns: Statistic name + one column per lineup
        columns = ['stat'] + [f'lineup_{i}' for i in range(num_lineups)]
        self.tree['columns'] = columns

        # Configure Statistic column
        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.column('#0', width=0, stretch=False)

        self.tree.heading('stat', text='Statistic', anchor=tk.W)
        self.tree.column('stat', width=200, anchor=tk.W, stretch=False)

        # Configure lineup columns
        for i, name in enumerate(lineup_names):
            col_id = f'lineup_{i}'
            self.tree.heading(col_id, text=name, anchor=tk.CENTER)
            self.tree.column(col_id, width=150, anchor=tk.CENTER, stretch=True)

    def add_row(self, stat_name: str, values: List[float],
                format_str: str = "{:.1f}",
                higher_is_better: bool = True,
                highlight: bool = True):
        """
        Add a row to the comparison table.

        Args:
            stat_name: Name of the statistic
            values: List of values (one per lineup)
            format_str: Format string for displaying values
            higher_is_better: If True, highest value is best; if False, lowest is best
            highlight: Whether to highlight best/worst values
        """
        if len(values) != len(self.lineup_names):
            raise ValueError(f"Expected {len(self.lineup_names)} values, got {len(values)}")

        # Format values
        formatted_values = [format_str.format(v) for v in values]

        # Determine best and worst indices
        best_idx = None
        worst_idx = None

        if highlight and len(values) > 1:
            if higher_is_better:
                best_idx = values.index(max(values))
                worst_idx = values.index(min(values))
            else:
                best_idx = values.index(min(values))
                worst_idx = values.index(max(values))

            # Don't highlight if all values are the same
            if max(values) == min(values):
                best_idx = None
                worst_idx = None

        # Create row values
        row_values = [stat_name] + formatted_values

        # Insert row
        item_id = self.tree.insert('', tk.END, values=row_values)

        # Apply highlighting using tags
        # Note: ttk.Treeview doesn't support per-cell coloring, so we'll highlight
        # by adding visual indicators to the text
        if highlight and best_idx is not None:
            # Re-insert with indicators
            formatted_with_indicators = []
            for i, val in enumerate(formatted_values):
                if i == best_idx and i != worst_idx:
                    formatted_with_indicators.append(f"{val} ★")
                elif i == worst_idx and i != best_idx:
                    formatted_with_indicators.append(f"{val} ▼")
                else:
                    formatted_with_indicators.append(val)

            row_values = [stat_name] + formatted_with_indicators
            self.tree.item(item_id, values=row_values)

    def add_row_with_ci(self, stat_name: str, ci_tuples: List[tuple],
                        higher_is_better: bool = True):
        """
        Add a row with confidence interval values.

        Args:
            stat_name: Name of the statistic
            ci_tuples: List of (low, high) tuples for confidence intervals
            higher_is_better: If True, highest mean is best
        """
        if len(ci_tuples) != len(self.lineup_names):
            raise ValueError(f"Expected {len(self.lineup_names)} CI tuples, got {len(ci_tuples)}")

        # Format as [low, high]
        formatted_values = [f"[{low:.1f}, {high:.1f}]" for low, high in ci_tuples]

        # Use mean of CI for determining best/worst
        mean_values = [(low + high) / 2 for low, high in ci_tuples]

        best_idx = None
        worst_idx = None

        if len(mean_values) > 1:
            if higher_is_better:
                best_idx = mean_values.index(max(mean_values))
                worst_idx = mean_values.index(min(mean_values))
            else:
                best_idx = mean_values.index(min(mean_values))
                worst_idx = mean_values.index(max(mean_values))

            if max(mean_values) == min(mean_values):
                best_idx = None
                worst_idx = None

        # Add indicators
        formatted_with_indicators = []
        for i, val in enumerate(formatted_values):
            if best_idx is not None and i == best_idx and i != worst_idx:
                formatted_with_indicators.append(f"{val} ★")
            elif worst_idx is not None and i == worst_idx and i != best_idx:
                formatted_with_indicators.append(f"{val} ▼")
            else:
                formatted_with_indicators.append(val)

        row_values = [stat_name] + formatted_with_indicators
        self.tree.insert('', tk.END, values=row_values)

    def add_header_row(self, text: str):
        """
        Add a header/separator row.

        Args:
            text: Header text
        """
        values = [text] + [''] * len(self.lineup_names)
        item_id = self.tree.insert('', tk.END, values=values, tags=('header',))

    def clear(self):
        """Clear all rows from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)


if __name__ == "__main__":
    # Test the ComparisonTable widget
    root = tk.Tk()
    root.title("ComparisonTable Test")
    root.geometry("800x400")

    # Create test frame
    test_frame = ttk.Frame(root, padding=20)
    test_frame.pack(fill=tk.BOTH, expand=True)

    # Create comparison table
    table = ComparisonTable(test_frame)
    table.pack(fill=tk.BOTH, expand=True)

    # Set up columns for 3 lineups
    table.setup_columns(['Lineup A', 'Lineup B', 'Lineup C'])

    # Add header
    table.add_header_row('RUNS PER SEASON')

    # Add rows with different statistics
    table.add_row('Mean Runs', [785.3, 802.7, 761.2], "{:.1f}", higher_is_better=True)
    table.add_row('Median Runs', [784.0, 801.0, 760.5], "{:.1f}", higher_is_better=True)
    table.add_row('Std Dev', [25.3, 27.1, 23.5], "{:.1f}", higher_is_better=False)
    table.add_row('Min', [720, 735, 705], "{:.0f}", higher_is_better=True)
    table.add_row('Max', [850, 870, 825], "{:.0f}", higher_is_better=True)

    # Add CI row
    table.add_row_with_ci('95% CI', [(736.4, 834.2), (749.7, 855.7), (715.2, 807.2)])

    # Add another header
    table.add_header_row('PERCENTILES')
    table.add_row('5th', [745.2, 760.1, 725.8], "{:.1f}", higher_is_better=True)
    table.add_row('95th', [825.4, 845.3, 796.6], "{:.1f}", higher_is_better=True)

    root.mainloop()
