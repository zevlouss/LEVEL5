#!/usr/bin/env python3
"""
ULTIMATE COMPREHENSIVE SOLVER
Combining ALL insights and trying EXTREME variations

This includes:
- All previous approaches
- Reversals, reflections, rotations
- Different starting points
- Skip patterns
- Weighted combinations
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key
import hashlib

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
                'shell': shell_area,
                'w': wo, 'h': ho,
                'wi': wi, 'hi': hi
            })
    
    rect_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    return rect_data

def validate_key(byte_list):
    if len(byte_list) != 32:
        return None, None, False
    byte_list = [int(b) % 256 for b in byte_list]
    hex_key = ''.join(f"{b:02x}" for b in byte_list)
    try:
        for compressed in [True, False]:
            key = Key(import_key=hex_key, compressed=compressed)
            if key.address() == EXPECTED_ADDRESS:
                print(f"\n{'='*70}")
                print(f"🎉 🎉 🎉 PUZZLE SOLVED! 🎉 🎉 🎉")
                print(f"{'='*70}")
                print(f"Private Key: {hex_key}")
                print(f"Address: {key.address()}")
                print(f"Compression: {'Compressed' if compressed else 'Uncompressed'}")
                with open("SOLUTION_FOUND.txt", "w") as f:
                    f.write(f"Private Key: {hex_key}\n")
                    f.write(f"Address: {key.address()}\n")
                return hex_key, key.address(), True
    except:
        pass
    return hex_key, None, False

print("="*70)
print("ULTIMATE COMPREHENSIVE SOLVER")
print("Testing EXTREME variations...")
print("="*70)

rect_data = load_and_extract(IMAGE_PATH)
print(f"\n[+] Loaded {len(rect_data)} rectangles\n")

test_count = 0

# Get different area lists
area_types = {
    'shell': [r['shell'] for r in rect_data[:64]],
    'outer': [r['outer'] for r in rect_data[:64]],
    'inner': [r['inner'] for r in rect_data[:64]],
    'width': [r['w'] for r in rect_data[:64]],
    'height': [r['h'] for r in rect_data[:64]],
    'w*h': [r['w'] * r['h'] for r in rect_data[:64]],
    'w+h': [r['w'] + r['h'] for r in rect_data[:64]],
    'perimeter': [2*(r['w'] + r['h']) for r in rect_data[:64]],
}

# Transformation functions
transforms = {
    'none': lambda x: x,
    'sqrt': lambda x: int(np.sqrt(x)),
    'square': lambda x: int(x ** 2) % 1000,
    'log': lambda x: int(np.log(x + 1) * 100),
    'div10': lambda x: int(x / 10),
    'div4': lambda x: int(x / 4),
    'mod128': lambda x: int(x) % 128,
}

# Combination operations
combine_ops = {
    'sum': lambda a, b: a + b,
    'diff': lambda a, b: abs(a - b),
    'product': lambda a, b: a * b,
    'avg': lambda a, b: (a + b) / 2,
    'xor': lambda a, b: int(a) ^ int(b),
    'and': lambda a, b: int(a) & int(b),
    'or': lambda a, b: int(a) | int(b),
}

# Pairing patterns
def get_pairing_patterns():
    patterns = []
    
    # Standard pairs
    patterns.append(('sequential', [(i, i+1) for i in range(0, 64, 2)]))
    patterns.append(('reverse', [(63-i, 62-i) for i in range(0, 64, 2)]))
    
    # Skip patterns
    for skip in [2, 3, 4, 7, 8, 15, 16, 31, 32]:
        pairs = []
        for i in range(64 - skip):
            if len(pairs) < 32:
                pairs.append((i, i + skip))
        if len(pairs) == 32:
            patterns.append((f'skip_{skip}', pairs))
    
    # Interleaved (odd-even)
    pairs = [(i, i+1) for i in range(0, 32, 1)]  # First half
    pairs += [(i, i+1) for i in range(32, 64, 1)]  # Second half
    if len(pairs) >= 32:
        patterns.append(('interleaved', pairs[:32]))
    
    # Crossed (mirror)
    patterns.append(('crossed', [(i, 63-i) for i in range(32)]))
    
    return patterns

pairing_patterns = get_pairing_patterns()

print(f"Testing {len(area_types)} area types × {len(transforms)} transforms × {len(combine_ops)} combine ops × {len(pairing_patterns)} pairing patterns")
print(f"Total combinations: {len(area_types) * len(transforms) * len(combine_ops) * len(pairing_patterns)}")
print()

# Main testing loop
for area_name, areas in area_types.items():
    for transform_name, transform_func in transforms.items():
        for combine_name, combine_op in combine_ops.items():
            for pattern_name, pairs in pairing_patterns:
                test_count += 1
                
                try:
                    # Apply transformation
                    transformed = [transform_func(a) for a in areas]
                    
                    # Apply pairing
                    bytes_out = []
                    for idx1, idx2 in pairs:
                        if idx1 < len(transformed) and idx2 < len(transformed):
                            combined = combine_op(transformed[idx1], transformed[idx2])
                            byte_val = int(combined) % 256
                            bytes_out.append(byte_val)
                    
                    if len(bytes_out) == 32:
                        hex_key, address, is_valid = validate_key(bytes_out)
                        
                        if test_count % 100 == 0:
                            print(f"[{test_count:4d}] {area_name:10s} + {transform_name:8s} + {combine_name:8s} + {pattern_name:15s} = {'✓' if is_valid else '✗'}", flush=True)
                        
                        if is_valid:
                            print(f"\n{'='*70}")
                            print(f"SOLUTION FOUND!")
                            print(f"Area type: {area_name}")
                            print(f"Transform: {transform_name}")
                            print(f"Combine op: {combine_name}")
                            print(f"Pairing: {pattern_name}")
                            exit(0)
                except Exception as e:
                    # Skip errors (log, sqrt of negative, etc.)
                    pass

print(f"\n{'='*70}")
print(f"ULTIMATE SOLVER COMPLETE")
print(f"Tested {test_count} combinations - None matched")
print(f"{'='*70}")

# One more thing: Try using SHA256 or other hashes on the areas
print("\n[*] Trying hash-based approaches...")

areas = [r['shell'] for r in rect_data[:64]]

# Try: Hash each pair of areas, take first byte of hash
bytes_out = []
for i in range(0, 64, 2):
    data = str(int(areas[i])) + str(int(areas[i+1]))
    hash_bytes = hashlib.sha256(data.encode()).digest()
    bytes_out.append(hash_bytes[0])

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    SHA256 hash of area pairs: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# Try: MD5
bytes_out = []
for i in range(0, 64, 2):
    data = str(int(areas[i])) + str(int(areas[i+1]))
    hash_bytes = hashlib.md5(data.encode()).digest()
    bytes_out.append(hash_bytes[0])

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    MD5 hash of area pairs: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

print("\n" + "="*70)
print("ALL APPROACHES EXHAUSTED")
print("="*70)
print("\nThe puzzle requires information not derivable from the image alone.")
print("Focus on decoding the mini-puzzle hint or finding additional context.")
