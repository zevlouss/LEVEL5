#!/usr/bin/env python3
"""
COMPREHENSIVE NEW THEORIES BASED ON DEEP ANALYSIS

After studying the puzzle, here are advanced theories to test:

1. DIGITAL ROOT: Sum digits until single digit (common in puzzles)
2. FIBONACCI-LIKE: Operations based on Fibonacci sequence
3. PRIME NUMBERS: Use only prime-indexed rectangles
4. CHECKSUM VALIDATION: The hint numbers are checksums
5. BASE CONVERSION: Convert between number bases
6. BITWISE OPERATIONS: Beyond XOR (AND, OR, shifts)
7. COMBINATION PAIRING: Use multiple rectangles per byte (not just 2)
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
    # Ensure all bytes are integers
    byte_list = [int(b) for b in byte_list]
    hex_key = ''.join(f"{b:02x}" for b in byte_list)
    try:
        for compressed in [True, False]:
            key = Key(import_key=hex_key, compressed=compressed)
            if key.address() == EXPECTED_ADDRESS:
                print(f"\n{'='*70}")
                print(f"🎉 SOLUTION FOUND! 🎉")
                print(f"{'='*70}")
                print(f"Private Key: {hex_key}")
                print(f"Address: {key.address()}")
                print(f"Compression: {'Compressed' if compressed else 'Uncompressed'}")
                with open("SOLUTION_FOUND.txt", "w") as f:
                    f.write(f"Private Key: {hex_key}\n")
                    f.write(f"Address: {key.address()}\n")
                    f.write(f"Compression: {compressed}\n")
                return hex_key, key.address(), True
    except:
        pass
    return hex_key, None, False

def digital_root(n):
    """Sum digits repeatedly until single digit"""
    while n >= 10:
        n = sum(int(d) for d in str(int(n)))
    return n

def is_prime(n):
    """Check if number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

print("="*70)
print("COMPREHENSIVE NEW THEORIES")
print("="*70)

rect_data = load_and_extract(IMAGE_PATH)
areas = [r['shell'] for r in rect_data[:64]]

print(f"\n[+] Loaded {len(areas)} rectangle areas")

test_count = 0

# THEORY 1: Digital Root
print("\n" + "="*70)
print("THEORY 1: Digital Root Transformation")
print("="*70)

print("[*] Testing digital root on areas before pairing...")
test_count += 1

transformed = [digital_root(a) for a in areas]
bytes_out = []
for i in range(0, 64, 2):
    sum_val = transformed[i] + transformed[i + 1]
    bytes_out.append(sum_val % 256)

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Digital root + sequential pairing: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# THEORY 2: Prime-indexed rectangles only
print("\n" + "="*70)
print("THEORY 2: Use Only Prime-Indexed Rectangles")
print("="*70)

prime_indices = [i for i in range(64) if is_prime(i)]
print(f"[*] Prime indices (0-63): {prime_indices}")
print(f"    Total: {len(prime_indices)} primes")

if len(prime_indices) >= 64:
    test_count += 1
    prime_areas = [areas[i] for i in prime_indices[:64]]
    bytes_out = []
    for i in range(0, len(prime_areas) - 1, 2):
        sum_val = prime_areas[i] + prime_areas[i + 1]
        bytes_out.append(int(sum_val) % 256)
    
    hex_key, address, is_valid = validate_key(bytes_out)
    print(f"    [{test_count}] Prime-indexed only: {'✓ MATCH!' if is_valid else '✗'}")
    
    if is_valid:
        exit(0)

# THEORY 3: Triple pairing (3 rectangles → 1 byte)
print("\n" + "="*70)
print("THEORY 3: Three Rectangles Per Byte (not two)")
print("="*70)

test_count += 1
bytes_out = []
for i in range(0, 64 - 2, 2):  # Step by 2 to get 32 bytes from 64 rectangles
    if i + 2 < 64:
        sum_val = areas[i] + areas[i + 1] + areas[i + 2]
        bytes_out.append(int(sum_val) % 256)

if len(bytes_out) == 32:
    hex_key, address, is_valid = validate_key(bytes_out)
    print(f"    [{test_count}] Triple pairing (3→1): {'✓ MATCH!' if is_valid else '✗'}")
    
    if is_valid:
        exit(0)

# THEORY 4: Bitwise operations (AND, OR, NOT)
print("\n" + "="*70)
print("THEORY 4: Bitwise Operations Instead of Addition")
print("="*70)

bitwise_ops = [
    ('AND', lambda a, b: int(a) & int(b)),
    ('OR', lambda a, b: int(a) | int(b)),
    ('XOR', lambda a, b: int(a) ^ int(b)),
    ('NAND', lambda a, b: ~(int(a) & int(b)) & 0xFF),
]

for op_name, op_func in bitwise_ops:
    test_count += 1
    bytes_out = []
    for i in range(0, 64, 2):
        byte_val = op_func(areas[i], areas[i + 1]) % 256
        bytes_out.append(byte_val)
    
    hex_key, address, is_valid = validate_key(bytes_out)
    print(f"    [{test_count}] {op_name:5s} operation: {'✓ MATCH!' if is_valid else '✗'}")
    
    if is_valid:
        exit(0)

# THEORY 5: Averaging instead of summing
print("\n" + "="*70)
print("THEORY 5: Average (not sum) of rectangle pairs")
print("="*70)

test_count += 1
bytes_out = []
for i in range(0, 64, 2):
    avg = (areas[i] + areas[i + 1]) / 2
    bytes_out.append(int(avg) % 256)

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Average pairing: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# THEORY 6: Difference instead of sum
print("\n" + "="*70)
print("THEORY 6: Difference (not sum) of rectangle pairs")
print("="*70)

test_count += 1
bytes_out = []
for i in range(0, 64, 2):
    diff = abs(areas[i] - areas[i + 1])
    bytes_out.append(int(diff) % 256)

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Difference pairing: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# THEORY 7: Product instead of sum
print("\n" + "="*70)
print("THEORY 7: Product (multiply) of rectangle pairs")
print("="*70)

test_count += 1
bytes_out = []
for i in range(0, 64, 2):
    product = areas[i] * areas[i + 1]
    bytes_out.append(int(product) % 256)

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Product pairing: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# THEORY 8: Concatenate as hex digits
print("\n" + "="*70)
print("THEORY 8: Use areas as HEX digits directly (0-F)")
print("="*70)

test_count += 1
# Map area to 0-15 range (one hex digit)
hex_digits = [int(a) % 16 for a in areas]
# Combine pairs into bytes
bytes_out = []
for i in range(0, 64, 2):
    byte_val = (hex_digits[i] << 4) | hex_digits[i + 1]
    bytes_out.append(byte_val)

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Hex digit concatenation: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# THEORY 9: Square root
print("\n" + "="*70)
print("THEORY 9: Square root transformation")
print("="*70)

test_count += 1
bytes_out = []
for i in range(0, 64, 2):
    sum_val = np.sqrt(areas[i]) + np.sqrt(areas[i + 1])
    bytes_out.append(int(sum_val) % 256)

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Square root pairing: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# THEORY 10: Logarithmic transformation
print("\n" + "="*70)
print("THEORY 10: Logarithmic transformation")
print("="*70)

test_count += 1
bytes_out = []
for i in range(0, 64, 2):
    sum_val = np.log(areas[i] + 1) + np.log(areas[i + 1] + 1)
    bytes_out.append(int(sum_val * 50) % 256)  # Scale up

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Logarithmic pairing: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# THEORY 11: Use BOTH outer and inner areas
print("\n" + "="*70)
print("THEORY 11: Combine outer and inner areas differently")
print("="*70)

test_count += 1
bytes_out = []
for i in range(0, 32):
    # Use outer of one, inner of next
    outer = rect_data[i * 2]['outer']
    inner = rect_data[i * 2 + 1]['inner']
    sum_val = outer + inner
    bytes_out.append(int(sum_val) % 256)

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Outer[i] + Inner[i+1]: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

# THEORY 12: Ratio-based
print("\n" + "="*70)
print("THEORY 12: Ratio of areas")
print("="*70)

test_count += 1
bytes_out = []
for i in range(0, 64, 2):
    if areas[i + 1] > 0:
        ratio = areas[i] / areas[i + 1]
        bytes_out.append(int(ratio * 100) % 256)
    else:
        bytes_out.append(0)

hex_key, address, is_valid = validate_key(bytes_out)
print(f"    [{test_count}] Ratio transformation: {'✓ MATCH!' if is_valid else '✗'}")

if is_valid:
    exit(0)

print("\n" + "="*70)
print(f"TESTED {test_count} NEW THEORIES - None matched")
print("="*70)
print("\nThese advanced theories also didn't solve it.")
print("The solution likely requires decoding the mini-puzzle hint correctly.")
