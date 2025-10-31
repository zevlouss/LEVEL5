#!/usr/bin/env python3
"""
Decode the mini-puzzle hint from the image:

Looking at the hint in bottom-left corner:
╔═══════════╗
║    -1     ║
║    ×%:    ║
║   LXIV    ║
║    /*/    ║
╚═══════════╝
     FIX

09111819            11122111

LXIV = 64 in Roman numerals

Possible interpretations:
1. Formula: (-1 × % : 64 / * /)
2. Operations to apply: -1, multiply, modulo, 64, divide
3. Numbers 09111819 and 11122111 might be part of the key or checksum

Let me test if these numbers appear in the correct solution somehow
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key

IMAGE_PATH = 'crypto5fix.png'
EXPECTED_ADDRESS = '1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'

def load_image(path):
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return binary

def find_rectangles(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
    
    hex_key = ''.join(f"{b:02x}" for b in byte_list)
    try:
        for compressed in [True, False]:
            key = Key(import_key=hex_key, compressed=compressed)
            address = key.address()
            if address == EXPECTED_ADDRESS:
                return hex_key, address, True
    except:
        pass
    return hex_key, None, False

# Interpretation 1: The hint numbers might be the START and END of the key
def check_hint_numbers():
    """
    09111819 and 11122111
    
    Maybe the key starts with 0x09, 0x11, 0x18, 0x19
    and ends with 0x11, 0x12, 0x21, 0x11?
    """
    print("="*70)
    print("ANALYZING MINI-PUZZLE HINT")
    print("="*70)
    
    print("\nHint numbers interpretation:")
    print("Left side:  09111819")
    print("Right side: 11122111")
    print()
    
    # Could be hex bytes
    print("As hex bytes:")
    print(f"  Start: 0x09, 0x11, 0x18, 0x19")
    print(f"  End:   0x11, 0x12, 0x21, 0x11")
    print()
    
    # Could be decimal
    print("As decimal digits split:")
    print(f"  Start: {[int(d) for d in '09111819']}")
    print(f"  End:   {[int(d) for d in '11122111']}")
    print()

# Interpretation 2: Formula operations
def apply_formula_operations(rect_data):
    """
    Try interpreting the mini-puzzle as a formula:
    -1  (subtract 1)
    ×%: (multiply, then modulo)
    LXIV (64)
    /*/  (divide, multiply, divide)
    """
    print("\n" + "="*70)
    print("TESTING FORMULA INTERPRETATIONS")
    print("="*70)
    
    # Get first 64 rectangles
    test_cases = [
        {
            'name': 'Formula: (area - 1) * X % 64',
            'func': lambda areas: [((int(a) - 1) * 2) % 64 for a in areas]
        },
        {
            'name': 'Formula: area / 64 * 256',
            'func': lambda areas: [int((a / 64) * 256) % 256 for a in areas]
        },
        {
            'name': 'Formula: (area * 64) % 256',
            'func': lambda areas: [int(a * 64) % 256 for a in areas]
        },
        {
            'name': 'Formula: (area / 16) % 64 * 4',
            'func': lambda areas: [int((a / 16) % 64 * 4) for a in areas]
        },
    ]
    
    for case in test_cases:
        print(f"\n[*] Testing: {case['name']}")
        
        # Try with shell areas
        areas = [r['shell'] for r in rect_data[:64]]
        
        # Apply formula to get intermediate values
        intermediate = case['func'](areas)
        
        # Pair sequentially
        bytes_out = []
        for i in range(0, len(intermediate), 2):
            if i + 1 < len(intermediate):
                sum_val = intermediate[i] + intermediate[i + 1]
                byte_val = sum_val % 256
                bytes_out.append(byte_val)
        
        hex_key, address, is_valid = validate_key(bytes_out)
        
        if is_valid:
            print(f"    ✓ SUCCESS! Key: {hex_key}")
            print(f"    Address: {address}")
            return True
        else:
            print(f"    ✗ No match")
    
    return False

# Interpretation 3: Use 64 rectangles differently
def test_8x8_grid_patterns(rect_data):
    """
    The mini-puzzle shows an 8x8 grid structure
    Maybe we need to process it as a grid, not linearly
    """
    print("\n" + "="*70)
    print("TESTING 8x8 GRID PATTERNS")
    print("="*70)
    
    areas = [r['shell'] for r in rect_data[:64]]
    
    # Reshape into 8x8 grid
    grid = np.array(areas).reshape(8, 8)
    
    patterns = [
        {
            'name': 'Zigzag (left-right, right-left alternating)',
            'order': [i if row % 2 == 0 else (row * 8 + (7 - i % 8)) 
                     for row in range(8) for i in range(row * 8, row * 8 + 8)]
        },
        {
            'name': 'Spiral inward',
            'order': [0, 1, 2, 3, 4, 5, 6, 7, 15, 23, 31, 39, 47, 55, 63, 62, 61, 60, 59, 58, 57, 56, 
                     48, 40, 32, 24, 16, 8, 9, 10, 11, 12, 13, 14, 22, 30, 38, 46, 54, 53, 52, 51, 50, 
                     49, 41, 33, 25, 17, 18, 19, 20, 21, 29, 37, 45, 44, 43, 42, 34, 26, 27, 35, 36]
        },
        {
            'name': 'Diagonal (top-left to bottom-right)',
            'order': [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26, 33, 40, 48, 41, 34, 
                     27, 20, 13, 6, 7, 14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 
                     51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63]
        },
    ]
    
    for pattern in patterns:
        print(f"\n[*] Testing: {pattern['name']}")
        
        # Reorder areas according to pattern
        reordered = [areas[i] for i in pattern['order']]
        
        # Sequential pairing
        bytes_out = []
        for i in range(0, len(reordered), 2):
            if i + 1 < len(reordered):
                sum_val = reordered[i] + reordered[i + 1]
                byte_val = int(sum_val) % 256
                bytes_out.append(byte_val)
        
        hex_key, address, is_valid = validate_key(bytes_out)
        
        if is_valid:
            print(f"    ✓ SUCCESS! Key: {hex_key}")
            print(f"    Address: {address}")
            return True
        else:
            print(f"    ✗ No match")
    
    return False

def main():
    binary = load_image(IMAGE_PATH)
    rect_data = find_rectangles(binary)
    
    print(f"[+] Loaded {len(rect_data)} rectangles\n")
    
    check_hint_numbers()
    
    if apply_formula_operations(rect_data):
        return True
    
    if test_8x8_grid_patterns(rect_data):
        return True
    
    print("\n" + "="*70)
    print("❌ Mini-puzzle hint interpretations unsuccessful")
    print("="*70)
    print("\nThe mini-puzzle hint likely requires:")
    print("  1. Understanding the creator's previous puzzle patterns")
    print("  2. Recognizing a specific mathematical notation")
    print("  3. Additional context not visible in the images")
    
    return False

if __name__ == "__main__":
    main()
