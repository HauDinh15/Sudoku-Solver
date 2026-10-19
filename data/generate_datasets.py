"""Script to automatically generate Sudoku benchmark datasets according to paper specifications."""

from pathlib import Path
import random


def generate_valid_board(n: int) -> list[list[int]]:
    """Generate a complete valid N x N Sudoku grid."""
    box = int(n**0.5)
    board = [[0] * n for _ in range(n)]

    def pattern(r, c):
        return (box * (r % box) + r // box + c) % n

    def shuffle(s):
        return random.sample(s, len(s))

    r_base = range(box)
    rows = [g * box + r for g in shuffle(r_base) for r in shuffle(r_base)]
    cols = [g * box + c for g in shuffle(r_base) for c in shuffle(r_base)]
    nums = shuffle(range(1, n + 1))

    board = [[nums[pattern(r, c)] for c in cols] for r in rows]
    return board


def create_puzzle(board: list[list[int]], num_clues: int) -> list[list[int]]:
    """Hide cell values to match the target clue count."""
    n = len(board)
    total_cells = n * n
    num_to_remove = total_cells - num_clues

    puzzle = [row[:] for row in board]
    indices = [(r, c) for r in range(n) for c in range(n)]
    remove_indices = random.sample(indices, num_to_remove)

    for r, c in remove_indices:
        puzzle[r][c] = 0

    return puzzle


def save_puzzle_to_file(puzzle: list[list[int]], filepath: Path):
    """Save grid in standard space-separated format."""
    lines = []
    for row in puzzle:
        lines.append(" ".join(f"{val:2d}" for val in row))
    filepath.write_text("\n".join(lines), encoding="utf-8")


def main():
    # Fix random seed for reproducibility
    random.seed(42)
    base_dir = Path(__file__).resolve().parent

    configs = [
        ("4x4", 4, 20, (4, 8)),
        ("9x9", 9, 20, (17, 35)),
        ("16x16", 16, 20, (60, 120)),
        ("25x25", 25, 10, (150, 300)),
    ]

    print("=== Initializing Benchmark Datasets ===")
    for folder_name, n, count, (min_clues, max_clues) in configs:
        target_dir = base_dir / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        for i in range(1, count + 1):
            board = generate_valid_board(n)
            num_clues = random.randint(min_clues, max_clues)
            puzzle = create_puzzle(board, num_clues)

            filename = f"puzzle_{folder_name}_{i:02d}.txt"
            filepath = target_dir / filename
            save_puzzle_to_file(puzzle, filepath)

        print(
            f"  [OK] Generated {count:2d} files in data/{folder_name}/ (Clues: {min_clues}-{max_clues})"
        )

    print("Benchmark dataset generation completed!\n")


if __name__ == "__main__":
    main()