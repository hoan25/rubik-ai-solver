"""
solver.py - Thuật toán IDA* Search giải Rubik 3x3.
"""

import time
from typing import List, Tuple, Optional
from src.rubik_state import State, GOAL_STATE, MOVES, apply_move
from src.heuristic import get_heuristic

# Quy ước mặt đối diện song song để ép thứ tự cố định (tránh trạng thái trùng lặp do giao hoán)
# U (0) - D (1), R (2) - L (3), F (4) - B (5)
_OPPOSITE_FIXED_ORDER = {
    "D": "U",  # Nếu last_move là D, không cho phép U
    "L": "R",  # Nếu last_move là L, không cho phép R
    "B": "F",  # Nếu last_move là B, không cho phép F
}

def is_redundant(move: str, last_move: Optional[str]) -> bool:
    """
    Cắt tỉa (Pruning) các nhánh di chuyển thừa:
    1. Không xoay cùng một mặt liên tiếp (chặn U sau U/U'/U2).
    2. Với hai mặt đối diện song song (giao hoán được như U và D): ép thứ tự cố định
       để tránh sinh 2 chuỗi trùng nhau (VD: [U, D] và [D, U]).
    """
    if last_move is None:
        return False

    move_face = move[0]
    last_face = last_move[0]

    # 1. Chặn xoay cùng 1 mặt liên tiếp
    if move_face == last_face:
        return True

    # 2. Với các cặp mặt đối diện, ép thứ tự ưu tiên cố định
    if move_face in _OPPOSITE_FIXED_ORDER and last_face == _OPPOSITE_FIXED_ORDER[move_face]:
        return True

    return False

def solve(scrambled_state: State, max_moves: int = 25) -> Tuple[Optional[List[str]], int, float]:
    """
    Giải Rubik từ trạng thái scrambled_state bằng thuật toán IDA*.
    Trả về: (solution_path, nodes_visited, elapsed_time_seconds).
    """
    start_time = time.perf_counter()
    nodes_visited = [0]  # Counter mutable trong hàm đệ quy

    threshold = get_heuristic(scrambled_state)
    path: List[str] = []

    def dfs(state: State, g: int, curr_threshold: int, last_move: Optional[str]):
        nodes_visited[0] += 1
        f = g + get_heuristic(state)

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
            if result == "FOUND":
                return "FOUND"
            if isinstance(result, (int, float)):
                min_exceed = min(min_exceed, result)
            path.pop()

        return min_exceed

    while threshold <= max_moves:
        result = dfs(scrambled_state, 0, threshold, None)
        if result == "FOUND":
            elapsed = time.perf_counter() - start_time
            return path, nodes_visited[0], elapsed
        if result == float("inf"):
            break
        threshold = int(result)

    elapsed = time.perf_counter() - start_time
    return None, nodes_visited[0], elapsed
