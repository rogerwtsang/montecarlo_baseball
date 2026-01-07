# Changelog

All notable changes to the Baseball Monte Carlo Simulation project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### In Progress
- Position-level contribution tracking (Sprint 3)
- Automated lineup optimization engine (Sprint 4-5)
- Enhanced visualizations: violin plots (Sprint 6)

## [0.4.0] - 2025-01-07

### Added - Sprint 2: Compare & Analyze Tab
**Complete lineup comparison interface**

- **Compare Tab** (`src/gui/tabs/compare_tab.py` - 739 lines):
  - Split panel layout: selection panel (left) and comparison display (right)
  - Results treeview with multi-select (2-4 lineups)
  - Keyboard shortcuts: Ctrl+A to select all, Escape to clear
  - Summary cards showing mean runs and difference from baseline
  - Four comparison views in a tabbed notebook:
    - **Overview**: Side-by-side statistics table with best/worst highlighting
    - **Distributions**: Overlaid histograms with mean lines
    - **Box Plots**: Box plot comparison across lineups
    - **Detailed Stats**: Extended statistics (hits, walks, SB, CS, SF)
  - Effect size analysis with Cohen's d for pairwise comparisons
  - Validation of comparison data before display

- **Summary Card Widget** (`src/gui/widgets/summary_card.py` - 161 lines):
  - Displays lineup name, timestamp, mean runs
  - Color-coded difference from baseline (green for +, red for -)
  - Baseline indicator for first lineup

- **Comparison Table Widget** (`src/gui/widgets/comparison_table.py` - 238 lines):
  - Dynamic columns based on number of lineups (2-4)
  - Automatic best (★) and worst (▼) value highlighting
  - Support for regular values and confidence intervals
  - Section headers for grouping statistics

### Changed
- Updated About dialog to version 0.4.0 with Sprint 2 features
- GUI now includes "9. Compare" tab

Stats: 3 new files, ~1,138 lines of code

## [0.3.0] - 2024-12-24

### Added - Validation Track
**Complete validation framework for model accuracy assessment**

- **Roster Consistency Analyzer** (`scripts/analyze_roster_consistency.py` - 420 lines):
  - Analyzes all 30 MLB teams to identify most roster-consistent teams
  - Single-season or multi-season analysis (2010-2024+)
  - Tracks: total players, qualified players (100+ PA), regulars (300+ PA)
  - Exports detailed CSV reports
  - 2024 results: Dodgers most consistent (15 players), Angels least (26 players)

- **Validation Dataset Preparation** (`scripts/prepare_validation_data.py` - 280 lines):
  - Prepares clean datasets from consistent teams
  - Fetches actual team results (runs, wins, losses)
  - Configurable minimum PA filter
  - Exports to `data/validation/validation_TEAM_YYYY.csv`
  - Displays top players and summary statistics

- **Validation Simulation** (`scripts/validate_simulation.py` - 350 lines):
  - Runs Monte Carlo simulations for validation teams
  - Compares simulated runs to actual runs scored
  - Calculates error metrics: absolute error, percentage error, CI coverage
  - Assessment categories: EXCELLENT (<5%), GOOD (<10%), ACCEPTABLE (<15%)
  - Validates model calibration (95% CI coverage)
  - Exports results with percentile analysis

- **Complete Validation Suite** (`scripts/run_validation_suite.py` - 250 lines):
  - Orchestrates full validation workflow automatically
  - Runs all three tasks in sequence
  - Summary reports with overall accuracy metrics
  - Batch validation across multiple teams/seasons

### Validation Results
- **2024 Dodgers Validation** (most consistent roster):
  - Simulated: 855.4 ± 42.6 runs
  - Actual: 842 runs
  - Error: +13.4 runs (+1.6%)
  - Assessment: ✅ EXCELLENT (within 5%)
  - Calibration: ✅ Actual within 95% CI [772.0, 936.0]

### Documentation
- Created `docs/VALIDATION_TRACK_SUMMARY.md` - Complete validation documentation
- Documented validation methodology and success criteria
- Usage examples for all validation scripts
- Identified model strengths and limitations

### Data
- New directories: `data/analysis/`, `data/validation/`
- Consistency analysis: `roster_consistency_2024.csv` (24 teams)
- Validation datasets: `validation_LAD_2024.csv`
- Validation results: `validation_results.csv`

Stats: 4 new scripts, ~1,300 lines of code, model accuracy validated at 1.6% error

## [0.2.0] - 2024-12-24

### Added - Sprint 1: Foundation
- **Results Manager** (`src/gui/utils/results_manager.py`):
  - Store up to 10 simulation results in memory with automatic cleanup
  - Unique ID generation for each saved result (8-character UUID)
  - Methods: `store_result()`, `get_result()`, `list_results()`, `delete_result()`, `clear_all()`, `compare_results()`
  - Support for comparing up to 4 results simultaneously
  - Full test suite included

- **Save Results Feature** (`src/gui/tabs/run_tab.py`):
  - New "Save Results" button in Run tab
  - User prompt for custom lineup naming
  - Integration with ResultsManager
  - Success confirmation with result ID
  - Error handling for edge cases

- **Optimization Configuration** (`config.py`):
  - `OPT_EXHAUSTIVE_THRESHOLD`: Roster size threshold for exhaustive vs genetic algorithm (default: 10)
  - `OPT_GA_POPULATION_SIZE`: Genetic algorithm population size (default: 50)
  - `OPT_GA_GENERATIONS`: Maximum generations (default: 100)
  - `OPT_GA_MUTATION_RATE`: Mutation probability (default: 0.1)
  - `OPT_GA_TOURNAMENT_SIZE`: Tournament selection size (default: 3)
  - `OPT_DEFAULT_SIMS_PER_LINEUP`: Simulations per lineup candidate (default: 1,000)
  - Full parameter set for both exhaustive search and genetic algorithm optimization

### Changed
- Updated README.md with current feature set and accurate project structure
- Enhanced documentation for GUI workflow and programmatic usage
- Added "What's New" section to README highlighting recent additions

### Documentation
- Created CHANGELOG.md for version tracking
- Updated project structure to reflect actual codebase organization
- Added examples for using ResultsManager programmatically
- Documented new optimization configuration parameters

## [0.1.0] - 2024-12-XX

### Initial Release

#### Simulation Engine
- Player performance modeling from slash line statistics (BA/OBP/SLG)
- Bayesian-smoothed hit type distribution (1B/2B/3B/HR)
- ISO-based hitter classification (singles/balanced/power)
- Probabilistic base-running with configurable aggression parameters
- Stolen base modeling with player-specific SB/CS rates
- Sacrifice fly simulation based on flyout percentage
- Error and wild pitch advancement (~1.5% of PAs)
- Full season simulation (1-162 games configurable)

#### GUI Application (8 Tabs)
- **Setup Tab**: Team selection (30 MLB teams), season picker (2015-2025), simulation parameters
- **Lineup Tab**:
  - Drag-and-drop lineup builder (9 positions)
  - Individual player search and addition from any season
  - Auto-ordering by OPS, OBP, SLG, BA, or ISO
  - Constraint system for lineup rules and position requirements
  - Save/load lineup configurations
- **Baserunning Tab**: Configure probabilistic advancement parameters
- **Errors Tab**: Toggle and configure error/wild pitch rates
- **Distribution Tab**: Customize ISO thresholds and hit distributions
- **Validation Tab**: Validation parameters
- **Output Tab**: Verbosity settings
- **Run Tab**:
  - Execute simulations (100-100,000 iterations)
  - Real-time progress bar
  - Text results with comprehensive statistics
  - Histogram visualization with mean/median markers
  - Export to CSV and JSON

#### Data Integration
- FanGraphs data via `pybaseball` library
- Automatic data caching to reduce API calls
- Support for all 30 MLB teams
- Historical data: 2015-2025 seasons
- Minimum PA filtering (configurable, default: 100)

#### Statistics Tracked
- Runs per season (mean, median, std, min, max, percentiles, 95% CI)
- Hits, walks, left on base
- Stolen bases and caught stealing
- Sacrifice flies
- Runs per game

#### Models Implemented
- `src/models/player.py`: Player dataclass with slash line stats
- `src/models/probability.py`: Hit distribution calculation with Bayesian smoothing
- `src/models/baserunning.py`: Deterministic and probabilistic runner advancement
- `src/models/stolen_bases.py`: SB attempt rates and success probabilities
- `src/models/sacrifice_fly.py`: Sacrifice fly logic
- `src/models/errors.py`: Error/wild pitch advancement

#### Engine
- `src/engine/pa_generator.py`: Plate appearance outcome generation
- `src/engine/inning.py`: Half-inning simulation (3-out logic)
- `src/engine/game.py`: Full 9-inning game simulation
- `src/simulation/season.py`: 162-game season orchestration
- `src/simulation/batch.py`: Multiple season runs with aggregated statistics

#### Configuration
- Centralized `config.py` with all tunable parameters
- Simulation parameters (iterations, games, seed)
- Baserunning aggression levels
- Stolen base scaling
- Hit distribution thresholds
- Bayesian prior weights
- Error rates

#### Testing
- ResultsManager unit tests
- Data scraper tests
- Batch simulation validation

---

## Version Numbering

- **Major** (X.0.0): Significant architectural changes or breaking API changes
- **Minor** (0.X.0): New features, sprints completed
- **Patch** (0.0.X): Bug fixes, minor improvements

Sprint completion increments minor version (0.1.0 → 0.2.0 → 0.3.0, etc.)
