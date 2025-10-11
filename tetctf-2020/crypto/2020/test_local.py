#!/usr/bin/env python3
"""
Test the solution locally without pwntools
Simulates the challenge and solves it
"""

import random
import subprocess
import sys

def brute_force_seed(idx1, idx2, val1, val2, max_seed=10000000):
    """Brute force the seed"""
    print(f"[*] Brute forcing seed with constraints:")
    print(f"    output[{idx1}] = {val1}")
    print(f"    output[{idx2}] = {val2}")

    for seed in range(max_seed):
        if seed % 100000 == 0 and seed > 0:
            print(f"    Progress: {seed:,}/{max_seed:,}")

        random.seed(seed)
        match = True
        for i in range(max(idx1, idx2) + 1):
            r = random.getrandbits(32)
            if i == idx1 and r != val1:
                match = False
                break
            if i == idx2 and r != val2:
                match = False
                break

        if match:
            return seed

    return None

def predict_2020th(seed):
    """Predict the 2020th number"""
    random.seed(seed)
    for i in range(2020):
        result = random.getrandbits(32)
    return result

def simulate_challenge():
    """Simulate the challenge locally"""
    print("="*60)
    print("TetCTF 2020 - 2020 Challenge Local Simulation")
    print("="*60)

    # Simulate random seed (in real challenge, this is unknown)
    actual_seed = random.randint(0, 1000000)
    print(f"\n[*] Challenge started (hidden seed: {actual_seed})")
    print("[*] Pick two indices to reveal, then guess the 2020th number!")

    # Our strategy: choose indices 0 and 1
    idx1, idx2 = 0, 1
    print(f"\n[+] Choosing indices: {idx1} and {idx2}")

    # Simulate the challenge generating numbers
    random.seed(actual_seed)
    outputs = []
    revealed = []

    for i in range(2019):
        r = random.getrandbits(32)
        outputs.append(r)
        if i == idx1 or i == idx2:
            revealed.append(r)
            print(f"[*] Output at index {i}: {r}")

    # Generate the 2020th number (target)
    target_2020 = random.getrandbits(32)
    print(f"\n[*] Target 2020th number: {target_2020} (hidden)")

    # Now solve it
    print("\n" + "="*60)
    print("Starting Solution Phase")
    print("="*60)

    val1, val2 = revealed[0], revealed[1]

    # Brute force seed
    print(f"\n[*] Attempting to recover seed...")
    found_seed = brute_force_seed(idx1, idx2, val1, val2, max_seed=2000000)

    if found_seed is None:
        print("[-] Failed to find seed!")
        return False

    print(f"\n[+] Found seed: {found_seed}")
    print(f"[+] Actual seed: {actual_seed}")
    print(f"[+] Match: {found_seed == actual_seed}")

    # Predict 2020th number
    prediction = predict_2020th(found_seed)
    print(f"\n[+] Predicted 2020th number: {prediction}")
    print(f"[+] Actual 2020th number: {target_2020}")

    if prediction == target_2020:
        print("\n" + "="*60)
        print("[+] SUCCESS! You would get the flag!")
        print("="*60)
        return True
    else:
        print("\n[-] FAILED! Prediction doesn't match")
        return False

if __name__ == '__main__':
    success = simulate_challenge()
    sys.exit(0 if success else 1)
