"""
test_heuristic.py - Unit test cho Heuristic v2 (Corner PDB).
"""

import pytest
from src.rubik_state import GOAL_STATE, apply_move, MOVES
from src.heuristic import get_heuristic, get_heuristic_v1, get_heuristic_v2, encode_corners

def test_encode_corners_bounds():
    """Kiểm tra encode_corners sinh ra index nằm trong khoảng [0, 88179839]."""
    goal_idx = encode_corners(GOAL_STATE.corner_perm, GOAL_STATE.corner_orient)
    assert goal_idx == 0

    rev_perm = (7, 6, 5, 4, 3, 2, 1, 0)
    rev_orient = (2, 2, 2, 2, 2, 2, 2, 2)
    max_idx = encode_corners(rev_perm, rev_orient)
    assert max_idx == 88_179_839

def test_heuristic_goal_state():
    """Heuristic của GOAL_STATE phải bằng 0."""
    assert get_heuristic(GOAL_STATE) == 0
    assert get_heuristic_v1(GOAL_STATE) == 0
    assert get_heuristic_v2(GOAL_STATE) == 0

def test_heuristic_admissibility_known_scrambles():
    """
    Kiểm tra tính Admissible của Heuristic v2 (PDB):
    Với các chuỗi scramble 1, 2, 3 bước mà ta biết chắc số bước tối đa,
    h(s) bắt buộc phải <= số bước thực tế.
    """
    # 1. Scramble 1 bước: h(s) phải == 1 hoặc 0 (thường = 1)
    for m in ["R", "U", "F", "D", "L", "B"]:
        state = apply_move(GOAL_STATE, m)
        h = get_heuristic(state)
        assert h <= 1, f"Lỗi: Heuristic v2 cho 1 bước {m} là {h} > 1!"

    # 2. Scramble 2 bước: h(s) phải <= 2
    two_step_scrambles = [
        ["R", "U"],
        ["F", "D'"],
        ["L2", "B"],
        ["U", "R'"],
    ]
    for seq in two_step_scrambles:
        state = GOAL_STATE
        for m in seq:
            state = apply_move(state, m)
        h = get_heuristic(state)
        assert h <= 2, f"Lỗi: Heuristic v2 cho chuỗi {' '.join(seq)} là {h} > 2!"

    # 3. Scramble 3 bước: h(s) phải <= 3
    three_step_scrambles = [
        ["R", "U", "F"],
        ["D", "L'", "B2"],
        ["U2", "R'", "D'"],
    ]
    for seq in three_step_scrambles:
        state = GOAL_STATE
        for m in seq:
            state = apply_move(state, m)
        h = get_heuristic(state)
        assert h <= 3, f"Lỗi: Heuristic v2 cho chuỗi {' '.join(seq)} là {h} > 3!"
