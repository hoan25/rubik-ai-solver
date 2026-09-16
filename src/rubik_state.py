"""
rubik_state.py - Biểu diễn trạng thái Rubik 3x3 và 18 toán tử xoay.

Biểu diễn:
- Corner (8 viên góc): 
  Vị trí: 0:UFL, 1:UFR, 2:UBR, 3:UBL, 4:DFL, 5:DFR, 6:DBR, 7:DBL
  Hoán vị: 0..7
  Hướng xoay (orientation): 0 (đúng), 1 (xoay theo chiều kim đồng hồ), 2 (xoay ngược chiều KĐH)
- Edge (12 viên cạnh):
  Vị trí: 0:UL, 1:UR, 2:UB, 3:UF, 4:BL, 5:BR, 6:FR, 7:FL, 8:DL, 9:DR, 10:DB, 11:DF
  Hoán vị: 0..11
  Hướng xoay (orientation): 0 (đúng), 1 (lật cạnh)
"""

from typing import NamedTuple

class State(NamedTuple):
    corner_perm: tuple[int, ...]   # 8 phần tử (0..7)
    corner_orient: tuple[int, ...] # 8 phần tử (0..2)
    edge_perm: tuple[int, ...]     # 12 phần tử (0..11)
    edge_orient: tuple[int, ...]   # 12 phần tử (0..1)

# Trạng thái đính (Goal State)
GOAL_STATE = State(
    corner_perm=tuple(range(8)),
    corner_orient=(0,) * 8,
    edge_perm=tuple(range(12)),
    edge_orient=(0,) * 12,
)

# Danh sách 18 nước đi chuẩn WCA
MOVES = [
    "U", "U'", "U2",
    "D", "D'", "D2",
    "R", "R'", "R2",
    "L", "L'", "L2",
    "F", "F'", "F2",
    "B", "B'", "B2"
]

# Định nghĩa 6 nước đi cơ bản (xoay 90 độ theo chiều kim đồng hồ)
# Mỗi nước đi định nghĩa:
# - corner_map: dict[dst] = src (viên ở src sẽ chuyển tới dst)
# - corner_delta: dict[dst] = delta (thay đổi hướng góc tại dst)
# - edge_map: dict[dst] = src
# - edge_delta: dict[dst] = delta (thay đổi lật cạnh tại dst)

_BASIC_MOVES_RAW = {
    "U": {
        "corner_map": {0: 3, 1: 0, 2: 1, 3: 2, 4: 4, 5: 5, 6: 6, 7: 7},
        "corner_delta": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
        "edge_map": {0: 2, 1: 0, 2: 3, 3: 1, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11},
        "edge_delta": {i: 0 for i in range(12)},
    },
    "D": {
        "corner_map": {0: 0, 1: 1, 2: 2, 3: 3, 4: 5, 5: 6, 6: 7, 7: 4},
        "corner_delta": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
        "edge_map": {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 11, 9: 8, 10: 9, 11: 10},
        "edge_delta": {i: 0 for i in range(12)},
    },
    "R": {
        "corner_map": {0: 0, 1: 5, 2: 1, 3: 3, 4: 4, 5: 6, 6: 2, 7: 7},
        "corner_delta": {1: 2, 2: 1, 6: 2, 5: 1, 0: 0, 3: 0, 4: 0, 7: 0},
        "edge_map": {0: 0, 1: 6, 2: 2, 3: 3, 4: 4, 5: 1, 6: 9, 7: 7, 8: 8, 9: 5, 10: 10, 11: 11},
        "edge_delta": {i: 0 for i in range(12)},
    },
    "L": {
        "corner_map": {0: 3, 1: 1, 2: 2, 3: 7, 4: 0, 5: 5, 6: 6, 7: 4},
        "corner_delta": {0: 1, 4: 2, 7: 1, 3: 2, 1: 0, 2: 0, 5: 0, 6: 0},
        "edge_map": {0: 4, 1: 1, 2: 2, 3: 3, 4: 8, 5: 5, 6: 6, 7: 0, 8: 7, 9: 9, 10: 10, 11: 11},
        "edge_delta": {i: 0 for i in range(12)},
    },
    "F": {
        "corner_map": {0: 4, 1: 0, 2: 2, 3: 3, 4: 5, 5: 1, 6: 6, 7: 7},
        "corner_delta": {0: 2, 1: 1, 5: 2, 4: 1, 2: 0, 3: 0, 6: 0, 7: 0},
        "edge_map": {0: 0, 1: 1, 2: 2, 3: 7, 4: 4, 5: 5, 6: 3, 7: 11, 8: 8, 9: 9, 10: 10, 11: 6},
        "edge_delta": {3: 1, 6: 1, 11: 1, 7: 1, 0: 0, 1: 0, 2: 0, 4: 0, 5: 0, 8: 0, 9: 0, 10: 0},
    },
    "B": {
        "corner_map": {0: 0, 1: 1, 2: 6, 3: 2, 4: 4, 5: 5, 6: 7, 7: 3},
        "corner_delta": {2: 2, 3: 1, 7: 2, 6: 1, 0: 0, 1: 0, 4: 0, 5: 0},
        "edge_map": {0: 0, 1: 1, 2: 5, 3: 3, 4: 2, 5: 10, 6: 6, 7: 7, 8: 8, 9: 9, 10: 4, 11: 11},
        "edge_delta": {2: 1, 4: 1, 10: 1, 5: 1, 0: 0, 1: 0, 3: 0, 6: 0, 7: 0, 8: 0, 9: 0, 11: 0},
    },
}

def _compose_moves(m1: dict, m2: dict) -> dict:
    """Tổng hợp 2 bước di chuyển m1 rồi m2 thành 1 bảng dịch chuyển duy nhất."""
    corner_map = {i: m1["corner_map"][m2["corner_map"][i]] for i in range(8)}
    corner_delta = {
        i: (m1["corner_delta"][m2["corner_map"][i]] + m2["corner_delta"][i]) % 3
        for i in range(8)
    }
    edge_map = {i: m1["edge_map"][m2["edge_map"][i]] for i in range(12)}
    edge_delta = {
        i: (m1["edge_delta"][m2["edge_map"][i]] + m2["edge_delta"][i]) % 2
        for i in range(12)
    }
    return {
        "corner_map": corner_map,
        "corner_delta": corner_delta,
        "edge_map": edge_map,
        "edge_delta": edge_delta,
    }

# Bảng tra cứu cho toàn bộ 18 nước đi
MOVE_TABLE: dict[str, dict] = {}

for face, data in _BASIC_MOVES_RAW.items():
    MOVE_TABLE[face] = data
    m2 = _compose_moves(data, data)
    MOVE_TABLE[f"{face}2"] = m2
    m3 = _compose_moves(m2, data)
    MOVE_TABLE[f"{face}'"] = m3

def apply_move(state: State, move: str) -> State:
    """Trả về trạng thái mới sau khi áp dụng nước đi `move`."""
    move_data = MOVE_TABLE[move]
    cmap = move_data["corner_map"]
    cdelta = move_data["corner_delta"]
    emap = move_data["edge_map"]
    edelta = move_data["edge_delta"]

    cp = state.corner_perm
    co = state.corner_orient
    ep = state.edge_perm
    eo = state.edge_orient

    new_cp = tuple(cp[cmap[i]] for i in range(8))
    new_co = tuple((co[cmap[i]] + cdelta[i]) % 3 for i in range(8))
    new_ep = tuple(ep[emap[i]] for i in range(12))
    new_eo = tuple((eo[emap[i]] + edelta[i]) % 2 for i in range(12))

    return State(new_cp, new_co, new_ep, new_eo)

def get_permutation_parity(perm: tuple[int, ...]) -> int:
    """Tính tính chẵn lẻ (parity) của hoán vị perm: 0 là chẵn, 1 là lẻ."""
    n = len(perm)
    visited = [False] * n
    num_cycles = 0
    for i in range(n):
        if not visited[i]:
            num_cycles += 1
            curr = i
            while not visited[curr]:
                visited[curr] = True
                curr = perm[curr]
    return (n - num_cycles) % 2

def is_valid_parity(state: State) -> bool:
    """Kiểm tra parity hoán vị góc và hoán vị cạnh có cùng tính chẵn/lẻ hay không."""
    return get_permutation_parity(state.corner_perm) == get_permutation_parity(state.edge_perm)
