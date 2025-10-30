#!/usr/bin/env python3
"""
Alternative approach: Try different area calculations and pairing patterns
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

def extract_rectangles(image, area_method='contour'):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    shell_data = []
    
    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:
            outer_cnt = contours[parent]
            x, y, w, h = cv2.boundingRect(outer_cnt)
            xi, yi, wi, hi = cv2.boundingRect(cnt)
            
            if area_method == 'contour':
                outer_area = cv2.contourArea(outer_cnt)
                inner_area = cv2.contourArea(cnt)
                shell_area = outer_area - inner_area
            elif area_method == 'pixels':
                shell_area = (w * h) - (wi * hi)
            elif area_method == 'outer_only':
                outer_area = cv2.contourArea(outer_cnt)
                shell_area = outer_area
            elif area_method == 'dimensions':
                # Use the dimensions themselves
                shell_area = w + h + wi + hi
            else:
                shell_area = cv2.contourArea(outer_cnt) - cv2.contourArea(cnt)
            
            shell_data.append({
                'area': shell_area,
                'x': x, 'y': y,
                'w': w, 'h': h
            })
    
    # Sort top-to-bottom, left-to-right
    shell_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    return [item['area'] for item in shell_data]

def pair_and_convert(areas, pairing_method='sequential', operation='mod256'):
    """
    Different pairing methods:
    - sequential: 1+2, 3+4, 5+6, ...
    - reverse: 64+63, 62+61, ...
    - mirror: 1+64, 2+63, 3+62, ...
    - odd_even: 1+3, 5+7, ... then 2+4, 6+8, ...
    - alternate: 1+32+1, 2+33, 3+34, ...
    """
    
    if pairing_method == 'sequential':
        pairs = [(i, i+1) for i in range(0, 64, 2)]
    elif pairing_method == 'reverse':
        pairs = [(63-i, 62-i) for i in range(0, 64, 2)]
    elif pairing_method == 'mirror':
        pairs = [(i, 63-i) for i in range(32)]
    elif pairing_method == 'odd_even':
        pairs = [(i, i+2) for i in range(0, 62, 4)] + [(i, i+2) for i in range(1, 62, 4)]
    elif pairing_method == 'alternate':
        pairs = [(i, i+32) for i in range(32)]
    elif pairing_method == 'every_8th':
        # Pair in rows if 8 per row
        pairs = []
        for row in range(8):
            for col in range(4):
                pairs.append((row * 8 + col * 2, row * 8 + col * 2 + 1))
    else:
        pairs = [(i, i+1) for i in range(0, 64, 2)]
    
    bytes_out = []
    for idx1, idx2 in pairs:
        if idx1 < len(areas) and idx2 < len(areas):
            sum_val = areas[idx1] + areas[idx2]
            
            if operation == 'mod256':
                byte_val = int(sum_val) % 256
            elif operation == 'div10_mod256':
                byte_val = int(sum_val / 10) % 256
            elif operation == 'div8_mod256':
                byte_val = int(sum_val / 8) % 256
            elif operation == 'sum_digits':
                # Sum of decimal digits mod 256
                byte_val = sum(int(d) for d in str(int(sum_val))) % 256
            else:
                byte_val = int(sum_val) % 256
            
            bytes_out.append(byte_val)
    
    return bytes_out

def validate_key(byte_list):
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

def main():
    print("="*70)
    print("ALTERNATIVE PUZZLE SOLVER")
    print("="*70)
    
    binary = load_image(IMAGE_PATH)
    
    area_methods = ['contour', 'pixels', 'outer_only']
    pairing_methods = ['sequential', 'reverse', 'mirror', 'odd_even', 'alternate', 'every_8th']
    operations = ['mod256', 'div10_mod256', 'div8_mod256', 'sum_digits']
    corrections = [True, False]
    
    total = 0
    for area_method in area_methods:
        for pairing_method in pairing_methods:
            for operation in operations:
                for use_corrections in corrections:
                    total += 1
                    
                    areas = extract_rectangles(binary, area_method)
                    if len(areas) < 64:
                        continue
                    
                    # Apply corrections
                    if use_corrections:
                        areas[39] += 17
                        areas[52] += 6
                    
                    byte_list = pair_and_convert(areas[:64], pairing_method, operation)
                    hex_key, address, is_valid = validate_key(byte_list)
                    
                    strategy = f"{area_method}+{pairing_method}+{operation}+{'corr' if use_corrections else 'nocorr'}"
                    print(f"[{total}] {strategy:50s} ", end="")
                    
                    if is_valid:
                        print("✓ SUCCESS!")
                        print(f"\n{'='*70}")
                        print(f"🎉 PUZZLE SOLVED!")
                        print(f"{'='*70}")
                        print(f"Strategy: {strategy}")
                        print(f"Private Key: {hex_key}")
                        print(f"Address: {address}")
                        
                        with open("SOLUTION_FOUND.txt", "w") as f:
                            f.write(f"Strategy: {strategy}\n")
                            f.write(f"Private Key: {hex_key}\n")
                            f.write(f"Address: {address}\n")
                        return True
                    else:
                        print("✗")
    
    print(f"\n{'='*70}")
    print(f"❌ Tested {total} combinations - none matched")
    print(f"{'='*70}")
    return False

if __name__ == "__main__":
    main()
