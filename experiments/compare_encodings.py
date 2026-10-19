"""Experiment RQ1: Evaluate 5 At-Most-One (AMO) SAT encodings on 9x9 and 16x16 Sudoku grids."""

import sys
from pathlib import Path

# Setup import path from src/
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from sudoku.benchmark import run_benchmark_suite
from sudoku.sat_solver import solve_sudoku_sat


def main():
    data_dir = ROOT_DIR / "data"
    results_csv = ROOT_DIR / "results" / "rq1_encodings.csv"

    # Collect puzzle instances from both 9x9 and 16x16 datasets
    puzzle_paths = []
    puzzle_paths.extend(sorted((data_dir / "9x9").glob("*.txt")))
    puzzle_paths.extend(sorted((data_dir / "16x16").glob("*.txt")))

    if not puzzle_paths:
        print("ERROR: Dataset missing! Please run 'python data/generate_datasets.py' first.")
        return

    encodings = ["pairwise", "binary", "commander", "product", "seqcounter"]
    solvers = {
        enc: (solve_sudoku_sat, {"encoding_type": enc, "solver_name": "cadical195"})
        for enc in encodings
    }

    print(f"=== Running Experiment RQ1: Comparing 5 AMO Encodings ({len(puzzle_paths)} instances) ===")
    run_benchmark_suite(puzzle_paths, solvers, results_csv, timeout=60.0)
    print(f"\n[DONE] RQ1 results saved to: {results_csv}\n")


if __name__ == "__main__":
    main()