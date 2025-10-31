#!/usr/bin/env python3
"""
BITCOIN CRYPTO PUZZLE LEVEL 5 - COMPREHENSIVE SOLUTION
========================================================
Tries multiple strategies to solve the puzzle
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key
import itertools

# Configuration
IMAGE_PATH = 'crypto5fix.png'
EXPECTED_ADDRESS = '1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'
THRESHOLD_BINARY = 127

def load_image(path):
    """Load and binarize the puzzle image"""
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found: {path}")
    _, binary = cv2.threshold(image, THRESHOLD_BINARY, 255, cv2.THRESH_BINARY)
    return binary

def find_shell_contours(image, sort_method='default'):
    """
    Extract shell areas from image with different sorting methods
    """
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    shell_data = []

    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:
            outer_cnt = contours[parent]
            outer_area = cv2.contourArea(outer_cnt)
            inner_area = cv2.contourArea(cnt)
            shell_area = outer_area - inner_area

            x, y, w, h = cv2.boundingRect(outer_cnt)
            shell_data.append({
                'area': shell_area,
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'outer_area': outer_area,
                'inner_area': inner_area
            })

    # Different sorting strategies
    if sort_method == 'default':
        # Original: top-to-bottom with rounding, then left-to-right
        shell_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    elif sort_method == 'strict_rows':
        # Strict row-by-row
        shell_data.sort(key=lambda item: (item['y'], item['x']))
    elif sort_method == 'left_to_right':
        # Left to right, then top to bottom
        shell_data.sort(key=lambda item: (item['x'], item['y']))
    elif sort_method == 'area_desc':
        # By area descending
        shell_data.sort(key=lambda item: -item['area'])
    elif sort_method == 'area_asc':
        # By area ascending
        shell_data.sort(key=lambda item: item['area'])
    
    return [item['area'] for item in shell_data]

def apply_operations(areas, operation='mod256'):
    """
    Apply different mathematical operations to get bytes
    """
    bytes_out = []
    
    for i in range(0, len(areas), 2):
        if i + 1 < len(areas):
            sum_val = areas[i] + areas[i + 1]
            
            if operation == 'mod256':
                byte_val = int(sum_val) % 256
            elif operation == 'div256':
                byte_val = int(sum_val) // 256 if sum_val >= 256 else int(sum_val)
                byte_val = byte_val % 256
            elif operation == 'sqrt_mod256':
                byte_val = int(np.sqrt(sum_val)) % 256
            elif operation == 'div16_mod256':
                byte_val = int(sum_val / 16) % 256
            elif operation == 'xor_mod256':
                byte_val = (int(areas[i]) ^ int(areas[i+1])) % 256
            else:
                byte_val = int(sum_val) % 256
            
            bytes_out.append(byte_val)
    
    return bytes_out

def validate_key(byte_list):
    """Generate private key and check if it matches"""
    if len(byte_list) != 32:
        return None, None, False
    
    hex_key = ''.join(f"{b:02x}" for b in byte_list)
    
    try:
        key = Key(import_key=hex_key)
        address = key.address()
        is_match = (address == EXPECTED_ADDRESS)
        return hex_key, address, is_match
    except Exception:
        return hex_key, None, False

def solve_with_strategy(areas, corrections=True, operation='mod256', name=""):
    """Try a specific solving strategy"""
    
    # Use first 64 rectangles
    test_areas = areas[:64].copy()
    
    # Apply corrections if enabled
    if corrections and len(test_areas) >= 53:
        test_areas[39] += 17  # Rectangle #40
        test_areas[52] += 6   # Rectangle #53
    
    # Apply operations to get bytes
    byte_list = apply_operations(test_areas, operation)
    
    # Validate
    hex_key, address, is_valid = validate_key(byte_list)
    
    if is_valid:
        print(f"\n{'='*60}")
        print(f"🎉 SUCCESS! PUZZLE SOLVED! 🎉")
        print(f"Strategy: {name}")
        print(f"{'='*60}")
        print(f"\nPrivate Key: {hex_key}")
        print(f"Address: {address}")
        
        with open("SOLUTION_FOUND.txt", "w") as f:
            f.write(f"SOLUTION - Strategy: {name}\n")
            f.write(f"Private Key: {hex_key}\n")
            f.write(f"Address: {address}\n")
        return True
    
    return False

def main():
    print("="*60)
    print("COMPREHENSIVE PUZZLE SOLVER")
    print("="*60)
    
    binary = load_image(IMAGE_PATH)
    
    # Try different combinations
    sort_methods = ['default', 'strict_rows', 'left_to_right', 'area_desc', 'area_asc']
    operations = ['mod256', 'div256', 'div16_mod256', 'sqrt_mod256']
    corrections_options = [True, False]
    
    strategies = list(itertools.product(sort_methods, operations, corrections_options))
    
    print(f"[*] Testing {len(strategies)} different strategies...\n")
    
    for i, (sort_method, operation, corrections) in enumerate(strategies, 1):
        areas = find_shell_contours(binary, sort_method)
        name = f"{sort_method} + {operation} + {'corrections' if corrections else 'no_corrections'}"
        
        print(f"[{i}/{len(strategies)}] Testing: {name}...", end=" ")
        
        if solve_with_strategy(areas, corrections, operation, name):
            return True
        
        print("✗")
    
    print("\n" + "="*60)
    print("❌ None of the standard strategies worked")
    print("="*60)
    print("\nThis suggests:")
    print("  1. A non-standard pairing pattern is needed")
    print("  2. Additional transformations are required")
    print("  3. The rectangles encode information differently")
    print("  4. More context from the puzzle creator is needed")
    
    return False

if __name__ == "__main__":
    main()
