"""
benchmark.py - Đo đạc hiệu năng và so sánh Heuristic v1 vs Heuristic v2 (Corner PDB).
"""

import os
import sys
import io

# Tự động thêm thư mục gốc dự án vào PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đảm bảo stdout in UTF-8 không bị lỗi trên Windows console
if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
from typing import List, Tuple, Optional
from src.rubik_state import State, GOAL_STATE, MOVES, apply_move
from src.scramble import scramble
from src.solver import is_redundant
import src.heuristic as heuristic_module


def solve_with_heuristic(scrambled_state: State, heuristic_func, max_moves: int = 25) -> Tuple[Optional[List[str]], int, float]:
    """Giải Rubik bằng IDA* sử dụng hàm heuristic truyền vào."""
    start_time = time.perf_counter()
    nodes_visited = [0]
    path: List[str] = []
    threshold = heuristic_func(scrambled_state)

    def dfs(state: State, g: int, curr_threshold: int, last_move: Optional[str]):
        nodes_visited[0] += 1
        
        if nodes_visited[0] > 300_000:
            return "TIMEOUT"
            
        f = g + heuristic_func(state)

        if f > curr_threshold:
            return f

        if state == GOAL_STATE:
            return "FOUND"

        min_exceed = float("inf")
        for move in MOVES:
            if is_redundant(move, last_move):
                continue

            new_state = apply_move(state, move)
            path.append(move)
            result = dfs(new_state, g + 1, curr_threshold, move)
            if result == "FOUND" or result == "TIMEOUT":
                return result
            if isinstance(result, (int, float)):
                min_exceed = min(min_exceed, result)
            path.pop()

        return min_exceed

    while threshold <= max_moves:
        result = dfs(scrambled_state, 0, threshold, None)
        if result == "FOUND":
            elapsed = time.perf_counter() - start_time
            return path, nodes_visited[0], elapsed
        if result == "TIMEOUT":
            elapsed = time.perf_counter() - start_time
            return None, nodes_visited[0], elapsed
        if result == float("inf"):
            break
        threshold = int(result)

    elapsed = time.perf_counter() - start_time
    return None, nodes_visited[0], elapsed


def run_benchmark():
    print("=" * 85)
    print("      BÁO CÁO BENCHMARK SO SÁNH HEURISTIC V1 (THÔ) VS HEURISTIC V2 (CORNER PDB)")
    print("=" * 85)

    # Nạp trước PDB vào bộ nhớ
    heuristic_module.get_heuristic_v2(GOAL_STATE)

    scramble_depths = [5, 8, 10]
    num_samples = 2

    print(f"\n{'Độ sâu':<8} | {'Seed':<6} | {'Phiên bản':<16} | {'Lời giải':<12} | {'Node đã mở':<16} | {'Thời gian (s)':<12}")
    print("-" * 85)

    for depth in scramble_depths:
        for sample_idx in range(num_samples):
            seed = depth * 100 + sample_idx
            state, moves = scramble(depth, seed=seed)

            # 1. Chạy với Heuristic v1 (Thô)
            sol_v1, nodes_v1, time_v1 = solve_with_heuristic(state, heuristic_module.get_heuristic_v1)
            len_v1 = f"{len(sol_v1)} bước" if sol_v1 else ("TIMEOUT" if nodes_v1 >= 300_000 else "N/A")

            # 2. Chạy với Heuristic v2 (Corner PDB)
            sol_v2, nodes_v2, time_v2 = solve_with_heuristic(state, heuristic_module.get_heuristic_v2)
            len_v2 = f"{len(sol_v2)} bước" if sol_v2 else ("TIMEOUT" if nodes_v2 >= 300_000 else "N/A")

            print(f"{depth:<8} | {seed:<6} | {'v1 (Thô)':<16} | {len_v1:<12} | {nodes_v1:<16,} | {time_v1:<12.4f}")
            print(f"{'':<8} | {'':<6} | {'v2 (Corner PDB)':<16} | {len_v2:<12} | {nodes_v2:<16,} | {time_v2:<12.4f}")
            print("-" * 85)

    print("\n" + "=" * 85)
    print("HOÀN TẤT BENCHMARK!")
    print("=" * 85)


if __name__ == "__main__":
    run_benchmark()
