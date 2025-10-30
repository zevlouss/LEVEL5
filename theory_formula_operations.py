#!/usr/bin/env python3
"""
NEW THEORY: The mini-puzzle formula defines OPERATIONS

Mini-puzzle shows:
  -1      (subtract 1)
  ×%:     (multiply, then modulo)
  LXIV    (64 in Roman numerals)
  /*/     (divide, multiply, divide)

Theory: Apply these operations IN SEQUENCE to transform areas before pairing
Formula interpretation: (area - 1) × X % 64 / Y * Z / W
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key

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
            
            outer_area = cv2.contourArea(outer_cnt)
            inner_area = cv2.contourArea(cnt)
            shell_area = outer_area - inner_area
            
            rect_data.append({
                'x': xo, 'y': yo,
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
print("TESTING FORMULA OPERATION THEORIES")
print("="*70)

rect_data = load_and_extract(IMAGE_PATH)
areas = [r['shell'] for r in rect_data[:64]]

print(f"\n[+] Loaded {len(areas)} rectangle areas")
print(f"    Range: {min(areas):.1f} to {max(areas):.1f}")

# Test various formula interpretations
formulas = [
    {
        'name': 'Formula: (area - 1) × 2 % 64',
        'func': lambda a: int((a - 1) * 2) % 64
    },
    {
        'name': 'Formula: (area - 1) × 4 % 64',
        'func': lambda a: int((a - 1) * 4) % 64
    },
    {
        'name': 'Formula: area % 64 × 4',
        'func': lambda a: (int(a) % 64) * 4
    },
    {
        'name': 'Formula: (area / 64) × 256',
        'func': lambda a: int((a / 64) * 256) % 256
    },
    {
        'name': 'Formula: (area - 1) / 2 % 64',
        'func': lambda a: int((a - 1) / 2) % 64 if a > 1 else 0
    },
    {
        'name': 'Formula: area % 64 * 256 / 64',
        'func': lambda a: int((int(a) % 64) * 256 / 64)
    },
    {
        'name': 'Formula: (area × 64) % 256',
        'func': lambda a: int(a * 64) % 256
    },
    {
        'name': 'Formula: area / 4 % 256',
        'func': lambda a: int(a / 4) % 256
    },
    {
        'name': 'Formula: (area - 1) × 64 / 256',
        'func': lambda a: int((a - 1) * 64 / 256) if a > 1 else 0
    },
    {
        'name': 'Formula: area % 256',
        'func': lambda a: int(a) % 256
    },
]

print("\n" + "="*70)
print("Testing formula transformations on INDIVIDUAL rectangles")
print("="*70)

for formula in formulas:
    print(f"\n[*] {formula['name']}")
    
    # Apply formula to each area to get direct byte values
    bytes_out = [formula['func'](a) for a in areas[:32]]
    
    hex_key, address, is_valid = validate_key(bytes_out)
    
    if is_valid:
        print(f"    ✓ SUCCESS!")
        print(f"    Key: {hex_key}")
        print(f"    Address: {address}")
        with open("SOLUTION_FOUND.txt", "w") as f:
            f.write(f"Formula: {formula['name']}\n")
            f.write(f"Applied to individual rectangles (first 32)\n")
            f.write(f"Key: {hex_key}\n")
            f.write(f"Address: {address}\n")
        exit(0)
    else:
        print(f"    ✗ No match")

print("\n" + "="*70)
print("Testing formula transformations with PAIRING")
print("="*70)

for formula in formulas:
    print(f"\n[*] {formula['name']} + sequential pairing")
    
    # Apply formula to each area, then pair
    transformed = [formula['func'](a) for a in areas]
    
    bytes_out = []
    for i in range(0, 64, 2):
        sum_val = transformed[i] + transformed[i + 1]
        byte_val = sum_val % 256
        bytes_out.append(byte_val)
    
    hex_key, address, is_valid = validate_key(bytes_out)
    
    if is_valid:
        print(f"    ✓ SUCCESS!")
        print(f"    Key: {hex_key}")
        print(f"    Address: {address}")
        with open("SOLUTION_FOUND.txt", "w") as f:
            f.write(f"Formula: {formula['name']}\n")
            f.write(f"Applied then paired\n")
            f.write(f"Key: {hex_key}\n")
            f.write(f"Address: {address}\n")
        exit(0)
    else:
        print(f"    ✗ No match")

# Test: Maybe each rectangle needs DIFFERENT operation based on position
print("\n" + "="*70)
print("THEORY: Apply operations CYCLICALLY to rectangles")
print("="*70)

print("\n[*] Cycle: -1, ×2, %64, /4 repeating...")
operations = [
    lambda a: a - 1,
    lambda a: a * 2,
    lambda a: a % 64,
    lambda a: a / 4
]

transformed = []
for i, a in enumerate(areas[:64]):
    op = operations[i % len(operations)]
    transformed.append(int(op(a)))

bytes_out = []
for i in range(0, len(transformed), 2):
    if i + 1 < len(transformed):
        sum_val = transformed[i] + transformed[i + 1]
        byte_val = sum_val % 256
        bytes_out.append(byte_val)

hex_key, address, is_valid = validate_key(bytes_out)

if is_valid:
    print(f"    ✓ SUCCESS!")
    print(f"    Key: {hex_key}")
    print(f"    Address: {address}")
else:
    print(f"    ✗ No match")

print("\n" + "="*70)
print("FORMULA THEORY TESTING COMPLETE")
print("="*70)
