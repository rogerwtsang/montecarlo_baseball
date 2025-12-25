# Baseball Monte Carlo Simulation

A Monte Carlo simulation framework for analyzing baseball lineup optimization using Bayesian statistical methods.

## 🆕 What's New

**Sprint 1 Complete** (December 2024):
- ✅ **Results Manager**: Store up to 10 simulation results in memory for comparison
- ✅ **Save Results Button**: Save lineups with custom names from the Run tab
- ✅ **Optimization Config**: Framework for automated lineup optimization (implementation in Sprint 4-5)

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## Project Overview

This project implements a Monte Carlo simulator to model baseball team performance based on player statistics. The primary research question: **Can we determine the optimal batting order arrangement across a full season?**

### Key Features

#### Simulation Engine
- Player performance modeling from slash line statistics (BA/OBP/SLG)
- Bayesian-smoothed hit type distribution (1B/2B/3B/HR)
- Probabilistic base-running with configurable aggression
- Stolen base modeling with player-specific SB/CS rates
- Sacrifice fly simulation
- Error and wild pitch advancement
- Full season simulation (configurable 1-162 games)

#### GUI Application
- **8-tab interface** for complete simulation control
- **Setup Tab**: Team/season selection, simulation parameters
- **Lineup Tab**: Drag-and-drop lineup builder with constraints system
- **Baserunning/Errors/Distribution Tabs**: Fine-tune simulation parameters
- **Run Tab**: Execute simulations with real-time progress
- **Results Management**: Save and compare multiple lineup simulations
- Individual player search and addition from any season

#### Data & Analysis
- FanGraphs data integration via `pybaseball`
- Statistical validation against actual team performance
- Results export to CSV/JSON formats
- Comprehensive statistics: runs, hits, walks, SB/CS, sacrifice flies

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd baseball-monte-carlo
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
montecarlo_baseball/
├── src/
│   ├── data/              # Data acquisition and processing
│   │   ├── scraper.py     # FanGraphs/pybaseball integration
│   │   └── processor.py   # Convert stats to Player objects
│   ├── models/            # Player models and probability calculations
│   │   ├── player.py      # Player dataclass
│   │   ├── probability.py # Hit distribution, Bayesian smoothing
│   │   ├── baserunning.py # Runner advancement logic
│   │   ├── stolen_bases.py
│   │   ├── sacrifice_fly.py
│   │   └── errors.py
│   ├── engine/            # Game simulation engine
│   │   ├── pa_generator.py # Plate appearance outcomes
│   │   ├── game_state.py
│   │   ├── inning.py      # Half-inning simulation
│   │   └── game.py        # 9-inning game
│   ├── simulation/        # Season and batch simulation
│   │   ├── season.py      # 162-game season
│   │   └── batch.py       # Multiple seasons with statistics
│   └── gui/               # Tkinter GUI application
│       ├── tabs/          # 8 main tabs
│       ├── widgets/       # Custom GUI components
│       └── utils/         # Results manager, config manager
├── tests/                 # Unit tests
├── data/                  # Data storage (git-ignored)
├── scripts/               # Utility scripts
├── config.py              # Central configuration
├── gui.py                 # GUI entry point
└── main.py                # CLI entry point (TODO)
```

## Usage

### GUI Application (Recommended)

Launch the graphical interface:

```bash
python gui.py
```

**Workflow**:
1. **Setup Tab**: Select team (e.g., TOR) and season (2015-2025)
2. **Lineup Tab**: Build your 9-player lineup using drag-and-drop or auto-order
3. **Configure**: Adjust baserunning, errors, and distribution settings (optional)
4. **Run Tab**: Execute simulation (100-100,000 iterations)
5. **Results**: View statistics, histogram, and export to CSV/JSON
6. **Save Results**: Store simulations for later comparison

### Programmatic Usage

```python
from src.data.scraper import get_team_batting_stats
from src.data.processor import prepare_roster
from src.simulation.batch import run_simulations

# Load player data
stats_df = get_team_batting_stats('TOR', 2024)
roster = prepare_roster(stats_df)

# Create lineup (top 9 players by OPS)
lineup = sorted(roster, key=lambda p: p.obp + p.slg, reverse=True)[:9]

# Run 10,000 season simulations
results = run_simulations(
    lineup,
    n_iterations=10000,
    n_games=162,
    random_seed=42
)

# Access results
print(f"Mean runs per season: {results['summary']['runs']['mean']:.1f}")
print(f"95% CI: {results['summary']['runs']['ci_95']}")
```

### Saving and Comparing Lineups

**In GUI**: Use the "Save Results" button to store simulation results, then access them in the Compare tab (coming soon in Sprint 2).

**Programmatically**:
```python
from src.gui.utils.results_manager import ResultsManager

# Create manager
manager = ResultsManager(max_results=10)

# Run and save multiple lineup simulations
for lineup_config in [lineup_a, lineup_b, lineup_c]:
    results = run_simulations(lineup_config, n_iterations=10000)
    manager.store_result(f"Lineup {lineup_config[0].name}", results)

# Compare results
comparison = manager.compare_results([id1, id2])
```

## Configuration

Edit `config.py` to adjust simulation behavior:

**Simulation Parameters**:
- `N_SIMULATIONS`: Number of seasons to simulate (default: 10,000)
- `N_GAMES_PER_SEASON`: Games per season (default: 162)
- `RANDOM_SEED`: For reproducible results

**Baserunning**:
- `ENABLE_PROBABILISTIC_BASERUNNING`: Toggle probabilistic advancement
- `BASERUNNING_AGGRESSION`: Probabilities for 1st→3rd, scoring on doubles

**Special Events**:
- `ENABLE_STOLEN_BASES`: Toggle SB attempts
- `ENABLE_SACRIFICE_FLIES`: Toggle sacrifice fly logic
- `ENABLE_ERRORS_WILD_PITCHES`: Toggle defensive errors

**Hit Distribution**:
- `ISO_THRESHOLDS`: Classify hitters as singles/balanced/power
- `HIT_DISTRIBUTIONS`: Hit type probabilities for each class
- `BAYESIAN_PRIOR_WEIGHT`: Smoothing strength for small samples

**Optimization** (NEW in Sprint 1):
- `OPT_EXHAUSTIVE_THRESHOLD`: Max roster size for exhaustive search
- `OPT_GA_POPULATION_SIZE`: Genetic algorithm population size
- `OPT_GA_GENERATIONS`: Maximum GA generations
- `OPT_DEFAULT_SIMS_PER_LINEUP`: Simulations per lineup candidate

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

The project follows a modular architecture:

1. **Data Layer**: Scrapes and processes player statistics
2. **Models**: Converts stats to probabilities, handles base-running
3. **Engine**: Simulates plate appearances, innings, and games
4. **Simulation**: Orchestrates multiple iterations
5. **Analysis**: Compares results and generates insights

### Current Development (Active)

**Sprint 1 - Complete** ✅:
- [x] Results Manager for storing/comparing simulations
- [x] "Save Results" functionality in GUI
- [x] Optimization configuration framework

**Sprint 2-7 - Planned** (See `/home/roger/.claude/plans/` for details):
- [ ] Compare & Analyze tab for side-by-side lineup comparison
- [ ] Position-level contribution tracking
- [ ] Automated lineup optimization (exhaustive + genetic algorithm)
- [ ] Enhanced visualizations (box plots, violin plots)
- [ ] Excel export with formatting

### Future Enhancements

**Model Improvements**:
- [ ] Opponent/pitching integration for win/loss tracking
- [ ] Platoon splits (L/R batter-pitcher matchups)
- [ ] Situational hitting (count-based outcomes)
- [ ] Park factors (ballpark adjustments)
- [ ] Advanced baserunning with speed ratings

**Technical Improvements**:
- [ ] CLI implementation (`main.py`)
- [ ] Performance optimization (vectorization, parallelization)
- [ ] Comprehensive test suite
- [ ] Web interface
- [ ] Pitch-level simulation

## Research Phases

### Phase 1: Validation (Current)
Validate model against actual 2025 Blue Jays performance

### Phase 2: Baseline Comparison
Test standard lineup configurations (OPS-based, conventional wisdom)

### Phase 3: Optimization
Explore lineup space to find optimal batting order

## Data Sources

- Primary: Baseball Reference via `pybaseball`
- League averages: MLB aggregate statistics
- Target: 2025 Toronto Blue Jays roster

## Contributing

This is a research project. Contributions welcome for:
- Enhanced probability models
- Additional validation metrics
- Visualization improvements
- Performance optimizations

## License

[To be determined]

## Contact

[Your contact information]

## Acknowledgments

- `pybaseball` package for data access
- Baseball statistical modeling literature
- Monte Carlo simulation methodology
