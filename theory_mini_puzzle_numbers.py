#!/usr/bin/env python3
"""
NEW THEORY: The numbers 09111819 and 11122111 are CRITICAL

Theory 1: These are rectangle INDICES to include/exclude
Theory 2: These are BYTE VALUES that should appear in the key (checksum)
Theory 3: These define a PAIRING PATTERN
Theory 4: These are GRID COORDINATES (row, column)
Theory 5: These are HEX VALUES that start/end the key
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key
import itertools

IMAGE_PATH = 'crypto5fix.png'
EXPECTED_ADDRESS = '1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'

def load_and_extract(path):
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rect_data = []
    
    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:
            outer_cnt = contours[parent]
            xo, yo, wo, ho = cv2.boundingRect(outer_cnt)
            xi, yi, wi, hi = cv2.boundingRect(cnt)
            
            outer_area = cv2.contourArea(outer_cnt)
            inner_area = cv2.contourArea(cnt)
            shell_area = outer_area - inner_area
            
            rect_data.append({
                'x': xo, 'y': yo,
                'outer': outer_area,
                'inner': inner_area,
                'shell': shell_area
            })
    
    rect_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    return rect_data

def validate_key(byte_list):
    if len(byte_list) != 32:
        return None, None, False
    hex_key = ''.join(f"{b:02x}" for b in byte_list)
    try:
        for compressed in [True, False]:
            key = Key(import_key=hex_key, compressed=compressed)
            if key.address() == EXPECTED_ADDRESS:
                return hex_key, key.address(), True
    except:
        pass
    return hex_key, None, False

print("="*70)
print("TESTING MINI-PUZZLE NUMBER THEORIES")
print("="*70)

rect_data = load_and_extract(IMAGE_PATH)
print(f"\n[+] Loaded {len(rect_data)} rectangles")

# Parse the hint numbers
left_num = "09111819"
right_num = "11122111"

# Theory 1: Numbers as BYTE VALUES (checksum verification)
print("\n" + "="*70)
print("THEORY 1: Numbers are byte values that should appear in key")
print("="*70)

# Parse as individual hex bytes
left_bytes = [int(left_num[i:i+2]) for i in range(0, len(left_num), 2)]   # [9, 11, 18, 19]
right_bytes = [int(right_num[i:i+2]) for i in range(0, len(right_num), 2)] # [11, 12, 21, 11]

print(f"Left bytes (decimal):  {left_bytes}")
print(f"Right bytes (decimal): {right_bytes}")
print(f"Left bytes (hex):  {[hex(b) for b in left_bytes]}")
print(f"Right bytes (hex): {[hex(b) for b in right_bytes]}")

# Try: Key should START with left_bytes and END with right_bytes
print("\n[*] Testing if key starts with left_bytes and ends with right_bytes...")

def try_constrained_key_generation(rect_data, start_bytes, end_bytes):
    """
    Generate keys and check if any start/end with the specified bytes
    """
    # Try different area types and pairings
    area_types = ['shell', 'outer', 'inner']
    
    for area_type in area_types:
        areas = [r[area_type] for r in rect_data[:64]]
        
        # Sequential pairing
        bytes_out = []
        for i in range(0, 64, 2):
            sum_val = areas[i] + areas[i + 1]
            byte_val = int(sum_val) % 256
            bytes_out.append(byte_val)
        
        # Check if starts with start_bytes and ends with end_bytes
        if bytes_out[:4] == start_bytes and bytes_out[-4:] == end_bytes:
            hex_key, address, is_valid = validate_key(bytes_out)
            print(f"   MATCH FOUND with {area_type}!")
            print(f"   Key: {hex_key}")
            print(f"   Address: {address}")
            if is_valid:
                print(f"   ✓ VALID ADDRESS!")
                return True
            else:
                print(f"   ✗ Wrong address")

try_constrained_key_generation(rect_data, left_bytes, right_bytes)

# Theory 2: Numbers as RECTANGLE INDICES
print("\n" + "="*70)
print("THEORY 2: Numbers specify which rectangles to use/pair")
print("="*70)

# Parse as individual digits
left_indices = [int(d) for d in left_num]   # [0,9,1,1,1,8,1,9]
right_indices = [int(d) for d in right_num] # [1,1,1,2,2,1,1,1]

print(f"Left indices:  {left_indices}")
print(f"Right indices: {right_indices}")

# Theory 2a: These are row/column indices for an 8x8 grid
print("\n[*] Testing as (row, column) pairs for 8x8 grid...")

def test_grid_indices(rect_data, left_idx, right_idx):
    areas = [r['shell'] for r in rect_data[:64]]
    grid = np.array(areas).reshape(8, 8)
    
    # Try using left_indices as rows, right_indices as columns
    selected_values = []
    for i in range(min(len(left_idx), len(right_idx))):
        row = left_idx[i] % 8
        col = right_idx[i] % 8
        idx = row * 8 + col
        if idx < 64:
            selected_values.append(areas[idx])
    
    if len(selected_values) >= 2:
        # Pair them
        bytes_out = []
        for i in range(0, len(selected_values) - 1, 2):
            sum_val = selected_values[i] + selected_values[i + 1]
            byte_val = int(sum_val) % 256
            bytes_out.append(byte_val)
        
        print(f"   Selected {len(selected_values)} values, generated {len(bytes_out)} bytes")

test_grid_indices(rect_data, left_indices, right_indices)

# Theory 3: Numbers define PAIRING OFFSETS
print("\n" + "="*70)
print("THEORY 3: Numbers define how far apart to pair rectangles")
print("="*70)

# Try pairing with different offsets based on the numbers
offsets_to_try = [9, 11, 18, 19, 12, 21]  # Unique values from both numbers

for offset in offsets_to_try:
    areas = [r['shell'] for r in rect_data[:64]]
    
    pairs = []
    for i in range(64 - offset):
        if i + offset < 64:
            pairs.append((i, i + offset))
    
    if len(pairs) >= 32:
        bytes_out = []
        for idx1, idx2 in pairs[:32]:
            sum_val = areas[idx1] + areas[idx2]
            byte_val = int(sum_val) % 256
            bytes_out.append(byte_val)
        
        hex_key, address, is_valid = validate_key(bytes_out)
        
        print(f"[*] Offset {offset:2d}: ", end="")
        if is_valid:
            print(f"✓ SUCCESS!")
            print(f"    Key: {hex_key}")
            print(f"    Address: {address}")
            with open("SOLUTION_FOUND.txt", "w") as f:
                f.write(f"Offset pairing: {offset}\n")
                f.write(f"Key: {hex_key}\n")
                f.write(f"Address: {address}\n")
            exit(0)
        else:
            print("✗")

# Theory 4: Numbers as HEX VALUES
print("\n" + "="*70)
print("THEORY 4: Numbers as hexadecimal start/end of key")
print("="*70)

# 09111819 as hex = certain bytes
# 11122111 as hex = certain bytes
print(f"0x09111819 = {0x09111819} (decimal)")
print(f"0x11122111 = {0x11122111} (decimal)")

# Try: First 4 bytes should be 0x09, 0x11, 0x18, 0x19
# Last 4 bytes should be 0x11, 0x12, 0x21, 0x11
start_hex = [0x09, 0x11, 0x18, 0x19]
end_hex = [0x11, 0x12, 0x21, 0x11]

print(f"\nLooking for keys starting with: {' '.join(f'{b:02x}' for b in start_hex)}")
print(f"And ending with: {' '.join(f'{b:02x}' for b in end_hex)}")

# This would require brute forcing the middle 24 bytes, which is infeasible
print("[*] This would require brute force (2^192 combinations) - SKIP")

print("\n" + "="*70)
print("THEORY TESTING COMPLETE")
print("="*70)
