#!/usr/bin/env python3
"""
CRITICAL NEW APPROACH: MULTIPLY corrections instead of ADD
Based on HomelessPhD's analysis showing multiplication of areas by line lengths
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key

IMAGE_PATH = 'crypto5fix.png'
EXPECTED_ADDRESS = '1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'
THRESHOLD_BINARY = 127

def load_image(path):
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found: {path}")
    _, binary = cv2.threshold(image, THRESHOLD_BINARY, 255, cv2.THRESH_BINARY)
    return binary

def find_rectangles_detailed(image):
    """Extract outer, inner, and shell areas for each rectangle"""
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rect_data = []
    
    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:
            outer_cnt = contours[parent]
            
            # Get bounding boxes
            xo, yo, wo, ho = cv2.boundingRect(outer_cnt)
            xi, yi, wi, hi = cv2.boundingRect(cnt)
            
            # Calculate areas
            outer_area = cv2.contourArea(outer_cnt)
            inner_area = cv2.contourArea(cnt)
            shell_area = outer_area - inner_area
            
            # Also calculate pixel-based
            outer_pixels = wo * ho
            inner_pixels = wi * hi
            shell_pixels = outer_pixels - inner_pixels
            
            rect_data.append({
                'x': xo, 'y': yo,
                'outer_area': outer_area,
                'inner_area': inner_area,
                'shell_area': shell_area,
                'outer_pixels': outer_pixels,
                'inner_pixels': inner_pixels,
                'shell_pixels': shell_pixels
            })
    
    # Sort top-to-bottom, left-to-right
    rect_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    return rect_data

def try_multiply_corrections(rect_data, area_type='outer_area'):
    """Apply MULTIPLICATION corrections to rectangles 40 and 53"""
    areas = [r[area_type] for r in rect_data[:64]]
    
    # MULTIPLY (not add) as shown in HomelessPhD's MATLAB code
    areas[39] = areas[39] * 17  # Rectangle #40
    areas[52] = areas[52] * 6   # Rectangle #53
    
    return areas

def pair_sequential_mod256(areas):
    """Sequential pairing with mod 256"""
    bytes_out = []
    for i in range(0, len(areas), 2):
        if i + 1 < len(areas):
            sum_val = areas[i] + areas[i + 1]
            byte_val = int(sum_val) % 256
            bytes_out.append(byte_val)
    return bytes_out

def validate_key(byte_list, compressed=True):
    """Validate both compressed and uncompressed addresses"""
    if len(byte_list) != 32:
        return None, None, False
    
    hex_key = ''.join(f"{b:02x}" for b in byte_list)
    
    try:
        # Try compressed
        key_compressed = Key(import_key=hex_key, compressed=compressed)
        addr_compressed = key_compressed.address()
        
        if addr_compressed == EXPECTED_ADDRESS:
            return hex_key, addr_compressed, True, compressed
        
        # Try uncompressed if compressed failed
        if compressed:
            key_uncompressed = Key(import_key=hex_key, compressed=False)
            addr_uncompressed = key_uncompressed.address()
            
            if addr_uncompressed == EXPECTED_ADDRESS:
                return hex_key, addr_uncompressed, True, False
        
        return hex_key, addr_compressed, False, compressed
    except Exception as e:
        return hex_key, None, False, compressed

def main():
    print("="*70)
    print("MULTIPLY CORRECTION APPROACH (from HomelessPhD analysis)")
    print("="*70)
    
    binary = load_image(IMAGE_PATH)
    rect_data = find_rectangles_detailed(binary)
    
    print(f"\n[+] Found {len(rect_data)} rectangles")
    
    # Test different area types with multiplication
    area_types = ['outer_area', 'inner_area', 'shell_area', 
                  'outer_pixels', 'inner_pixels', 'shell_pixels']
    
    # Different pairing methods
    pairing_patterns = {
        'sequential': lambda: [(i, i+1) for i in range(0, 64, 2)],
        'column_pairs': lambda: [(i, i+8) for r in range(4) for i in range(r*16, r*16+8)] + 
                                [(i, i+8) for r in range(4) for i in range(r*16+8, r*16+16)],
        'row_column': lambda: [(i, 8+i) for i in range(8)] + [(16+i, 24+i) for i in range(8)] +
                              [(32+i, 40+i) for i in range(8)] + [(48+i, 56+i) for i in range(8)],
    }
    
    test_count = 0
    
    for area_type in area_types:
        for pair_name, pair_func in pairing_patterns.items():
            test_count += 1
            
            # Get areas with MULTIPLY correction
            areas = try_multiply_corrections(rect_data, area_type)
            
            # Apply pairing
            pairs = pair_func()
            bytes_out = []
            for idx1, idx2 in pairs:
                if idx1 < len(areas) and idx2 < len(areas):
                    sum_val = areas[idx1] + areas[idx2]
                    byte_val = int(sum_val) % 256
                    bytes_out.append(byte_val)
            
            if len(bytes_out) != 32:
                continue
            
            hex_key, address, is_valid, compressed = validate_key(bytes_out)
            
            strategy = f"{area_type}+{pair_name}+multiply"
            print(f"[{test_count}] {strategy:50s} ", end="")
            
            if is_valid:
                print("✓ SUCCESS!")
                print(f"\n{'='*70}")
                print(f"🎉 PUZZLE SOLVED!")
                print(f"{'='*70}")
                print(f"Strategy: {strategy}")
                print(f"Compression: {'Compressed' if compressed else 'Uncompressed'}")
                print(f"Private Key: {hex_key}")
                print(f"Address: {address}")
                
                with open("SOLUTION_FOUND.txt", "w") as f:
                    f.write(f"Strategy: {strategy}\n")
                    f.write(f"Compression: {'Compressed' if compressed else 'Uncompressed'}\n")
                    f.write(f"Private Key: {hex_key}\n")
                    f.write(f"Address: {address}\n")
                return True
            else:
                print("✗")
    
    print(f"\n{'='*70}")
    print(f"❌ Tested {test_count} combinations with MULTIPLY - none matched")
    print(f"{'='*70}")
    
    # Now try without ANY corrections (maybe the lines are red herrings?)
    print("\n[*] Trying WITHOUT corrections...")
    test_count = 0
    
    for area_type in area_types:
        areas = [r[area_type] for r in rect_data[:64]]
        byte_list = pair_sequential_mod256(areas)
        hex_key, address, is_valid, compressed = validate_key(byte_list)
        
        test_count += 1
        strategy = f"{area_type}+sequential+no_corrections"
        print(f"[{test_count}] {strategy:50s} ", end="")
        
        if is_valid:
            print("✓ SUCCESS!")
            print(f"\nPrivate Key: {hex_key}")
            print(f"Address: {address}")
            return True
        else:
            print("✗")
    
    return False

if __name__ == "__main__":
    main()
