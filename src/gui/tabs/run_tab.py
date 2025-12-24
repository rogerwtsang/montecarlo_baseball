"""Tab for running simulations and viewing results."""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import csv
from typing import Optional, Dict
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class RunTab(ttk.Frame):
    """Tab for running simulations."""

    def __init__(self, parent, **kwargs):
        """Initialize run tab."""
        super().__init__(parent, **kwargs)

        self.results: Optional[Dict] = None
        self.run_callback = None
        self.stop_callback = None

        self._create_widgets()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top control section
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Run button
        self.run_btn = ttk.Button(
            control_frame,
            text="▶ RUN SIMULATION",
            command=self._on_run_clicked,
            style='Accent.TButton'
        )
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Stop button
        self.stop_btn = ttk.Button(
            control_frame,
            text="■ STOP",
            command=self._on_stop_clicked,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready to run simulation")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))

        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack(side=tk.LEFT)

        # Results display section
        results_frame = ttk.LabelFrame(main_frame, text="Simulation Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for results tabs
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)

        # Text results tab
        text_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(text_frame, text="Text Results")

        self.results_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Courier', 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Chart tab
        chart_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(chart_frame, text="Histogram")

        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Export buttons
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(export_frame, text="Export to CSV", command=self._export_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export to JSON", command=self._export_json).pack(side=tk.LEFT)

    def _on_run_clicked(self):
        """Handle run button click."""
        if self.run_callback:
            self.run_callback()

    def _on_stop_clicked(self):
        """Handle stop button click."""
        if self.stop_callback:
            self.stop_callback()

    def set_run_callback(self, callback):
        """Set callback for run button."""
        self.run_callback = callback

    def set_stop_callback(self, callback):
        """Set callback for stop button."""
        self.stop_callback = callback

    def set_running(self, is_running: bool):
        """Update UI for running state."""
        if is_running:
            self.run_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="Simulation running...")
        else:
            self.run_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.status_label.config(text="Ready")

    def update_progress(self, current: int, total: int):
        """
        Update progress bar.

        Args:
            current: Current iteration
            total: Total iterations
        """
        percentage = (current / total) * 100
        self.progress_bar['value'] = percentage
        self.progress_label.config(text=f"{percentage:.1f}%")
        self.status_label.config(text=f"Running: {current:,} / {total:,} iterations")
        self.update()

    def display_results(self, results: Dict):
        """
        Display simulation results.

        Args:
            results: Results dictionary from simulation
        """
        self.results = results

        # Format and display text results
        text = self._format_results(results)
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', text)

        # Create histogram
        self._create_histogram(results)

        # Update status
        self.status_label.config(text="Simulation complete!")
        self.progress_bar['value'] = 100
        self.progress_label.config(text="100%")

    def _format_results(self, results: Dict) -> str:
        """Format results as text."""
        if not results or 'error' in results:
            return f"Error: {results.get('error', 'Unknown error')}"

        summary = results.get('summary', {})
        lineup = results.get('lineup', [])

        lines = []
        lines.append("="*80)
        lines.append("MONTE CARLO BASEBALL SIMULATION RESULTS")
        lines.append("="*80)
        lines.append("")

        # Simulation parameters
        lines.append("Simulation Parameters:")
        lines.append(f"  Iterations:        {summary.get('n_simulations', 'N/A'):,}")
        lines.append(f"  Games per season:  {summary.get('n_games_per_season', 'N/A')}")
        lines.append("")

        # Lineup
        lines.append("Lineup:")
        for i, player in enumerate(lineup, 1):
            if isinstance(player, dict):
                name = player.get('name', 'Unknown')
                ba = player.get('ba', 0)
                obp = player.get('obp', 0)
                slg = player.get('slg', 0)
                lines.append(f"  {i}. {name:25s} {ba:.3f}/{obp:.3f}/{slg:.3f}")
        lines.append("")

        # Runs statistics
        lines.append("-"*80)
        lines.append("RUNS PER SEASON")
        lines.append("-"*80)

        runs = summary.get('runs', {})
        lines.append(f"  Mean:               {runs.get('mean', 0):.1f}")
        lines.append(f"  Median:             {runs.get('median', 0):.1f}")
        lines.append(f"  Std Dev:            {runs.get('std', 0):.1f}")
        lines.append(f"  Min:                {runs.get('min', 0)}")
        lines.append(f"  Max:                {runs.get('max', 0)}")
        lines.append("")

        # Percentiles
        percentiles = runs.get('percentiles', {})
        if percentiles:
            lines.append("  Percentiles:")
            for pct in ['5th', '25th', '50th', '75th', '95th']:
                value = percentiles.get(pct, 0)
                lines.append(f"    {pct:5s}:           {value:.1f}")
            lines.append("")

        # Confidence interval
        ci = runs.get('ci_95', (0, 0))
        lines.append(f"  95% Confidence Interval:")
        lines.append(f"    [{ci[0]:.1f}, {ci[1]:.1f}]")
        lines.append("")

        # Other statistics
        lines.append("-"*80)
        lines.append("OTHER STATISTICS")
        lines.append("-"*80)

        for stat_name, stat_key in [
            ('Hits', 'hits'),
            ('Walks', 'walks'),
            ('Stolen Bases', 'stolen_bases'),
            ('Caught Stealing', 'caught_stealing'),
            ('Sacrifice Flies', 'sacrifice_flies'),
        ]:
            stat = summary.get(stat_key, {})
            mean = stat.get('mean', 0)
            std = stat.get('std', 0)
            lines.append(f"  {stat_name:20s} {mean:.1f} ± {std:.1f}")

        # Runs per game
        rpg = summary.get('runs_per_game', {})
        mean_rpg = rpg.get('mean', 0)
        std_rpg = rpg.get('std', 0)
        lines.append(f"  {'Runs per Game':20s} {mean_rpg:.2f} ± {std_rpg:.2f}")

        lines.append("")
        lines.append("="*80)

        return "\n".join(lines)

    def _create_histogram(self, results: Dict):
        """Create runs distribution histogram."""
        self.ax.clear()

        raw_data = results.get('raw_data', {})
        season_runs = raw_data.get('season_runs', [])

        if not season_runs:
            self.ax.text(0.5, 0.5, 'No data to display', ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return

        # Create histogram
        self.ax.hist(season_runs, bins=30, alpha=0.7, color='steelblue', edgecolor='black')

        # Add mean and median lines
        mean = np.mean(season_runs)
        median = np.median(season_runs)

        self.ax.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean:.1f}')
        self.ax.axvline(median, color='green', linestyle='--', linewidth=2, label=f'Median: {median:.1f}')

        self.ax.set_xlabel('Runs per Season')
        self.ax.set_ylabel('Frequency')
        self.ax.set_title('Distribution of Simulated Runs per Season')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.canvas.draw()

    def _export_csv(self):
        """Export results to CSV."""
        if not self.results:
            messagebox.showwarning("No Results", "No results to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)

                # Write summary statistics
                summary = self.results.get('summary', {})
                writer.writerow(['Statistic', 'Mean', 'Std', 'Median', 'Min', 'Max'])

                for stat_key in ['runs', 'hits', 'walks', 'stolen_bases', 'caught_stealing', 'sacrifice_flies']:
                    stat = summary.get(stat_key, {})
                    writer.writerow([
                        stat_key.replace('_', ' ').title(),
                        stat.get('mean', ''),
                        stat.get('std', ''),
                        stat.get('median', ''),
                        stat.get('min', ''),
                        stat.get('max', '')
                    ])

                # Write raw data
                writer.writerow([])
                writer.writerow(['Raw Season Data'])
                writer.writerow(['Iteration', 'Runs', 'Hits', 'Walks', 'SB', 'CS', 'SF'])

                raw_data = self.results.get('raw_data', {})
                for i in range(len(raw_data.get('season_runs', []))):
                    writer.writerow([
                        i + 1,
                        raw_data.get('season_runs', [])[i],
                        raw_data.get('season_hits', [])[i],
                        raw_data.get('season_walks', [])[i],
                        raw_data.get('season_sb', [])[i],
                        raw_data.get('season_cs', [])[i],
                        raw_data.get('season_sf', [])[i],
                    ])

            messagebox.showinfo("Success", f"Results exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{str(e)}")

    def _export_json(self):
        """Export results to JSON."""
        if not self.results:
            messagebox.showwarning("No Results", "No results to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            # Convert numpy arrays to lists for JSON serialization
            results_copy = {}
            for key, value in self.results.items():
                if isinstance(value, dict):
                    results_copy[key] = {}
                    for k, v in value.items():
                        if isinstance(v, np.ndarray):
                            results_copy[key][k] = v.tolist()
                        elif isinstance(v, (list, tuple)) and len(v) > 0 and isinstance(v[0], np.ndarray):
                            results_copy[key][k] = [arr.tolist() for arr in v]
                        else:
                            results_copy[key][k] = v
                else:
                    results_copy[key] = value

            with open(filename, 'w') as f:
                json.dump(results_copy, f, indent=2)

            messagebox.showinfo("Success", f"Results exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export JSON:\n{str(e)}")
