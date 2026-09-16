## 📈 Báo cáo Benchmark: Heuristic v1 (Thô) vs v2 (Corner PDB)

Kịch bản thử nghiệm: So sánh số Node đã mở và Thời gian chạy của IDA* giữa 2 heuristic khi giải các xáo trộn ngẫu nhiên ở độ sâu 5, 8, và 10. Giới hạn `MAX_NODES = 300,000` (nếu vượt quá sẽ bị đánh dấu là TIMEOUT).

| Độ sâu | Seed | Phiên bản | Lời giải | Node đã mở | Thời gian (s) |
| :---: | :---: | :--- | :---: | ---: | ---: |
| **5** | 500 | v1 (Thô) | 5 bước | 1,291 | 0.0234 |
| | | v2 (Corner PDB) | 5 bước | 38 | 0.0910 |
| **5** | 501 | v1 (Thô) | 5 bước | 5,616 | 0.1416 |
| | | v2 (Corner PDB) | 5 bước | 79 | 0.0010 |
| **8** | 800 | v1 (Thô) | TIMEOUT | > 300,000 | 4.2606 |
| | | v2 (Corner PDB) | 8 bước | 4,450 | 0.0733 |
| **8** | 801 | v1 (Thô) | TIMEOUT | > 300,000 | 4.1195 |
| | | v2 (Corner PDB) | 8 bước | 1,632 | 0.0185 |
| **10** | 1000 | v1 (Thô) | TIMEOUT | > 300,000 | 3.6893 |
| | | v2 (Corner PDB) | TIMEOUT | > 300,000 | 3.8561 |

**Kết luận từ Benchmark:**
- **Độ sâu <= 5:** Cả hai phiên bản đều giải quyết tốt, tuy nhiên v2 giảm số node mở từ hàng nghìn xuống chỉ còn vài chục (giảm hơn **98%** node mở).
- **Độ sâu 8:** Heuristic v1 bắt đầu nổ điểm không gian (vượt quá 300k node). Trong khi đó v2 (Corner PDB) vẫn giải quyết cực kỳ nhanh chóng chỉ trong vòng vài nghìn node và dưới 0.1 giây.
- **Độ sâu >= 10:** Ngay cả với Corner PDB (v2), không gian tìm kiếm đôi khi vẫn bùng nổ vượt 300k node. Điều này là do ta chưa xây dựng **Edge Pattern Database**. Đối với các scramble sâu, nếu chỉ có PDB của góc, $h(s)$ vẫn khá lỏng lẻo khi cạnh bị xáo trộn nhiều, IDA* phải lục lọi rất sâu để tìm ra nhánh đúng. (Đó là lý do Korf 1997 chia thêm 2 Edge PDB).
