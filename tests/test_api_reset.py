import json
import urllib.request
import urllib.error
import pytest

def test_api():
    print("\n--- KIỂM TRA BIẾN ĐẾM NODE QUA API THỰC TẾ ---")
    print("1. Gọi API Scramble để lấy trạng thái gốc...")
    req = urllib.request.Request('http://127.0.0.1:8000/scramble?n=12')
    try:
        with urllib.request.urlopen(req) as response:
            state = json.loads(response.read())['state']
        
        print("2. Gọi API Solve 3 lần liên tiếp cùng 1 trạng thái:")
        for i in range(1, 4):
            req = urllib.request.Request(
                'http://127.0.0.1:8000/solve',
                data=json.dumps({"state": state, "heuristic": "v2"}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                print(f"  - Lần {i}: Nodes opened = {data['nodes_opened']:,}, Time = {data['time_ms']} ms")
        
        print("=> KẾT LUẬN: Nếu Nodes mở không đổi, API hoàn toàn biệt lập qua các request!")
    except (urllib.error.URLError, ConnectionRefusedError):
        pytest.skip("Server API 127.0.0.1:8000 không hoạt động, bỏ qua test_api_reset.py.")

if __name__ == "__main__":
    test_api()
