#!/usr/bin/env python3
"""
Monte Carlo Baseball Simulator - GUI Application

Main entry point for the Tkinter-based GUI application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.tabs import (
    SetupTab,
    LineupTab,
    BaserunningTab,
    ErrorsTab,
    DistributionTab,
    ValidationTab,
    OutputTab,
    RunTab,
    CompareTab
)
from src.gui.utils import SimulationRunner, ConfigManager, ResultsManager


class MonteCarloBaseballGUI:
    """Main GUI application for Monte Carlo Baseball Simulator."""

    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Monte Carlo Baseball Simulator")
        self.root.geometry("1200x800")

        # Initialize managers
        self.sim_runner = SimulationRunner()
        self.config_manager = ConfigManager()
        self.results_manager = ResultsManager(max_results=10)

        # Create UI
        self._create_menu()
        self._create_main_ui()
        self._create_status_bar()

        # Set up tab interactions
        self._setup_callbacks()

        # Load last configuration
        self._load_last_config()

    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Configuration", command=self._save_config)
        file_menu.add_command(label="Load Configuration", command=self._load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_ui(self):
        """Create main UI with tabs."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create all tabs
        self.setup_tab = SetupTab(self.notebook)
        self.lineup_tab = LineupTab(self.notebook)
        self.baserunning_tab = BaserunningTab(self.notebook)
        self.errors_tab = ErrorsTab(self.notebook)
        self.distribution_tab = DistributionTab(self.notebook)
        self.validation_tab = ValidationTab(self.notebook)
        self.output_tab = OutputTab(self.notebook)
        self.run_tab = RunTab(self.notebook, results_manager=self.results_manager)
        self.compare_tab = CompareTab(self.notebook, results_manager=self.results_manager)

        # Add tabs to notebook
        self.notebook.add(self.setup_tab, text="1. Setup")
        self.notebook.add(self.lineup_tab, text="2. Lineup")
        self.notebook.add(self.baserunning_tab, text="3. Baserunning")
        self.notebook.add(self.errors_tab, text="4. Errors")
        self.notebook.add(self.distribution_tab, text="5. Distribution")
        self.notebook.add(self.validation_tab, text="6. Validation")
        self.notebook.add(self.output_tab, text="7. Output")
        self.notebook.add(self.run_tab, text="8. Run")
        self.notebook.add(self.compare_tab, text="9. Compare")

        # Initially disable lineup tab until data is loaded
        self.notebook.tab(1, state='disabled')

    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_callbacks(self):
        """Set up callbacks between tabs."""
        # Setup tab: data loaded callback
        self.setup_tab.set_data_loaded_callback(self._on_data_loaded)

        # Run tab: run and stop callbacks
        self.run_tab.set_run_callback(self._run_simulation)
        self.run_tab.set_stop_callback(self._stop_simulation)

    def _on_data_loaded(self, roster, roster_df):
        """Handle data loaded from setup tab."""
        # Enable lineup tab
        self.notebook.tab(1, state='normal')

        # Load data into lineup tab
        self.lineup_tab.load_data(roster, roster_df)

        # Update status
        team = self.setup_tab.get_team_code()
        season = self.setup_tab.get_config()['season']
        self.status_bar.config(text=f"Loaded {len(roster)} players from {team} {season}")

        # Switch to lineup tab
        self.notebook.select(1)

    def _run_simulation(self):
        """Run the simulation."""
        # Validate lineup
        lineup = self.lineup_tab.get_lineup()
        if not lineup or not all(lineup):
            messagebox.showerror("Incomplete Lineup", "Please fill all 9 lineup slots before running simulation")
            return

        # Validate constraints
        is_valid, errors = self.lineup_tab.validate_lineup()
        if not is_valid:
            error_msg = "Lineup violates constraints:\n\n" + "\n".join(f"• {err}" for err in errors)
            messagebox.showerror("Constraint Violation", error_msg)
            return

        # Collect all configuration
        config_overrides = {}

        # From setup tab
        setup_config = self.setup_tab.get_config()
        config_overrides['n_iterations'] = setup_config['n_iterations']
        config_overrides['n_games'] = setup_config['n_games']
        config_overrides['n_innings'] = setup_config['n_innings']
        config_overrides['random_seed'] = setup_config['random_seed']

        # From baserunning tab
        config_overrides.update(self.baserunning_tab.get_config())

        # From errors tab
        config_overrides.update(self.errors_tab.get_config())

        # From distribution tab
        config_overrides.update(self.distribution_tab.get_config())

        # From validation tab
        config_overrides.update(self.validation_tab.get_config())

        # From output tab
        output_config = self.output_tab.get_config()
        config_overrides['verbosity'] = output_config['verbosity']

        # Update UI
        self.run_tab.set_running(True)
        self.status_bar.config(text="Running simulation...")

        # Start simulation in thread
        self.sim_runner.run_in_thread(
            lineup=lineup,
            config_overrides=config_overrides,
            progress_callback=self._on_progress,
            complete_callback=self._on_simulation_complete
        )

    def _stop_simulation(self):
        """Stop the running simulation."""
        self.sim_runner.stop()
        self.status_bar.config(text="Stopping simulation...")

    def _on_progress(self, current: int, total: int):
        """Handle simulation progress update."""
        self.run_tab.update_progress(current, total)

    def _on_simulation_complete(self, results):
        """Handle simulation completion."""
        self.run_tab.set_running(False)

        if results is None:
            # Simulation was stopped
            self.status_bar.config(text="Simulation stopped")
            messagebox.showinfo("Stopped", "Simulation was stopped")
        elif 'error' in results:
            # Error occurred
            self.status_bar.config(text="Simulation error")
            messagebox.showerror("Error", f"Simulation failed:\n{results['error']}")
        else:
            # Success
            self.run_tab.display_results(results)
            self.status_bar.config(text="Simulation complete")
            self.notebook.select(7)  # Switch to run tab

    def _save_config(self):
        """Save current GUI configuration."""
        config = {
            'setup': self.setup_tab.get_config(),
            'baserunning': self.baserunning_tab.get_config(),
            'errors': self.errors_tab.get_config(),
            'distribution': self.distribution_tab.get_config(),
            'validation': self.validation_tab.get_config(),
            'output': self.output_tab.get_config(),
        }

        if self.config_manager.save_gui_config(config):
            messagebox.showinfo("Success", "Configuration saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save configuration")

    def _load_config(self):
        """Load GUI configuration."""
        config = self.config_manager.load_gui_config()
        if not config:
            messagebox.showinfo("No Config", "No saved configuration found")
            return

        # Note: This would require implementing set_config methods for all tabs
        messagebox.showinfo("Info", "Configuration loading not yet implemented")

    def _load_last_config(self):
        """Load last used configuration on startup."""
        config = self.config_manager.load_gui_config()
        # Could load saved config here, but for now we use defaults

    def _show_about(self):
        """Show about dialog."""
        about_text = """Monte Carlo Baseball Simulator

Version 0.4.0 (Sprint 2 Complete)

A sophisticated Monte Carlo simulation tool for baseball
lineup optimization and season analysis.

New in 0.4.0:
• Compare Tab for side-by-side lineup analysis
• Summary cards with baseline comparison
• Distribution and box plot visualizations
• Effect size analysis (Cohen's d)

Previous:
• Results Manager for storing simulations
• Model validation (1.6% error vs MLB data)

Built with Python and Tkinter."""

        messagebox.showinfo("About", about_text)

    def _on_exit(self):
        """Handle application exit."""
        if self.sim_runner.is_running():
            if messagebox.askyesno("Confirm Exit", "Simulation is running. Exit anyway?"):
                self.sim_runner.stop()
                self.root.quit()
        else:
            self.root.quit()


def main():
    """Main entry point."""
    root = tk.Tk()

    # Configure ttk style
    style = ttk.Style()
    style.theme_use('clam')  # Use modern theme

    # Create and run application
    app = MonteCarloBaseballGUI(root)

    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app._on_exit)

    root.mainloop()


if __name__ == "__main__":
    main()
