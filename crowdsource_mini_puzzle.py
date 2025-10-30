#!/usr/bin/env python3
"""
MINI-PUZZLE CROWDSOURCING TOOL

This interactive tool helps the community submit and test theories
about decoding the mini-puzzle hint:

   ┌─────────┐
   │   -1    │
   │   ×%:   │
   │  LXIV   │  (64 in Roman numerals)
   │   /*/   │
   └─────────┘
      FIX
   
   09111819    11122111

Usage:
  1. Run this script
  2. Choose a theory category
  3. Enter your interpretation
  4. Script tests it automatically
  5. Results saved to theories_tested.json
"""

import cv2
import numpy as np
from bitcoinlib.keys import Key
import json
import os
from datetime import datetime

IMAGE_PATH = 'crypto5fix.png'
EXPECTED_ADDRESS = '1cryptoGeCRiTzVgxBQcKFFjSVydN1GW7'
THEORIES_FILE = 'theories_tested.json'

def load_rectangles():
    """Load and extract rectangle data"""
    image = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rect_data = []
    
    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:
            outer_cnt = contours[parent]
            xo, yo, wo, ho = cv2.boundingRect(outer_cnt)
            xi, yi, wi, hi = cv2.boundingRect(cnt)
            
            rect_data.append({
                'outer': cv2.contourArea(outer_cnt),
                'inner': cv2.contourArea(cnt),
                'shell': cv2.contourArea(outer_cnt) - cv2.contourArea(cnt),
                'x': xo, 'y': yo, 'w': wo, 'h': ho
            })
    
    rect_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    return rect_data[:64]

def validate_key(byte_list):
    """Check if bytes generate the target address"""
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

def load_theories():
    """Load previously tested theories"""
    if os.path.exists(THEORIES_FILE):
        with open(THEORIES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_theory(theory_data):
    """Save a tested theory"""
    theories = load_theories()
    theories.append(theory_data)
    with open(THEORIES_FILE, 'w') as f:
        json.dump(theories, indent=2, fp=f)

def test_formula_theory(rectangles, formula_func, description):
    """Test a formula-based theory"""
    print(f"\n[*] Testing: {description}")
    
    areas = [r['shell'] for r in rectangles]
    
    try:
        # Apply formula
        transformed = [formula_func(a) for a in areas]
        
        # Pair sequentially
        bytes_out = []
        for i in range(0, 64, 2):
            if i + 1 < len(transformed):
                sum_val = transformed[i] + transformed[i + 1]
                bytes_out.append(int(sum_val) % 256)
        
        hex_key, address, is_valid = validate_key(bytes_out)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'category': 'formula',
            'description': description,
            'success': is_valid,
            'generated_key': hex_key,
            'generated_address': address
        }
        
        save_theory(result)
        
        if is_valid:
            print(f"    🎉 SUCCESS! This formula works!")
            print(f"    Private Key: {hex_key}")
            print(f"    Address: {address}")
            return True
        else:
            print(f"    ✗ No match")
            return False
            
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def test_pairing_theory(rectangles, pairing_func, description):
    """Test a pairing pattern theory"""
    print(f"\n[*] Testing: {description}")
    
    areas = [r['shell'] for r in rectangles]
    
    try:
        pairs = pairing_func(areas)
        
        if len(pairs) != 32:
            print(f"    ✗ Invalid pairing (got {len(pairs)} pairs, need 32)")
            return False
        
        bytes_out = []
        for val1, val2 in pairs:
            sum_val = val1 + val2
            bytes_out.append(int(sum_val) % 256)
        
        hex_key, address, is_valid = validate_key(bytes_out)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'category': 'pairing',
            'description': description,
            'success': is_valid,
            'generated_key': hex_key,
            'generated_address': address
        }
        
        save_theory(result)
        
        if is_valid:
            print(f"    🎉 SUCCESS! This pairing works!")
            print(f"    Private Key: {hex_key}")
            print(f"    Address: {address}")
            return True
        else:
            print(f"    ✗ No match")
            return False
            
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False

def interactive_mode():
    """Interactive mode for community members"""
    print("="*70)
    print("MINI-PUZZLE CROWDSOURCING TOOL")
    print("="*70)
    print("\nMini-Puzzle Hint:")
    print("   ┌─────────┐")
    print("   │   -1    │")
    print("   │   ×%:   │")
    print("   │  LXIV   │  (= 64)")
    print("   │   /*/   │")
    print("   └─────────┘")
    print("      FIX")
    print()
    print("   09111819    11122111")
    print()
    
    rectangles = load_rectangles()
    print(f"[+] Loaded {len(rectangles)} rectangles\n")
    
    theories = load_theories()
    print(f"[+] {len(theories)} theories tested so far\n")
    
    while True:
        print("\n" + "="*70)
        print("THEORY CATEGORIES:")
        print("="*70)
        print("1. Formula Operations (-1, ×%:, LXIV, /*/)")
        print("2. Pairing Patterns (how to pair 64 rectangles)")
        print("3. Number Interpretation (09111819, 11122111)")
        print("4. View Previous Theories")
        print("5. Exit")
        print()
        
        choice = input("Select category (1-5): ").strip()
        
        if choice == '1':
            formula_submenu(rectangles)
        elif choice == '2':
            pairing_submenu(rectangles)
        elif choice == '3':
            number_submenu(rectangles)
        elif choice == '4':
            view_theories()
        elif choice == '5':
            print("\nThank you for contributing!")
            break
        else:
            print("Invalid choice")

def formula_submenu(rectangles):
    """Formula theory submission"""
    print("\n" + "="*70)
    print("FORMULA THEORY")
    print("="*70)
    print("The mini-puzzle shows: -1, ×%:, LXIV (64), /*/")
    print()
    print("Common interpretations:")
    print("  Example 1: (area - 1) × 2 % 64")
    print("  Example 2: area % 64 × 4")
    print("  Example 3: (area / 64) × 256")
    print()
    
    print("Enter Python expression (use 'a' for area):")
    print("Example: (a - 1) * 2 % 64")
    formula_str = input("> ").strip()
    
    description = input("Brief description of your theory: ").strip()
    
    try:
        # Create lambda from user input (careful - this is for crowdsourcing)
        formula_func = eval(f"lambda a: {formula_str}")
        
        # Test with a sample value first
        test_val = formula_func(100)
        print(f"\n[*] Testing formula with sample area=100: result={test_val}")
        
        confirm = input("Test this formula? (y/n): ").strip().lower()
        if confirm == 'y':
            test_formula_theory(rectangles, formula_func, description)
        
    except Exception as e:
        print(f"Error in formula: {e}")

def pairing_submenu(rectangles):
    """Pairing pattern submission"""
    print("\n" + "="*70)
    print("PAIRING PATTERN THEORY")
    print("="*70)
    print("How should the 64 rectangles be paired into 32 bytes?")
    print()
    print("Predefined patterns:")
    print("  1. Sequential: (0+1), (2+3), (4+5), ...")
    print("  2. Skip by N: Custom offset pairing")
    print("  3. Grid-based: Based on 8×8 arrangement")
    print("  4. Number-guided: Use 09111819 / 11122111")
    print()
    
    pattern_choice = input("Select pattern (1-4): ").strip()
    
    if pattern_choice == '1':
        print("[*] Sequential pairing already tested extensively")
        
    elif pattern_choice == '2':
        offset = int(input("Enter skip offset (e.g., 7, 9, 11): "))
        
        def skip_pairing(areas):
            pairs = []
            used = set()
            for i in range(64):
                if i not in used and i + offset < 64:
                    if i + offset not in used:
                        pairs.append((areas[i], areas[i + offset]))
                        used.add(i)
                        used.add(i + offset)
                        if len(pairs) >= 32:
                            break
            return pairs
        
        test_pairing_theory(rectangles, skip_pairing, f"Skip pairing with offset {offset}")
        
    elif pattern_choice == '3':
        print("Grid-based pairing (8×8 grid)")
        print("  1. Pair rows: (row1+row2), (row3+row4), ...")
        print("  2. Pair columns: (col1+col2), (col3+col4), ...")
        print("  3. Pair diagonals")
        
        grid_choice = input("Select (1-3): ").strip()
        # Implement based on choice...
        print("[*] Grid-based pairing needs implementation")
        
    elif pattern_choice == '4':
        print("Using hint numbers: 09111819 and 11122111")
        print("Not yet implemented - contribute your interpretation!")

def number_submenu(rectangles):
    """Number interpretation submission"""
    print("\n" + "="*70)
    print("NUMBER INTERPRETATION")
    print("="*70)
    print("The mini-puzzle shows:")
    print("  Left:  09111819")
    print("  Right: 11122111")
    print()
    print("What do you think these numbers mean?")
    print()
    print("Possible interpretations:")
    print("  1. Byte values (09, 11, 18, 19) and (11, 12, 21, 11)")
    print("  2. Rectangle indices to use/skip")
    print("  3. Pairing instructions")
    print("  4. Checksum/verification")
    print("  5. Custom interpretation")
    print()
    
    interp = input("Select (1-5) or describe custom: ").strip()
    
    if interp == '1':
        print("\n[*] Testing if key starts with [09,11,18,19] and ends with [11,12,21,11]")
        # Already tested - check results
        print("    Already tested in previous runs - no match found")
        
    elif interp == '5':
        description = input("Describe your interpretation: ")
        print(f"\n[*] Theory recorded: {description}")
        print("    To test this, you'll need to implement the logic in the code")
        
        save_theory({
            'timestamp': datetime.now().isoformat(),
            'category': 'number_interpretation',
            'description': description,
            'success': False,
            'status': 'needs_implementation'
        })

def view_theories():
    """View previously tested theories"""
    theories = load_theories()
    
    print("\n" + "="*70)
    print(f"PREVIOUSLY TESTED THEORIES ({len(theories)} total)")
    print("="*70)
    
    if not theories:
        print("No theories tested yet.")
        return
    
    # Group by category
    by_category = {}
    for theory in theories:
        cat = theory.get('category', 'unknown')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(theory)
    
    for category, items in by_category.items():
        print(f"\n{category.upper()} ({len(items)} theories):")
        for i, theory in enumerate(items[-5:], 1):  # Show last 5
            status = "✓ SUCCESS" if theory.get('success') else "✗ Failed"
            desc = theory.get('description', 'No description')[:50]
            print(f"  {i}. [{status}] {desc}")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
