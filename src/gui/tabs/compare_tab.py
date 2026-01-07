"""Tab for comparing multiple lineup simulation results side-by-side."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, List, Set
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from ..widgets.summary_card import SummaryCard
from ..widgets.comparison_table import ComparisonTable


class CompareTab(ttk.Frame):
    """Tab for comparing simulation results from multiple lineups."""

    def __init__(self, parent, results_manager=None, **kwargs):
        """
        Initialize compare tab.

        Args:
            parent: Parent widget
            results_manager: ResultsManager instance for accessing saved results
            **kwargs: Additional arguments passed to Frame
        """
        super().__init__(parent, **kwargs)

        self.results_manager = results_manager
        self.selected_ids: Set[str] = set()
        self.comparison_data: Optional[Dict] = None
        self.summary_cards: List[SummaryCard] = []
        self.figures: Dict[str, Figure] = {}

        # UI element references
        self.results_tree = None
        self.compare_btn = None
        self.clear_btn = None
        self.summary_frame = None
        self.comparison_notebook = None
        self.placeholder_label = None

        self._create_widgets()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container with two panels
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel: Results selection (25% width)
        left_panel = self._create_selection_panel()
        main_paned.add(left_panel, weight=1)

        # Right panel: Comparison display (75% width)
        right_panel = self._create_comparison_panel()
        main_paned.add(right_panel, weight=3)

    def _create_selection_panel(self) -> ttk.Frame:
        """
        Create the left panel for selecting results to compare.

        Returns:
            Frame containing selection UI
        """
        panel = ttk.LabelFrame(self, text="Select Results to Compare (2-4)", padding=10)

        # Control buttons at top
        button_frame = ttk.Frame(panel)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.compare_btn = ttk.Button(
            button_frame,
            text="Compare Selected",
            command=self._run_comparison,
            state='disabled'
        )
        self.compare_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_btn = ttk.Button(
            button_frame,
            text="Clear Selection",
            command=self._clear_selection
        )
        self.clear_btn.pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self._load_available_results
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Results list with scrollbar
        list_frame = ttk.Frame(panel)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for results
        columns = ('select', 'name', 'mean_runs', 'date')
        self.results_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            selectmode='none'
        )
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_tree.yview)

        # Configure columns
        self.results_tree.heading('select', text='✓', anchor=tk.CENTER)
        self.results_tree.heading('name', text='Lineup Name', anchor=tk.W)
        self.results_tree.heading('mean_runs', text='Mean Runs', anchor=tk.CENTER)
        self.results_tree.heading('date', text='Date', anchor=tk.CENTER)

        self.results_tree.column('select', width=30, anchor=tk.CENTER, stretch=False)
        self.results_tree.column('name', width=150, anchor=tk.W, stretch=True)
        self.results_tree.column('mean_runs', width=80, anchor=tk.CENTER, stretch=False)
        self.results_tree.column('date', width=100, anchor=tk.CENTER, stretch=False)

        # Bind click event for selection
        self.results_tree.bind('<Button-1>', self._on_tree_click)

        # Bind keyboard shortcuts
        self.results_tree.bind('<Control-a>', self._select_all_results)
        self.results_tree.bind('<Escape>', lambda e: self._clear_selection())

        # Load initial results
        self._load_available_results()

        return panel

    def _create_comparison_panel(self) -> ttk.Frame:
        """
        Create the right panel for displaying comparisons.

        Returns:
            Frame containing comparison displays
        """
        panel = ttk.Frame(self)

        # Placeholder label (shown when no comparison is active)
        self.placeholder_label = ttk.Label(
            panel,
            text="Select 2-4 results from the left panel and click 'Compare Selected'",
            font=('TkDefaultFont', 12),
            foreground='gray'
        )
        self.placeholder_label.pack(expand=True)

        # Summary cards frame (hidden initially)
        self.summary_frame = ttk.Frame(panel)
        # Will be packed when comparison is shown

        # Comparison notebook (hidden initially)
        self.comparison_notebook = ttk.Notebook(panel)
        # Will be packed when comparison is shown

        return panel

    def _select_all_results(self, event=None):
        """
        Select all available results (up to 4).

        Args:
            event: Keyboard event (optional)
        """
        if not self.results_manager:
            return

        results_list = self.results_manager.list_results()
        if not results_list:
            return

        # Select up to first 4 results
        self.selected_ids.clear()
        for result in results_list[:4]:
            self.selected_ids.add(result['id'])

        self._load_available_results()
        self._update_compare_button_state()

    def _load_available_results(self):
        """Load available results from ResultsManager into the tree."""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        if not self.results_manager:
            return

        # Get results list
        results_list = self.results_manager.list_results()

        if not results_list:
            # Show message in tree
            self.results_tree.insert('', tk.END, values=('', 'No results available', '', ''))
            self.results_tree.insert('', tk.END, values=('', 'Run simulations and save results to compare', '', ''))
            return

        # Validate selected_ids (remove any that no longer exist)
        valid_ids = {r['id'] for r in results_list}
        self.selected_ids = self.selected_ids.intersection(valid_ids)

        # Populate tree
        for result in results_list:
            result_id = result['id']
            name = result['lineup_name']
            mean_runs = f"{result['mean_runs']:.1f}"
            date = result['timestamp'].strftime("%Y-%m-%d")

            # Check mark if selected
            check = '✓' if result_id in self.selected_ids else ''

            self.results_tree.insert(
                '',
                tk.END,
                iid=result_id,
                values=(check, name, mean_runs, date)
            )

    def _on_tree_click(self, event):
        """
        Handle click on results tree to toggle selection.

        Args:
            event: Click event
        """
        region = self.results_tree.identify('region', event.x, event.y)
        if region != 'cell':
            return

        item = self.results_tree.identify_row(event.y)
        column = self.results_tree.identify_column(event.x)

        if not item or column != '#1':  # Only handle clicks on select column
            return

        # Toggle selection
        self._toggle_selection(item)

    def _toggle_selection(self, result_id: str):
        """
        Toggle selection of a result.

        Args:
            result_id: ID of the result to toggle
        """
        if result_id in self.selected_ids:
            self.selected_ids.remove(result_id)
        else:
            if len(self.selected_ids) >= 4:
                messagebox.showwarning(
                    "Selection Limit",
                    "You can only compare up to 4 lineups at once."
                )
                return
            self.selected_ids.add(result_id)

        # Update tree display
        self._load_available_results()

        # Update compare button state
        self._update_compare_button_state()

    def _clear_selection(self):
        """Clear all selections."""
        self.selected_ids.clear()
        self._load_available_results()
        self._update_compare_button_state()

    def _update_compare_button_state(self):
        """Enable/disable compare button based on selection count."""
        count = len(self.selected_ids)
        if 2 <= count <= 4:
            self.compare_btn.config(state='normal')
        else:
            self.compare_btn.config(state='disabled')

    def _run_comparison(self):
        """Execute comparison of selected results."""
        if len(self.selected_ids) < 2 or len(self.selected_ids) > 4:
            messagebox.showerror(
                "Invalid Selection",
                "Please select 2-4 results to compare."
            )
            return

        if not self.results_manager:
            messagebox.showerror("Error", "Results manager not available")
            return

        try:
            # Get comparison data from ResultsManager
            self.comparison_data = self.results_manager.compare_results(list(self.selected_ids))

            # Validate comparison data
            if not self._validate_comparison_data():
                messagebox.showerror(
                    "Invalid Data",
                    "One or more selected results have missing or incompatible data.\n"
                    "Please ensure all results are from complete simulations."
                )
                return

            # Display comparison
            self._display_comparison()

        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Failed to compare results:\n{str(e)}")

    def _validate_comparison_data(self) -> bool:
        """
        Validate that comparison data is complete and compatible.

        Returns:
            True if valid, False otherwise
        """
        if not self.comparison_data:
            return False

        try:
            results_list = self.comparison_data['results']

            for result in results_list:
                # Check for required summary data
                if 'summary' not in result:
                    return False

                summary = result['summary']
                if 'runs' not in summary:
                    return False

                # Check for required raw data
                if 'raw_data' not in result:
                    return False

                raw_data = result['raw_data']
                if 'season_runs' not in raw_data or not raw_data['season_runs']:
                    return False

            return True

        except (KeyError, TypeError, IndexError):
            return False

    def _display_comparison(self):
        """Display the comparison in the right panel."""
        if not self.comparison_data:
            return

        # Hide placeholder
        self.placeholder_label.pack_forget()

        # Clear previous comparison
        self._clear_comparison_display()

        # Show summary cards
        self._create_summary_cards()

        # Show comparison notebook
        self._create_comparison_notebook()

    def _clear_comparison_display(self):
        """Clear existing comparison displays."""
        # Clear summary cards
        for card in self.summary_cards:
            card.destroy()
        self.summary_cards.clear()

        # Clear notebook tabs
        if self.comparison_notebook:
            for tab in self.comparison_notebook.tabs():
                self.comparison_notebook.forget(tab)

    def _create_summary_cards(self):
        """Create summary cards for each lineup."""
        # Pack summary frame
        self.summary_frame.pack(fill=tk.X, pady=(0, 10))

        lineup_names = self.comparison_data['lineup_names']
        timestamps = self.comparison_data['timestamps']
        results_list = self.comparison_data['results']

        # Get mean runs for each lineup
        mean_runs_list = [
            r['summary']['runs']['mean']
            for r in results_list
        ]

        # Baseline is the first lineup
        baseline_mean = mean_runs_list[0]

        # Create cards
        for i, (name, timestamp, mean_runs) in enumerate(zip(lineup_names, timestamps, mean_runs_list)):
            is_baseline = (i == 0)
            difference = None if is_baseline else mean_runs - baseline_mean

            card = SummaryCard(
                self.summary_frame,
                lineup_name=name,
                timestamp=timestamp,
                mean_runs=mean_runs,
                difference=difference,
                is_baseline=is_baseline
            )
            card.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            self.summary_cards.append(card)

        # Configure grid weights
        for i in range(len(lineup_names)):
            self.summary_frame.columnconfigure(i, weight=1)

    def _create_comparison_notebook(self):
        """Create notebook with comparison views."""
        self.comparison_notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self._create_overview_table_tab()
        self._create_distribution_chart_tab()
        self._create_boxplot_chart_tab()
        self._create_detailed_stats_tab()

    def _create_overview_table_tab(self):
        """Create Tab 1: Overview statistics table."""
        # Create tab frame
        tab_frame = ttk.Frame(self.comparison_notebook, padding=10)
        self.comparison_notebook.add(tab_frame, text="Overview")

        # Info label at top
        info_frame = ttk.Frame(tab_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_label = ttk.Label(
            info_frame,
            text="★ = Best value  |  ▼ = Worst value  |  Effect sizes shown below for pairwise comparisons",
            font=('TkDefaultFont', 9),
            foreground='gray'
        )
        info_label.pack(anchor=tk.W)

        # Create comparison table
        table = ComparisonTable(tab_frame)
        table.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Set up columns
        lineup_names = self.comparison_data['lineup_names']
        table.setup_columns(lineup_names)

        # Extract data from results
        results_list = self.comparison_data['results']

        # Add runs statistics
        table.add_header_row('RUNS PER SEASON')

        # Mean runs
        mean_runs = [r['summary']['runs']['mean'] for r in results_list]
        table.add_row('Mean', mean_runs, "{:.1f}", higher_is_better=True)

        # Median runs
        median_runs = [r['summary']['runs']['median'] for r in results_list]
        table.add_row('Median', median_runs, "{:.1f}", higher_is_better=True)

        # Std dev
        std_runs = [r['summary']['runs']['std'] for r in results_list]
        table.add_row('Std Dev', std_runs, "{:.1f}", higher_is_better=False)

        # Min/Max
        min_runs = [r['summary']['runs']['min'] for r in results_list]
        table.add_row('Min', min_runs, "{:.0f}", higher_is_better=True)

        max_runs = [r['summary']['runs']['max'] for r in results_list]
        table.add_row('Max', max_runs, "{:.0f}", higher_is_better=True)

        # 95% CI
        ci_tuples = [tuple(r['summary']['runs']['ci_95']) for r in results_list]
        table.add_row_with_ci('95% CI', ci_tuples, higher_is_better=True)

        # Percentiles
        table.add_header_row('PERCENTILES')
        for pct in ['5th', '25th', '50th', '75th', '95th']:
            pct_values = [r['summary']['runs']['percentiles'][pct] for r in results_list]
            table.add_row(pct, pct_values, "{:.1f}", higher_is_better=True)

        # Runs per game
        table.add_header_row('RUNS PER GAME')
        rpg_mean = [r['summary']['runs_per_game']['mean'] for r in results_list]
        rpg_std = [r['summary']['runs_per_game']['std'] for r in results_list]

        # Format as mean ± std
        rpg_formatted = [f"{m:.2f} ± {s:.2f}" for m, s in zip(rpg_mean, rpg_std)]
        # For highlighting, just use the mean values
        table.add_row('Mean ± Std', rpg_mean, "{:.2f}", higher_is_better=True)

        # Add statistical significance section
        self._add_effect_size_info(tab_frame, results_list, lineup_names)

    def _add_effect_size_info(self, parent, results_list, lineup_names):
        """
        Add effect size information for pairwise comparisons.

        Args:
            parent: Parent widget
            results_list: List of result dictionaries
            lineup_names: List of lineup names
        """
        # Create frame for effect size info
        effect_frame = ttk.LabelFrame(parent, text="Effect Size Analysis (Cohen's d)", padding=10)
        effect_frame.pack(fill=tk.X, pady=(10, 0))

        # Info label
        info_label = ttk.Label(
            effect_frame,
            text="Effect size magnitude: Small (0.2-0.5), Medium (0.5-0.8), Large (>0.8)",
            font=('TkDefaultFont', 9, 'italic'),
            foreground='gray'
        )
        info_label.pack(anchor=tk.W, pady=(0, 5))

        # Calculate effect sizes for all pairwise comparisons
        n = len(results_list)
        if n < 2:
            return

        # Extract raw data
        raw_data = [r['raw_data']['season_runs'] for r in results_list]

        # Create grid of comparisons
        comparison_text = []
        for i in range(n):
            for j in range(i + 1, n):
                effect_size = self._calculate_cohens_d(
                    np.array(raw_data[i]),
                    np.array(raw_data[j])
                )

                # Determine magnitude
                abs_d = abs(effect_size)
                if abs_d < 0.2:
                    magnitude = "Negligible"
                elif abs_d < 0.5:
                    magnitude = "Small"
                elif abs_d < 0.8:
                    magnitude = "Medium"
                else:
                    magnitude = "Large"

                # Determine which lineup is better
                if effect_size > 0:
                    better = lineup_names[i]
                    direction = ">"
                else:
                    better = lineup_names[j]
                    direction = "<"
                    effect_size = -effect_size

                comparison_text.append(
                    f"  {lineup_names[i]} vs {lineup_names[j]}: "
                    f"d = {effect_size:+.3f} ({magnitude}) - {better} performs better"
                )

        # Display comparisons
        if comparison_text:
            text_widget = tk.Text(
                effect_frame,
                height=min(len(comparison_text) + 1, 6),
                width=80,
                font=('Courier', 9),
                wrap=tk.WORD,
                relief=tk.FLAT,
                background='#f0f0f0'
            )
            text_widget.pack(fill=tk.X)

            text_widget.insert('1.0', '\n'.join(comparison_text))
            text_widget.config(state='disabled')  # Make read-only

    def _create_distribution_chart_tab(self):
        """Create Tab 2: Overlaid histograms."""
        # Create tab frame
        tab_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(tab_frame, text="Distributions")

        # Create matplotlib figure
        figure = Figure(figsize=(10, 6), dpi=100)
        ax = figure.add_subplot(111)

        # Get data
        lineup_names = self.comparison_data['lineup_names']
        results_list = self.comparison_data['results']

        # Plot overlaid histograms
        colors = self._get_lineup_colors(len(lineup_names))

        for i, (name, result) in enumerate(zip(lineup_names, results_list)):
            season_runs = result['raw_data']['season_runs']
            mean_runs = np.mean(season_runs)

            # Histogram
            ax.hist(season_runs, bins=30, alpha=0.6, color=colors[i],
                   edgecolor='black', linewidth=0.5, label=name)

            # Mean line
            ax.axvline(mean_runs, color=colors[i], linestyle='--',
                      linewidth=2, alpha=0.8)

        ax.set_xlabel('Runs per Season')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Simulated Runs per Season')
        ax.legend()
        ax.grid(True, alpha=0.3)

        figure.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(figure, master=tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['distribution'] = figure

    def _create_boxplot_chart_tab(self):
        """Create Tab 3: Box plots."""
        # Create tab frame
        tab_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(tab_frame, text="Box Plots")

        # Create matplotlib figure
        figure = Figure(figsize=(10, 6), dpi=100)
        ax = figure.add_subplot(111)

        # Get data
        lineup_names = self.comparison_data['lineup_names']
        results_list = self.comparison_data['results']
        colors = self._get_lineup_colors(len(lineup_names))

        # Extract season runs for each lineup
        data = [result['raw_data']['season_runs'] for result in results_list]

        # Create box plots
        bp = ax.boxplot(data, labels=lineup_names, patch_artist=True)

        # Color the boxes
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Runs per Season')
        ax.set_title('Box Plot Comparison of Simulated Runs')
        ax.grid(True, alpha=0.3, axis='y')

        figure.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(figure, master=tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['boxplot'] = figure

    def _create_detailed_stats_tab(self):
        """Create Tab 4: Detailed statistics table."""
        # Create tab frame
        tab_frame = ttk.Frame(self.comparison_notebook, padding=10)
        self.comparison_notebook.add(tab_frame, text="Detailed Stats")

        # Create comparison table
        table = ComparisonTable(tab_frame)
        table.pack(fill=tk.BOTH, expand=True)

        # Set up columns
        lineup_names = self.comparison_data['lineup_names']
        table.setup_columns(lineup_names)

        # Extract data from results
        results_list = self.comparison_data['results']

        # Add detailed statistics
        stats_config = [
            ('hits', 'Hits per Season', True),
            ('walks', 'Walks per Season', True),
            ('stolen_bases', 'Stolen Bases', True),
            ('caught_stealing', 'Caught Stealing', False),
            ('sacrifice_flies', 'Sacrifice Flies', True),
        ]

        for stat_key, stat_name, higher_is_better in stats_config:
            stat_data = results_list[0]['summary'].get(stat_key, {})

            if stat_data:  # Only show if data exists
                means = [r['summary'][stat_key]['mean'] for r in results_list]
                table.add_row(stat_name, means, "{:.1f}", higher_is_better=higher_is_better)

    def _get_lineup_colors(self, num_lineups: int) -> List[str]:
        """
        Get color scheme for lineups.

        Args:
            num_lineups: Number of lineups (2-4)

        Returns:
            List of color hex codes
        """
        colors = [
            '#4682B4',  # Steel Blue
            '#FF7F50',  # Coral
            '#3CB371',  # Medium Sea Green
            '#FFD700',  # Gold
        ]
        return colors[:num_lineups]

    def _calculate_cohens_d(self, data1: np.ndarray, data2: np.ndarray) -> float:
        """
        Calculate Cohen's d effect size between two datasets.

        Args:
            data1: First dataset
            data2: Second dataset

        Returns:
            Cohen's d value
        """
        mean1, mean2 = np.mean(data1), np.mean(data2)
        std1, std2 = np.std(data1, ddof=1), np.std(data2, ddof=1)
        n1, n2 = len(data1), len(data2)

        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

        # Cohen's d
        d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0

        return d
