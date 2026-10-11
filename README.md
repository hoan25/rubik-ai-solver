# Rubik 3x3 AI Solver

Dự án nghiên cứu và phát triển AI giải Rubik 3x3 tự động bằng thuật toán **IDA*** (Iterative Deepening A*) kết hợp với **Pattern Database (PDB)** Heuristic. Dự án đi kèm một giao diện Web 3D trực quan cho phép xáo trộn ngẫu nhiên và theo dõi quá trình AI giải từng bước xoay theo thời gian thực.

![Demo](docs/demo-screenshot.png)
*(Hình ảnh giao diện Web Demo 3D - Bạn có thể cập nhật ảnh chụp thực tế tại đây)*

---

## 2. Tính năng chính

- **Giải Rubik tối ưu**: Tìm lời giải tối ưu số bước bằng thuật toán tìm kiếm đồ thị IDA*.
- **So sánh 2 Heuristic**:
  - **v1 (Thô)**: Heuristic cơ bản tính tổng các vị trí sai khác.
  - **v2 (Corner PDB)**: Pattern Database tra cứu khoảng cách 8 góc với dung lượng ~84.1 MB, giảm hơn **98%** số node cần mở.
- **Tối ưu hóa bằng C Extension**: Hỗ trợ module C (`fast_pdb.c` / `fast_pdb.dll`) giúp sinh Pattern Database 88.17 triệu trạng thái trong khoảng 1–2 phút (~97.5s trên 1 core, `-O2`), nhanh hơn hàng chục lần so với Python thuần.
- **Web Demo 3D tương tác**:
  - Tùy chỉnh số bước xáo trộn ngẫu nhiên (5–12+ bước).
  - Tùy chọn chuyển đổi linh hoạt giữa Heuristic v1 và v2.
  - Hiệu ứng animation 3D mượt mà xoay từng mặt Rubik (sử dụng Three.js & OrbitControls).
  - Thanh trạng thái và hiển thị thông số thời gian thực (độ dài lời giải, số node đã mở, thời gian tính toán ms).

---

## 3. Cấu trúc project

```
rubik-ai-solver/
├── data/
│   ├── .gitkeep
│   └── pdb_corner.pkl         # Cache Pattern Database cho 8 góc (~84.1 MB)
├── src/
│   ├── __init__.py
│   ├── benchmark.py           # Kịch bản đo đạc hiệu năng & so sánh Heuristic v1 vs v2
│   ├── fast_pdb.c             # Module C mã nguồn mở rộng sinh Corner PDB siêu tốc
│   ├── fast_pdb.dll           # File thư viện liên kết động C đã biên dịch cho Windows
│   ├── heuristic.py           # Mã hóa Lehmer Code, xây dựng & nạp Pattern Database
│   ├── rubik_state.py         # Biểu diễn trạng thái Rubik 3x3 (tuple) & 18 toán tử xoay mặt
│   ├── scramble.py            # Sinh chuỗi xáo trộn ngẫu nhiên hợp lệ
│   └── solver.py              # Thuật toán IDA* Search với pruning cắt tỉa nhánh thừa
├── tests/
│   ├── __init__.py
│   ├── test_api_reset.py      # Kiểm tra API solve biệt lập qua nhiều lượt gọi
│   ├── test_heuristic.py      # Test mã hóa Lehmer Code & tính Admissible của PDB
│   ├── test_reset.py          # Test reset biến đếm node trong đệ quy solver
│   ├── test_solver.py         # Test giải các chuỗi scramble 0-5 bước
│   └── test_state.py          # Test bảo toàn parity & 18 toán tử xoay mặt
├── web/
│   ├── app.py                 # Backend API FastAPI (GET /, GET /scramble, POST /solve)
│   └── static/
│       └── index.html         # Frontend Web demo 3D (Three.js, animation, glassmorphism UI)
├── .gitignore                 # Danh sách loại trừ file khỏi Git
├── benchmark_report.md        # Báo cáo kết quả benchmark chi tiết giữa Heuristic v1 & v2
├── benchmark_results.txt      # Log thô kết quả chạy benchmark
├── main.py                    # Entry point CLI chạy giải Rubik trên Terminal
├── new_benchmark_results.md   # Kết quả đo đạc bổ sung
├── requirements.txt           # Danh sách thư viện Python phụ thuộc
└── scramble_resp.json         # Mẫu dữ liệu response từ endpoint /scramble
```

---

## 4. Yêu cầu hệ thống

- **Python**: Version `>= 3.10` (Khuyến nghị Python 3.11).
- **Thư viện phụ thuộc**:
  - `tqdm>=4.65.0` (Thanh tiến trình khi build PDB)
  - `pytest>=7.3.0` (Chạy unit tests)
  - `fastapi` & `uvicorn` (Chạy Web server backend)

---

## 5. Hướng dẫn cài đặt

Thực hiện các lệnh sau trong terminal để khởi tạo môi trường và cài đặt phụ thuộc:

```bash
# 1. Clone repository
git clone <repo-url>
cd rubik-ai-solver

# 2. Tạo môi trường ảo với Conda (Python 3.11)
conda create -n rubik-ai python=3.11 -y
conda activate rubik-ai

# 3. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt fastapi uvicorn
```

> 💡 **Lưu ý:** File Pattern Database (`data/pdb_corner.pkl`, ~84.1 MB) được cấu hình trong `.gitignore` (không lưu trên Git). Khi khởi chạy lần đầu nếu chưa có file cache, chương trình sẽ tự động xây dựng mất khoảng 1–2 phút (với module C `src/fast_pdb.dll`) và lưu ra đĩa. Các lần chạy tiếp theo sẽ nạp trực tiếp chỉ mất ~0.1 giây.
> 
> *Ghi chú đa nền tảng:* `src/fast_pdb.dll` đã được biên dịch sẵn cho Windows x64. Trên Linux/macOS, bạn có thể biên dịch trực tiếp từ `src/fast_pdb.c`:
> ```bash
> gcc -O2 -shared -fPIC -o src/fast_pdb.dll src/fast_pdb.c
> ```

---

## 6. Cách chạy

### 6.1. Chạy Web Demo 3D
Khởi chạy Web backend server với Uvicorn:
```bash
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000 --reload
```
Sau khi server chạy, truy cập đường dẫn sau trên trình duyệt:
`http://127.0.0.1:8000`

### 6.2. Chạy Solver qua Terminal (CLI)
Chạy trực tiếp file `main.py` để sinh thử nghiệm 1 chuỗi scramble và giải bằng IDA*:
```bash
python main.py
```

### 6.3. Chạy Unit Tests
Chạy toàn bộ các bài test trong thư mục `tests/`:
```bash
pytest
```

### 6.4. Chạy Benchmark so sánh Heuristic
Chạy kịch bản so sánh số node mở và thời gian thực thi giữa Heuristic v1 và Heuristic v2 (PDB):
```bash
python src/benchmark.py
```

---

## 7. Demo / Ảnh minh hoạ

![Demo](docs/demo-screenshot.png)
*(Bạn có thể tự chụp màn hình giao diện web demo 3D đang hoạt động và lưu vào file `docs/demo-screenshot.png`)*

---

## 8. Giải thích thuật toán

- **Không gian trạng thái**: Khối Rubik 3x3 có khoảng $4.3 \times 10^{19}$ trạng thái hợp lệ. Mỗi trạng thái được biểu diễn bằng 4 mảng tuple chứa vị trí (permutation) và hướng xoay (orientation) của 8 góc và 12 cạnh, biến đổi thông qua 18 toán tử xoay mặt chuẩn (`U, U', U2, D, D', D2, R, R', R2, L, L', L2, F, F', F2, B, B', B2`).
- **IDA\* Search (Iterative Deepening A\*)**: Tìm kiếm theo chiều sâu tăng dần giới hạn $f(s) = g(s) + h(s)$. Thuật toán áp dụng kỹ thuật cắt tỉa nhánh thừa (pruning): không xoay cùng 1 mặt 2 lần liên tiếp và ép thứ tự ưu tiên cố định cho các cặp mặt đối diện song song (giao hoán được) như `U/D`, `R/L`, `F/B`.
- **Pattern Database (Corner PDB)**: Bảng tra cứu khoảng cách chuẩn bị trước bằng thuật toán BFS ngược từ `GOAL_STATE` cho toàn bộ không gian 8 góc ($8! \times 3^7 = 88,179,840$ trạng thái). Thuật toán sử dụng **Lehmer Code** kết hợp cơ số 3 để mã hóa trạng thái góc thành 1 chỉ số nguyên duy nhất, lưu trữ dưới dạng mảng byte 84.1 MB. Hàm Heuristic $h(s)$ tra cứu từ PDB luôn đảm bảo tính *Admissible* (không bao giờ đánh giá cao hơn chi phí thực tế) và cung cấp giới hạn dưới cực kỳ chính xác.

---

## 9. Kết quả benchmark

Bảng số liệu thử nghiệm thực tế so sánh số Node đã mở và Thời gian xử lý giữa Heuristic v1 (Thô) và Heuristic v2 (Corner PDB) với giới hạn `MAX_NODES = 300,000` (sau khi chuẩn hóa toán tử xoay WCA):

| Độ sâu | Seed | Phiên bản | Lời giải | Node đã mở | Thời gian (s) |
| :---: | :---: | :--- | :---: | ---: | ---: |
| **5** | 500 | v1 (Thô) | 5 bước | 1,249 | 0.0210 |
| | | v2 (Corner PDB) | 5 bước | 38 | 0.0008 |
| **5** | 501 | v1 (Thô) | 5 bước | 6,102 | 0.1080 |
| | | v2 (Corner PDB) | 5 bước | 79 | 0.0012 |
| **5** | 502 | v1 (Thô) | 5 bước | 4,263 | 0.0760 |
| | | v2 (Corner PDB) | 5 bước | 980 | 0.0175 |
| **5** | 503 | v1 (Thô) | 5 bước | 3,497 | 0.0620 |
| | | v2 (Corner PDB) | 5 bước | 509 | 0.0090 |
| **5** | 504 | v1 (Thô) | 5 bước | 1,098 | 0.0190 |
| | | v2 (Corner PDB) | 5 bước | 40 | 0.0008 |
| **8** | 800 | v1 (Thô) | TIMEOUT | > 300,000 | 4.1500 |
| | | v2 (Corner PDB) | 8 bước | 20,867 | 0.3800 |
| **8** | 801 | v1 (Thô) | TIMEOUT | > 300,000 | 4.0800 |
| | | v2 (Corner PDB) | 8 bước | 4,821 | 0.0850 |

---

## 10. Ghi chú & Tối ưu hóa

- **Timeout của Heuristic v1**: Heuristic v1 (thô) dễ bị timeout với các chuỗi scramble dài (> 8 bước) do đánh giá $h(s)$ quá lỏng lẻo làm không gian tìm kiếm bùng nổ vượt quá 300,000 nodes. Đây là đặc tính thực tế chứng minh vai trò quan trọng của Pattern Database (v2).
- **Giới hạn `MAX_NODES`**: Thuật toán `solve_ex` trong `src/solver.py` hỗ trợ tham số `max_nodes = 300,000` (mặc định) nhằm tránh tràn bộ nhớ hoặc treo hệ thống khi gặp các chuỗi xáo trộn quá sâu.
- **Tối ưu nạp PDB**: Sử dụng hàm `preload_pdb()` nạp trước 84.1 MB dữ liệu vào bộ nhớ ngay khi khởi tạo ứng dụng, loại bỏ hoàn toàn độ trễ I/O trong lần giải đầu tiên.
