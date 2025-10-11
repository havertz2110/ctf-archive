#!/usr/bin/env python3
"""
Simple brute force solution for TetCTF 2020 - 2020 challenge
No external dependencies needed
"""

import random
import time

def check_seed(seed, idx1, idx2, val1, val2):
    """Check if a seed produces the expected values at given indices"""
    random.seed(seed)
    for i in range(max(idx1, idx2) + 1):
        r = random.getrandbits(32)
        if i == idx1 and r != val1:
            return False
        if i == idx2 and r != val2:
            return False
    return True

def brute_force_seed(idx1, idx2, val1, val2, max_seed=2**32):
    """Brute force the seed - optimized for time-based seeds"""
    print(f"[*] Brute forcing seed...")
    print(f"[*] Constraints: output[{idx1}]={val1}, output[{idx2}]={val2}")

    # Strategy 1: Try small seeds first (often used in CTFs)
    print("[*] Trying small seeds (0-1000000)...")
    for seed in range(1000000):
        if seed % 100000 == 0:
            print(f"    Progress: {seed}")
        if check_seed(seed, idx1, idx2, val1, val2):
            print(f"[+] Found seed: {seed}")
            return seed

    # Strategy 2: Try time-based seeds (last hour to next hour)
    print("[*] Trying time-based seeds...")
    current_time = int(time.time())
    for offset in range(-3600, 3600):
        seed = current_time + offset
        if check_seed(seed, idx1, idx2, val1, val2):
            print(f"[+] Found seed: {seed}")
            return seed

    # Strategy 3: Full range if needed (very slow)
    print(f"[*] Full range search up to {max_seed} (this will take a while)...")
    for seed in range(max_seed):
        if seed % 10000000 == 0:
            print(f"    Progress: {seed}/{max_seed}")
        if check_seed(seed, idx1, idx2, val1, val2):
            print(f"[+] Found seed: {seed}")
            return seed

    return None

def predict_2020th(seed):
    """Generate the 2020th number from the seed"""
    random.seed(seed)
    result = None
    for i in range(2020):
        result = random.getrandbits(32)
    return result

def interactive_solve():
    """Interactive solver for connecting to the challenge"""
    try:
        import pwn

        # Connect to challenge
        # Adjust host and port as needed
        io = pwn.process(['python', '2020.py'])
        # io = pwn.remote('host', 1337)

        io.recvline()  # "Pick two indices..."

        # Choose indices (pick 0 and 1 for fastest brute force)
        idx1, idx2 = 0, 1

        print(f"[*] Sending indices: {idx1}, {idx2}")
        io.sendline(str(idx1).encode())
        io.sendline(str(idx2).encode())

        # Collect outputs
        vals = []
        for i in range(2019):
            line = io.recvline().decode().strip()
            if line != 'Nope!':
                val = int(line)
                vals.append(val)
                print(f"[*] Got value at index {len(vals)-1}: {val}")

        if len(vals) != 2:
            print(f"[-] Error: Expected 2 values, got {len(vals)}")
            return

        val1, val2 = vals[0], vals[1]

        # Brute force the seed
        seed = brute_force_seed(idx1, idx2, val1, val2, max_seed=10000000)

        if seed is None:
            print("[-] Could not find seed in reasonable range")
            return

        # Predict 2020th number
        prediction = predict_2020th(seed)
        print(f"\n[+] Sending prediction: {prediction}")
        io.sendline(str(prediction).encode())

        # Get flag
        response = io.recvall(timeout=2).decode()
        print(f"\n[*] Response:\n{response}")

        io.close()

    except ImportError:
        print("[-] pwntools not installed. Run: pip install pwntools")
    except Exception as e:
        print(f"[-] Error: {e}")

def manual_solve():
    """Manual solver for when you have the values"""
    print("=== Manual Solver ===")
    print("Enter the two indices you chose:")
    idx1 = int(input("Index 1: "))
    idx2 = int(input("Index 2: "))

    print("\nEnter the values received:")
    val1 = int(input(f"Value at index {idx1}: "))
    val2 = int(input(f"Value at index {idx2}: "))

    # Brute force
    seed = brute_force_seed(idx1, idx2, val1, val2, max_seed=10000000)

    if seed is None:
        print("[-] Could not find seed")
        return

    # Predict
    prediction = predict_2020th(seed)
    print(f"\n{'='*50}")
    print(f"[+] ANSWER: {prediction}")
    print(f"{'='*50}")

def test_solver():
    """Test the solver with known values"""
    print("=== Testing Solver ===\n")

    test_seed = 12345
    idx1, idx2 = 0, 1

    print(f"[*] Test seed: {test_seed}")
    print(f"[*] Indices: {idx1}, {idx2}")

    # Generate test values
    random.seed(test_seed)
    outputs = [random.getrandbits(32) for _ in range(2020)]

    val1, val2 = outputs[idx1], outputs[idx2]
    target = outputs[2019]

    print(f"[*] Value at {idx1}: {val1}")
    print(f"[*] Value at {idx2}: {val2}")
    print(f"[*] Target 2020th: {target}")

    # Solve
    found_seed = brute_force_seed(idx1, idx2, val1, val2, max_seed=1000000)

    if found_seed == test_seed:
        print(f"\n[+] SUCCESS! Found correct seed: {found_seed}")

        prediction = predict_2020th(found_seed)
        if prediction == target:
            print(f"[+] Prediction matches! {prediction} == {target}")
        else:
            print(f"[-] Prediction mismatch: {prediction} != {target}")
    else:
        print(f"[-] FAILED! Found {found_seed}, expected {test_seed}")

if __name__ == '__main__':
    print("TetCTF 2020 - 2020 Challenge Solver")
    print("=" * 50)
    print("1. Test solver")
    print("2. Interactive solve (auto-connect)")
    print("3. Manual solve (enter values)")
    print()

    choice = input("Choose mode (1/2/3): ").strip()

    if choice == '1':
        test_solver()
    elif choice == '2':
        interactive_solve()
    elif choice == '3':
        manual_solve()
    else:
        print("Invalid choice")
