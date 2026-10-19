"""Constraint-programming Sudoku solver using IBM DOcplex CP Optimizer."""

from __future__ import annotations

import time
from typing import Any, Sequence

from sudoku.validator import is_consistent_puzzle
from sudoku.parser import validate_input

try:
    from docplex.cp.model import CpoModel
    from docplex.cp.modeler import all_diff
    HAS_DOCPLEX = True
except ImportError as exc:
    HAS_DOCPLEX = False
    DOCPLEX_ERROR = exc


def solve_sudoku_cp(
    grid: Sequence[Sequence[int]],
    time_limit: float = 300.0,
) -> tuple[list[list[int]] | None, dict[str, Any]]:
    """Solve Sudoku with DOcplex CP Optimizer."""
    if not HAS_DOCPLEX:
        raise ImportError(f"docplex.cp is unavailable: {DOCPLEX_ERROR}")

    if not validate_input(grid) or not is_consistent_puzzle(grid):
        raise ValueError("Invalid or inconsistent Sudoku grid.")

    size = len(grid)
    box_size = int(size**0.5)

    build_started = time.perf_counter()
    model = CpoModel(name="Sudoku_CP")
    cells = [
        [
            model.integer_var(min=1, max=size, name=f"cell_{row}_{col}")
            for col in range(size)
        ]
        for row in range(size)
    ]

    for row in range(size):
        model.add(all_diff(cells[row]))
        model.add(all_diff([cells[r][row] for r in range(size)]))

    for box_row in range(0, size, box_size):
        for box_col in range(0, size, box_size):
            box_cells = [
                cells[r][c]
                for r in range(box_row, box_row + box_size)
                for c in range(box_col, box_col + box_size)
            ]
            model.add(all_diff(box_cells))

    for row in range(size):
        for col in range(size):
            val = grid[row][col]
            if val:
                model.add(cells[row][col] == val)

    build_time = time.perf_counter() - build_started
    stats: dict[str, Any] = {
        "solver": "CPLEX_CP",
        "num_vars": size * size,
        "num_clauses": size * 3,  # 3 N AllDifferent constraints
        "build_time": build_time,
        "solve_time": 0.0,
        "satisfiable": False,
        "status": "UNKNOWN",
    }

    solve_started = time.perf_counter()
    result = model.solve(TimeLimit=time_limit, trace_log=False)
    solve_time = time.perf_counter() - solve_started
    stats["solve_time"] = solve_time

    if result:
        solve_status = str(result.get_solve_status())
        if result.is_solution():
            stats["satisfiable"] = True
            stats["status"] = "SAT"
            solution = [
                [int(result.get_value(cells[r][c])) for c in range(size)]
                for r in range(size)
            ]
            return solution, stats
        elif "Infeasible" in solve_status:
            stats["status"] = "INFEASIBLE"
        elif "TimeLimit" in solve_status or solve_time >= time_limit:
            stats["status"] = "TIMEOUT"
        else:
            stats["status"] = solve_status
    else:
        stats["status"] = "TIMEOUT" if solve_time >= time_limit else "UNKNOWN"

    return None, stats