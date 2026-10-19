"""Validation utilities for Sudoku puzzles and candidate solutions."""

from __future__ import annotations

from typing import Sequence

Grid = Sequence[Sequence[int]]


def _valid_grid_shape(grid: Grid) -> bool:
    if not grid:
        return False
    n = len(grid)
    if int(n**0.5) ** 2 != n:
        return False
    return all(len(row) == n for row in grid)


def _valid_values(grid: Grid) -> bool:
    n = len(grid)
    return all(
        isinstance(value, int)
        and not isinstance(value, bool)
        and 0 <= value <= n
        for row in grid
        for value in row
    )


def is_consistent_puzzle(puzzle: Grid) -> bool:
    """Return True if given clues do not conflict with Sudoku rules."""
    if not _valid_grid_shape(puzzle) or not _valid_values(puzzle):
        return False

    n = len(puzzle)
    box = int(n**0.5)

    for i in range(n):
        row_vals = [v for v in puzzle[i] if v != 0]
        col_vals = [puzzle[r][i] for r in range(n) if puzzle[r][i] != 0]
        if len(row_vals) != len(set(row_vals)) or len(col_vals) != len(set(col_vals)):
            return False

    for box_r in range(0, n, box):
        for box_c in range(0, n, box):
            vals = [
                puzzle[r][c]
                for r in range(box_r, box_r + box)
                for c in range(box_c, box_c + box)
                if puzzle[r][c] != 0
            ]
            if len(vals) != len(set(vals)):
                return False

    return True


def validate_solution(puzzle: Grid, solution: Grid) -> bool:
    """Return True if solution is a complete, correct solution for puzzle."""
    if not _valid_grid_shape(puzzle) or not _valid_grid_shape(solution):
        return False

    n = len(puzzle)
    if len(solution) != n or not _valid_values(puzzle) or not _valid_values(solution):
        return False

    if not is_consistent_puzzle(puzzle):
        return False

    if any(val == 0 for row in solution for val in row):
        return False

    expected = set(range(1, n + 1))

    for i in range(n):
        if set(solution[i]) != expected:
            return False
        if {solution[r][i] for r in range(n)} != expected:
            return False

    box = int(n**0.5)
    for box_r in range(0, n, box):
        for box_c in range(0, n, box):
            vals = {
                solution[r][c]
                for r in range(box_r, box_r + box)
                for c in range(box_c, box_c + box)
            }
            if vals != expected:
                return False

    for r in range(n):
        for c in range(n):
            if puzzle[r][c] != 0 and solution[r][c] != puzzle[r][c]:
                return False

    return True