#!/usr/bin/env python3
"""
Deep analysis of rectangle structure
"""

import cv2
import numpy as np

IMAGE_PATH = 'crypto5fix.png'

def load_image(path):
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return binary, image

def analyze_rectangles():
    binary, original = load_image(IMAGE_PATH)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    shell_data = []
    
    for i, cnt in enumerate(contours):
        parent = hierarchy[0][i][3]
        if parent != -1:
            outer_cnt = contours[parent]
            
            # Get bounding boxes
            x, y, w, h = cv2.boundingRect(outer_cnt)
            xi, yi, wi, hi = cv2.boundingRect(cnt)
            
            # Calculate areas in different ways
            outer_area = cv2.contourArea(outer_cnt)
            inner_area = cv2.contourArea(cnt)
            shell_area = outer_area - inner_area
            
            # Pixel-based calculation
            rect_pixels = w * h
            inner_pixels = wi * hi
            pixel_shell = rect_pixels - inner_pixels
            
            shell_data.append({
                'index': len(shell_data),
                'x': x, 'y': y, 'w': w, 'h': h,
                'xi': xi, 'yi': yi, 'wi': wi, 'hi': hi,
                'outer_area': outer_area,
                'inner_area': inner_area,
                'shell_area': shell_area,
                'rect_pixels': rect_pixels,
                'inner_pixels': inner_pixels,
                'pixel_shell': pixel_shell,
                'width': w,
                'height': h,
                'inner_width': wi,
                'inner_height': hi
            })
    
    # Sort by position (top to bottom, left to right)
    shell_data.sort(key=lambda item: (round(item['y'] / 10), item['x']))
    
    print(f"Found {len(shell_data)} rectangles\n")
    print("="*80)
    print("First 10 rectangles analysis:")
    print("="*80)
    
    for i, rect in enumerate(shell_data[:10]):
        print(f"\nRectangle {i+1}:")
        print(f"  Position: ({rect['x']}, {rect['y']})")
        print(f"  Outer: {rect['w']}x{rect['h']} = {rect['rect_pixels']} pixels")
        print(f"  Inner: {rect['wi']}x{rect['hi']} = {rect['inner_pixels']} pixels")
        print(f"  Shell (contour): {rect['shell_area']:.1f}")
        print(f"  Shell (pixels): {rect['pixel_shell']}")
        print(f"  Difference: {rect['shell_area'] - rect['pixel_shell']:.1f}")
    
    # Print rectangle distribution
    print("\n" + "="*80)
    print("Rectangle size distribution:")
    print("="*80)
    
    sizes = {}
    for rect in shell_data[:64]:
        key = f"{rect['w']}x{rect['h']}"
        sizes[key] = sizes.get(key, 0) + 1
    
    for size, count in sorted(sizes.items(), key=lambda x: -x[1]):
        print(f"  {size}: {count} rectangles")
    
    # Check for patterns in first 64
    print("\n" + "="*80)
    print("Analysis of first 64 rectangles:")
    print("="*80)
    
    areas_64 = [r['shell_area'] for r in shell_data[:64]]
    print(f"Min area: {min(areas_64):.1f}")
    print(f"Max area: {max(areas_64):.1f}")
    print(f"Mean area: {np.mean(areas_64):.1f}")
    print(f"Median area: {np.median(areas_64):.1f}")
    
    # Try to detect row structure
    print("\n" + "="*80)
    print("Row structure (grouping by Y position):")
    print("="*80)
    
    rows = {}
    for rect in shell_data[:64]:
        row_key = round(rect['y'] / 10)
        if row_key not in rows:
            rows[row_key] = []
        rows[row_key].append(rect)
    
    for row_key in sorted(rows.keys()):
        rects_in_row = rows[row_key]
        print(f"Row {row_key}: {len(rects_in_row)} rectangles at Y≈{rects_in_row[0]['y']}")

if __name__ == "__main__":
    analyze_rectangles()
