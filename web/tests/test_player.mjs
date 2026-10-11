import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
// Nạp đúng file web/static/player.js (ES module) mà không cần package.json "type": "module"
const here = path.dirname(fileURLToPath(import.meta.url));
const code = fs.readFileSync(path.join(here, process.env.PLAYER_JS || '../static/player.js'), 'utf8');
const { createPlayer, inverseMove } = await import('data:text/javascript;charset=utf-8,' + encodeURIComponent(code));
import assert from 'node:assert/strict';

// Khối "trừu tượng": ngăn xếp các nước, nước đi gặp nghịch đảo ở đỉnh thì triệt tiêu
function makeCube() {
  const stack = []; let concurrent = 0, maxConcurrent = 0; const log = [];
  const apply = (m) => {
    if (stack.length && stack[stack.length - 1] === inverseMove(m)) stack.pop(); else stack.push(m);
  };
  return {
    stack, log, get maxConcurrent() { return maxConcurrent; },
    animate: async (m) => { concurrent++; maxConcurrent = Math.max(maxConcurrent, concurrent);
      log.push(['anim', m]); await new Promise(r => setTimeout(r, 8)); apply(m); concurrent--; },
    applyInstant: (m) => { log.push(['inst', m]); apply(m); },
  };
}
const MOVES = ["R", "U'", "F2", "D", "L'", "B"];
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const mk = () => { const c = makeCube(); const p = createPlayer({ animate: c.animate, applyInstant: c.applyInstant, gapMs: 3 }); p.load(MOVES); return [c, p]; };
let n = 0; const ok = (name) => console.log('  ok', ++n, name);

// 1. Phát hết: đúng thứ tự, mỗi nước đúng một lần
{ const [c, p] = mk(); await p.play(); await sleep(20);
  assert.deepEqual(c.log.map(x => x[1]), MOVES); assert.equal(p.state.index, 6); assert.equal(p.state.mode, 'paused');
  assert.deepEqual(c.stack, MOVES); assert.equal(c.maxConcurrent, 1); ok('phát hết, đúng thứ tự'); }

// 2. Tạm dừng giữa chừng: nước đang xoay được hoàn tất, sau đó đứng yên
{ const [c, p] = mk(); const run = p.play(); await sleep(20); p.pause(); await run; await sleep(60);
  const idx = p.state.index; assert.ok(idx >= 1 && idx < 6, 'dừng giữa chừng: ' + idx);
  assert.deepEqual(c.stack, MOVES.slice(0, idx)); const before = c.log.length; await sleep(60);
  assert.equal(c.log.length, before, 'không chạy tiếp sau khi dừng'); assert.equal(c.maxConcurrent, 1); ok('tạm dừng, khối khớp đúng bước'); }

// 3. Lùi từng bước từ cuối về đầu
{ const [c, p] = mk(); await p.play(); await sleep(20);
  for (let i = 6; i > 0; i--) { await p.stepBack(); assert.deepEqual(c.stack, MOVES.slice(0, i - 1)); }
  assert.equal(p.state.index, 0); await p.stepBack(); assert.equal(p.state.index, 0); ok('lùi từng bước, chặn ở 0'); }

// 4. Tiến từng bước, chặn ở cuối
{ const [c, p] = mk(); for (let i = 1; i <= 6; i++) { await p.stepForward(); assert.deepEqual(c.stack, MOVES.slice(0, i)); }
  await p.stepForward(); assert.equal(p.state.index, 6); ok('tiến từng bước, chặn ở cuối'); }

// 5. Nhảy tới bước bất kỳ (xuôi và ngược), không hiệu ứng
{ const [c, p] = mk(); await p.seek(4); assert.deepEqual(c.stack, MOVES.slice(0, 4));
  await p.seek(1); assert.deepEqual(c.stack, MOVES.slice(0, 1)); await p.seek(99); assert.deepEqual(c.stack, MOVES);
  await p.seek(-5); assert.deepEqual(c.stack, []); assert.ok(c.log.every(x => x[0] === 'inst')); ok('seek tức thì đúng'); }

// 6. Phát -> dừng -> phát ngay: không có hai vòng chạy chồng, mỗi nước đúng một lần
{ const [c, p] = mk(); const r1 = p.play(); await sleep(15); p.pause(); const r2 = p.play(); await Promise.all([r1, r2]); await sleep(80);
  assert.deepEqual(c.stack, MOVES); assert.equal(c.log.filter(x => x[0] === 'anim').length, 6); assert.equal(c.maxConcurrent, 1); ok('dừng rồi phát ngay, không nhân đôi'); }

// 7. Tua khi đang bận: được xếp hàng và thực hiện sau khi nước hiện tại xong
{ const [c, p] = mk(); const r = p.play(); await sleep(12); await p.seek(0); await r; await sleep(60);
  assert.equal(p.state.index, 0); assert.deepEqual(c.stack, []); assert.equal(c.maxConcurrent, 1); ok('seek khi đang bận được xếp hàng'); }

// 8. Bấm nhiều lần stepForward cùng lúc: chỉ chạy một lần mỗi lượt (khoá bận)
{ const [c, p] = mk(); await Promise.all([p.stepForward(), p.stepForward(), p.stepForward()]);
  assert.equal(p.state.index, 1); assert.deepEqual(c.stack, MOVES.slice(0, 1)); ok('bấm dồn không làm nhảy bước'); }

// 9. Nạp lời giải mới giữa chừng: về trạng thái sạch
{ const [c, p] = mk(); await p.stepForward(); p.load(["U", "R"]); assert.equal(p.state.index, 0); assert.equal(p.state.total, 2); ok('load lại đặt về bước 0'); }

assert.deepEqual(["U","U'","U2","D2"].map(inverseMove), ["U'","U","U2","D2"]); ok('inverseMove');
console.log('TẤT CẢ ĐẠT:', n, 'kiểm tra');
