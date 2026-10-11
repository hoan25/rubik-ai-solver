"""
solver.py - Thuật toán IDA* Search giải Rubik 3x3.
"""

import time
from typing import Callable, List, NamedTuple, Optional, Tuple
from src.rubik_state import State, GOAL_STATE, MOVES, apply_move
from src.heuristic import get_heuristic

# Cặp mặt đối diện giao hoán (U/D, R/L, F/B). Chỉ cho phép MỘT thứ tự:
# cấm D ngay sau U, cấm L ngay sau R, cấm B ngay sau F (cho phép "D U", cấm "U D").
_OPPOSITE_FIXED_ORDER = {
    "D": "U",  # Nếu last_move là U, cấm D
    "L": "R",  # Nếu last_move là R, cấm L
    "B": "F",  # Nếu last_move là F, cấm B
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

MAX_NODES_DEFAULT = 300_000

class SolveResult(NamedTuple):
    path: Optional[List[str]]   # None nếu không có lời giải
    nodes: int                  # số lần gọi dfs, cộng dồn mọi vòng ngưỡng
    elapsed: float              # giây
    status: str                 # "OK" | "TIMEOUT" | "NO_SOLUTION"

class _NodeLimit(Exception):
    pass

def solve_ex(scrambled_state: State,
             heuristic: Callable[[State], int] = get_heuristic,
             max_moves: int = 25,
             max_nodes: int = MAX_NODES_DEFAULT) -> SolveResult:
    """
    IDA*. 'node' = một lần gọi dfs (tính cả nút bị cắt ngay vì f > ngưỡng),
    cộng dồn qua tất cả các vòng ngưỡng.
    """
    start = time.perf_counter()
    nodes = 0
    path: List[str] = []

    def dfs(state: State, g: int, threshold: int, last: Optional[str]):
        nonlocal nodes
        nodes += 1
        if nodes > max_nodes:
            raise _NodeLimit
        f = g + heuristic(state)
        if f > threshold:
            return f
        if state == GOAL_STATE:
            return "FOUND"
        best = float("inf")
        for move in MOVES:
            if is_redundant(move, last):
                continue
            path.append(move)
            r = dfs(apply_move(state, move), g + 1, threshold, move)
            if r == "FOUND":
                return "FOUND"
            best = min(best, r)
            path.pop()
        return best

    threshold = heuristic(scrambled_state)
    try:
        while threshold <= max_moves:
            r = dfs(scrambled_state, 0, threshold, None)
            if r == "FOUND":
                return SolveResult(list(path), nodes, time.perf_counter() - start, "OK")
            if r == float("inf"):
                break
            threshold = int(r)
    except _NodeLimit:
        return SolveResult(None, nodes, time.perf_counter() - start, "TIMEOUT")
    return SolveResult(None, nodes, time.perf_counter() - start, "NO_SOLUTION")

def solve(scrambled_state: State, max_moves: int = 25,
          max_nodes: int = MAX_NODES_DEFAULT) -> Tuple[Optional[List[str]], int, float]:
    """Giữ nguyên chữ ký cũ (path, nodes, elapsed) để không vỡ code gọi hiện có."""
    r = solve_ex(scrambled_state, max_moves=max_moves, max_nodes=max_nodes)
    return r.path, r.nodes, r.elapsed

