# TetCTF 2020 - 2020 Challenge Writeup

## Challenge Description

Một challenge về Python's Random Number Generator (MT19937). Chương trình cho phép:
- Chọn 2 indices để xem giá trị random
- Sinh 2019 số random 32-bit
- Phải đoán số random thứ 2020 để lấy flag

## Source Code Analysis

```python
import os
import random

if __name__ == '__main__':
    print("Pick two indices to reveal, then guess the 2020th number!")

    nIndices = 2
    indices = [int(input()) for _ in range(nIndices)]

    for i in range(2019):
        r = random.getrandbits(32)
        print(r if i in indices else 'Nope!')

    if int(input()) == random.getrandbits(32):
        print(os.environ["FLAG"])
```

## Vulnerability

Python's `random` module sử dụng **Mersenne Twister (MT19937)** PRNG. Những điểm quan trọng:

1. **Deterministic**: Với cùng một seed, MT19937 luôn sinh ra cùng một chuỗi số
2. **State Recovery**: Với 624 outputs liên tiếp, có thể recover toàn bộ internal state
3. **Seed Brute Force**: Với chỉ 2 outputs, nếu seed nằm trong khoảng nhỏ (thường là time-based), có thể brute force

## Solution Strategy

### Approach 1: Brute Force Seed (Recommended)

Vì chương trình không tự set seed, Python sẽ sử dụng seed mặc định (thường từ system time hoặc entropy). Trong môi trường CTF, seed thường:
- Là số nhỏ (< 1,000,000)
- Hoặc là timestamp (thời gian hiện tại)

**Algorithm:**
1. Chọn indices = [0, 1] (2 số đầu tiên)
2. Nhận được 2 giá trị: `val1` và `val2`
3. Brute force seed từ 0 → max_range:
   - Với mỗi seed candidate:
     - `random.seed(candidate)`
     - Sinh 2 số đầu tiên
     - Nếu khớp với `val1` và `val2` → Found!
4. Sử dụng seed tìm được để predict số thứ 2020

### Approach 2: Z3 Symbolic Execution (Advanced)

Sử dụng Z3 SMT solver để giải symbolic constraints của MT19937:
- Tạo biến symbolic cho seed
- Model hóa MT19937 initialization và tempering
- Add constraints cho 2 outputs đã biết
- Solve để tìm seed

## Implementation

### Quick Solve (simple_solve.py)

```python
python simple_solve.py
```

Chọn mode:
1. **Test solver** - Kiểm tra solver với seed đã biết
2. **Interactive solve** - Auto connect và solve challenge
3. **Manual solve** - Nhập giá trị thủ công

### Usage

#### Local Testing
```bash
# Run test mode
echo "1" | python simple_solve.py
```

#### Against Remote Server
```python
# Edit simple_solve.py, uncomment and modify:
io = remote('host', 1337)
```

#### Manual Mode
```bash
python simple_solve.py
# Choose option 3
# Enter indices: 0, 1
# Enter the two values you received
# Get prediction
```

## Key Points

1. **Index Selection**: Chọn indices 0 và 1 giúp brute force nhanh nhất (chỉ cần sinh 2 số)

2. **Seed Range**:
   - Thử small seeds trước (0-1M)
   - Sau đó thử time-based seeds
   - Cuối cùng mới full range

3. **Optimization**:
   - Với indices nhỏ, mỗi seed check rất nhanh
   - Có thể parallel brute force nếu cần

## Tools

- `simple_solve.py` - Main solver (no dependencies)
- `solve.py` - Z3-based solver (requires z3-solver)
- `exploit.py` - Initial version với MT19937 implementation

## Timeline

- Brute force 0-1M seeds: ~1-2 phút
- Nếu seed lớn hơn, có thể mất thời gian hơn

## Flag

Sau khi predict đúng số thứ 2020, server sẽ trả về flag.

## References

- [Mersenne Twister - Wikipedia](https://en.wikipedia.org/wiki/Mersenne_Twister)
- [Breaking Python's PRNG](https://stackered.com/blog/python-random-prediction/)
- [MT19937 Predictor](https://github.com/kmyk/mersenne-twister-predictor)
