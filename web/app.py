import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

# Tự động thêm thư mục gốc dự án vào PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rubik_state import State, GOAL_STATE, is_valid_parity
from src.scramble import scramble as scramble_func
from src.solver import solve_ex
import src.heuristic as heuristic_module

app = FastAPI(title="Rubik AI Web Demo")

# Bật CORS cho phép gọi từ file HTML local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo trước PDB ngay khi start server
print("Loading Pattern Database...")
heuristic_module.preload_pdb()
print("Pattern Database loaded!")

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

class StateModel(BaseModel):
    corner_perm: List[int]
    corner_orient: List[int]
    edge_perm: List[int]
    edge_orient: List[int]

class SolveRequest(BaseModel):
    state: StateModel
    heuristic: str  # "v1" or "v2"

def _to_state(m: StateModel) -> State:
    s = State(
        corner_perm=tuple(m.corner_perm),
        corner_orient=tuple(m.corner_orient),
        edge_perm=tuple(m.edge_perm),
        edge_orient=tuple(m.edge_orient),
    )
    valid = (
        sorted(s.corner_perm) == list(range(8))
        and sorted(s.edge_perm) == list(range(12))
        and len(s.corner_orient) == 8 and len(s.edge_orient) == 12
        and all(o in (0, 1, 2) for o in s.corner_orient)
        and all(o in (0, 1) for o in s.edge_orient)
        and sum(s.corner_orient) % 3 == 0
        and sum(s.edge_orient) % 2 == 0
        and is_valid_parity(s)
    )
    if not valid:
        raise HTTPException(status_code=422, detail="Trạng thái khối không hợp lệ")
    return s

@app.get("/")
def read_root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))

@app.get("/scramble")
def get_scramble(n: int = 10):
    try:
        state, moves = scramble_func(n)
        return {
            "state": {
                "corner_perm": list(state.corner_perm),
                "corner_orient": list(state.corner_orient),
                "edge_perm": list(state.edge_perm),
                "edge_orient": list(state.edge_orient)
            },
            "moves": moves
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve")
def post_solve(req: SolveRequest):
    state = _to_state(req.state)
    if req.heuristic not in ("v1", "v2"):
        raise HTTPException(status_code=422, detail="heuristic phải là 'v1' hoặc 'v2'")
    h_func = (
        heuristic_module.get_heuristic_v2
        if req.heuristic == "v2"
        else heuristic_module.get_heuristic_v1
    )
    try:
        r = solve_ex(state, heuristic=h_func, max_moves=25)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "moves": r.path,  # None nếu TIMEOUT / NO_SOLUTION
        "nodes_opened": r.nodes,
        "time_ms": round(r.elapsed * 1000, 2),
        "heuristic_used": req.heuristic,
        "status": r.status,  # "OK" | "TIMEOUT" | "NO_SOLUTION"
    }
