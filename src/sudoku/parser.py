"""Read and validate Sudoku puzzle input files across 4x4, 9x9, 16x16, and 25x25 sizes."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Sequence


BLANK_SYMBOLS = {".", "-", "0"}


class SudokuParseError(ValueError):
    """Raised when a file cannot be parsed as a Sudoku grid."""


def _parse_row(line: str, line_number: int) -> list[int]:
    """Parse one non-empty row into integer cell values."""
    line = line.strip().strip("|")
    if not line:
        return []

    if re.search(r"[\s,|]", line):
        tokens = [token for token in re.split(r"[\s,|]+", line) if token]
    else:
        # Compact string format (e.g., 530070000 for 9x9)
        tokens = list(line)

    values: list[int] = []
    for token in tokens:
        if token in BLANK_SYMBOLS:
            values.append(0)
        elif token.isdigit():
            values.append(int(token))
        else:
            raise SudokuParseError(
                f"Invalid token {token!r} on line {line_number}. "
                "Use digits or '.', '-', '0' for empty cells."
            )
    return values


def parse_sudoku_text(text: str) -> list[list[int]]:
    """Parse Sudoku puzzle text into a square integer grid."""
    rows: list[list[int]] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if re.fullmatch(r"(?i)(?:size\s*:\s*)?\d+\s*[x×]\s*\d+", line):
            continue
        if re.fullmatch(r"(?i)size\s*:\s*\d+", line):
            continue

        row = _parse_row(line, line_number)
        if row:
            rows.append(row)

    if not rows:
        raise SudokuParseError("No Sudoku rows were found in the input.")

    n = len(rows)
    if any(len(row) != n for row in rows):
        lengths = [len(row) for row in rows]
        raise SudokuParseError(
            f"Sudoku grid must be square: found {n} rows with row lengths {lengths}."
        )

    if int(n**0.5) ** 2 != n:
        raise SudokuParseError(
            f"Grid size must be a perfect square; got {n}x{n}."
        )

    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row, start=1):
            if value < 0 or value > n:
                raise SudokuParseError(
                    f"Value {value} at row {r}, column {c} is outside 0..{n}."
                )

    return rows


def load_sudoku(path: str | Path) -> list[list[int]]:
    """Load a Sudoku puzzle from a text file."""
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SudokuParseError(f"Cannot read file {file_path}: {exc}") from exc

    return parse_sudoku_text(text)


def validate_input(grid: Sequence[Sequence[int]]) -> bool:
    """Return True if grid structure and value domains are valid."""
    if not grid:
        return False

    n = len(grid)
    if int(n**0.5) ** 2 != n:
        return False

    if any(len(row) != n for row in grid):
        return False

    return all(
        isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= n
        for row in grid
        for value in row
    )