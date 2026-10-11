// player.js - Bộ điều khiển phát / tạm dừng / tua từng bước cho lời giải Rubik.
// Không phụ thuộc Three.js: nhận vào hai hàm do index.html cung cấp:
//   animate(moveStr, durationMs) -> Promise   (xoay có hiệu ứng)
//   applyInstant(moveStr)                      (xoay tức thì, dùng khi nhảy tới bước bất kỳ)

export function inverseMove(m) {
  if (m.endsWith("2")) return m;
  return m.endsWith("'") ? m[0] : m + "'";
}

export function createPlayer({ animate, applyInstant, onChange, gapMs = 120 }) {
  let moves = [];
  let index = 0;            // số nước đã áp dụng lên khối (0..moves.length)
  let mode = "paused";      // "playing" | "paused"
  let busy = false;         // đang có đúng 1 thao tác chạy
  let speedMs = 350;
  let loopId = 0;           // chống hai vòng phát chạy chồng nhau
  let pendingSeek = null;   // yêu cầu tua đến khi đang bận

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const emit = () =>
    onChange && onChange({
      index, total: moves.length, mode, busy,
      last: index > 0 ? moves[index - 1] : null,
      next: index < moves.length ? moves[index] : null,
      moves,
    });

  // Mọi thao tác thay đổi khối đều đi qua run(): tại một thời điểm chỉ có một thao tác.
  async function run(fn) {
    if (busy) return false;
    busy = true; emit();
    try { await fn(); }
    finally {
      busy = false; emit();
      if (pendingSeek !== null) {
        const k = pendingSeek; pendingSeek = null;
        queueMicrotask(() => seek(k));
      }
    }
    return true;
  }

  async function forwardOne() {
    if (index >= moves.length) return;
    await animate(moves[index], speedMs);
    index++;
  }
  async function backOne() {
    if (index <= 0) return;
    await animate(inverseMove(moves[index - 1]), speedMs);
    index--;
  }

  async function play() {
    if (mode === "playing" || index >= moves.length) return;
    const myLoop = ++loopId;
    mode = "playing"; emit();
    while (mode === "playing" && myLoop === loopId && index < moves.length) {
      const ran = await run(forwardOne);
      if (!ran) { await sleep(20); continue; }
      if (mode !== "playing" || myLoop !== loopId) break;
      await sleep(gapMs);
    }
    if (myLoop === loopId && mode === "playing") mode = "paused";
    emit();
  }

  function pause() {
    if (mode === "playing") { mode = "paused"; loopId++; emit(); }
  }

  async function stepForward() { pause(); return run(forwardOne); }
  async function stepBack()    { pause(); return run(backOne); }

  // Nhảy tức thì tới "sau k nước" (k = 0..total), không hiệu ứng.
  async function seek(k) {
    pause();
    k = Math.max(0, Math.min(moves.length, k));
    if (busy) { pendingSeek = k; return false; }
    return run(async () => {
      while (index < k) { applyInstant(moves[index]); index++; }
      while (index > k) { applyInstant(inverseMove(moves[index - 1])); index--; }
    });
  }

  function load(newMoves) { loopId++; moves = newMoves.slice(); index = 0; mode = "paused"; pendingSeek = null; emit(); }
  function reset() { load([]); }
  function setSpeed(ms) { speedMs = ms; }

  return { load, reset, play, pause, stepForward, stepBack, seek, setSpeed,
           get state() { return { index, total: moves.length, mode, busy }; } };
}
