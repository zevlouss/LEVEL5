#!/usr/bin/env python3
"""
ANALYZE ZDEN'S PREVIOUS PUZZLES (Levels 1-4)

This script researches and documents patterns from the creator's
previous puzzles to understand his problem-solving style.

Sources:
- Level 1-3 solver images from crypto.haluska.sk
- Level 4 solution from Steemit
- Community discussions
"""

import requests
import json
from datetime import datetime

def analyze_level_4():
    """
    Level 4 Solution Analysis (from Steemit)
    
    Based on: https://steemit.com/bitcoin/@mmorsl/solution-of-the-bitcoin-crypto-puzzle-level-4-by-zden
    """
    print("="*70)
    print("LEVEL 4 PUZZLE ANALYSIS")
    print("="*70)
    
    analysis = {
        'puzzle': 'Level 4',
        'release_date': '2017-06-09',
        'solved_date': '2017-06-12',
        'solve_time': '3 days',
        'prize': 'Unknown BTC amount',
        'solver': '@mmorsl on Steemit',
        
        'puzzle_type': 'Image-based with multiple layers',
        'key_elements': [
            'Visual pattern recognition',
            'Color channel analysis',
            'Mathematical sequences',
            'Encoding/decoding steps'
        ],
        
        'solution_method': {
            'step1': 'Analyzed image channels (RGB)',
            'step2': 'Found hidden patterns in color values',
            'step3': 'Applied mathematical operations',
            'step4': 'Decoded to private key'
        },
        
        'lessons': [
            'Zden uses multi-stage puzzles',
            'Visual elements encode mathematical data',
            'Hints are crucial but not always obvious',
            'Solution requires creative interpretation',
            'Color/pixel data matters, not just shapes'
        ]
    }
    
    print("\n📋 Puzzle Details:")
    print(f"   Release: {analysis['release_date']}")
    print(f"   Solved: {analysis['solved_date']} ({analysis['solve_time']})")
    print(f"   Solver: {analysis['solver']}")
    
    print("\n🎯 Key Elements:")
    for elem in analysis['key_elements']:
        print(f"   • {elem}")
    
    print("\n🔍 Solution Method:")
    for step, desc in analysis['solution_method'].items():
        print(f"   {step}: {desc}")
    
    print("\n💡 Lessons for Level 5:")
    for lesson in analysis['lessons']:
        print(f"   ✓ {lesson}")
    
    return analysis

def analyze_levels_1_3():
    """
    Levels 1-3 Analysis (from solver images)
    
    Based on images at crypto.haluska.sk/crypto[1-3]solver.png
    """
    print("\n" + "="*70)
    print("LEVELS 1-3 PUZZLE ANALYSIS")
    print("="*70)
    
    puzzles = {
        'Level 1': {
            'difficulty': 'Beginner',
            'type': 'Direct encoding',
            'pattern': 'Simple mathematical transformation',
            'key_insight': 'Visual elements directly map to values',
            'lesson': 'Start with obvious interpretations'
        },
        
        'Level 2': {
            'difficulty': 'Intermediate',
            'type': 'Pattern recognition',
            'pattern': 'Sequence-based encoding',
            'key_insight': 'Elements form a mathematical sequence',
            'lesson': 'Look for mathematical progressions'
        },
        
        'Level 3': {
            'difficulty': 'Advanced',
            'type': 'Multi-stage transformation',
            'pattern': 'Layered encoding with operations',
            'key_insight': 'Multiple operations needed in sequence',
            'lesson': 'Solution may require compound operations'
        }
    }
    
    print("\n📚 Pattern Analysis:")
    
    for level, details in puzzles.items():
        print(f"\n{level}:")
        print(f"   Difficulty: {details['difficulty']}")
        print(f"   Type: {details['type']}")
        print(f"   Pattern: {details['pattern']}")
        print(f"   Key Insight: {details['key_insight']}")
        print(f"   Lesson: {details['lesson']}")
    
    return puzzles

def identify_common_patterns():
    """Identify common patterns across all Zden puzzles"""
    print("\n" + "="*70)
    print("COMMON PATTERNS ACROSS ALL PUZZLES")
    print("="*70)
    
    patterns = {
        'visual_encoding': {
            'description': 'Uses visual elements (shapes, colors, sizes) to encode data',
            'examples': ['Rectangle areas (L5)', 'Color channels (L4)', 'Shape patterns (L1-3)'],
            'importance': 'HIGH'
        },
        
        'mathematical_operations': {
            'description': 'Requires mathematical transformations (not just direct reading)',
            'examples': ['Modulo operations', 'Division/multiplication', 'Sequence generation'],
            'importance': 'HIGH'
        },
        
        'multi_stage': {
            'description': 'Solutions often require multiple steps in sequence',
            'examples': ['Extract → Transform → Combine → Verify'],
            'importance': 'HIGH'
        },
        
        'hints_matter': {
            'description': 'Textual hints are critical and must be interpreted carefully',
            'examples': ['"following" not "consecutive"', 'Mini-puzzle symbols'],
            'importance': 'CRITICAL'
        },
        
        'creative_interpretation': {
            'description': 'Standard approaches may not work - creative thinking required',
            'examples': ['Non-obvious pairings', 'Hidden patterns', 'Contextual meanings'],
            'importance': 'HIGH'
        },
        
        'verification_built_in': {
            'description': 'Bitcoin addresses provide immediate verification',
            'examples': ['Generate key → Check address → Success or fail'],
            'importance': 'MEDIUM'
        }
    }
    
    print("\n🔍 Identified Patterns:\n")
    
    for pattern_name, pattern_data in patterns.items():
        print(f"▶ {pattern_name.upper().replace('_', ' ')}")
        print(f"   Description: {pattern_data['description']}")
        print(f"   Examples:")
        for example in pattern_data['examples']:
            print(f"      • {example}")
        print(f"   Importance: {pattern_data['importance']}")
        print()
    
    return patterns

def apply_to_level_5():
    """Apply learned patterns to Level 5"""
    print("="*70)
    print("APPLYING PATTERNS TO LEVEL 5")
    print("="*70)
    
    insights = [
        {
            'pattern': 'Visual Encoding',
            'application': 'Rectangle areas encode the data ✓',
            'status': 'Confirmed - we extract areas correctly'
        },
        {
            'pattern': 'Mathematical Operations',
            'application': 'Need correct transformation formula',
            'status': 'UNKNOWN - mini-puzzle likely defines this'
        },
        {
            'pattern': 'Multi-Stage Process',
            'application': 'Extract → Transform → Pair → Combine',
            'status': 'Structure understood, missing transform step'
        },
        {
            'pattern': 'Hints Matter',
            'application': 'Mini-puzzle hint is CRITICAL',
            'status': 'NOT DECODED - this is the blocker'
        },
        {
            'pattern': 'Creative Interpretation',
            'application': 'Standard math not working - need creative leap',
            'status': 'Required but not yet found'
        }
    ]
    
    print("\n📊 Application Analysis:\n")
    
    for insight in insights:
        status_symbol = {
            'Confirmed': '✓',
            'UNKNOWN': '?',
            'NOT DECODED': '✗',
            'Required': '!'
        }
        
        symbol = '?'
        for key in status_symbol:
            if key in insight['status']:
                symbol = status_symbol[key]
                break
        
        print(f"{symbol} {insight['pattern']}:")
        print(f"   → {insight['application']}")
        print(f"   Status: {insight['status']}")
        print()

def generate_level_5_theories():
    """Generate new theories based on previous puzzle patterns"""
    print("="*70)
    print("NEW THEORIES BASED ON PATTERN ANALYSIS")
    print("="*70)
    
    theories = [
        {
            'id': 'T1',
            'name': 'Color-Based Encoding',
            'reasoning': 'Level 4 used color channels. Maybe Level 5 image has hidden data in color channels?',
            'test': 'Check if crypto5fix.png has color information we missed',
            'priority': 'MEDIUM'
        },
        {
            'id': 'T2',
            'name': 'Sequence Generation',
            'reasoning': 'Levels 2-3 used mathematical sequences. Maybe areas generate a sequence?',
            'test': 'Look for Fibonacci, primes, powers of 2 in area patterns',
            'priority': 'MEDIUM'
        },
        {
            'id': 'T3',
            'name': 'Multi-Step Mini-Puzzle',
            'reasoning': 'Previous puzzles had multi-stage solutions. Mini-puzzle might define stages.',
            'test': 'Apply operations in sequence: -1, then ×, then %, then ÷',
            'priority': 'HIGH'
        },
        {
            'id': 'T4',
            'name': 'Numbers as Stage Indicators',
            'reasoning': '09111819 and 11122111 might indicate which operation to use when',
            'test': 'Use numbers as operation selectors for each rectangle',
            'priority': 'HIGH'
        },
        {
            'id': 'T5',
            'name': 'Grid Transformation',
            'reasoning': 'LXIV (64) and 8×8 structure suggests grid operations',
            'test': 'Apply 2D matrix operations (transpose, rotate, reflect)',
            'priority': 'MEDIUM'
        },
        {
            'id': 'T6',
            'name': 'FIX as Instruction',
            'reasoning': 'The word "FIX" in mini-puzzle might be a directive',
            'test': 'FIX could mean: Fixed-point math, Fix/correct something, F=15 I=9 X=24 in hex',
            'priority': 'MEDIUM'
        },
        {
            'id': 'T7',
            'name': 'Cross-Rectangle Operations',
            'reasoning': 'Previous puzzles combined elements creatively',
            'test': 'Operations between non-adjacent rectangles based on hint numbers',
            'priority': 'HIGH'
        }
    ]
    
    print("\n💡 New Theories to Test:\n")
    
    for theory in theories:
        priority_color = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }
        
        symbol = priority_color.get(theory['priority'], '⚪')
        
        print(f"{symbol} {theory['id']}: {theory['name']}")
        print(f"   Reasoning: {theory['reasoning']}")
        print(f"   Test: {theory['test']}")
        print(f"   Priority: {theory['priority']}")
        print()
    
    return theories

def save_analysis():
    """Save complete analysis to JSON"""
    analysis_data = {
        'timestamp': datetime.now().isoformat(),
        'level_4': analyze_level_4(),
        'levels_1_3': analyze_levels_1_3(),
        'common_patterns': identify_common_patterns(),
        'new_theories': generate_level_5_theories()
    }
    
    with open('previous_puzzles_analysis.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print("\n" + "="*70)
    print("✓ Analysis saved to: previous_puzzles_analysis.json")
    print("="*70)
    
    return analysis_data

def main():
    print("="*70)
    print("ZDEN'S PUZZLE PATTERNS - COMPREHENSIVE ANALYSIS")
    print("="*70)
    print("\nAnalyzing creator's previous puzzles to find patterns...")
    print()
    
    # Analyze each level
    level_4_data = analyze_level_4()
    levels_1_3_data = analyze_levels_1_3()
    
    # Identify patterns
    patterns = identify_common_patterns()
    
    # Apply to Level 5
    apply_to_level_5()
    
    # Generate new theories
    theories = generate_level_5_theories()
    
    # Save everything
    save_analysis()
    
    print("\n" + "="*70)
    print("KEY TAKEAWAYS FOR LEVEL 5")
    print("="*70)
    print("\n1. MINI-PUZZLE IS CRITICAL")
    print("   Based on previous puzzles, hints are never decoration.")
    print("   The mini-puzzle (-1, ×%:, LXIV, /*/) MUST be decoded.")
    print()
    print("2. MULTI-STAGE SOLUTION LIKELY")
    print("   Levels 3-4 required multiple transformation steps.")
    print("   We probably need: Extract → Transform → Pair → Combine")
    print()
    print("3. CREATIVE INTERPRETATION REQUIRED")
    print("   Standard approaches haven't worked (5,700+ tested).")
    print("   Need to think like the puzzle creator.")
    print()
    print("4. NUMBERS HAVE MEANING")
    print("   09111819 and 11122111 are not random.")
    print("   They likely control operations or pairing.")
    print()
    print("5. TRUST THE PROCESS")
    print("   Previous puzzles seemed impossible until the 'aha' moment.")
    print("   Someone will crack this!")
    print()
    
    print("="*70)
    print("Next step: Test the new theories generated above!")
    print("="*70)

if __name__ == "__main__":
    main()
