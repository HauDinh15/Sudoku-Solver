"""SAT solver interface for Sudoku using PySAT (CaDiCaL)."""

from __future__ import annotations

import time
from typing import Any, Sequence
from pysat.solvers import Solver

from sudoku.sat_encodings import build_sudoku_cnf


def solve_sudoku_sat(
    grid: Sequence[Sequence[int]],
    encoding_type: str = "pairwise",
    solver_name: str = "cadical195",
) -> tuple[list[list[int]] | None, dict[str, Any]]:
    """Solve a Sudoku puzzle using PySAT solver."""
    n = len(grid)

    start_cnf = time.perf_counter()
    cnf = build_sudoku_cnf(grid, encoding_type=encoding_type)
    build_time = time.perf_counter() - start_cnf

    stats: dict[str, Any] = {
        "num_vars": cnf.nv,
        "num_clauses": cnf.nc,
        "build_time": build_time,
        "solve_time": 0.0,
        "satisfiable": False,
        "status": "UNSAT",
        "encoding_type": encoding_type,
        "solver_name": solver_name,
    }

    start_solve = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        is_sat = solver.solve()
        solve_time = time.perf_counter() - start_solve
        stats["solve_time"] = solve_time

        if not is_sat:
            stats["status"] = "UNSAT"
            return None, stats

        model = solver.get_model()
        stats["satisfiable"] = True
        stats["status"] = "SAT"

    solution = [[0] * n for _ in range(n)]
    var_map = cnf.var_map
    true_lits = {lit for lit in model if 0 < lit <= var_map.max_base_var}

    for var_id in true_lits:
        r, c, v = var_map.decode(var_id)
        solution[r - 1][c - 1] = v

    return solution, stats