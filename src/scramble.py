"""
scramble.py - Sinh chuỗi xáo trộn Rubik 3x3 ngẫu nhiên hợp lệ.
"""

import random
from typing import Tuple, List
from src.rubik_state import State, GOAL_STATE, MOVES, apply_move
from src.solver import is_redundant

def scramble(n_moves: int, seed: int | None = None) -> Tuple[State, List[str]]:
    """
    Sinh trạng thái xáo trộn hợp lệ n_moves bước bằng cách xoay liên tiếp.
    Trả về: (scrambled_state, moves_used).
    """
    if seed is not None:
        random.seed(seed)

    state = GOAL_STATE
    moves_used: List[str] = []
    last_move = None

    for _ in range(n_moves):
        valid_choices = [m for m in MOVES if not is_redundant(m, last_move)]
        move = random.choice(valid_choices)
        state = apply_move(state, move)
        moves_used.append(move)
        last_move = move

    return state, moves_used
