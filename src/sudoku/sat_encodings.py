"""SAT encoding techniques for Sudoku constraints (ALO, AMO, EO).

Supported AMO Encodings:
1. Pairwise: O(m^2) clauses, 0 aux vars.
2. Binary (Bitwise): PySAT EncType.bitwise, O(m log m) clauses, O(log m) aux vars.
3. Commander: Custom implementation, partitioning into groups of size ~3.
4. Product: Custom 2D matrix decomposition (p x q ~ m).
5. Sequential Counter: PySAT EncType.seqcounter, O(m) clauses, O(m) aux vars.
"""

from __future__ import annotations

import math
from typing import Sequence
from pysat.card import CardEnc, EncType

from sudoku.encoding import CNFFormula, VarMap


def encode_alo(lits: Sequence[int], cnf: CNFFormula) -> None:
    """At-Least-One (ALO) constraint: at least one literal must be true."""
    cnf.add_clause(list(lits))


def encode_amo_pairwise(lits: Sequence[int], cnf: CNFFormula) -> None:
    """Manual Pairwise AMO: C(m, 2) binary clauses."""
    m = len(lits)
    for i in range(m):
        for j in range(i + 1, m):
            cnf.add_clause([-lits[i], -lits[j]])


def encode_amo_commander(lits: Sequence[int], cnf: CNFFormula, group_size: int = 3) -> None:
    """Custom Commander AMO Encoding.

    Partitions literals into groups of size `group_size`.
    For each group, introduces a commander variable.
    """
    m = len(lits)
    if m <= 1:
        return
    if m <= group_size:
        encode_amo_pairwise(lits, cnf)
        return

    num_groups = math.ceil(m / group_size)
    groups = [lits[i * group_size : (i + 1) * group_size] for i in range(num_groups)]
    commanders = [cnf.var_map.get_new_var() for _ in range(num_groups)]

    # 1. AMO inside each group
    for g in groups:
        encode_amo_pairwise(g, cnf)

    # 2. AMO among commander variables
    encode_amo_pairwise(commanders, cnf)

    # 3. Commander implications:
    # (a) commander_i -> ALO(group_i)  =>  -commander_i OR x1 OR x2 ...
    # (b) x_j -> commander_i            =>  -x_j OR commander_i
    for g, c_var in zip(groups, commanders):
        cnf.add_clause([-c_var] + list(g))
        for x in g:
            cnf.add_clause([-x, c_var])


def encode_amo_product(lits: Sequence[int], cnf: CNFFormula) -> None:
    """Custom Product AMO Encoding.

    Decomposes m variables into a 2D grid p x q >= m.
    Introduces p row auxiliary vars and q column auxiliary vars.
    """
    m = len(lits)
    if m <= 1:
        return
    if m <= 3:
        encode_amo_pairwise(lits, cnf)
        return

    p = math.ceil(math.sqrt(m))
    q = math.ceil(m / p)

    row_vars = [cnf.var_map.get_new_var() for _ in range(p)]
    col_vars = [cnf.var_map.get_new_var() for _ in range(q)]

    # 1. Linking clauses: x_{i,j} -> row_i and x_{i,j} -> col_j
    for idx, x in enumerate(lits):
        r_idx = idx // q
        c_idx = idx % q
        cnf.add_clause([-x, row_vars[r_idx]])
        cnf.add_clause([-x, col_vars[c_idx]])

    # 2. AMO on row vars and col vars
    encode_amo_pairwise(row_vars, cnf)
    encode_amo_pairwise(col_vars, cnf)


def encode_amo(lits: Sequence[int], cnf: CNFFormula, encoding_type: str = "pairwise") -> None:
    """At-Most-One (AMO) constraint router for the 5 supported encodings."""
    enc_type_str = encoding_type.lower()

    if enc_type_str == "pairwise":
        encode_amo_pairwise(lits, cnf)
    elif enc_type_str in ("binary", "bitwise"):
        # EncType.bitwise is the correct binary encoding in PySAT
        amo_cnf = CardEnc.atmost(
            lits=list(lits),
            bound=1,
            top_id=cnf.var_map.num_vars,
            encoding=EncType.bitwise,
        )
        if amo_cnf.nv > cnf.var_map.num_vars:
            cnf.var_map._next_aux_var = amo_cnf.nv + 1
        cnf.add_clauses(amo_cnf.clauses)
    elif enc_type_str == "commander":
        encode_amo_commander(lits, cnf)
    elif enc_type_str == "product":
        encode_amo_product(lits, cnf)
    elif enc_type_str == "seqcounter":
        amo_cnf = CardEnc.atmost(
            lits=list(lits),
            bound=1,
            top_id=cnf.var_map.num_vars,
            encoding=EncType.seqcounter,
        )
        if amo_cnf.nv > cnf.var_map.num_vars:
            cnf.var_map._next_aux_var = amo_cnf.nv + 1
        cnf.add_clauses(amo_cnf.clauses)
    else:
        raise ValueError(f"Unsupported encoding_type: '{encoding_type}'")


def encode_eo(lits: Sequence[int], cnf: CNFFormula, encoding_type: str = "pairwise") -> None:
    """Exactly-One (EO) constraint: EO(S) = ALO(S) & AMO(S)."""
    encode_alo(lits, cnf)
    encode_amo(lits, cnf, encoding_type=encoding_type)


def build_sudoku_cnf(
    grid: Sequence[Sequence[int]], encoding_type: str = "pairwise"
) -> CNFFormula:
    """Construct full CNF formula for a given N x N Sudoku grid."""
    n = len(grid)
    box = int(n**0.5)

    var_map = VarMap(n)
    cnf = CNFFormula(var_map)

    # 1. Cell constraints
    for r in range(1, n + 1):
        for c in range(1, n + 1):
            lits = [var_map.encode(r, c, v) for v in range(1, n + 1)]
            encode_eo(lits, cnf, encoding_type)

    # 2. Row constraints
    for r in range(1, n + 1):
        for v in range(1, n + 1):
            lits = [var_map.encode(r, c, v) for c in range(1, n + 1)]
            encode_eo(lits, cnf, encoding_type)

    # 3. Column constraints
    for c in range(1, n + 1):
        for v in range(1, n + 1):
            lits = [var_map.encode(r, c, v) for r in range(1, n + 1)]
            encode_eo(lits, cnf, encoding_type)

    # 4. Subgrid / Box constraints
    for br in range(0, n, box):
        for bc in range(0, n, box):
            for v in range(1, n + 1):
                lits = [
                    var_map.encode(r, c, v)
                    for r in range(br + 1, br + box + 1)
                    for c in range(bc + 1, bc + box + 1)
                ]
                encode_eo(lits, cnf, encoding_type)

    # 5. Clue constraints (unit clauses)
    for r_idx in range(n):
        for c_idx in range(n):
            val = grid[r_idx][c_idx]
            if val != 0:
                var_id = var_map.encode(r_idx + 1, c_idx + 1, val)
                cnf.add_clause([var_id])

    return cnf