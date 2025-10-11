#!/usr/bin/env python3
"""
Optimized solution for 2020 CTF challenge

Key insights:
1. Python's random module uses MT19937 with default seed from time
2. We need to recover seed from just 2 outputs
3. Challenge runs on server, so seed is likely time-based (limited range)
4. We can use the relationship between consecutive MT19937 outputs

Better approach: Use Z3 constraint solver to find seed symbolically
"""

from z3 import *
import random
import time

def symbolic_mt19937_step(state, index):
    """Symbolically compute one MT19937 output"""
    # MT19937 parameters
    w, n, m, r = 32, 624, 397, 31
    a = 0x9908B0DF
    u, d = 11, 0xFFFFFFFF
    s, b = 7, 0x9D2C5680
    t, c = 15, 0xEFC60000
    l = 18
    f = 1812433253

    # Temper the output
    y = state[index]
    y = y ^ LShR(y, u)
    y = y ^ ((y << s) & b)
    y = y ^ ((y << t) & c)
    y = y ^ LShR(y, l)
    return y & 0xFFFFFFFF

def solve_with_z3(idx1, idx2, val1, val2, seed_min=0, seed_max=2**32):
    """Use Z3 to solve for the seed"""
    print(f"[*] Using Z3 solver for seed in range [{seed_min}, {seed_max})")

    # Create Z3 variables
    seed = BitVec('seed', 32)
    solver = Solver()

    # Add seed range constraint
    solver.add(UGE(seed, seed_min))
    solver.add(ULT(seed, seed_max))

    # Initialize MT state symbolically
    mt = [BitVec(f'mt_{i}', 32) for i in range(624)]
    solver.add(mt[0] == seed)

    # Generate initial state
    for i in range(1, 624):
        solver.add(mt[i] == (1812433253 * (mt[i-1] ^ LShR(mt[i-1], 30)) + i) & 0xFFFFFFFF)

    # Add constraints for known outputs
    # This is complex because we need to handle the twist operation
    # For simplicity, let's assume indices are before first twist (< 624)
    if max(idx1, idx2) < 624:
        out1 = symbolic_mt19937_step(mt, idx1)
        out2 = symbolic_mt19937_step(mt, idx2)
        solver.add(out1 == val1)
        solver.add(out2 == val2)

        print("[*] Solving constraints...")
        if solver.check() == sat:
            model = solver.model()
            seed_val = model[seed].as_long()
            print(f"[+] Found seed: {seed_val}")
            return seed_val
        else:
            print("[-] No solution found")
            return None
    else:
        print("[-] Indices too large for simple symbolic execution")
        return None

def predict_2020th(seed):
    """Predict the 2020th number given the seed"""
    random.seed(seed)
    for i in range(2020):
        result = random.getrandbits(32)
    return result

def main():
    print("=== TetCTF 2020 - 2020 Challenge Solver ===\n")

    # For interactive solving:
    # from pwn import *
    # io = remote('host', port)
    # io.recvline()

    idx1 = int(input("Enter first index: "))
    idx2 = int(input("Enter second index: "))

    print(f"\n[*] Using indices: {idx1}, {idx2}")
    # io.sendline(str(idx1).encode())
    # io.sendline(str(idx2).encode())

    # Read the values
    # In real scenario, parse from server output
    val1 = int(input(f"Enter value at index {idx1}: "))
    val2 = int(input(f"Enter value at index {idx2}: "))

    # Try to solve with Z3 (works if indices < 624)
    if max(idx1, idx2) < 624:
        seed = solve_with_z3(idx1, idx2, val1, val2, 0, 2**20)  # Limit range for speed

        if seed is None:
            print("[*] Trying larger seed range...")
            seed = solve_with_z3(idx1, idx2, val1, val2, 0, 2**32)

        if seed is not None:
            prediction = predict_2020th(seed)
            print(f"\n[+] Prediction for 2020th number: {prediction}")
            # io.sendline(str(prediction).encode())
            # print(io.recvall().decode())
        else:
            print("[-] Could not recover seed")
    else:
        print("[-] Indices too large. Try indices < 624")

if __name__ == '__main__':
    # Test mode
    test = input("Run in test mode? (y/n): ").lower() == 'y'

    if test:
        # Test the solver
        test_seed = 42
        random.seed(test_seed)

        idx1, idx2 = 0, 1
        outputs = []
        for i in range(2020):
            r = random.getrandbits(32)
            outputs.append(r)

        print(f"\n[*] Test mode with seed {test_seed}")
        print(f"[*] Values: {outputs[idx1]} at {idx1}, {outputs[idx2]} at {idx2}")
        print(f"[*] Target (2020th): {outputs[2019]}")

        seed = solve_with_z3(idx1, idx2, outputs[idx1], outputs[idx2], 0, 1000)
        if seed == test_seed:
            print(f"[+] Test passed! Recovered seed: {seed}")
            prediction = predict_2020th(seed)
            print(f"[+] Predicted: {prediction}, Actual: {outputs[2019]}")
            print(f"[+] Match: {prediction == outputs[2019]}")
        else:
            print(f"[-] Test failed. Got {seed}, expected {test_seed}")
    else:
        main()
