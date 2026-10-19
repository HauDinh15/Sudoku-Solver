"""Single CLI entry point for the Sudoku Solver framework."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from sudoku.parser import load_sudoku
from sudoku.sat_solver import solve_sudoku_sat
from sudoku.cp_solver import solve_sudoku_cp
from sudoku.mip_solver import solve_sudoku_cplex_mip
from sudoku.validator import validate_solution


def main():
    parser = argparse.ArgumentParser(description="Sudoku Solver Benchmark CLI")
    parser.add_argument("--input", type=str, required=True, help="Path to input Sudoku puzzle file")
    parser.add_argument("--solver", type=str, choices=["sat", "cp", "mip"], default="sat", help="Solver framework")
    parser.add_argument("--encoding", type=str, choices=["pairwise", "binary", "commander", "product", "seqcounter"], default="pairwise", help="AMO encoding technique for SAT")
    parser.add_argument("--timeout", type=float, default=60.0, help="Time limit in seconds")

    args = parser.parse_args()
    input_path = Path(args.input)

    grid = load_sudoku(input_path)
    n = len(grid)
    print(f"Loaded {n}x{n} Sudoku grid from {input_path.name}")

    if args.solver == "sat":
        solution, stats = solve_sudoku_sat(grid, encoding_type=args.encoding)
    elif args.solver == "cp":
        solution, stats = solve_sudoku_cp(grid, time_limit=args.timeout)
    elif args.solver == "mip":
        solution, stats = solve_sudoku_cplex_mip(grid, time_limit=args.timeout)

    print(f"Solver Status: {stats.get('status')}")
    print(f"Build Time: {stats.get('build_time', 0.0):.5f} s")
    print(f"Solve Time: {stats.get('solve_time', 0.0):.5f} s")
    print(f"Variables: {stats.get('num_vars')}, Clauses/Constraints: {stats.get('num_clauses')}")

    if solution:
        is_valid = validate_solution(grid, solution)
        print(f"Solution Validation: {'PASSED' if is_valid else 'FAILED'}")
        if is_valid:
            print("\nSolved Grid:")
            for row in solution:
                print(" ".join(f"{val:2d}" for val in row))
    else:
        print("No valid solution found.")


if __name__ == "__main__":
    main()