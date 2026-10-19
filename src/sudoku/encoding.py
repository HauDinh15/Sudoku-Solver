"""Variable mapping and CNF formula management for Sudoku SAT formulations."""

from __future__ import annotations


class VarMap:
    """Bi-directional mapping between (row, col, val) and CNF variable IDs (1-indexed)."""

    def __init__(self, n: int) -> None:
        self.n = n
        self.max_base_var = n * n * n
        self._next_aux_var = self.max_base_var + 1

    def encode(self, r: int, c: int, v: int) -> int:
        """Map 1-indexed (r, c, v) to a unique integer ID in 1..N^3."""
        return (r - 1) * self.n * self.n + (c - 1) * self.n + v

    def decode(self, var_id: int) -> tuple[int, int, int]:
        """Decode base variable ID back into 1-indexed (r, c, v)."""
        if not (1 <= var_id <= self.max_base_var):
            raise ValueError(f"Var ID {var_id} is outside base range 1..{self.max_base_var}")
        val = (var_id - 1) % self.n + 1
        rem = (var_id - 1) // self.n
        col = rem % self.n + 1
        row = rem // self.n + 1
        return row, col, val

    def get_new_var(self) -> int:
        """Allocate and return a fresh auxiliary variable ID."""
        var = self._next_aux_var
        self._next_aux_var += 1
        return var

    @property
    def num_vars(self) -> int:
        """Total number of variables allocated so far."""
        return self._next_aux_var - 1


class CNFFormula:
    """Container for CNF clauses and variable management."""

    def __init__(self, var_map: VarMap) -> None:
        self.var_map = var_map
        self.clauses: list[list[int]] = []

    def add_clause(self, clause: list[int]) -> None:
        self.clauses.append(clause)

    def add_clauses(self, clauses: list[list[int]]) -> None:
        self.clauses.extend(clauses)

    @property
    def nv(self) -> int:
        return self.var_map.num_vars

    @property
    def nc(self) -> int:
        return len(self.clauses)