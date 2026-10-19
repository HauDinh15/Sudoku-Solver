"""Sudoku Solver Package using SAT, CP, and MIP optimization techniques."""

from sudoku.parser import load_sudoku, parse_sudoku_text
from sudoku.validator import validate_solution, is_consistent_puzzle

__version__ = "1.0.0"
__all__ = ["load_sudoku", "parse_sudoku_text", "validate_solution", "is_consistent_puzzle"]