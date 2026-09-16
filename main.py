"""
main.py - Entry point cho chương trình AI Giải Rubik 3x3 bằng IDA*.
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
from src.solver import solve
from src.rubik_state import GOAL_STATE, apply_move

def main():
    print("=" * 60)
    print("      CHƯƠNG TRÌNH AI GIẢI RUBIK 3X3 BẰNG THUẬT TOÁN IDA*")
    print("=" * 60)

    n_scramble_steps = 5
    print(f"\n1. Đang sinh chuỗi xáo trộn {n_scramble_steps} bước...")
    scrambled_state, scramble_moves = scramble(n_scramble_steps, seed=42)
    print("   Chuỗi xáo trộn (Scramble):", " ".join(scramble_moves))

    print(f"\n2. Đang tìm lời giải bằng IDA* (Heuristic v1)...")
    solution, nodes, elapsed = solve(scrambled_state)

    if solution is not None:
        print("\n" + "=" * 60)
        print("KẾT QUẢ GIẢI THÀNH CÔNG!")
        print("=" * 60)
        print(f"Chuỗi lời giải (Solution) : {' '.join(solution)}")
        print(f"Số bước lời giải          : {len(solution)} bước")
        print(f"Số bước xáo trộn ban đầu  : {n_scramble_steps} bước")
        print(f"Số lượng node đã mở       : {nodes:,} nodes")
        print(f"Thời gian tính toán       : {elapsed:.4f} giây")

        # Xác minh lời giải bằng cách áp dụng chuỗi lời giải lên trạng thái xáo trộn
        test_state = scrambled_state
        for move in solution:
            test_state = apply_move(test_state, move)

        assert test_state == GOAL_STATE, "LỖI: Lời giải không đưa khối Rubik về GOAL_STATE!"
        print("Xác minh lời giải        : CHÍNH XÁC (Khối Rubik đã về GOAL_STATE)")
        print("=" * 60)
    else:
        print("Không tìm thấy lời giải trong giới hạn số bước cho phép!")

if __name__ == "__main__":
    main()
