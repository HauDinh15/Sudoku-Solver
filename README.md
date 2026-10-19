# 🧩 $N^2 \times N^2$ SAT-Based Sudoku Solver

An $N^2 \times N^2$ generalized Sudoku solver supporting $9 \times 9$, $16 \times 16$, $25 \times 25$, and $36 \times 36$ grids based on reduction to **Boolean Satisfiability (SAT)** solved via the CDCL-based **CaDiCaL** solver.

This repository provides a comprehensive framework to encode *Exactly-One* / *At-Most-One* (AMO) constraints, evaluate spatial complexity (variable and clause counts), and benchmark performance against commercial optimization solvers (**CPLEX CP**, **CPLEX MIP**).

---

## ✨ Key Features

- **Multiple Encoding Schemes:** Supports 5 different At-Most-One (AMO) constraint encodings:
  - `Pairwise` (Base variables only, $O(M^2)$ clauses)
  - `Binary` (Logarithmic encoding)
  - `Commander` (Group-based encoding)
  - `Product` (Grid-based 2D encoding)
  - `Sequential Counter` (Linear clause count $O(M)$)
- **Benchmarking Suite:** Automatically generates experimental datasets (`rq1_encodings.csv` and `rq2_solvers.csv`) for research and academic reporting.

---
