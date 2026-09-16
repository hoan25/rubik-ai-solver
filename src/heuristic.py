"""
heuristic.py - Hàm heuristic đánh giá khoảng cách đến GOAL_STATE.

Mô tả phiên bản:
- Heuristic v1 — tạm thời, không chặt, dùng để thông toàn bộ pipeline (Giai đoạn 1 -> Giai đoạn 4).
- Phương pháp: Đếm tổng số viên góc và viên cạnh bị sai vị trí hoặc sai hướng so với GOAL_STATE,
  sau đó chia cho 8 (vì 1 nước đi xoay mặt thay đổi tối đa 4 viên góc và 4 viên cạnh).
- Đảm bảo tính chấp nhận được (admissible): h(s) <= h*(s).
- Lưu ý: Phiên bản v2 ở bước sau sẽ nâng cấp lên Pattern Database (PDB) để có heuristic chặt hơn.
"""

from src.rubik_state import State, GOAL_STATE

def get_heuristic_v1(state: State) -> int:
    """
    Tính heuristic v1 (thô) cho trạng thái s.
    Trả về số bước tối thiểu ước lượng để đưa trạng thái s về GOAL_STATE.
    """
    if state == GOAL_STATE:
        return 0

    # Đếm số viên góc sai vị trí hoặc sai hướng
    misplaced_corners = sum(
        1 for i in range(8)
        if state.corner_perm[i] != GOAL_STATE.corner_perm[i] or state.corner_orient[i] != GOAL_STATE.corner_orient[i]
    )

    # Đếm số viên cạnh sai vị trí hoặc sai hướng
    misplaced_edges = sum(
        1 for i in range(12)
        if state.edge_perm[i] != GOAL_STATE.edge_perm[i] or state.edge_orient[i] != GOAL_STATE.edge_orient[i]
    )

    total_misplaced = misplaced_corners + misplaced_edges

    # 1 nước đi thay đổi tối đa 4 viên góc và 4 viên cạnh (tổng 8 viên)
    # Chia cho 8 (lấy trần) để đảm bảo tính Admissible: h(s) <= h*(s)
    return (total_misplaced + 7) // 8

# Gán alias mặc định cho phiên bản heuristic hiện tại
get_heuristic = get_heuristic_v1
