"""Manager for storing and retrieving simulation results."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional


class ResultsManager:
    """Manages storage and retrieval of simulation results in memory."""

    def __init__(self, max_results: int = 10):
        """
        Initialize results manager.

        Args:
            max_results: Maximum number of results to store (oldest removed when exceeded)
        """
        self.max_results = max_results
        self._results: List[Dict] = []  # List of result dictionaries

    def store_result(self, lineup_name: str, results_dict: Dict) -> str:
        """
        Store a simulation result.

        Args:
            lineup_name: User-provided name for the lineup
            results_dict: Complete results dictionary from run_simulations()

        Returns:
            Unique ID for the stored result
        """
        # Generate unique ID
        result_id = str(uuid.uuid4())[:8]

        # Create result entry with metadata
        result_entry = {
            'id': result_id,
            'lineup_name': lineup_name,
            'timestamp': datetime.now(),
            'results': results_dict
        }

        # Add to storage
        self._results.append(result_entry)

        # Remove oldest if exceeded max
        if len(self._results) > self.max_results:
            self._results.pop(0)

        return result_id

    def get_result(self, result_id: str) -> Optional[Dict]:
        """
        Retrieve a stored result by ID.

        Args:
            result_id: ID of the result to retrieve

        Returns:
            Complete result dictionary, or None if not found
        """
        for entry in self._results:
            if entry['id'] == result_id:
                return entry['results']
        return None

    def get_result_entry(self, result_id: str) -> Optional[Dict]:
        """
        Retrieve a complete result entry (including metadata) by ID.

        Args:
            result_id: ID of the result to retrieve

        Returns:
            Complete result entry with metadata, or None if not found
        """
        for entry in self._results:
            if entry['id'] == result_id:
                return entry
        return None

    def list_results(self) -> List[Dict]:
        """
        List all stored results with summary information.

        Returns:
            List of dictionaries with keys:
                - id: Result ID
                - lineup_name: User-provided name
                - timestamp: When result was stored
                - summary: Summary statistics (mean runs, etc.)
        """
        result_list = []

        for entry in self._results:
            # Extract summary info
            results = entry['results']
            summary = results.get('summary', {})
            runs = summary.get('runs', {})

            result_list.append({
                'id': entry['id'],
                'lineup_name': entry['lineup_name'],
                'timestamp': entry['timestamp'],
                'mean_runs': runs.get('mean', 0),
                'n_simulations': summary.get('n_simulations', 0),
                'n_games': summary.get('n_games_per_season', 0)
            })

        return result_list

    def delete_result(self, result_id: str) -> bool:
        """
        Delete a stored result by ID.

        Args:
            result_id: ID of the result to delete

        Returns:
            True if deleted, False if not found
        """
        for i, entry in enumerate(self._results):
            if entry['id'] == result_id:
                self._results.pop(i)
                return True
        return False

    def clear_all(self):
        """Clear all stored results."""
        self._results.clear()

    def get_count(self) -> int:
        """
        Get the number of stored results.

        Returns:
            Number of results currently stored
        """
        return len(self._results)

    def get_results_by_ids(self, result_ids: List[str]) -> List[Dict]:
        """
        Retrieve multiple results by their IDs.

        Args:
            result_ids: List of result IDs to retrieve

        Returns:
            List of result dictionaries (includes metadata)
        """
        results = []
        for result_id in result_ids:
            entry = self.get_result_entry(result_id)
            if entry:
                results.append(entry)
        return results

    def compare_results(self, result_ids: List[str]) -> Dict:
        """
        Create a comparison dictionary for multiple results.

        Args:
            result_ids: List of 2-4 result IDs to compare

        Returns:
            Dictionary containing comparison data for all requested results
        """
        if len(result_ids) < 2:
            raise ValueError("Need at least 2 results to compare")
        if len(result_ids) > 4:
            raise ValueError("Can only compare up to 4 results at once")

        # Get all result entries
        entries = self.get_results_by_ids(result_ids)

        if len(entries) != len(result_ids):
            raise ValueError("One or more result IDs not found")

        # Build comparison dictionary
        comparison = {
            'result_ids': result_ids,
            'lineup_names': [e['lineup_name'] for e in entries],
            'timestamps': [e['timestamp'] for e in entries],
            'results': [e['results'] for e in entries]
        }

        return comparison


if __name__ == "__main__":
    # Test the ResultsManager
    print("=== Testing ResultsManager ===\n")

    # Create manager
    manager = ResultsManager(max_results=3)

    # Create dummy results
    dummy_result_1 = {
        'summary': {
            'n_simulations': 1000,
            'n_games_per_season': 162,
            'runs': {
                'mean': 750.5,
                'median': 748.0,
                'std': 25.3
            }
        },
        'raw_data': {
            'season_runs': [750, 748, 752, 755]
        }
    }

    dummy_result_2 = {
        'summary': {
            'n_simulations': 1000,
            'n_games_per_season': 162,
            'runs': {
                'mean': 820.2,
                'median': 819.0,
                'std': 27.1
            }
        },
        'raw_data': {
            'season_runs': [820, 819, 821, 818]
        }
    }

    dummy_result_3 = {
        'summary': {
            'n_simulations': 1000,
            'n_games_per_season': 162,
            'runs': {
                'mean': 680.8,
                'median': 682.0,
                'std': 23.5
            }
        },
        'raw_data': {
            'season_runs': [680, 682, 679, 681]
        }
    }

    # Store results
    id1 = manager.store_result("Lineup A", dummy_result_1)
    print(f"Stored result 1 with ID: {id1}")

    id2 = manager.store_result("Lineup B", dummy_result_2)
    print(f"Stored result 2 with ID: {id2}")

    id3 = manager.store_result("Lineup C", dummy_result_3)
    print(f"Stored result 3 with ID: {id3}\n")

    # List results
    print("=== Stored Results ===")
    for result_info in manager.list_results():
        print(f"  {result_info['id']}: {result_info['lineup_name']} - "
              f"{result_info['mean_runs']:.1f} runs (n={result_info['n_simulations']})")
    print()

    # Retrieve a result
    print(f"=== Retrieving result {id2} ===")
    retrieved = manager.get_result(id2)
    if retrieved:
        print(f"  Mean runs: {retrieved['summary']['runs']['mean']}")
    print()

    # Compare results
    print(f"=== Comparing results {id1} and {id2} ===")
    comparison = manager.compare_results([id1, id2])
    print(f"  Lineups: {comparison['lineup_names']}")
    print(f"  Mean runs: {[r['summary']['runs']['mean'] for r in comparison['results']]}")
    print()

    # Test max limit (add 4th result, should remove 1st)
    id4 = manager.store_result("Lineup D", dummy_result_1)
    print(f"=== Added 4th result (max=3), should remove oldest ===")
    print(f"  Count: {manager.get_count()}")
    print(f"  Results: {[r['lineup_name'] for r in manager.list_results()]}")
    print()

    # Delete a result
    deleted = manager.delete_result(id2)
    print(f"=== Deleted result {id2}: {deleted} ===")
    print(f"  Remaining: {[r['lineup_name'] for r in manager.list_results()]}")
    print()

    # Clear all
    manager.clear_all()
    print(f"=== Cleared all results ===")
    print(f"  Count: {manager.get_count()}")

    print("\n✓ ResultsManager tests complete")
