import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scramble import scramble
from src.benchmark import solve_with_heuristic
import src.heuristic as heuristic_module

def test_nodes_not_accumulating():
    print("--- KIỂM TRA BIẾN ĐẾM NODE TRONG CODE ---")
    state, moves = scramble(10, seed=42)
    print(f"Chuỗi xáo trộn 10 bước: {' '.join(moves)}")

    sol1, nodes1, time1 = solve_with_heuristic(state, heuristic_module.get_heuristic_v2)
    print(f"Lần 1: Nodes opened = {nodes1:,}, Thời gian = {time1:.4f}s")

    sol2, nodes2, time2 = solve_with_heuristic(state, heuristic_module.get_heuristic_v2)
    print(f"Lần 2: Nodes opened = {nodes2:,}, Thời gian = {time2:.4f}s")

    if nodes1 == nodes2:
        print("=> THÀNH CÔNG: Số node giống hệt nhau. Biến đếm không bị cộng dồn!")
    else:
        print("=> THẤT BẠI: Số node bị cộng dồn!")

if __name__ == "__main__":
    from src.rubik_state import GOAL_STATE
    heuristic_module.get_heuristic_v2(GOAL_STATE) # load PDB
    test_nodes_not_accumulating()
