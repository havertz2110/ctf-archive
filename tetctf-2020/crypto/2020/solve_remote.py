#!/usr/bin/env python3
"""
Solve the remote challenge at archive.cryptohack.org:63222
"""

import socket
import random
import time
from multiprocessing import Pool, cpu_count

def check_seed_match(args):
    """Check if a seed matches - for multiprocessing"""
    seed, idx1, idx2, val1, val2 = args
    random.seed(seed)
    for i in range(max(idx1, idx2) + 1):
        r = random.getrandbits(32)
        if i == idx1 and r != val1:
            return None
        if i == idx2 and r != val2:
            return None
    return seed

def brute_force_seed_parallel(idx1, idx2, val1, val2, start, end):
    """Brute force using multiprocessing"""
    print(f"[*] Parallel brute force from {start:,} to {end:,}")

    chunk_size = 10000
    with Pool(processes=cpu_count()) as pool:
        args_list = [(seed, idx1, idx2, val1, val2) for seed in range(start, end)]

        for i, result in enumerate(pool.imap_unordered(check_seed_match, args_list, chunksize=chunk_size)):
            if i % 1000000 == 0 and i > 0:
                print(f"    Progress: {start + i:,}/{end:,}")
            if result is not None:
                pool.terminate()
                return result

    return None

def brute_force_seed(idx1, idx2, val1, val2, max_seed=10000000):
    """Brute force the seed - single threaded"""
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

def solve_remote(host, port):
    """Connect and solve the remote challenge"""
    print("="*60)
    print(f"Connecting to {host}:{port}")
    print("="*60)

    # Connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # Receive initial message
    data = s.recv(1024).decode()
    print(f"\n[*] Server: {data.strip()}")

    # Choose indices 0 and 1
    idx1, idx2 = 0, 1
    print(f"\n[+] Sending index 1: {idx1}")
    s.sendall(f"{idx1}\n".encode())

    print(f"[+] Sending index 2: {idx2}")
    s.sendall(f"{idx2}\n".encode())

    # Receive all outputs at once
    print("\n[*] Receiving outputs...")
    all_data = b""
    while True:
        chunk = s.recv(8192)
        all_data += chunk
        # Check if we received all 2019 lines
        if all_data.count(b'\n') >= 2019:
            break

    # Parse outputs
    lines = all_data.decode().strip().split('\n')
    print(f"[*] Received {len(lines)} lines")

    revealed_values = []
    for i, line in enumerate(lines[:2019]):
        if line.strip() != 'Nope!':
            try:
                val = int(line.strip())
                revealed_values.append(val)
                print(f"[*] Output at index {i}: {val}")
            except ValueError:
                pass

    if len(revealed_values) != 2:
        print(f"[-] Error: Expected 2 values, got {len(revealed_values)}")
        print(f"[-] First few lines: {lines[:10]}")
        s.close()
        return

    val1, val2 = revealed_values[0], revealed_values[1]

    # Brute force seed
    print("\n" + "="*60)
    print("Brute forcing seed...")
    print("="*60 + "\n")

    # Strategy 1: Try small seeds first (common in CTF)
    print("[*] Strategy 1: Trying small seeds (0-10M)...")
    found_seed = brute_force_seed(idx1, idx2, val1, val2, max_seed=10000000)

    # Strategy 2: Try timestamp range (challenge likely uses time-based seed)
    if found_seed is None:
        print("\n[*] Strategy 2: Trying timestamp-based seeds...")
        current_time = int(time.time())
        # Try from 2020 (year of challenge) to now
        start_time = 1577836800  # Jan 1, 2020
        end_time = current_time + 3600  # Current + 1 hour

        print(f"[*] Trying range: {start_time} to {end_time}")
        found_seed = brute_force_seed_parallel(idx1, idx2, val1, val2, start_time, end_time)

    # Strategy 3: Extended range with parallel processing
    if found_seed is None:
        print("\n[*] Strategy 3: Extended range (10M-100M) with parallel processing...")
        found_seed = brute_force_seed_parallel(idx1, idx2, val1, val2, 10000000, 100000000)

    if found_seed is None:
        print("[-] Could not find seed in range!")
        s.close()
        return

    print(f"\n[+] Found seed: {found_seed}")

    # Predict 2020th number
    prediction = predict_2020th(found_seed)
    print(f"[+] Predicted 2020th number: {prediction}")

    # Send prediction
    print(f"\n[+] Sending prediction...")
    s.sendall(f"{prediction}\n".encode())

    # Receive response (flag)
    print("\n[*] Waiting for response...")
    response = s.recv(4096).decode()

    print("\n" + "="*60)
    print("SERVER RESPONSE:")
    print("="*60)
    print(response)

    s.close()

if __name__ == '__main__':
    host = 'archive.cryptohack.org'
    port = 63222

    solve_remote(host, port)
