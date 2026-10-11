import pytest
import collections
from src.rubik_state import GOAL_STATE, MOVES, apply_move
from src.solver import is_redundant
import src.heuristic as H

def order(word: str) -> int:
    st, k = GOAL_STATE, 0
    while True:
        for m in word.split():
            st = apply_move(st, m)
        k += 1
        if st == GOAL_STATE:
            return k

def test_known_element_orders():
    # Bậc của các chuỗi đã biết trên khối Rubik thật
    assert order("R U") == 105
    assert order("R U2 D' B D'") == 1260
    assert order("R U R' U'") == 6

def test_states_by_depth_match_real_cube():
    seen, frontier, counts = {GOAL_STATE}, [(GOAL_STATE, None)], [1]
    for _ in range(5):
        nxt, new = [], 0
        for st, last in frontier:
            for m in MOVES:
                if is_redundant(m, last):
                    continue
                ns = apply_move(st, m)
                if ns not in seen:
                    seen.add(ns); nxt.append((ns, m)); new += 1
        counts.append(new); frontier = nxt
    assert counts == [1, 18, 243, 3240, 43239, 574908]

def test_preload_loads_pdb():
    H.CORNER_PDB = None
    H.preload_pdb()
    assert H.CORNER_PDB is not None

def test_corner_pdb_distribution():
    pdb = H._get_corner_pdb()
    cnt = collections.Counter(pdb)
    assert [cnt[d] for d in range(12)] == [
        1, 18, 243, 2874, 28000, 205416, 1168516,
        5402628, 20776176, 45391616, 15139616, 64736
    ]
