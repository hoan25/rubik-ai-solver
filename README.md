# Rubik 3x3 AI Solver using IDA* Search

Dự án giải Rubik 3x3 tự động sử dụng thuật toán **IDA*** (Iterative Deepening A*) kết hợp với **Pattern Database (PDB)** Heuristic.

---

## 📁 Cấu trúc dự án

```
rubik-ai-solver/
├── README.md               # Hướng dẫn dự án & Git manual
├── requirements.txt        # Các thư viện Python phụ thuộc
├── .gitignore              # Danh sách loại trừ file khỏi Git
├── data/                   # Chứa dữ liệu Pattern Database (pdb_corner.pkl, ...)
├── src/
│   ├── __init__.py
│   ├── rubik_state.py      # Trạng thái Rubik & 18 toán tử xoay
│   ├── heuristic.py        # Pattern Database Heuristic (Corner PDB)
│   ├── solver.py           # Thuật toán IDA* Search
│   ├── scramble.py         # Sinh chuỗi xáo trộn ngẫu nhiên hợp lệ
│   └── benchmark.py        # Đánh giá hiệu năng & so sánh Heuristic
├── tests/
│   ├── __init__.py
│   ├── test_state.py       # Test toán tử xoay và tính hợp lệ của State
│   ├── test_heuristic.py   # Test tính Admissible của Heuristic
│   └── test_solver.py      # Test IDA* solver với chuỗi scramble
└── main.py                 # Chương trình chính: Xáo trộn → Giải → In kết quả
```

---

## 🛠️ Hướng dẫn thiết lập môi trường

### 1. Kích hoạt môi trường ảo Python (`.venv`)

Môi trường ảo đã được khởi tạo trong dự án tại `.venv/`.

- **Trên Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Trên Windows (Command Prompt - cmd):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

### 2. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

### 3. Kiểm thử dự án (Unit Test)

```bash
pytest
```

---

## 📖 Hướng dẫn chi tiết sử dụng Git cho người mới bắt đầu

### 1. Git là gì và tại sao cần dùng?

**Git** là hệ thống quản lý phiên bản mã nguồn (Version Control System). Bạn hãy tưởng tượng Git giống như tính năng "Save Game" hoặc tạo "Điểm lưu" (Checkpoints) trong game:
- Mỗi khi hoàn thành 1 tính năng hoặc sửa được 1 lỗi, bạn lưu lại 1 điểm mốc (**Commit**).
- Nếu sau này thử nghiệm code mới bị lỗi hoặc "nát", bạn có thể dễ dàng quay lại bất kỳ điểm mốc nào trước đó.

### 2. Các khái niệm cốt lõi

1. **Repository (Kho lưu trữ / Repo)**: Toàn bộ thư mục dự án được Git theo dõi lịch sử.
2. **Working Directory (Thư mục làm việc)**: Các file bạn đang trực tiếp chỉnh sửa trong VS Code hoặc Notepad.
3. **Staging Area (Khu vực chuẩn bị)**: Nơi gom các file bạn muốn đưa vào lượt "lưu checkpoint" tiếp theo.
4. **Commit (Lượt lưu)**: Đóng gói các thay đổi ở Staging Area thành một mốc lịch sử vĩnh viễn, kèm thông điệp (message) mô tả bạn đã làm gì.
5. **.gitignore**: File ghi danh sách các file/thư mục Git **KHÔNG** theo dõi (ví dụ thư mục thư viện `.venv`, các file dữ liệu trung gian cực nặng `.pkl`, file tạm của hệ điều hành).

### 3. Quy trình làm việc hàng ngày với Git (Workflow 4 bước)

Mỗi khi bạn hoàn thành một phần việc (ví dụ: viết xong `rubik_state.py`), hãy thực hiện 4 bước sau:

#### Bước 1: Kiểm tra trạng thái hiện tại
```bash
git status
```
> Lệnh này cho bạn biết những file nào mới được tạo, file nào bị chỉnh sửa.

#### Bước 2: Đưa các file đã chỉnh sửa vào khu vực chuẩn bị (Staging)
```bash
# Thêm toàn bộ các file thay đổi vào staging:
git add .

# Hoặc chỉ thêm 1 file cụ thể:
git add src/rubik_state.py
```

#### Bước 3: Tạo điểm lưu (Commit)
```bash
git commit -m "Hoàn thành định nghĩa trạng thái Rubik và 18 toán tử xoay"
```
> ⚠️ **Lưu ý**: Lời nhắn sau `-m` nên viết rõ ràng, ngắn gọn về nội dung công việc vừa làm.

#### Bước 4: Xem lịch sử các điểm lưu (Commit log)
```bash
git log --oneline
```
> Lệnh này giúp bạn thấy danh sách tất cả các điểm mốc đã lưu từ trước đến nay.

---

## 💡 Mẹo nhỏ & Lưu ý cho người mới
- **Đừng sợ làm hỏng code**: Vì đã có Git commit các mốc làm việc tốt, bạn có thể thử nghiệm thoải mái.
- **Commit thường xuyên**: Nên commit sau mỗi tính năng nhỏ hoặc bài test vượt qua, không nên tích tụ cả tuần mới commit 1 lần.
- **Kiểm tra kỹ trước khi add**: Dùng `git status` trước khi `git add .` để chắc chắn không add nhầm file rác vào Git.
