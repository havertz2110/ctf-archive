#!/usr/bin/env python3
"""
Fast solver using optimized C-style brute force with Numba JIT compilation
If numba not available, falls back to pure Python with optimizations
"""

import socket
import random

# Try to use numba for JIT compilation (much faster)
try:
    from numba import jit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    # Fallback: no-op decorator
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# MT19937 constants
N = 624
M = 397
MATRIX_A = 0x9908b0df
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7fffffff

@jit(nopython=HAS_NUMBA)
def init_genrand(seed):
    """Initialize MT19937 state"""
    mt = [0] * N
    mt[0] = seed & 0xffffffff
    for mti in range(1, N):
        mt[mti] = (1812433253 * (mt[mti-1] ^ (mt[mti-1] >> 30)) + mti) & 0xffffffff
    return mt

@jit(nopython=HAS_NUMBA)
def genrand_int32(mt, index):
    """Generate one random number from MT state"""
    if index >= N:
        # twist
        for kk in range(N - M):
            y = (mt[kk] & UPPER_MASK) | (mt[kk+1] & LOWER_MASK)
            mt[kk] = mt[kk+M] ^ (y >> 1) ^ (MATRIX_A if y & 1 else 0)
        for kk in range(N - M, N - 1):
            y = (mt[kk] & UPPER_MASK) | (mt[kk+1] & LOWER_MASK)
            mt[kk] = mt[kk+(M-N)] ^ (y >> 1) ^ (MATRIX_A if y & 1 else 0)
        y = (mt[N-1] & UPPER_MASK) | (mt[0] & LOWER_MASK)
        mt[N-1] = mt[M-1] ^ (y >> 1) ^ (MATRIX_A if y & 1 else 0)
        index = 0

    y = mt[index]
    y ^= (y >> 11)
    y ^= ((y << 7) & 0x9d2c5680)
    y ^= ((y << 15) & 0xefc60000)
    y ^= (y >> 18)

    return y & 0xffffffff, index + 1

def check_seed_fast(seed, idx1, idx2, val1, val2):
    """Fast check if seed produces expected values"""
    mt = init_genrand(seed)
    index = N

    for i in range(max(idx1, idx2) + 1):
        r, index = genrand_int32(mt, index)
        if i == idx1 and r != val1:
            return False
        if i == idx2 and r != val2:
            return False
    return True

def brute_force_optimized(idx1, idx2, val1, val2, start=0, end=2**32):
    """Optimized brute force"""
    print(f"[*] Brute forcing range [{start:,}, {end:,})")
    print(f"[*] Using Numba JIT: {HAS_NUMBA}")

    chunk = 1000000
    for base in range(start, end, chunk):
        if base % 10000000 == 0 and base > start:
            print(f"    Progress: {base:,}/{end:,}")

        limit = min(base + chunk, end)
        for seed in range(base, limit):
            if check_seed_fast(seed, idx1, idx2, val1, val2):
                return seed

    return None

def solve_remote(host, port):
    """Solve the challenge"""
    print("="*70)
    print(f"TetCTF 2020 - Fast Solver")
    print(f"Connecting to {host}:{port}")
    print("="*70)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    data = s.recv(1024).decode()
    print(f"\n{data.strip()}\n")

    idx1, idx2 = 0, 1
    print(f"[+] Sending indices: {idx1}, {idx2}")
    s.sendall(f"{idx1}\n{idx2}\n".encode())

    # Receive all data
    all_data = b""
    while all_data.count(b'\n') < 2019:
        all_data += s.recv(8192)

    lines = all_data.decode().strip().split('\n')
    revealed = []
    for i, line in enumerate(lines[:2019]):
        if line.strip() != 'Nope!':
            val = int(line.strip())
            revealed.append(val)
            print(f"[*] Output[{i}] = {val}")

    val1, val2 = revealed[0], revealed[1]

    # Try different ranges
    print("\n" + "="*70)
    print("Starting brute force...")
    print("="*70 + "\n")

    # Range 1: 0-50M (most likely)
    print("[*] Range 1: 0-50,000,000")
    seed = brute_force_optimized(idx1, idx2, val1, val2, 0, 50000000)

    if seed is None:
        # Range 2: 10M-2^31
        print("\n[*] Range 2: 50M-2^31")
        seed = brute_force_optimized(idx1, idx2, val1, val2, 50000000, 2**31)

    if seed is not None:
        print(f"\n{'='*70}")
        print(f"[+] FOUND SEED: {seed}")
        print(f"{'='*70}\n")

        # Predict 2020th
        random.seed(seed)
        for _ in range(2020):
            prediction = random.getrandbits(32)

        print(f"[+] Sending prediction: {prediction}")
        s.sendall(f"{prediction}\n".encode())

        response = s.recv(4096).decode()
        print(f"\n{'='*70}")
        print("RESPONSE:")
        print(f"{'='*70}")
        print(response)
    else:
        print("\n[-] Could not find seed!")

    s.close()

if __name__ == '__main__':
    solve_remote('archive.cryptohack.org', 63222)
