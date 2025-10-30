#!/usr/bin/env python3
"""
BITCOIN CRYPTO PUZZLE LEVEL 5 - CORRECTED SOLUTION
===================================================
This solves the puzzle using the CORRECT interpretation:
- Sequential (consecutive/following) pairing of rectangles
- Not random pairing!
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key

# Configuration
IMAGE_PATH = 'crypto5fix.png'
EXPECTED_ADDRESS = '1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'
THRESHOLD_BINARY = 127

def load_image(path):
    """Load and binarize the puzzle image"""
    print(f"[*] Loading image: {path}")
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found: {path}")
    _, binary = cv2.threshold(image, THRESHOLD_BINARY, 255, cv2.THRESH_BINARY)
    return binary

def find_shell_contours(image):
    """
    Extract shell areas from image.
    Shell area = outer rectangle area - inner rectangle area
    """
    print("[*] Detecting rectangles and calculating shell areas...")
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    shell_areas = []
    boxes = []

    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:  # Has a parent = this is an inner contour
            outer_cnt = contours[parent]
            outer_area = cv2.contourArea(outer_cnt)
            inner_area = cv2.contourArea(cnt)
            shell_area = outer_area - inner_area

            x, y, w, h = cv2.boundingRect(outer_cnt)
            shell_areas.append(shell_area)
            boxes.append((x, y, w, h))

    # Sort rectangles top-to-bottom, then left-to-right
    combined = list(zip(shell_areas, boxes))
    sorted_combined = sorted(combined, key=lambda item: (round(item[1][1] / 10), item[1][0]))
    sorted_areas = [item[0] for item in sorted_combined]
    
    print(f"[+] Found {len(sorted_areas)} rectangles")
    return sorted_areas

def sequential_pairing_to_bytes(areas):
    """
    Pair rectangles SEQUENTIALLY as the hint says: "following rectangles"
    Pair 1+2, 3+4, 5+6, etc.
    Apply mod 256 to get bytes in proper range.
    """
    print("[*] Pairing rectangles sequentially (1+2, 3+4, 5+6, ...)...")
    bytes_out = []
    
    for i in range(0, len(areas), 2):
        if i + 1 < len(areas):
            sum_areas = areas[i] + areas[i + 1]
            byte_value = int(sum_areas) % 256
            bytes_out.append(byte_value)
            print(f"   Rect {i+1} + Rect {i+2}: {areas[i]:.1f} + {areas[i+1]:.1f} = {sum_areas:.1f} → byte {byte_value:3d} (0x{byte_value:02x})")
    
    return bytes_out

def validate_key(byte_list):
    """Generate private key and check if it matches the target address"""
    if len(byte_list) != 32:
        print(f"[!] ERROR: Expected 32 bytes, got {len(byte_list)}")
        return None, None, False
    
    hex_key = ''.join(f"{b:02x}" for b in byte_list)
    print(f"\n[*] Generated private key (hex): {hex_key}")
    
    try:
        key = Key(import_key=hex_key)
        address = key.address()
        is_match = (address == EXPECTED_ADDRESS)
        return hex_key, address, is_match
    except Exception as e:
        print(f"[!] Error generating key: {e}")
        return hex_key, None, False

def solve_puzzle():
    """Main solving function"""
    print("="*60)
    print("BITCOIN CRYPTO PUZZLE LEVEL 5 - SOLUTION ATTEMPT")
    print("="*60)
    
    # Load and analyze image
    binary = load_image(IMAGE_PATH)
    original_areas = find_shell_contours(binary)
    
    if len(original_areas) < 64:
        print(f"[!] ERROR: Need at least 64 rectangles, found {len(original_areas)}")
        return False
    
    # Use first 64 rectangles
    areas = original_areas[:64].copy()
    
    # Apply white-line pixel hint corrections
    print("\n[*] Applying white-line pixel corrections:")
    print(f"   Rectangle #40: {areas[39]:.1f} + 17 = {areas[39] + 17:.1f}")
    print(f"   Rectangle #53: {areas[52]:.1f} + 6 = {areas[52] + 6:.1f}")
    areas[39] += 17  # Rectangle #40 (0-indexed = 39)
    areas[52] += 6   # Rectangle #53 (0-indexed = 52)
    
    print("\n" + "="*60)
    # Convert to bytes using SEQUENTIAL pairing
    byte_list = sequential_pairing_to_bytes(areas)
    
    # Validate the key
    print("\n" + "="*60)
    print("VALIDATION")
    print("="*60)
    hex_key, address, is_valid = validate_key(byte_list)
    
    print(f"\n[*] Generated Address: {address}")
    print(f"[*] Expected Address:  {EXPECTED_ADDRESS}")
    print(f"\n{'='*60}")
    
    if is_valid:
        print("🎉 SUCCESS! PUZZLE SOLVED! 🎉")
        print(f"\nPrivate Key: {hex_key}")
        print(f"BTC Address: {address}")
        
        # Save to file
        with open("SOLUTION_FOUND.txt", "w") as f:
            f.write("BITCOIN CRYPTO PUZZLE LEVEL 5 - SOLUTION\n")
            f.write("="*60 + "\n\n")
            f.write(f"Private Key (hex): {hex_key}\n")
            f.write(f"BTC Address: {address}\n")
            f.write(f"Target Address: {EXPECTED_ADDRESS}\n")
            f.write(f"Match: {is_valid}\n")
        print("\n[+] Solution saved to SOLUTION_FOUND.txt")
        return True
    else:
        print("❌ Solution does not match expected address")
        print("\n[*] This might mean:")
        print("    1. The rectangles need different sorting")
        print("    2. Additional operations beyond mod 256 are needed")
        print("    3. Different pairing strategy required")
        print("    4. More pixel corrections needed")
        return False

if __name__ == "__main__":
    solve_puzzle()
