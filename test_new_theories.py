#!/usr/bin/env python3
"""
TEST NEW THEORIES FROM PATTERN ANALYSIS

Based on insights from Zden's previous puzzles, this script tests
the 7 new theories generated from pattern analysis.
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key
import json

IMAGE_PATH = 'crypto5fix.png'
EXPECTED_ADDRESS = '1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'

def load_rectangles():
    """Load rectangle data"""
    image = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    # Also load color version
    color_image = cv2.imread(IMAGE_PATH)
    
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rect_data = []
    
    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:
            outer_cnt = contours[parent]
            xo, yo, wo, ho = cv2.boundingRect(outer_cnt)
            
            rect_data.append({
                'shell': cv2.contourArea(outer_cnt) - cv2.contourArea(cnt),
                'x': xo, 'y': yo
            })
    
    rect_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    return rect_data[:64], color_image

def validate_key(byte_list):
    """Validate key"""
    if len(byte_list) != 32:
        return None, None, False
    byte_list = [int(b) % 256 for b in byte_list]
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
print("TESTING NEW THEORIES FROM PATTERN ANALYSIS")
print("="*70)

rectangles, color_image = load_rectangles()
areas = [r['shell'] for r in rectangles]

test_count = 0

# THEORY T1: Color-Based Encoding
print("\n" + "="*70)
print("THEORY T1: Color-Based Encoding")
print("="*70)
print("Reasoning: Level 4 used color channels")
print("Testing: Check for color data in crypto5fix.png")

if color_image is not None:
    print(f"\n[*] Image shape: {color_image.shape}")
    print(f"[*] Channels: {color_image.shape[2] if len(color_image.shape) > 2 else 1}")
    
    if len(color_image.shape) > 2:
        b, g, r = cv2.split(color_image)
        print(f"[*] Blue channel unique values: {len(np.unique(b))}")
        print(f"[*] Green channel unique values: {len(np.unique(g))}")
        print(f"[*] Red channel unique values: {len(np.unique(r))}")
        
        # Check if RGB channels are identical (grayscale)
        if np.array_equal(b, g) and np.array_equal(g, r):
            print("    ✗ Image is grayscale (all channels identical)")
        else:
            print("    ! Image has color data - investigating...")
            # Try using color channel values
            test_count += 1
    else:
        print("    ✗ Image is single-channel (grayscale)")

# THEORY T2: Sequence Generation
print("\n" + "="*70)
print("THEORY T2: Sequence Generation")
print("="*70)
print("Reasoning: Levels 2-3 used mathematical sequences")
print("Testing: Look for Fibonacci, primes, powers in areas")

# Check for Fibonacci-like patterns
def is_fibonacci_like(areas):
    """Check if areas follow Fibonacci-like pattern"""
    ratios = []
    for i in range(1, len(areas)):
        if areas[i-1] > 0:
            ratios.append(areas[i] / areas[i-1])
    
    # Golden ratio ≈ 1.618
    golden_ratio = 1.618
    close_to_golden = sum(1 for r in ratios if abs(r - golden_ratio) < 0.2)
    
    return close_to_golden, len(ratios)

test_count += 1
close, total = is_fibonacci_like(areas)
print(f"\n[*] Ratios close to golden ratio: {close}/{total}")
if close / total > 0.3:
    print("    ! Possible Fibonacci pattern detected")
else:
    print("    ✗ No clear Fibonacci pattern")

# THEORY T3: Multi-Step Mini-Puzzle
print("\n" + "="*70)
print("THEORY T3: Multi-Step Mini-Puzzle Operations")
print("="*70)
print("Reasoning: Mini-puzzle defines operation sequence")
print("Testing: Apply -1, ×, %, ÷ in sequence")

operations_sequences = [
    ("(-1, ×2, %64, ÷1)", lambda a: ((a - 1) * 2) % 64),
    ("(-1, ×4, %256, ÷1)", lambda a: ((a - 1) * 4) % 256),
    ("(area, ×1, %64, ×4)", lambda a: (int(a) % 64) * 4),
    ("(-1, ×64, %256, ÷4)", lambda a: (((a - 1) * 64) % 256) / 4 if a > 1 else 0),
]

for name, op_func in operations_sequences:
    test_count += 1
    print(f"\n[*] Testing sequence: {name}")
    
    transformed = [op_func(a) for a in areas]
    bytes_out = []
    for i in range(0, 64, 2):
        if i + 1 < len(transformed):
            sum_val = transformed[i] + transformed[i + 1]
            bytes_out.append(int(sum_val) % 256)
    
    hex_key, address, is_valid = validate_key(bytes_out)
    
    if is_valid:
        print(f"    🎉 SUCCESS! Sequence {name} works!")
        print(f"    Private Key: {hex_key}")
        print(f"    Address: {address}")
        exit(0)
    else:
        print(f"    ✗ No match")

# THEORY T4: Numbers as Operation Selectors
print("\n" + "="*70)
print("THEORY T4: Numbers as Stage Indicators")
print("="*70)
print("Reasoning: 09111819 and 11122111 select operations")
print("Testing: Use digits to choose operation per rectangle")

# Parse hint numbers
left_digits = [int(d) for d in "09111819"]   # [0,9,1,1,1,8,1,9]
right_digits = [int(d) for d in "11122111"]  # [1,1,1,2,2,1,1,1]

# Define operations 0-9
operations = {
    0: lambda a: a,
    1: lambda a: a - 1,
    2: lambda a: a * 2,
    3: lambda a: a * 3,
    4: lambda a: a / 4 if a >= 4 else a,
    5: lambda a: a % 128,
    6: lambda a: a + 6,
    7: lambda a: a * 7 % 256,
    8: lambda a: a / 8 if a >= 8 else a,
    9: lambda a: a + 9,
}

test_count += 1
print(f"\n[*] Applying operations based on hint digits (cycling)")

# Apply operations cyclically
transformed = []
for i, a in enumerate(areas):
    left_op = operations[left_digits[i % len(left_digits)]]
    right_op = operations[right_digits[i % len(right_digits)]]
    
    # Apply left, then right
    result = right_op(left_op(a))
    transformed.append(result)

bytes_out = []
for i in range(0, 64, 2):
    if i + 1 < len(transformed):
        sum_val = transformed[i] + transformed[i + 1]
        bytes_out.append(int(sum_val) % 256)

hex_key, address, is_valid = validate_key(bytes_out)

if is_valid:
    print(f"    🎉 SUCCESS! Operation selector theory works!")
    print(f"    Private Key: {hex_key}")
    print(f"    Address: {address}")
    exit(0)
else:
    print(f"    ✗ No match")

# THEORY T5: Grid Transformation
print("\n" + "="*70)
print("THEORY T5: 2D Grid Operations")
print("="*70)
print("Reasoning: 8×8 structure suggests matrix operations")
print("Testing: Transpose, rotate, reflect the grid")

grid = np.array(areas).reshape(8, 8)

transformations = [
    ("Transpose", np.transpose(grid)),
    ("Rotate 90°", np.rot90(grid)),
    ("Rotate 180°", np.rot90(grid, 2)),
    ("Rotate 270°", np.rot90(grid, 3)),
    ("Flip horizontal", np.fliplr(grid)),
    ("Flip vertical", np.flipud(grid)),
]

for name, transformed_grid in transformations:
    test_count += 1
    print(f"\n[*] Testing: {name}")
    
    flat = transformed_grid.flatten()
    bytes_out = []
    for i in range(0, 64, 2):
        if i + 1 < len(flat):
            sum_val = flat[i] + flat[i + 1]
            bytes_out.append(int(sum_val) % 256)
    
    hex_key, address, is_valid = validate_key(bytes_out)
    
    if is_valid:
        print(f"    🎉 SUCCESS! {name} works!")
        print(f"    Private Key: {hex_key}")
        print(f"    Address: {address}")
        exit(0)
    else:
        print(f"    ✗ No match")

# THEORY T6: FIX as Instruction
print("\n" + "="*70)
print("THEORY T6: 'FIX' as Directive")
print("="*70)
print("Reasoning: 'FIX' might mean something specific")
print("Testing: F=15, I=9, X=24 in hex")

# F=15, I=9, X=24 (hex values)
FIX_value = 15 + 9 + 24  # = 48

test_count += 1
print(f"\n[*] FIX as number: F(15) + I(9) + X(24) = {FIX_value}")
print(f"[*] Testing operations with {FIX_value}")

# Try: divide by 48, multiply by 48, modulo 48
fix_operations = [
    (f"/ {FIX_value}", lambda a: a / FIX_value),
    (f"* {FIX_value} % 256", lambda a: (a * FIX_value) % 256),
    (f"% {FIX_value}", lambda a: a % FIX_value),
]

for name, op in fix_operations:
    transformed = [op(a) for a in areas]
    bytes_out = []
    for i in range(0, 64, 2):
        if i + 1 < len(transformed):
            sum_val = transformed[i] + transformed[i + 1]
            bytes_out.append(int(sum_val) % 256)
    
    hex_key, address, is_valid = validate_key(bytes_out)
    
    if is_valid:
        print(f"    🎉 SUCCESS! FIX operation {name} works!")
        print(f"    Private Key: {hex_key}")
        print(f"    Address: {address}")
        exit(0)

print(f"    ✗ No match with FIX operations")

# THEORY T7: Cross-Rectangle Operations
print("\n" + "="*70)
print("THEORY T7: Non-Adjacent Rectangle Operations")
print("="*70)
print("Reasoning: Creative combinations like previous puzzles")
print("Testing: Operations between rectangles at specific distances")

# Use hint numbers as distances
distances = [9, 11, 18, 19, 12, 21]

for distance in distances:
    test_count += 1
    print(f"\n[*] Testing cross-operations at distance {distance}")
    
    bytes_out = []
    used = set()
    
    for i in range(64):
        if i in used:
            continue
        j = (i + distance) % 64
        if j not in used and len(bytes_out) < 32:
            sum_val = areas[i] + areas[j]
            bytes_out.append(int(sum_val) % 256)
            used.add(i)
            used.add(j)
    
    if len(bytes_out) == 32:
        hex_key, address, is_valid = validate_key(bytes_out)
        
        if is_valid:
            print(f"    🎉 SUCCESS! Distance {distance} works!")
            print(f"    Private Key: {hex_key}")
            print(f"    Address: {address}")
            exit(0)
        else:
            print(f"    ✗ No match")
    else:
        print(f"    ✗ Invalid byte count: {len(bytes_out)}")

print("\n" + "="*70)
print(f"THEORY TESTING COMPLETE")
print(f"Tested {test_count} new theory variations")
print("="*70)
print("\nNone of the pattern-based theories matched.")
print("This confirms the mini-puzzle decoding is truly critical.")
print("\nRecommendation: Focus on understanding the creator's previous")
print("mini-puzzle hints or contact the creator for clarification.")
