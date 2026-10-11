import pytest
from src.rubik_state import GOAL_STATE, apply_move
from src.scramble import scramble
from src.solver import solve_ex
import src.heuristic as H

def test_solution_returns_to_goal():
    """Kiểm tra lời giải tìm được khi áp dụng lên trạng thái xáo trộn đưa về đúng GOAL_STATE."""
    H.preload_pdb()
    for depth in [1, 3, 5]:
        for seed in range(3):
            state, scramble_moves = scramble(depth, seed=100 * depth + seed)
            res = solve_ex(state, heuristic=H.get_heuristic_v2)
            assert res.status == "OK"
            assert res.path is not None
            
            # Áp dụng lời giải
            curr = state
            for m in res.path:
                curr = apply_move(curr, m)
            assert curr == GOAL_STATE, f"Lỗi: Lời giải không đưa về GOAL_STATE cho seed {100 * depth + seed}"
