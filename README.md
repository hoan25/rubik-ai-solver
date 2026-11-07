# Rubik 3×3 AI Solver

Giải Rubik bằng IDA*, kết hợp hai heuristic: đếm vị trí sai (v1) và Corner Pattern Database cùng cận dưới cạnh (v2). Web demo dùng FastAPI và Three.js để xáo trộn và phát từng nước giải.

## Cài môi trường

Dùng Python 3.11. Trong PowerShell trên Windows:

```powershell
git clone https://github.com/hoan25/rubik-ai-solver.git
cd rubik-ai-solver
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000. Frontend tải Three.js từ CDN nên trình duyệt cần kết nối Internet.

Hoặc dùng Conda với cấu hình có sẵn:

```bash
conda env create -f environment.yml
conda activate rubik-ai
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Với Linux/macOS, có thể dùng `python3 -m venv .venv`, `source .venv/bin/activate`, rồi `python -m pip install -r requirements.txt`.

## Pattern Database

Chương trình tự tạo `data/pdb_corner.pkl` khi chưa có cache. Dữ liệu góc gồm `8! × 3^7 = 88.179.840` ô byte, khoảng 84 MiB. Lần khởi động đầu cần thời gian tạo bảng; những lần sau nạp lại cache.

`src/fast_pdb.dll` là thư viện C biên dịch sẵn cho Windows. Có thể biên dịch lại từ mã nguồn với GCC tương ứng hệ điều hành và kiến trúc Python:

```bash
# Windows (MinGW-w64)
gcc -O2 -shared -o src/fast_pdb.dll src/fast_pdb.c

# Linux/macOS: ten file .dll theo duong dan loader trong heuristic.py
gcc -O2 -shared -fPIC -o src/fast_pdb.dll src/fast_pdb.c
```

Khi không có thư viện C, chương trình có đường xây dựng PDB bằng Python, chậm hơn. Cache và môi trường ảo được tạo tại máy chạy.

## Chạy CLI và kiểm thử

Sau khi kích hoạt môi trường:

```bash
python main.py
python -m pytest tests -q
node --test web/tests/test_player.mjs
```

Bài kiểm thử gọi API qua HTTP cần server tại `127.0.0.1:8000`; bài đó được bỏ qua khi không kết nối được server. Kiểm thử JavaScript cần Node.js 18 trở lên.

## Cấu trúc mã nguồn

| Đường dẫn | Chức năng |
| --- | --- |
| `main.py` | Chạy solver từ terminal |
| `src/rubik_state.py` | Trạng thái 8 góc, 12 cạnh và 18 nước xoay |
| `src/solver.py` | IDA*, cắt nhánh, giới hạn node |
| `src/heuristic.py` | Mã hóa góc, tạo/nạp PDB và heuristic |
| `src/fast_pdb.c` | Tăng tốc tạo PDB bằng C |
| `src/scramble.py` | Tạo chuỗi xáo trộn |
| `src/benchmark.py` | Mã đo hiệu năng |
| `web/app.py` | API và phục vụ giao diện |
| `web/static/` | Giao diện và bộ phát hoạt ảnh |
| `tests/`, `web/tests/` | Kiểm thử Python và JavaScript |
| `requirements.txt`, `environment.yml` | Cấu hình cài môi trường |

Mỗi nước trong tập 18 toán tử có chi phí 1, bao gồm cả nước quay 180°. Solver tìm đường từ trạng thái đầu vào đến trạng thái đích; heuristic và cắt nhánh giúp giảm số trạng thái phải duyệt.
