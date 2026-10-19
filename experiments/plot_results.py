"""Generate publication-quality plots from benchmark CSV results."""

import sys
from pathlib import Path

# Setup import path from src/
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

import csv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_rq1(rq1_csv: Path, output_dir: Path):
    if not rq1_csv.exists():
        print(f"Skipping RQ1 plot: {rq1_csv} not found.")
        return

    df = pd.read_csv(rq1_csv)
    df = df[df["status"] == "SAT"]

    sns.set_theme(style="whitegrid", font_scale=1.1)

    # Plot 1: CNF Clause Counts across Encodings
    plt.figure(figsize=(8, 4.5))
    ax = sns.barplot(
        data=df,
        x="solver_name",
        y="num_clauses",
        hue="grid_size",
        palette="muted",
        errorbar=None,
    )
    plt.yscale("log")
    plt.xlabel("AMO Encoding Technique", fontweight="bold")
    plt.ylabel("Number of CNF Clauses (Log Scale)", fontweight="bold")
    plt.title("RQ1: CNF Clause Count Across AMO Encodings", fontweight="bold")
    plt.legend(title="Grid Size")
    plt.tight_layout()

    out_file1 = output_dir / "rq1_cnf_clauses.pdf"
    plt.savefig(out_file1, dpi=300)
    plt.close()
    print(f"[OK] RQ1 Clause Plot saved: {out_file1}")


def plot_rq2(rq2_csv: Path, output_dir: Path):
    if not rq2_csv.exists():
        print(f"Skipping RQ2 plot: {rq2_csv} not found.")
        return

    df = pd.read_csv(rq2_csv)
    df["solve_time_clean"] = df["solve_time"].apply(lambda x: max(float(x), 0.0001))

    sns.set_theme(style="whitegrid", font_scale=1.1)

    # Plot 1: Solve Time Comparison (Log Scale)
    plt.figure(figsize=(8.5, 5))
    ax = sns.barplot(
        data=df,
        x="grid_size",
        y="solve_time_clean",
        hue="solver_name",
        palette="Set2",
        errorbar=None,
    )
    plt.yscale("log")
    plt.xlabel("Sudoku Grid Dimension", fontweight="bold")
    plt.ylabel("Solve Time in Seconds (Log Scale)", fontweight="bold")
    plt.title("RQ2: Scalability & Solve Time Across Solvers", fontweight="bold")
    plt.legend(title="Solver Engine")
    plt.tight_layout()

    out_file1 = output_dir / "rq2_solver_runtimes.pdf"
    plt.savefig(out_file1, dpi=300)
    plt.close()
    print(f"[OK] RQ2 Runtime Plot saved: {out_file1}")

    # Plot 2: Peak Memory Consumption (RSS)
    plt.figure(figsize=(8.5, 5))
    ax = sns.barplot(
        data=df,
        x="grid_size",
        y="peak_memory_mb",
        hue="solver_name",
        palette="Reds_d",
        errorbar=None,
    )
    plt.xlabel("Sudoku Grid Dimension", fontweight="bold")
    plt.ylabel("Peak RSS Memory (MB)", fontweight="bold")
    plt.title("RQ2: Peak Memory Consumption Comparison", fontweight="bold")
    plt.legend(title="Solver Engine")
    plt.tight_layout()

    out_file2 = output_dir / "rq2_memory_rss.pdf"
    plt.savefig(out_file2, dpi=300)
    plt.close()
    print(f"[OK] RQ2 Memory Plot saved: {out_file2}")


def main():
    fig_dir = ROOT_DIR / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    plot_rq1(ROOT_DIR / "results" / "rq1_encodings.csv", fig_dir)
    plot_rq2(ROOT_DIR / "results" / "rq2_solvers.csv", fig_dir)


if __name__ == "__main__":
    main()