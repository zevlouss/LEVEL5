#!/usr/bin/env python3
"""
BREAKTHROUGH THEORIES - Based on Actual Solver Patterns

After analyzing the actual solver images from Levels 1-3, we discovered:
- ORIENTATION matters (Level 2 center bit flips everything)
- DIRECTIONAL encoding (Level 3 horizontal/vertical)
- BINARY operations (Levels 2 & 3)
- VISUAL cues determine HOW to read

Applying these patterns to Level 5!
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key

IMAGE_PATH = 'crypto5fix.png'
EXPECTED_ADDRESS = '1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'

def load_rectangles_with_details():
    """Load rectangles with shape details"""
    image = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rect_data = []
    
    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:
            outer_cnt = contours[parent]
            xo, yo, wo, ho = cv2.boundingRect(outer_cnt)
            
            shell_area = cv2.contourArea(outer_cnt) - cv2.contourArea(cnt)
            aspect_ratio = wo / ho if ho > 0 else 1.0
            
            rect_data.append({
                'shell': shell_area,
                'x': xo, 'y': yo,
                'w': wo, 'h': ho,
                'aspect_ratio': aspect_ratio,
                'is_wide': aspect_ratio > 1.3,
                'is_tall': aspect_ratio < 0.77,
                'is_square': 0.77 <= aspect_ratio <= 1.3
            })
    
    rect_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    return rect_data[:64]

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
print("BREAKTHROUGH THEORIES - Based on Actual Solving Patterns")
print("="*70)

rectangles = load_rectangles_with_details()
test_count = 0

# THEORY 1: Aspect Ratio Determines Encoding Method
print("\n" + "="*70)
print("THEORY 1: Aspect Ratio Determines Encoding (Like Level 3)")
print("="*70)
print("Level 3 used directional encoding based on visual orientation")
print("Testing: Wide/Tall/Square rectangles encode differently")

test_count += 1
print(f"\n[{test_count}] Shape-based encoding...")

bytes_out = []
for i in range(0, 64, 2):
    r1, r2 = rectangles[i], rectangles[i+1]
    
    # Wide rectangles: Use area directly
    if r1['is_wide']:
        v1 = int(r1['shell']) % 128
    # Tall rectangles: Invert
    elif r1['is_tall']:
        v1 = (256 - int(r1['shell'])) % 128
    # Square: Divide
    else:
        v1 = int(r1['shell'] / 2) % 128
    
    if r2['is_wide']:
        v2 = int(r2['shell']) % 128
    elif r2['is_tall']:
        v2 = (256 - int(r2['shell'])) % 128
    else:
        v2 = int(r2['shell'] / 2) % 128
    
    byte_val = (v1 + v2) % 256
    bytes_out.append(byte_val)

hex_key, address, is_valid = validate_key(bytes_out)
if is_valid:
    print(f"    🎉 SUCCESS! Shape-based encoding works!")
    print(f"    Private Key: {hex_key}")
    print(f"    Address: {address}")
    exit(0)
else:
    print(f"    ✗ No match")

# THEORY 2: Binary Bit Extraction (Like Levels 2 & 3)
print("\n" + "="*70)
print("THEORY 2: Binary Encoding (Like Levels 2 & 3)")
print("="*70)
print("Level 2 & 3 used binary encoding, not decimal")
print("Testing: Extract bits from areas")

test_count += 1
print(f"\n[{test_count}] Binary bit extraction (4+4 bits per byte)...")

bytes_out = []
for i in range(0, 64, 2):
    # Take low 4 bits from each area
    area1_bits = int(rectangles[i]['shell']) & 0x0F  # Low 4 bits
    area2_bits = int(rectangles[i+1]['shell']) & 0x0F  # Low 4 bits
    
    # Combine: area1 as high nibble, area2 as low nibble
    byte_val = (area1_bits << 4) | area2_bits
    bytes_out.append(byte_val)

hex_key, address, is_valid = validate_key(bytes_out)
if is_valid:
    print(f"    🎉 SUCCESS! Binary extraction works!")
    print(f"    Private Key: {hex_key}")
    print(f"    Address: {address}")
    exit(0)
else:
    print(f"    ✗ No match")

# Try different bit positions
for bit_start in [0, 4, 8, 12]:
    test_count += 1
    print(f"\n[{test_count}] Binary extraction starting at bit {bit_start}...")
    
    bytes_out = []
    for i in range(0, 64, 2):
        area1_int = int(rectangles[i]['shell'])
        area2_int = int(rectangles[i+1]['shell'])
        
        # Extract bits starting at bit_start
        bits1 = (area1_int >> bit_start) & 0x0F
        bits2 = (area2_int >> bit_start) & 0x0F
        
        byte_val = (bits1 << 4) | bits2
        bytes_out.append(byte_val)
    
    hex_key, address, is_valid = validate_key(bytes_out)
    if is_valid:
        print(f"        🎉 SUCCESS!")
        print(f"        Private Key: {hex_key}")
        print(f"        Address: {address}")
        exit(0)
    else:
        print(f"        ✗ No match")

# THEORY 3: Orientation Flipping Control (Like Level 2)
print("\n" + "="*70)
print("THEORY 3: Orientation Flipping (Like Level 2's Center Bit)")
print("="*70)
print("Level 2: Center bit controlled flipping of all other bits")
print("Testing: Numbers control flipping/orientation")

flip_controls_left = [int(d) for d in "09111819"]
flip_controls_right = [int(d) for d in "11122111"]

test_count += 1
print(f"\n[{test_count}] Flip control based on mini-puzzle numbers...")

bytes_out = []
for i in range(0, 64, 2):
    area1 = int(rectangles[i]['shell'])
    area2 = int(rectangles[i+1]['shell'])
    
    # Get flip controls
    byte_idx = i // 2
    flip1 = flip_controls_left[byte_idx % len(flip_controls_left)]
    flip2 = flip_controls_right[byte_idx % len(flip_controls_right)]
    
    # Apply flipping
    if flip1 == 1:
        v1 = area1 % 256
    elif flip1 == 0:
        v1 = (256 - (area1 % 256)) % 256  # Invert
    else:
        v1 = (area1 * flip1) % 256  # Scale
    
    if flip2 == 1:
        v2 = area2 % 256
    elif flip2 == 0:
        v2 = (256 - (area2 % 256)) % 256  # Invert
    else:
        v2 = (area2 * flip2) % 256  # Scale
    
    byte_val = (v1 + v2) // 2  # Average instead of sum
    bytes_out.append(byte_val)

hex_key, address, is_valid = validate_key(bytes_out)
if is_valid:
    print(f"    🎉 SUCCESS! Flip control works!")
    print(f"    Private Key: {hex_key}")
    print(f"    Address: {address}")
    exit(0)
else:
    print(f"    ✗ No match")

# THEORY 4: Non-Sequential Reading Order
print("\n" + "="*70)
print("THEORY 4: Reading Order Determined by Numbers")
print("="*70)
print("Testing: Use mini-puzzle numbers to determine pairing")

test_count += 1
print(f"\n[{test_count}] Grid-based pairing using hint numbers...")

# Arrange in 8×8 grid
grid = [rectangles[i]['shell'] for i in range(64)]
grid_2d = np.array(grid).reshape(8, 8)

order_left = [int(d) for d in "09111819"]
order_right = [int(d) for d in "11122111"]

bytes_out = []
for row in range(8):
    col1 = order_left[row % len(order_left)]
    col2 = order_right[row % len(order_right)]
    
    if col1 < 8 and col2 < 8:
        v1 = grid_2d[row][col1]
        v2 = grid_2d[row][col2]
        byte_val = int((v1 + v2) % 256)
        bytes_out.append(byte_val)

if len(bytes_out) >= 32:
    hex_key, address, is_valid = validate_key(bytes_out[:32])
    if is_valid:
        print(f"    🎉 SUCCESS! Grid reading order works!")
        print(f"    Private Key: {hex_key}")
        print(f"    Address: {address}")
        exit(0)
    else:
        print(f"    ✗ No match")

# THEORY 5: Width/Height as Separate Values (Like Level 1)
print("\n" + "="*70)
print("THEORY 5: Width/Height Encode Separately (Like Level 1)")
print("="*70)
print("Level 1: Position on axis encoded character")
print("Testing: Width and height as separate values")

test_count += 1
print(f"\n[{test_count}] Width/Height combination...")

bytes_out = []
for i in range(0, 64, 2):
    # Use width from one, height from another
    w1 = rectangles[i]['w']
    h2 = rectangles[i+1]['h']
    
    byte_val = ((w1 + h2) * 2) % 256
    bytes_out.append(byte_val)

hex_key, address, is_valid = validate_key(bytes_out)
if is_valid:
    print(f"    🎉 SUCCESS! Width/Height encoding works!")
    print(f"    Private Key: {hex_key}")
    print(f"    Address: {address}")
    exit(0)
else:
    print(f"    ✗ No match")

# THEORY 6: Area as Binary, Operations as Bit Manipulation
print("\n" + "="*70)
print("THEORY 6: Mini-Puzzle as Bit Operations")
print("="*70)
print("Testing: -1 (NOT), × (shift), % (mask), / (shift)")

test_count += 1
print(f"\n[{test_count}] Bit operations: -1=NOT, ×=SHIFT, %=MASK...")

bytes_out = []
for i in range(0, 64, 2):
    area1 = int(rectangles[i]['shell'])
    area2 = int(rectangles[i+1]['shell'])
    
    # Apply operations: -1 (flip), × 2 (left shift), % 256 (mask)
    v1 = (~area1) & 0xFF  # NOT and mask to 8 bits
    v2 = (area2 << 1) & 0xFF  # Left shift 1
    
    byte_val = (v1 ^ v2) & 0xFF  # XOR and mask
    bytes_out.append(byte_val)

hex_key, address, is_valid = validate_key(bytes_out)
if is_valid:
    print(f"    🎉 SUCCESS! Bit operations work!")
    print(f"    Private Key: {hex_key}")
    print(f"    Address: {address}")
    exit(0)
else:
    print(f"    ✗ No match")

print("\n" + "="*70)
print(f"BREAKTHROUGH THEORY TESTING COMPLETE")
print(f"Tested {test_count} pattern-based theories")
print("="*70)
print("\nThese theories based on actual solving patterns didn't match yet.")
print("But we're applying the CORRECT methodology:")
print("  • Orientation matters")
print("  • Binary encoding")
print("  • Visual cues determine reading method")
print("  • Mini-puzzle controls interpretation")
print("\nThe exact combination is still being found...")
