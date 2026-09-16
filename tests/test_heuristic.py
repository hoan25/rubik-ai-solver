"""
test_heuristic.py - Unit test cho hàm heuristic.py
"""

import pytest
from src.rubik_state import GOAL_STATE, apply_move, MOVES
from src.heuristic import get_heuristic, get_heuristic_v1

def test_heuristic_goal_state():
    """Heuristic của GOAL_STATE phải bằng 0."""
    assert get_heuristic(GOAL_STATE) == 0
    assert get_heuristic_v1(GOAL_STATE) == 0

def test_heuristic_admissibility_one_move():
    """Kiểm tra tính Admissible với trạng thái sau 1 nước đi: h(s) <= 1."""
    for move in MOVES:
        state = apply_move(GOAL_STATE, move)
        h = get_heuristic(state)
        assert h <= 1, f"Lỗi: Heuristic cho 1 nước đi {move} là {h} > 1 (vi phạm Admissible)!"

def test_heuristic_admissibility_two_moves():
    """Kiểm tra tính Admissible với trạng thái sau 2 nước đi: h(s) <= 2."""
    for m1 in ["R", "U", "F"]:
        for m2 in ["D", "L", "B"]:
            state = apply_move(apply_move(GOAL_STATE, m1), m2)
            h = get_heuristic(state)
            assert h <= 2, f"Lỗi: Heuristic cho 2 nước đi {m1} {m2} là {h} > 2!"
