# Kế hoạch cập nhật v2 — Rubik AI Solver (sau khi đọc `index.html` và `app.py`)

> **Thay thế** Giai đoạn 4–6 của `ke_hoach_sua_code_rubik_ai.md` (v1). Giai đoạn 1–3 của v1 bạn đã làm xong; mục 1 bên dưới ghi lại những gì mình đã **chạy kiểm chứng** trên code mới của bạn.
> Kèm theo hai file đã chạy thử: `web_update/static/player.js` (bộ điều khiển phát/dừng/tua) và `web_update/tests/test_player.mjs` (10 kiểm tra, đạt cả 10 bằng Node 22).
>
> Quy ước nguồn: **[CHẠY]** = mình đã chạy; **[ĐỌC]** = chỉ đọc code; **[CHƯA CHẠY]** = viết sẵn nhưng môi trường của mình không chạy được (ví dụ không có trình duyệt hoặc FastAPI).

---

## 1. Trạng thái hiện tại

### 1.1. Giai đoạn 1–3 của v1: đã hoàn thành và đúng

| Hạng mục | Kết quả kiểm chứng |
|---|---|
| Bảng nước đi U/D | Giống hệt bản mình đã đối chiếu với khối vật lý độc lập [CHẠY] |
| Số nút benchmark (độ sâu 5, 8, 10) | 12/12 dòng trong `bao_cao_ket_qua_thuc_thi_rubik_ai.md` **khớp Bảng B** của mình [CHẠY] |
| Ví dụ CLI trong báo cáo kết quả | Tái hiện đúng: v1 **6 875** nút, v2 **213** nút, lời giải `R' D B2 D' U'` [CHẠY] |
| AI giải từ trạng thái, không đảo scramble | 150 scramble có nước thừa: 117 ca lời giải **ngắn hơn** scramble [CHẠY] |
| `solve_ex`, `preload_pdb`, `scramble` dùng `random.Random` | Đã đúng như kế hoạch [ĐỌC] |

### 1.2. Web demo: những gì đã đúng

| Kiểm tra | Kết quả |
|---|---|
| `/solve` chỉ dùng **trạng thái** (`req.state`) | Đúng. `currentScrambleMoves` ở frontend chỉ dùng để **vẽ lại** hình 3D, không gửi cho solver [ĐỌC] |
| `MOVE_MAP` (chiều quay 18 nước đi) so với chuẩn WCA | **18/18 khớp** (mình đọc trực tiếp từ `index.html` và so với mô hình khối độc lập) [CHẠY] |
| Quy trình đầy đủ: backend giải từ state → áp scramble + lời giải bằng đúng `MOVE_MAP` | **160/160** ca về 6 mặt đồng màu; 3 phản ví dụ của lỗi U/D cũ cũng về đích [CHẠY] |
| `app.py` gọi `preload_pdb()` khi khởi động | Đúng [ĐỌC] |

Nói cách khác: **mô hình backend và hình 3D hiện đã nhất quán** (trước khi sửa U/D thì không, nhưng lỗi ẩn vì lời giải gần như luôn là nghịch đảo scramble).

### 1.3. Web demo: những vấn đề còn lại

| Mã | Vấn đề | Vị trí | Mức |
|---|---|---|---|
| **W1** | `app.py` import `solve_with_heuristic` từ `src.benchmark` → web phụ thuộc module benchmark (và kéo theo đoạn cấu hình stdout trong đó). Nên gọi thẳng `solve_ex` | `app.py` | P1 |
| **W2** | Timeout và "không có lời giải" không phân biệt; `index.html` luôn báo **"Heuristic thô không giải được"** kể cả khi người dùng đang chọn **v2** | `app.py`, `index.html` | P1 |
| **W3** | Số bước xáo mặc định **ngẫu nhiên 5–12** (`Math.random()*8+5`). v2 ở 10 bước đã timeout 1/5 ca [BC], nên khi demo có xác suất cao rơi vào ca timeout (11–12 bước chưa đo) | `index.html` | P1 |
| **W4** | Sau khi giải xong, `currentCubeState = null; isScrambled = false` → **không xem lại được lời giải**; không thể dừng/tua | `index.html` | P1 (tính năng bạn yêu cầu) |
| **W5** | URL cứng `http://127.0.0.1:8000`; mở bằng `localhost` hoặc cổng khác sẽ phụ thuộc CORS | `index.html` | P2 |
| **W6** | `/solve` không kiểm tra hợp lệ trạng thái (độ dài, giá trị, parity). Ngoài ra khối `except Exception` sẽ biến mọi `HTTPException` thành 500 | `app.py` | P2 |
| **W7** | Phụ thuộc CDN (Three.js, Google Fonts): **cần Internet khi demo** | `index.html` | P2 (rủi ro ngày báo cáo) |
| **W8** | `rounded: true` không phải thuộc tính của `MeshPhongMaterial` (bị bỏ qua); 3 dòng `console.log` thừa | `index.html` | P2 |

Ghi chú: báo cáo kết quả có câu "render … với bóng đổ", nhưng code không bật đổ bóng (`renderer.shadowMap` và `castShadow` đều chưa có). Xem mục 6.

---

## 2. Tổng quan các giai đoạn còn lại

| GĐ | Nội dung | Giải quyết | Thời gian |
|---|---|---|---|
| **4** | Sửa backend web | W1, W2 (phần backend), W6 | ~30 phút |
| **5** | Sửa nhỏ `index.html` | W2 (phần thông báo), W3, W5, W8, (W7 tùy chọn) | ~30 phút |
| **6** | **Tạm dừng và tua lại từng bước** (tính năng mới) | W4 | 1–1,5 giờ |
| **7** | Test cho web | Chặn tái phát | ~30 phút |
| **8** | Cập nhật báo cáo, slide | Số liệu và câu chữ | ~1 giờ |

Mỗi giai đoạn một commit. Không giai đoạn nào đụng vào `src/` (đã chốt).

---

## Giai đoạn 4 — Backend web (W1, W2, W6)

Thay phần liên quan trong `web/app.py`:

```python
from src.rubik_state import State, is_valid_parity
from src.scramble import scramble as scramble_func
from src.solver import solve_ex                    # W1: gọi thẳng solver, không qua benchmark
import src.heuristic as heuristic_module
```

(Xóa dòng `from src.benchmark import solve_with_heuristic`.)

Thêm hàm kiểm tra và sửa `/solve`:

```python
def _to_state(m: "StateModel") -> State:
    s = State(tuple(m.corner_perm), tuple(m.corner_orient),
              tuple(m.edge_perm), tuple(m.edge_orient))
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

@app.post("/solve")
def post_solve(req: SolveRequest):
    state = _to_state(req.state)                    # W6: ngoài try để giữ nguyên mã 422
    if req.heuristic not in ("v1", "v2"):
        raise HTTPException(status_code=422, detail="heuristic phải là 'v1' hoặc 'v2'")
    h_func = (heuristic_module.get_heuristic_v2 if req.heuristic == "v2"
              else heuristic_module.get_heuristic_v1)
    try:
        r = solve_ex(state, heuristic=h_func, max_moves=25)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "moves": r.path,                 # None nếu TIMEOUT / NO_SOLUTION (giữ tương thích frontend)
        "nodes_opened": r.nodes,
        "time_ms": round(r.elapsed * 1000, 2),
        "heuristic_used": req.heuristic,
        "status": r.status,              # W2: "OK" | "TIMEOUT" | "NO_SOLUTION"
    }
```

`/scramble` giữ nguyên (có thể thêm tham số `seed: int | None = None` để demo lặp lại được; không bắt buộc).

**Tiêu chí đạt:** `uvicorn` khởi động được; `POST /solve` với state hợp lệ trả `status: "OK"`; với `corner_perm` có số trùng (ví dụ `[0,0,2,3,4,5,6,7]`) trả **422** (không phải 500). [CHƯA CHẠY: môi trường của mình không có FastAPI]

---

## Giai đoạn 5 — Sửa nhỏ `index.html`

Làm theo đúng thứ tự dưới đây (mỗi mục là một thay thế nhỏ, dễ kiểm tra).

**5.1 (W5) URL tương đối.** Đổi hai chỗ gọi API:

```js
// trước: fetch(`http://127.0.0.1:8000/scramble?n=${nMoves}`)
const res = await fetch(`/scramble?n=${nMoves}`);
// trước: fetch('http://127.0.0.1:8000/solve', {...})
const res = await fetch('/solve', { /* giữ nguyên method, headers, body */ });
```

Trang được phục vụ từ chính server (`GET /`), nên đường dẫn tương đối chạy ở mọi host/cổng. Lưu ý: mở file `index.html` trực tiếp bằng `file://` sẽ không còn gọi được API; luôn mở qua `http://127.0.0.1:8000`.

**5.2 (W3) Số bước xáo mặc định hợp lý.**

```js
// trước: inpScrambleMoves.value = Math.floor(Math.random() * 8) + 5;   // 5..12
inpScrambleMoves.value = Math.floor(Math.random() * 4) + 5;            // 5..8
```

Và cập nhật cảnh báo để cũng cảnh báo cho v2 (số liệu từ benchmark: v2 giải 4/5 ca ở 10 bước):

```html
<div id="warn-heuristic" style="display:none; color:#fbbf24; font-size:12px; line-height:1.4;"></div>
```

```js
function checkWarning() {
  const n = parseInt(inpScrambleMoves.value) || 0;
  const v = selHeuristic.value;
  let msg = '';
  if (v === 'v1' && n > 8)  msg = '⚠️ Heuristic thô thường timeout với scramble > 8 bước. Hãy thử v2 hoặc giảm số bước.';
  if (v === 'v2' && n > 9)  msg = '⚠️ Từ ~10 bước, ngay cả v2 (Corner PDB) có thể timeout (đo được: 4/5 ca 10 bước giải được).';
  warnHeuristic.textContent = msg;
  warnHeuristic.style.display = msg ? 'block' : 'none';
}
```

**5.3 (W2, phần frontend) Thông báo timeout đúng theo heuristic.** Dùng trong trình xử lý nút Giải (xem mã đầy đủ ở Giai đoạn 6.4):

```js
function failMessage(status, heuristic) {
  if (status !== 'TIMEOUT') return 'Không tìm thấy lời giải trong giới hạn độ sâu.';
  return heuristic === 'v1'
    ? 'TIMEOUT: heuristic thô không giải được trong 300 000 nút. Thử v2 hoặc giảm số bước xáo.'
    : 'TIMEOUT: ngay cả Corner PDB cũng vượt 300 000 nút với ca này (scramble quá sâu). Giảm số bước xáo.';
}
```

**5.4 (W8) Dọn nhỏ.** Bỏ `rounded: true` trong `createMaterial`, bỏ ba dòng `console.log` ("Cube added", "currentCubeState", "Rendered").

**5.5 (W7, tùy chọn nhưng khuyến nghị cho ngày báo cáo) Chạy được khi mất mạng.**

1. Tải hai file về máy (khi còn mạng):
   - `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` → `web/static/vendor/three.module.js`
   - `https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js` → `web/static/vendor/addons/controls/OrbitControls.js`
2. Đổi `importmap`:

```html
<script type="importmap">
{ "imports": { "three": "/static/vendor/three.module.js",
               "three/addons/": "/static/vendor/addons/" } }
</script>
```

3. Phông Inter đã có phông dự phòng `sans-serif`, nên mất mạng chỉ đổi kiểu chữ, không vỡ giao diện.

**Tiêu chí đạt GĐ5:** bật server, mở `http://127.0.0.1:8000` bằng cả `127.0.0.1` lẫn `localhost`: xáo trộn và giải đều chạy. (Nếu làm 5.5: tắt Wi-Fi, tải lại trang, khối 3D vẫn hiện.) [CHƯA CHẠY]

---

## Giai đoạn 6 — Tạm dừng và tua lại từng bước (W4)

### 6.1. Yêu cầu

| Chức năng | Hành vi |
|---|---|
| **Phát / Tạm dừng** | Nhấn tạm dừng: khối **hoàn tất nước đang xoay rồi dừng hẳn** (không dừng giữa chừng một nước) |
| **Tiến 1 bước / Lùi 1 bước** | Có hiệu ứng xoay; lùi = xoay **nước nghịch đảo** của nước vừa đi |
| **Về đầu / Về cuối** | Nhảy tức thì (không hiệu ứng) |
| **Thanh trượt** | Kéo tới "sau k nước", tức thì |
| **Danh sách nước (chip)** | Bấm vào nước thứ k để xem khối **sau nước k** |
| **Tốc độ** | 0,5× / 1× / 2× / 4× |
| **Phím tắt** | `Space` phát/dừng, `←` `→` lùi/tiến, `Home` `End` đầu/cuối |
| **Xác minh** | Khi tới cuối: tự kiểm 6 mặt đồng màu và hiển thị "✔ 6 mặt đồng màu" |

Lời giải được **giữ lại** sau khi giải xong, nên có thể xem lại thoải mái cho tới lần "Xáo trộn" tiếp theo.

### 6.2. Thiết kế

- `player.js` (đã gửi kèm) là **module độc lập**, không phụ thuộc Three.js. Nó nhận hai hàm từ `index.html`: `animate(move, ms)` (xoay có hiệu ứng) và `applyInstant(move)` (xoay tức thì), cả hai **đã có sẵn** trong `index.html` (`animateMoveAsync`, `applyMoveInstant`).
- Chỉ có **một thao tác chạy tại một thời điểm** (khóa bận). Bấm dồn không làm nhảy bước; tua khi đang bận được xếp hàng và chạy ngay sau khi nước hiện tại xong.
- Vòng phát có mã định danh nên "Dừng rồi Phát ngay" không tạo hai vòng chạy chồng.
- `MOVE_MAP` đã có đủ 18 khóa gồm cả nước nghịch đảo, nên lùi chỉ là `animate(inverseMove(m))`.

### 6.3. Thêm vào `index.html`

**(a) CSS** (thêm cuối khối `<style>`; đồng thời thêm hai thuộc tính cho `#control-panel`):

```css
#control-panel { max-height: calc(100vh - 80px); overflow-y: auto; }   /* thêm vào quy tắc có sẵn */

#player { display: none; flex-direction: column; gap: 10px; }
.pl-head { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; }
.pl-buttons { display: flex; gap: 6px; }
.pl-buttons .btn { flex: 1; padding: 10px 0; }
#pl-slider { width: 100%; }
#pl-chips { display: flex; flex-wrap: wrap; gap: 4px; max-height: 84px; overflow-y: auto; }
.chip { font: 600 12px 'Inter', sans-serif; color: var(--text); background: rgba(255,255,255,.08);
        border: 1px solid var(--border); border-radius: 8px; padding: 4px 8px; cursor: pointer; }
.chip.done { background: rgba(59,130,246,.35); }
.chip.current { outline: 2px solid #fbbf24; }
```

**(b) HTML**: chèn ngay **sau** khối `<div class="stats">…</div>` trong `#control-panel`, và thêm một dòng "Xác minh" vào trong `.stats`:

```html
<!-- thêm vào trong <div class="stats"> -->
<div class="stat-row"><span>Xác minh:</span> <span class="stat-val" id="stat-verify">-</span></div>

<!-- thêm sau </div> của .stats -->
<div id="player">
  <div class="pl-head"><span id="pl-label">Bước 0/0</span><span id="pl-move"></span></div>
  <input type="range" id="pl-slider" min="0" max="0" value="0">
  <div class="pl-buttons">
    <button class="btn" id="pl-first" title="Về đầu (Home)">⏮</button>
    <button class="btn" id="pl-prev"  title="Lùi 1 bước (←)">◀</button>
    <button class="btn btn-primary" id="pl-play" title="Phát / Tạm dừng (Space)">▶</button>
    <button class="btn" id="pl-next"  title="Tiến 1 bước (→)">▶</button>
    <button class="btn" id="pl-last"  title="Về cuối (End)">⏭</button>
  </div>
  <select id="pl-speed">
    <option value="700">Tốc độ 0,5×</option>
    <option value="350" selected>Tốc độ 1×</option>
    <option value="175">Tốc độ 2×</option>
    <option value="80">Tốc độ 4×</option>
  </select>
  <div id="pl-chips"></div>
</div>
```

**(c) JS: import** — thêm vào đầu `<script type="module">`, cạnh hai dòng import hiện có:

```js
import { createPlayer } from '/static/player.js';
```

**(d) JS: hàm xác minh khối đã về đích** (đặt sau phần tạo 27 khối, dùng `cubies`, `COLORS`):

```js
// Thứ tự trùng thứ tự vật liệu: 0:x+ 1:x- 2:y+ 3:y- 4:z+ 5:z-
const FACE_NORMALS = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
function isCubeSolved() {
  const v = new THREE.Vector3(), home = new THREE.Vector3(), nrm = new THREE.Vector3();
  return cubies.every(c => {
    home.set(c.userData.initX, c.userData.initY, c.userData.initZ);
    if (c.position.distanceTo(home) > 1e-3) return false;
    return FACE_NORMALS.every((n, i) => {
      if (c.material[i].color.getHex() === COLORS.I) return true;   // mặt trong, bỏ qua
      nrm.set(n[0], n[1], n[2]);
      v.copy(nrm).applyQuaternion(c.quaternion);
      return v.distanceTo(nrm) < 1e-3;                              // mặt màu phải quay về hướng ban đầu
    });
  });
}
window.__isCubeSolved = isCubeSolved;   // tiện kiểm tra trong DevTools
```

**(e) JS: trạng thái giai đoạn và nối `player`** (đặt sau phần "STATE MANAGEMENT", trước các trình xử lý nút):

```js
let phase = 'idle';   // 'idle' | 'scrambled' | 'solving' | 'review'

const plBox = document.getElementById('player');
const plLabel = document.getElementById('pl-label'), plMove = document.getElementById('pl-move');
const plSlider = document.getElementById('pl-slider'), plChips = document.getElementById('pl-chips');
const plFirst = document.getElementById('pl-first'), plPrev = document.getElementById('pl-prev');
const plPlay = document.getElementById('pl-play'), plNext = document.getElementById('pl-next');
const plLast = document.getElementById('pl-last'), plSpeed = document.getElementById('pl-speed');
const statVerify = document.getElementById('stat-verify');

let chipsFor = null;
function buildChips(moves) {
  plChips.innerHTML = '';
  moves.forEach((m, i) => {
    const b = document.createElement('button');
    b.className = 'chip'; b.textContent = m; b.title = `Xem khối sau bước ${i + 1}`;
    b.addEventListener('click', () => player.seek(i + 1));
    plChips.appendChild(b);
  });
}

function renderPlayerUI(s) {
  if (chipsFor !== s.moves) { chipsFor = s.moves; buildChips(s.moves); }
  plLabel.textContent = `Bước ${s.index}/${s.total}`;
  plMove.textContent = s.last ? `Vừa xoay: ${s.last}` : 'Trạng thái xáo trộn';
  plSlider.max = s.total; plSlider.value = s.index;
  plPlay.textContent = s.mode === 'playing' ? '⏸' : '▶';
  plFirst.disabled = plPrev.disabled = s.busy || s.index === 0;
  plNext.disabled = plLast.disabled = s.busy || s.index === s.total;
  [...plChips.children].forEach((c, i) => {
    c.classList.toggle('done', i < s.index);
    c.classList.toggle('current', i === s.index - 1);
  });
  if (phase === 'review') btnScramble.disabled = s.busy || s.mode === 'playing';
  statVerify.textContent = (s.total > 0 && s.index === s.total && !s.busy)
    ? (isCubeSolved() ? '✔ 6 mặt đồng màu' : '✖ chưa về đích') : '-';
}

const player = createPlayer({
  animate: (m, ms) => animateMoveAsync(m, ms),
  applyInstant: (m) => applyMoveInstant(m),
  onChange: renderPlayerUI,
});

async function togglePlay() {
  const s = player.state;
  if (s.mode === 'playing') return player.pause();
  if (s.index === s.total) await player.seek(0);      // ở cuối: phát lại từ đầu
  player.play();
}
plPlay.onclick = togglePlay;
plFirst.onclick = () => player.seek(0);
plLast.onclick  = () => player.seek(player.state.total);
plPrev.onclick  = () => player.stepBack();
plNext.onclick  = () => player.stepForward();
plSlider.oninput = () => player.seek(parseInt(plSlider.value));
plSpeed.onchange = () => player.setSpeed(parseInt(plSpeed.value));

document.addEventListener('keydown', (e) => {
  if (phase !== 'review') return;
  const tag = e.target.tagName;
  if (tag === 'INPUT' || tag === 'SELECT') return;
  if (e.key === ' ' && tag === 'BUTTON') return;      // nút tự xử lý Space
  const act = { ' ': togglePlay, ArrowRight: () => player.stepForward(), ArrowLeft: () => player.stepBack(),
                Home: () => player.seek(0), End: () => player.seek(player.state.total) }[e.key];
  if (act) { e.preventDefault(); act(); }
});
```

### 6.4. Sửa hai trình xử lý nút hiện có

**Nút Xáo trộn** — thêm ở **đầu** hàm (ngay sau `setUIDisabled(true);`) và ở **cuối** (khi thành công):

```js
// đầu hàm, sau setUIDisabled(true):
player.reset(); plBox.style.display = 'none'; statVerify.textContent = '-';

// cuối khối try, thay cho các dòng gán sau khi animate xong:
currentCubeState = data.state;
currentScrambleMoves = data.moves;
isScrambled = true;
phase = 'scrambled';
setUIDisabled(false);
```

**Nút Giải** — thay **toàn bộ** trình xử lý bằng:

```js
btnSolve.addEventListener('click', async () => {
  if (phase !== 'scrambled' || !currentCubeState) return alert("Vui lòng xáo trộn khối Rubik trước!");
  phase = 'solving';
  setUIDisabled(true);
  banner.style.display = 'block';
  sContainer.style.display = 'block';
  pContainer.style.display = 'none';
  statusText.innerText = "AI ĐANG TÍNH TOÁN LỜI GIẢI...";
  const heuristic = selHeuristic.value;

  try {
    const res = await fetch('/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state: currentCubeState, heuristic })   // chỉ gửi TRẠNG THÁI
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    banner.style.display = 'none';

    if (data.moves === null) {
      alert(failMessage(data.status, heuristic));
      renderCubeFromState();                       // khôi phục hình 3D như trước khi giải
      phase = 'scrambled'; setUIDisabled(false);
      return;
    }

    document.getElementById('stat-len').innerText = data.moves.length + " bước";
    document.getElementById('stat-node').innerText = data.nodes_opened.toLocaleString();
    document.getElementById('stat-time').innerText = data.time_ms + " ms";

    plBox.style.display = 'flex';
    player.load(data.moves);                       // giữ lại lời giải để dừng/tua
    phase = 'review';
    setUIDisabled(false);
    btnSolve.disabled = true;                      // đã giải; muốn thử lại hãy Xáo trộn
    player.play();                                 // tự phát; bấm ⏸ để dừng

  } catch (err) {
    banner.style.display = 'none';
    alert("Lỗi gọi API Solve! " + err);
    phase = 'scrambled'; setUIDisabled(false);
  }
});
```

(`failMessage` ở mục 5.3. Các biến `currentCubeState`, `currentScrambleMoves`, `isScrambled` **không còn bị xóa** sau khi giải; chúng chỉ bị đặt lại ở lượt Xáo trộn kế tiếp.)

### 6.5. Kiểm tra logic bằng Node (đã chạy) [CHẠY]

```bash
node web/tests/test_player.mjs        # kỳ vọng: "TẤT CẢ ĐẠT: 10 kiểm tra"
```

10 kiểm tra gồm: phát hết đúng thứ tự; tạm dừng giữa chừng rồi đứng yên; lùi từng bước về 0; tiến từng bước tới cuối; nhảy tức thì (xuôi/ngược/vượt biên); dừng rồi phát ngay không nhân đôi; tua khi đang bận được xếp hàng; bấm dồn không nhảy bước; nạp lời giải mới đặt về 0; nghịch đảo nước đi. Mỗi lần kiểm tra đều đối chiếu "khối trừu tượng" (ngăn xếp các nước, triệt tiêu theo nghịch đảo) với đúng `moves[0..index)`, và xác nhận **không bao giờ có hai hiệu ứng chồng nhau**.

### 6.6. Kiểm tra bằng tay trong trình duyệt [CHƯA CHẠY]

Mình không có trình duyệt, nên phần nhìn thấy cần bạn xác nhận:

1. Xáo 6 bước → Giải: lời giải tự phát. Bấm **⏸** ở khoảng bước 3: khối **dừng hẳn sau khi xong nước đang xoay**, nhãn hiện "Bước 3/6".
2. Bấm **◀**: khối quay về trạng thái ngay sau bước 2 (nước vừa xoay đảo chiều). Bấm **▶** (tiến): quay lại như cũ.
3. Kéo thanh trượt về **0**: khối trùng đúng hình **ngay sau lúc xáo trộn**. Kéo về cuối: hiện **"✔ 6 mặt đồng màu"**.
4. Bấm một chip bất kỳ: khối nhảy tức thì đến trạng thái sau nước đó.
5. `Space`, `←`, `→`, `Home`, `End` hoạt động; gõ vào ô "Số bước xáo trộn" không kích hoạt phím tắt.
6. Ở cuối, bấm **▶**: phát lại từ đầu. Bấm **Xáo trộn** khi đang xem: bảng điều khiển ẩn, khối reset, không lỗi.
7. Lặp lại bước 1–3 với ít nhất 3 lần xáo có **U hoặc D** (kiểm hướng quay).
8. Mở DevTools, gõ `__isCubeSolved()` sau khi giải: phải ra `true`.

Giới hạn đã biết: nếu bạn chuyển sang tab khác khi đang phát, trình duyệt ngừng `requestAnimationFrame` nên hiệu ứng tạm dừng và tiếp tục khi quay lại tab (không gây sai trạng thái).

---

## Giai đoạn 7 — Test cho web

**7.1. Test API** (`tests/test_web_api.py`) [CHƯA CHẠY: cần `pip install httpx` để dùng `TestClient`]:

```python
from fastapi.testclient import TestClient
from src.rubik_state import GOAL_STATE, apply_move
from web.app import app

client = TestClient(app)

def _json(st):
    return {"corner_perm": list(st.corner_perm), "corner_orient": list(st.corner_orient),
            "edge_perm": list(st.edge_perm), "edge_orient": list(st.edge_orient)}

def test_solve_uses_state_only():
    word = "F2 B2 F2 F2 B' R D2 B'".split()          # có nước thừa
    st = GOAL_STATE
    for m in word:
        st = apply_move(st, m)
    r = client.post("/solve", json={"state": _json(st), "heuristic": "v2"})
    d = r.json()
    assert r.status_code == 200 and d["status"] == "OK"
    assert len(d["moves"]) < len(word)                # không thể là "đảo ngược scramble"
    for m in d["moves"]:
        st = apply_move(st, m)
    assert st == GOAL_STATE

def test_invalid_state_is_422():
    bad = _json(GOAL_STATE); bad["corner_perm"][1] = 0   # trùng số
    r = client.post("/solve", json={"state": bad, "heuristic": "v2"})
    assert r.status_code == 422

def test_unknown_heuristic_is_422():
    r = client.post("/solve", json={"state": _json(GOAL_STATE), "heuristic": "v9"})
    assert r.status_code == 422
```

**7.2. Test logic player:** `node web/tests/test_player.mjs` (đã đạt). Có thể thêm vào script chạy kiểm thử của nhóm.

**7.3. Test độc lập chứng minh AI giải từ trạng thái** (đã đề xuất lần trước, `tests/test_independent_solve.py`): giữ lại; kết hợp với `test_solve_uses_state_only` ở trên là đủ bằng chứng cho vấn đáp.

---

## Giai đoạn 8 — Báo cáo, slide

### 8.1. Báo cáo kết quả (`bao_cao_ket_qua_thuc_thi_rubik_ai.md`) cần sửa

| # | Chỗ | Vấn đề | Cách sửa |
|---|---|---|---|
| R1 | Mục 2, "Nhận xét" | "Lời giải … chính là chuỗi nghịch đảo tối ưu hoàn hảo" dễ gợi ý AI đảo ngược scramble. Hơn nữa lời giải `R' D B2 D' U'` **không** trùng chuỗi nghịch đảo `R' D B2 U' D'` (khác thứ tự U', D') | "AI chỉ nhận trạng thái khối; lời giải trùng nghịch đảo scramble tới hoán đổi hai mặt đối nhau, vì với scramble ngắn lời giải tối ưu thường như vậy. Với scramble có nước thừa, AI tìm được lời giải ngắn hơn scramble (117/150 ca thử)." |
| R2 | Mục 5.1 | "Giảm trung bình 29,7 lần" là **trung bình các tỉ lệ**; thời gian "14,1 lần" là **tỉ lệ hai trung bình** → hai con số không cùng cách tính. Tỉ lệ hai trung bình của số nút là 3 242 / 329 ≈ **9,9 lần** | Dùng một cách tính cho cả hai và ghi rõ |
| R3 | Mục 7, kết luận | "Cắt tỉa hiệu quả hơn 95–98% không gian tìm kiếm" không đúng ở độ sâu 5 (mỗi seed giảm 77%–99%, trung bình ≈ 90%) | Sửa thành khoảng giảm đo được, hoặc bỏ |
| R4 | Mục 4, các dòng độ sâu 8 | Thời gian có số tròn bất thường (4.1500, 4.0800, 0.3800, 0.0850) và `benchmark.py` chỉ chạy độ sâu 5, 10, 15 | Thêm 8 vào `scramble_depths` (và chạy seed 800–801 hoặc 800–804) rồi dán lại bảng chạy thật |
| R5 | Mục 6 | "render … với bóng đổ": code không bật đổ bóng | Bỏ cụm "bóng đổ", hoặc bật `renderer.shadowMap.enabled`, `dirLight.castShadow` và `castShadow/receiveShadow` cho cubie |
| R6 | Mục 6, "100% chính xác" | Có thể dẫn chứng bằng hàm `isCubeSolved()` (GĐ6) và kết quả mô phỏng 160/160 | Thêm một câu nêu cách kiểm |
| R7 | Mục 1 điểm 5 | "Trục và góc quay … khớp 1:1": **đúng**, đã đối chiếu 18/18 | Giữ nguyên; có thể ghi thêm cách kiểm |

### 8.2. Slide (`ke_hoach_slide_rubik_ai.md`)

- **Slide 8 (demo):** thêm 20–30 giây cho đoạn tạm dừng/tua: *"bấm tạm dừng ở bước 3, lùi một bước, rồi phát tiếp"*. Giảm bớt thời gian ở đoạn demo v1 timeout nếu cần giữ 2 phút. Sửa kịch bản: số bước xáo mặc định bây giờ 5–8.
- **Ảnh chụp:** nên chụp thêm ảnh giao diện có thanh điều khiển (ảnh `demo-player.png`), dùng cho slide dự phòng.
- **Q&A:** thêm câu mới:
  - **Q16. "AI có đảo ngược chuỗi xáo trộn không?"** → *Không. `/solve` chỉ nhận trạng thái khối. Nhóm kiểm bằng scramble có nước thừa (ví dụ `F2 B2 F2 F2 B' R D2 B'`, 8 nước) và AI giải trong 5 nước; nếu chỉ đảo ngược thì không thể ngắn hơn.*
  - **Q17. "Tạm dừng/tua hoạt động thế nào?"** → *Lời giải được giữ lại; lùi một bước là xoay nước nghịch đảo; nhảy tới bước bất kỳ áp dụng tức thì.*
- **Q12** (kiểm chứng trên khối thật) dùng phiên bản "đã sửa": đối chiếu số trạng thái theo độ sâu `1, 18, 243, 3 240, 43 239, 574 908` và bậc `R U` = 105.

---

## 9. Checklist tổng cuối

- [ ] GĐ4: `uvicorn` chạy; `/solve` trả `status`; trạng thái sai → 422
- [ ] GĐ5: URL tương đối; mặc định 5–8 bước; thông báo timeout đúng theo heuristic; (tùy chọn) vendor offline
- [ ] GĐ6: copy `web_update/static/player.js` → `web/static/player.js`; chèn CSS/HTML/JS theo 6.3–6.4; qua 8 mục kiểm tay (6.6)
- [ ] GĐ7: `pytest` (kèm 3 test API) và `node web/tests/test_player.mjs` đều đạt
- [ ] GĐ8: sửa R1–R7; cập nhật slide 8, thêm Q16–Q17
- [ ] Quay **video demo mới** có đoạn tạm dừng/tua để làm phương án dự phòng
- [ ] Chạy thử lại toàn bộ ở đúng máy và mạng của buổi báo cáo

## 10. Rủi ro

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| Hai thao tác xoay chồng nhau làm lệch khối | Khối hiện sai sau khi bấm dồn | `player.js` đã khóa bận và có test; nếu vẫn lệch, dùng `__isCubeSolved()` và nút Về đầu/Về cuối để đối chiếu |
| Panel quá cao trên màn hình nhỏ | Thanh điều khiển bị cắt | Đã thêm `max-height` và `overflow-y: auto` ở 6.3(a) |
| Quên đặt `player.js` vào `web/static/` | Console báo 404, trang không chạy phần giải | Kiểm tra đường dẫn `/static/player.js` mở được trong trình duyệt |
| Mở bằng `file://` | Lỗi gọi API sau khi đổi sang URL tương đối | Luôn mở `http://127.0.0.1:8000` |
| Muốn quay về | | `git checkout` nhánh trước đó; `player.js` là file mới nên không ảnh hưởng gì nếu bỏ |
