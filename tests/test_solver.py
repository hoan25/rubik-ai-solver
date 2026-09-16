"""
test_solver.py - Unit test cho thuật toán IDA* solver.
"""

import pytest
from src.rubik_state import GOAL_STATE, apply_move
from src.scramble import scramble
from src.solver import solve

def test_solve_goal_state():
    """Giải GOAL_STATE trả về 0 bước."""
    solution, nodes, elapsed = solve(GOAL_STATE)
    assert solution == []
    assert nodes >= 1

def test_solve_one_move():
    """Giải scramble 1 bước."""
    state, moves = scramble(1, seed=10)
    solution, nodes, elapsed = solve(state)
    assert solution is not None
    assert len(solution) == 1

    # Kiểm tra áp dụng solution phải đưa về GOAL_STATE
    curr = state
    for m in solution:
        curr = apply_move(curr, m)
    assert curr == GOAL_STATE

def test_solve_three_moves():
    """Giải scramble 3 bước."""
    state, moves = scramble(3, seed=20)
    solution, nodes, elapsed = solve(state)
    assert solution is not None
    assert len(solution) <= 3

    curr = state
    for m in solution:
        curr = apply_move(curr, m)
    assert curr == GOAL_STATE

def test_solve_five_moves():
    """Giải scramble 5 bước."""
    state, moves = scramble(5, seed=30)
    solution, nodes, elapsed = solve(state)
    assert solution is not None
    assert len(solution) <= 5

    curr = state
    for m in solution:
        curr = apply_move(curr, m)
    assert curr == GOAL_STATE
