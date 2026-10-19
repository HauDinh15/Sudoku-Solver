"""MIP Solver for Sudoku using IBM ILOG CPLEX MIP (docplex.mp)."""

from __future__ import annotations

import time
from typing import Any, Sequence

try:
    from docplex.mp.model import Model as CplexMPModel
    HAS_CPLEX_MP = True
except ImportError:
    HAS_CPLEX_MP = False


def solve_sudoku_cplex_mip(
    grid: Sequence[Sequence[int]],
    time_limit: float = 300.0,
) -> tuple[list[list[int]] | None, dict[str, Any]]:
    """Solve Sudoku using CPLEX MIP Engine with exact status reporting."""
    if not HAS_CPLEX_MP:
        raise ImportError("docplex.mp is not installed or accessible.")

    n = len(grid)
    box = int(n**0.5)

    start_build = time.perf_counter()
    mdl = CplexMPModel(name="Sudoku_CPLEX_MIP")
    mdl.context.solver.trace = 0
    mdl.time_limit = time_limit

    x = {
        (r, c, v): mdl.binary_var(name=f"x_{r}_{c}_{v}")
        for r in range(n)
        for c in range(n)
        for v in range(n)
    }

    # 1. Cell constraint
    for r in range(n):
        for c in range(n):
            mdl.add_constraint(mdl.sum(x[r, c, v] for v in range(n)) == 1)

    # 2. Row constraint
    for r in range(n):
        for v in range(n):
            mdl.add_constraint(mdl.sum(x[r, c, v] for c in range(n)) == 1)

    # 3. Column constraint
    for c in range(n):
        for v in range(n):
            mdl.add_constraint(mdl.sum(x[r, c, v] for r in range(n)) == 1)

    # 4. Box constraint
    for br in range(0, n, box):
        for bc in range(0, n, box):
            for v in range(n):
                mdl.add_constraint(
                    mdl.sum(
                        x[r, c, v]
                        for r in range(br, br + box)
                        for c in range(bc, bc + box)
                    )
                    == 1
                )

    # 5. Fix given clues
    clue_count = 0
    for r in range(n):
        for c in range(n):
            val = grid[r][c]
            if val != 0:
                mdl.add_constraint(x[r, c, val - 1] == 1)
                clue_count += 1

    build_time = time.perf_counter() - start_build
    num_constraints = 4 * n * n + clue_count

    stats: dict[str, Any] = {
        "solver": "CPLEX_MIP",
        "num_vars": n * n * n,
        "num_clauses": num_constraints,
        "build_time": build_time,
        "solve_time": 0.0,
        "satisfiable": False,
        "status": "UNKNOWN",
    }

    start_solve = time.perf_counter()
    try:
        sol = mdl.solve()
    except Exception as exc:
        stats["status"] = f"ERROR ({type(exc).__name__})"
        return None, stats

    solve_time = time.perf_counter() - start_solve
    stats["solve_time"] = solve_time

    status_str = str(mdl.solve_details.status).upper() if mdl.solve_details else ""

    if sol:
        stats["satisfiable"] = True
        stats["status"] = "SAT"
        solution = [[0] * n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                for v in range(n):
                    if sol.get_value(x[r, c, v]) > 0.5:
                        solution[r][c] = v + 1
        return solution, stats

    if "TIME_LIMIT" in status_str or "TIMEOUT" in status_str or solve_time >= time_limit:
        stats["status"] = "TIMEOUT"
    elif "INFEASIBLE" in status_str:
        stats["status"] = "INFEASIBLE"
    else:
        stats["status"] = "UNSAT"

    return None, stats