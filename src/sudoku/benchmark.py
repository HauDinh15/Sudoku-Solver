"""Benchmarking module with Multiprocessing Subprocess Runner, Timeouts, and Peak RSS memory tracking."""

from __future__ import annotations

import csv
import multiprocessing as mp
import os
import time
from pathlib import Path
from typing import Any, Callable

import psutil

from sudoku.parser import load_sudoku, validate_input
from sudoku.validator import is_consistent_puzzle, validate_solution

SolverFunc = Callable[..., tuple[list[list[int]] | None, dict[str, Any]]]


def _worker_process(
    solver_func: SolverFunc,
    grid: list[list[int]],
    kwargs: dict[str, Any],
    queue: mp.Queue,
) -> None:
    """Worker process function executed in an isolated process."""
    try:
        proc = psutil.Process(os.getpid())
        start_time = time.perf_counter()

        solution, stats = solver_func(grid, **kwargs)

        exec_time = time.perf_counter() - start_time
        peak_rss_mb = proc.memory_info().rss / (1024 * 1024)

        queue.put({
            "solution": solution,
            "stats": stats,
            "exec_time": exec_time,
            "peak_rss_mb": peak_rss_mb,
            "error": None,
        })
    except Exception as exc:
        queue.put({
            "solution": None,
            "stats": {},
            "exec_time": 0.0,
            "peak_rss_mb": 0.0,
            "error": f"{type(exc).__name__}: {str(exc)}",
        })


def run_solver_with_timeout(
    solver_func: SolverFunc,
    grid: list[list[int]],
    kwargs: dict[str, Any] | None = None,
    timeout: float = 60.0,
) -> tuple[list[list[int]] | None, dict[str, Any], float, float]:
    """Execute solver function in a subprocess with strict timeout and RSS memory tracking.

    Returns:
        (solution, stats, total_time, peak_rss_mb)
    """
    if kwargs is None:
        kwargs = {}

    ctx = mp.get_context("spawn")
    queue = ctx.Queue()

    process = ctx.Process(
        target=_worker_process,
        args=(solver_func, grid, kwargs, queue),
    )

    start_total = time.perf_counter()
    process.start()
    process.join(timeout=timeout)

    total_time = time.perf_counter() - start_total

    if process.is_alive():
        process.terminate()
        process.join()
        stats = {
            "status": "TIMEOUT",
            "satisfiable": False,
            "build_time": 0.0,
            "solve_time": round(timeout, 2),
            "num_vars": 0,
            "num_clauses": 0,
        }
        return None, stats, round(total_time, 4), 0.0

    if not queue.empty():
        res = queue.get()
        if res["error"]:
            stats = {
                "status": f"ERROR ({res['error']})",
                "satisfiable": False,
                "build_time": 0.0,
                "solve_time": 0.0,
                "num_vars": 0,
                "num_clauses": 0,
            }
            return None, stats, round(total_time, 4), 0.0

        return res["solution"], res["stats"], round(res["exec_time"], 4), round(res["peak_rss_mb"], 2)

    stats = {
        "status": "ERROR (No result)",
        "satisfiable": False,
        "build_time": 0.0,
        "solve_time": 0.0,
    }
    return None, stats, round(total_time, 4), 0.0


def run_benchmark_suite(
    puzzle_paths: list[Path],
    solvers: dict[str, tuple[SolverFunc, dict[str, Any]]],
    output_csv: Path,
    timeout: float = 60.0,
) -> list[dict[str, Any]]:
    """Run benchmark suite across puzzles and solvers, saving output to CSV."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "instance_name",
        "grid_size",
        "solver_name",
        "satisfiable",
        "status",
        "num_vars",
        "num_clauses",
        "build_time",
        "solve_time",
        "total_time",
        "peak_memory_mb",
        "validation",
    ]

    results: list[dict[str, Any]] = []

    with output_csv.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for path in puzzle_paths:
            instance_name = path.name
            try:
                grid = load_sudoku(path)
            except Exception as exc:
                print(f"[SKIP] Failed to load {instance_name}: {exc}")
                continue

            if not validate_input(grid) or not is_consistent_puzzle(grid):
                print(f"[SKIP] Invalid/inconsistent puzzle: {instance_name}")
                continue

            grid_size = len(grid)

            for solver_label, (solver_func, kwargs) in solvers.items():
                solution, stats, total_time, peak_mb = run_solver_with_timeout(
                    solver_func, grid, kwargs, timeout=timeout
                )

                satisfiable = bool(stats.get("satisfiable", False))
                status = stats.get("status", "SAT" if satisfiable else "UNSAT")

                is_valid = False
                if solution is not None:
                    is_valid = validate_solution(grid, solution)

                row = {
                    "instance_name": instance_name,
                    "grid_size": f"{grid_size}x{grid_size}",
                    "solver_name": solver_label,
                    "satisfiable": satisfiable,
                    "status": status,
                    "num_vars": stats.get("num_vars", 0),
                    "num_clauses": stats.get("num_clauses", 0),
                    "build_time": round(stats.get("build_time", 0.0), 5),
                    "solve_time": round(stats.get("solve_time", 0.0), 5),
                    "total_time": round(total_time, 5),
                    "peak_memory_mb": round(peak_mb, 2),
                    "validation": "PASSED" if is_valid else ("FAILED" if solution else "N/A"),
                }

                writer.writerow(row)
                csv_file.flush()
                results.append(row)
                print(
                    f"[{grid_size}x{grid_size}] {instance_name:<15} | {solver_label:<15} -> "
                    f"Status: {row['status']:<8} | SolveTime: {row['solve_time']}s | Memory: {row['peak_memory_mb']}MB"
                )

    return results