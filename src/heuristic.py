"""
heuristic.py - Pattern Database Heuristic (v2) cho Rubik 3x3.

Mô tả:
- encode_corners: Mã hoá 8 góc thành 1 index nguyên duy nhất (0 .. 88,179,839)
  sử dụng Lehmer code cho hoán vị (0..40319) và cơ số 3 cho orientation (0..2186).
- build_corner_pdb: BFS ngược từ GOAL_STATE (chỉ xét phần góc), lưu khoảng cách tối thiểu
  vào mảng array.array('B') có dung lượng ~84.1 MB.
- Sử dụng module C tối ưu (fast_pdb.dll) giúp hoàn tất BFS 88.17 triệu trạng thái trong khoảng 1–2 phút (~97,5 giây trên 1 core, -O2).
- Dữ liệu PDB được lưu vĩnh viễn tại `data/pdb_corner.pkl` để dùng lại cho các lần chạy sau.
- get_heuristic_v2: Lấy max(h_corner_pdb, h_edge_fallback) để đảm bảo tính Admissible.
"""

import os
import sys
import io
import time
import pickle
import array
import ctypes
from typing import Optional
from tqdm import tqdm
from src.rubik_state import State, GOAL_STATE, MOVES, MOVE_TABLE

# Đảm bảo stdout in UTF-8 không bị lỗi trên Windows console
if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PDB_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pdb_corner.pkl")
PDB_SIZE = 88_179_840  # 8! * 3^7 = 40,320 * 2,187 = 88,179,840

def encode_corners(cp: tuple[int, ...], co: tuple[int, ...]) -> int:
    """
    Mã hoá (corner_perm, corner_orient) thành số nguyên duy nhất [0 .. 88,179,839].
    Dùng Lehmer Code cho hoán vị 8 góc và cơ số 3 cho 7 hướng góc đầu tiên.
    """
    p0, p1, p2, p3, p4, p5, p6, p7 = cp
    c0 = (p1 < p0) + (p2 < p0) + (p3 < p0) + (p4 < p0) + (p5 < p0) + (p6 < p0) + (p7 < p0)
    c1 = (p2 < p1) + (p3 < p1) + (p4 < p1) + (p5 < p1) + (p6 < p1) + (p7 < p1)
    c2 = (p3 < p2) + (p4 < p2) + (p5 < p2) + (p6 < p2) + (p7 < p2)
    c3 = (p4 < p3) + (p5 < p3) + (p6 < p3) + (p7 < p3)
    c4 = (p5 < p4) + (p6 < p4) + (p7 < p4)
    c5 = (p6 < p5) + (p7 < p5)
    c6 = (p7 < p6)

    perm_idx = c0 * 5040 + c1 * 720 + c2 * 120 + c3 * 24 + c4 * 6 + c5 * 2 + c6
    orient_idx = (((((co[0] * 3 + co[1]) * 3 + co[2]) * 3 + co[3]) * 3 + co[4]) * 3 + co[5]) * 3 + co[6]

    return perm_idx * 2187 + orient_idx


def build_corner_pdb() -> array.array:
    """
    Xây dựng Pattern Database cho 8 góc bằng BFS ngược từ GOAL_STATE.
    Sử dụng C-DLL siêu tốc nếu có, hoặc fallback Python BFS.
    """
    dll_path = os.path.join(os.path.dirname(__file__), "fast_pdb.dll")
    if os.path.exists(dll_path):
        print("Đang sinh Pattern Database (Corner PDB) bằng module C (fast_pdb.dll)...")
        start_t = time.perf_counter()

        c_maps = ((ctypes.c_uint8 * 8) * 18)()
        c_deltas = ((ctypes.c_uint8 * 8) * 18)()

        for idx, move in enumerate(MOVES):
            mdata = MOVE_TABLE[move]
            for i in range(8):
                c_maps[idx][i] = mdata["corner_map"][i]
                c_deltas[idx][i] = mdata["corner_delta"][i]

        lib = ctypes.CDLL(dll_path)
        lib.set_move_tables(c_maps, c_deltas)

        pdb = array.array("B", [255]) * PDB_SIZE
        ptr = (ctypes.c_uint8 * PDB_SIZE).from_buffer(pdb)

        visited_count = lib.build_c_pdb(ptr)
        elapsed = time.perf_counter() - start_t
        print(f"Hoàn tất BFS Corner PDB bằng C trong {elapsed:.2f} giây! Đã duyệt đủ {visited_count:,} trạng thái góc.")
        return pdb

    # Fallback Python BFS (nếu không có DLL)
    print("Môi trường: Đang sinh Pattern Database (Corner PDB) bằng Python BFS...")
    start_time = time.perf_counter()
    pdb = array.array("B", [255]) * PDB_SIZE

    start_perm = GOAL_STATE.corner_perm
    start_orient = GOAL_STATE.corner_orient
    start_idx = encode_corners(start_perm, start_orient)
    pdb[start_idx] = 0

    _corner_transforms = [
        (tuple(MOVE_TABLE[m]["corner_map"][i] for i in range(8)),
         tuple(MOVE_TABLE[m]["corner_delta"][i] for i in range(8)))
        for m in MOVES
    ]

    curr_level = [(start_perm, start_orient)]
    depth = 0
    total_visited = 1

    pbar = tqdm(total=PDB_SIZE, desc="Build Corner PDB", unit="states")
    pbar.update(1)

    while curr_level:
        next_level = []
        depth_plus_1 = depth + 1

        for cp, co in curr_level:
            for cmap, cdelta in _corner_transforms:
                new_cp = (
                    cp[cmap[0]], cp[cmap[1]], cp[cmap[2]], cp[cmap[3]],
                    cp[cmap[4]], cp[cmap[5]], cp[cmap[6]], cp[cmap[7]]
                )
                new_co = (
                    (co[cmap[0]] + cdelta[0]) % 3,
                    (co[cmap[1]] + cdelta[1]) % 3,
                    (co[cmap[2]] + cdelta[2]) % 3,
                    (co[cmap[3]] + cdelta[3]) % 3,
                    (co[cmap[4]] + cdelta[4]) % 3,
                    (co[cmap[5]] + cdelta[5]) % 3,
                    (co[cmap[6]] + cdelta[6]) % 3,
                    (co[cmap[7]] + cdelta[7]) % 3
                )
                idx = encode_corners(new_cp, new_co)
                if pdb[idx] == 255:
                    pdb[idx] = depth_plus_1
                    next_level.append((new_cp, new_co))
                    total_visited += 1
                    pbar.update(1)

        depth += 1
        curr_level = next_level

    pbar.close()
    elapsed = time.perf_counter() - start_time
    print(f"Hoàn tất BFS Corner PDB trong {elapsed:.2f} giây! Đã duyệt đủ {total_visited:,} trạng thái góc.")
    return pdb


def load_or_build_corner_pdb() -> array.array:
    """Load Corner PDB từ file pkl nếu có, nếu chưa thì build mới và lưu lại."""
    if os.path.exists(PDB_FILE_PATH):
        print(f"Đang nạp Corner PDB từ file cache: {PDB_FILE_PATH}...")
        start_t = time.perf_counter()
        with open(PDB_FILE_PATH, "rb") as f:
            pdb = pickle.load(f)
        elapsed = time.perf_counter() - start_t
        file_size_mb = os.path.getsize(PDB_FILE_PATH) / (1024 * 1024)
        print(f"Đã nạp xong Corner PDB ({file_size_mb:.2f} MB) trong {elapsed:.2f} giây.")
        return pdb
    else:
        pdb = build_corner_pdb()
        os.makedirs(os.path.dirname(PDB_FILE_PATH), exist_ok=True)
        print(f"Đang lưu Corner PDB ra file {PDB_FILE_PATH}...")
        start_save = time.perf_counter()
        with open(PDB_FILE_PATH, "wb") as f:
            pickle.dump(pdb, f, protocol=pickle.HIGHEST_PROTOCOL)
        save_elapsed = time.perf_counter() - start_save
        file_size_mb = os.path.getsize(PDB_FILE_PATH) / (1024 * 1024)
        print(f"Đã lưu thành công ({file_size_mb:.2f} MB) trong {save_elapsed:.2f} giây.")
        return pdb


# Nạp biến toàn cục CORNER_PDB
CORNER_PDB: Optional[array.array] = None

def _get_corner_pdb() -> array.array:
    global CORNER_PDB
    if CORNER_PDB is None:
        CORNER_PDB = load_or_build_corner_pdb()
    return CORNER_PDB

def preload_pdb() -> None:
    """Nạp Corner PDB vào RAM (gọi 1 lần khi khởi động, trước khi đo thời gian)."""
    _get_corner_pdb()


def get_heuristic_v2(state: State) -> int:
    """
    Heuristic v2 (Pattern Database cho Góc + Fallback cho Cạnh):
    - h_corner: Giá trị chính xác từ Corner PDB (0..11)
    - h_edge: Fallback cho 12 cạnh (misplaced_edges + 3) // 4
    - Trả về max(h_corner, h_edge) để đảm bảo tính Admissible.
    """
    if state == GOAL_STATE:
        return 0

    pdb = _get_corner_pdb()
    c_idx = encode_corners(state.corner_perm, state.corner_orient)
    h_corner = pdb[c_idx]

    misplaced_edges = sum(
        1 for i in range(12)
        if state.edge_perm[i] != GOAL_STATE.edge_perm[i] or state.edge_orient[i] != GOAL_STATE.edge_orient[i]
    )
    h_edge = (misplaced_edges + 3) // 4

    return max(h_corner, h_edge)


def get_heuristic_v1(state: State) -> int:
    """Heuristic v1 thô (tạm thời)."""
    if state == GOAL_STATE:
        return 0
    misplaced_corners = sum(
        1 for i in range(8)
        if state.corner_perm[i] != GOAL_STATE.corner_perm[i] or state.corner_orient[i] != GOAL_STATE.corner_orient[i]
    )
    misplaced_edges = sum(
        1 for i in range(12)
        if state.edge_perm[i] != GOAL_STATE.edge_perm[i] or state.edge_orient[i] != GOAL_STATE.edge_orient[i]
    )
    return (misplaced_corners + misplaced_edges + 7) // 8


# Gán heuristic v2 làm heuristic chính mặc định
get_heuristic = get_heuristic_v2
