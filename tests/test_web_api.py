from fastapi.testclient import TestClient
from src.rubik_state import GOAL_STATE, apply_move
from web.app import app

client = TestClient(app)

def _json(st):
    return {
        "corner_perm": list(st.corner_perm),
        "corner_orient": list(st.corner_orient),
        "edge_perm": list(st.edge_perm),
        "edge_orient": list(st.edge_orient),
    }

def test_solve_uses_state_only():
    word = "F2 B2 F2 F2 B' R D2 B'".split()  # có nước thừa
    st = GOAL_STATE
    for m in word:
        st = apply_move(st, m)
    r = client.post("/solve", json={"state": _json(st), "heuristic": "v2"})
    d = r.json()
    assert r.status_code == 200 and d["status"] == "OK"
    assert len(d["moves"]) < len(word)  # không thể là "đảo ngược scramble"
    for m in d["moves"]:
        st = apply_move(st, m)
    assert st == GOAL_STATE

def test_invalid_state_is_422():
    bad = _json(GOAL_STATE)
    bad["corner_perm"][1] = 0  # trùng số
    r = client.post("/solve", json={"state": bad, "heuristic": "v2"})
    assert r.status_code == 422

def test_unknown_heuristic_is_422():
    r = client.post("/solve", json={"state": _json(GOAL_STATE), "heuristic": "v9"})
    assert r.status_code == 422
