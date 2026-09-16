"""
test_state.py - Unit test cho không gian trạng thái Rubik 3x3 và 18 toán tử xoay.
"""

import pytest
from src.rubik_state import State, GOAL_STATE, MOVES, apply_move, is_valid_parity

FACES = ["U", "D", "R", "L", "F", "B"]

def test_goal_state_validity():
    """Kiểm tra GOAL_STATE hợp lệ."""
    assert len(GOAL_STATE.corner_perm) == 8
    assert len(GOAL_STATE.corner_orient) == 8
    assert len(GOAL_STATE.edge_perm) == 12
    assert len(GOAL_STATE.edge_orient) == 12
    assert is_valid_parity(GOAL_STATE) is True

def test_four_turns_identity():
    """Xoay 1 mặt 4 lần liên tiếp (X -> X -> X -> X) phải quay về trạng thái ban đầu."""
    for face in FACES:
        state = GOAL_STATE
        for _ in range(4):
            state = apply_move(state, face)
        assert state == GOAL_STATE, f"Lỗi: Xoay {face} 4 lần không trả về GOAL_STATE!"

def test_move_inverse_identity():
    """Xoay X rồi X' (trên cả 6 mặt) phải trả về trạng thái ban đầu."""
    for face in FACES:
        state = GOAL_STATE
        state = apply_move(state, face)
        state = apply_move(state, f"{face}'")
        assert state == GOAL_STATE, f"Lỗi: {face} + {face}' không trả về GOAL_STATE!"

        # Thử lại theo chiều ngược: X' rồi X
        state = GOAL_STATE
        state = apply_move(state, f"{face}'")
        state = apply_move(state, face)
        assert state == GOAL_STATE, f"Lỗi: {face}' + {face} không trả về GOAL_STATE!"

def test_double_move_twice_identity():
    """Xoay X2 hai lần liên tiếp (trên cả 6 mặt) phải trả về trạng thái ban đầu."""
    for face in FACES:
        state = GOAL_STATE
        state = apply_move(state, f"{face}2")
        state = apply_move(state, f"{face}2")
        assert state == GOAL_STATE, f"Lỗi: {face}2 + {face}2 không trả về GOAL_STATE!"

def test_parity_preservation():
    """Kiểm tra tính chẵn lẻ parity (corner_parity == edge_parity) luôn được duy trì sau mọi nước đi."""
    import random
    random.seed(42)

    state = GOAL_STATE
    for _ in range(100):
        move = random.choice(MOVES)
        state = apply_move(state, move)
        assert is_valid_parity(state) is True, f"Lỗi parity sau nước đi {move}!"

def test_domain_ranges():
    """Kiểm tra các giá trị trong State nằm trong miền giá trị hợp lệ."""
    state = GOAL_STATE
    for move in ["R", "U", "F2", "L'", "B2", "D'"]:
        state = apply_move(state, move)
        assert sorted(state.corner_perm) == list(range(8))
        assert all(0 <= o <= 2 for o in state.corner_orient)
        assert sorted(state.edge_perm) == list(range(12))
        assert all(0 <= o <= 1 for o in state.edge_orient)
