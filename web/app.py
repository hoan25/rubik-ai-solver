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

from src.rubik_state import State, GOAL_STATE
from src.scramble import scramble as scramble_func
from src.benchmark import solve_with_heuristic
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
heuristic_module.get_heuristic_v2(GOAL_STATE)
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
    try:
        state_tuple = State(
            corner_perm=tuple(req.state.corner_perm),
            corner_orient=tuple(req.state.corner_orient),
            edge_perm=tuple(req.state.edge_perm),
            edge_orient=tuple(req.state.edge_orient)
        )
        
        if req.heuristic == "v2":
            h_func = heuristic_module.get_heuristic_v2
        else:
            h_func = heuristic_module.get_heuristic_v1
            
        path, nodes, time_s = solve_with_heuristic(state_tuple, h_func, max_moves=25)
        
        return {
            "moves": path, # Sẽ là null nếu TIMEOUT (nổ > 300,000 node)
            "nodes_opened": nodes,
            "time_ms": round(time_s * 1000, 2),
            "heuristic_used": req.heuristic
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
