# TetCTF 2020 - 2020 Challenge Solution

## Tóm tắt

Challenge về dự đoán Python Random Number Generator (MT19937) khi chỉ được xem 2 outputs.

## Cách giải

### Bước 1: Hiểu challenge

- Challenge sinh 2019 số random 32-bit
- Ta được chọn 2 indices để xem giá trị
- Phải đoán đúng số thứ 2020 để lấy flag

### Bước 2: Phân tích lỗ hổng

Python's `random.getrandbits(32)` sử dụng MT19937 PRNG:
- **Deterministic**: Cùng seed → cùng chuỗi số
- **Có thể brute force seed** nếu nằm trong khoảng nhỏ

### Bước 3: Strategy

1. Chọn indices **0** và **1** (để brute force nhanh nhất)
2. Brute force seed từ 0 → 10,000,000
3. Với mỗi seed candidate:
   - Khởi tạo `random.seed(candidate)`
   - Sinh 2 số đầu tiên
   - Nếu khớp → Tìm thấy seed!
4. Dùng seed để predict số thứ 2020

## Chạy solution

### Test local

```bash
python test_local.py
```

Output mẫu:
```
[*] Challenge started (hidden seed: 623285)
[+] Choosing indices: 0 and 1
[*] Output at index 0: 601410079
[*] Output at index 1: 1496902673
...
[+] Found seed: 623285
[+] Predicted 2020th number: 101880869
[+] SUCCESS! You would get the flag!
```

### Với server thực

#### Option 1: Sử dụng simple_solve.py (manual mode)

```bash
python simple_solve.py
# Chọn option 3 (Manual solve)
# Nhập indices: 0
# Nhập indices: 1
# Connect tới server và gửi indices
# Copy 2 giá trị nhận được
# Paste vào solver
# Nhận được prediction
# Gửi prediction tới server
# Nhận flag
```

#### Option 2: Sử dụng pwntools (nếu đã cài)

Sửa `simple_solve.py`, trong hàm `interactive_solve()`:
```python
io = pwn.remote('host', port)  # Thay host và port
```

Chạy:
```bash
python simple_solve.py
# Chọn option 2
```

## Files

- `2020.py` - Source code challenge
- `simple_solve.py` - Main solver (3 modes)
- `test_local.py` - Test solver locally
- `solve.py` - Z3-based solver (advanced)
- `exploit.py` - Initial approach
- `README.md` - Detailed writeup
- `SOLUTION.md` - Quick solution guide (file này)

## Timeline

- Brute force 1M seeds: ~10-20 giây
- Brute force 10M seeds: ~1-2 phút

## Key Insight

**Chọn indices càng nhỏ càng tốt** (0, 1) vì:
- Chỉ cần sinh ít số để kiểm tra
- Brute force nhanh hơn nhiều lần
- Indices lớn (vd: 1000, 1001) sẽ chậm hơn đáng kể

## Kết quả

Với seed trong khoảng 0-1M, solver tìm ra đáp án trong < 1 phút.

Flag sẽ được in ra khi đoán đúng số thứ 2020.
