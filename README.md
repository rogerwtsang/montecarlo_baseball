# Baseball Monte Carlo Simulation

A Monte Carlo simulation framework for analyzing baseball lineup optimization using Bayesian statistical methods.

## Project Overview

This project implements a Monte Carlo simulator to model baseball team performance based on player statistics. The primary research question: **Can we determine the optimal batting order arrangement across a full season?**

### Key Features

- Player performance modeling from slash line statistics (BA/OBP/SLG)
- ISO-based hit type distribution calculation
- Deterministic base-running rules (extensible to probabilistic)
- Full season simulation (162 games)
- Lineup comparison and optimization framework
- Statistical validation against actual team performance

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
baseball-monte-carlo/
├── src/              # Core simulation code
│   ├── data/         # Data acquisition and processing
│   ├── models/       # Player representation and probability models
│   ├── engine/       # Game state and simulation engine
│   ├── simulation/   # Season and batch simulation
│   └── analysis/     # Results analysis and visualization
├── tests/            # Unit tests
├── notebooks/        # Jupyter notebooks for exploration
├── data/             # Data storage (git-ignored)
├── scripts/          # Utility scripts
└── main.py           # Entry point
```

## Usage

### Basic Simulation

Run a season simulation for the 2025 Blue Jays:

```bash
python main.py
```

### Custom Lineup Testing

```python
from src.data.scraper import get_team_batting_stats
from src.data.processor import prepare_lineup
from src.simulation.batch import run_simulations

# Load player data
stats = get_team_batting_stats('TOR', 2025)

# Configure lineup order
lineup = prepare_lineup(stats, order=[0, 3, 1, 5, 2, 4, 6, 7, 8])

# Run simulations
results = run_simulations(lineup, n_iterations=10000)
```

### Lineup Comparison

```python
from src.analysis.comparison import compare_lineups

# Test multiple batting orders
results = compare_lineups(
    players=roster,
    orders=[order1, order2, order3],
    n_simulations=10000
)
```

## Configuration

Edit `config.py` to adjust:
- Number of simulations
- Season length
- Base-running aggressiveness
- ISO thresholds for hit distributions
- Validation parameters

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

### Future Enhancements

- [ ] Upgrade to count-based Bayesian distributions
- [ ] Probabilistic base-running
- [ ] Stolen base modeling
- [ ] Opponent/pitching integration
- [ ] Pitch-level simulation
- [ ] Web interface

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
