"""Experiment RQ2: Compare SAT (CaDiCaL), CPLEX CP, and CPLEX MIP across grid dimensions."""

import sys
from pathlib import Path

# Setup import path from src/
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from sudoku.benchmark import run_benchmark_suite
from sudoku.cp_solver import solve_sudoku_cp
from sudoku.mip_solver import solve_sudoku_cplex_mip
from sudoku.sat_solver import solve_sudoku_sat


def main():
    data_dir = ROOT_DIR / "data"
    results_csv = ROOT_DIR / "results" / "rq2_solvers.csv"

    grid_configs = [
        ("4x4", 60.0),
        ("9x9", 60.0),
        ("16x16", 300.0),
        ("25x25", 300.0),
    ]

    solvers = {
        "SAT_CaDiCaL": (solve_sudoku_sat, {"encoding_type": "pairwise"}),
        "CPLEX_CP": (solve_sudoku_cp, {}),
        "CPLEX_MIP": (solve_sudoku_cplex_mip, {}),
    }

    results_csv.parent.mkdir(parents=True, exist_ok=True)

    print("=== Running Experiment RQ2: Solver Comparison (SAT vs CPLEX CP vs CPLEX MIP) ===")
    for g_size, timeout in grid_configs:
        puzzles = sorted((data_dir / g_size).glob("*.txt"))
        if not puzzles:
            print(f"[WARNING] No files found in data/{g_size}/")
            continue

        print(f"\n---> Running Grid Size {g_size} ({len(puzzles)} instances, Timeout={timeout}s)")
        run_benchmark_suite(puzzles, solvers, results_csv, timeout=timeout)

    print(f"\n[DONE] RQ2 results saved to: {results_csv}\n")


if __name__ == "__main__":
    main()