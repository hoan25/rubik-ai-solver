"""
main.py - Entry point cho chương trình AI Giải Rubik 3x3 bằng IDA*.
So sánh hiệu năng giữa Heuristic v1 (Thô) và Heuristic v2 (Corner PDB).
"""

import sys
import io

# Đảm bảo stdout in UTF-8 không bị lỗi trên Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.scramble import scramble
from src.rubik_state import GOAL_STATE, apply_move
from src.solver import solve_ex
import src.heuristic as heuristic_module

def main():
    print("=" * 65)
    print("      CHƯƠNG TRÌNH AI GIẢI RUBIK 3X3 BẰNG THUẬT TOÁN IDA*")
    print("=" * 65)

    n_scramble_steps = 5
    print(f"\n1. Đang sinh chuỗi xáo trộn {n_scramble_steps} bước...")
    scrambled_state, scramble_moves = scramble(n_scramble_steps, seed=42)
    print("   Chuỗi xáo trộn (Scramble):", " ".join(scramble_moves))

    # 1. Giải bằng Heuristic v1 (Thô)
    h1 = heuristic_module.get_heuristic_v1
    name_h1 = f"{h1.__name__} (Thô)"
    print(f"\n2. Đang tìm lời giải bằng IDA* ({name_h1})...")
    res_v1 = solve_ex(scrambled_state, heuristic=h1)

    # 2. Giải bằng Heuristic v2 (Corner PDB)
    h2 = heuristic_module.get_heuristic_v2
    name_h2 = f"{h2.__name__} (Corner PDB)"
    print(f"3. Đang tìm lời giải bằng IDA* ({name_h2})...")
    res_v2 = solve_ex(scrambled_state, heuristic=h2)

    solution = res_v2.path if res_v2.path is not None else res_v1.path

    if solution is not None:
        print("\n" + "=" * 65)
        print("KẾT QUẢ GIẢI THÀNH CÔNG!")
        print("=" * 65)
        print(f"Chuỗi lời giải (Solution) : {' '.join(solution)}")
        print(f"Số bước lời giải          : {len(solution)} bước")
        print(f"Số bước xáo trộn ban đầu  : {n_scramble_steps} bước")
        
        # Bảng so sánh 2 Heuristic
        t1_str = f"{res_v1.elapsed:.4f} s"
        t2_str = f"{res_v2.elapsed:.4f} s"
        print("\n--- BẢNG SO SÁNH HIỆU NĂNG 2 HEURISTIC ---")
        print(f"{'Tiêu chí':<22} | {name_h1:<24} | {name_h2:<24}")
        print("-" * 75)
        print(f"{'Trạng thái':<22} | {res_v1.status:<24} | {res_v2.status:<24}")
        print(f"{'Số lượng node đã mở':<22} | {res_v1.nodes:<24,} | {res_v2.nodes:<24,}")
        print(f"{'Thời gian tính toán':<22} | {t1_str:<24} | {t2_str:<24}")
        if res_v2.nodes > 0:
            reduction = res_v1.nodes / res_v2.nodes
            print(f"{'Hiệu quả cắt tỉa':<22} | {'Gốc':<24} | Giảm {reduction:.1f}x lần node")
        print("-" * 75)

        # Xác minh lời giải bằng cách áp dụng chuỗi lời giải lên trạng thái xáo trộn
        test_state = scrambled_state
        for move in solution:
            test_state = apply_move(test_state, move)

        assert test_state == GOAL_STATE, "LỖI: Lời giải không đưa khối Rubik về GOAL_STATE!"
        print("Xác minh lời giải        : CHÍNH XÁC (Khối Rubik đã về GOAL_STATE)")
        print("=" * 65)
    else:
        print("Không tìm thấy lời giải trong giới hạn số bước / số node cho phép!")

if __name__ == "__main__":
    main()
