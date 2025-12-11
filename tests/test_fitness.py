#!/usr/bin/env python3
"""Test fitness functions with sample inputs.

Run with: python -m tests.test_fitness
Or: python tests/test_fitness.py

This script tests all primitive fitness functions and prints their scores
for various test inputs. Use this to understand how each function behaves.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fitness.rhythm import (
    rhythm_complexity,
    rhythm_rest_ratio,
    rhythm_density,
    rhythm_syncopation,
    rhythm_groove,
    rhythm_consistency,
    rhythm_offbeat_emphasis,
)
from fitness.drums import (
    strong_beat_emphasis,
    backbeat_emphasis,
    sparsity,
    simplicity,
    offbeat_pattern,
)


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def test_rhythm(name: str, rhythm: str):
    """Test all rhythm fitness functions on a single pattern."""
    print(f"\n  Pattern: '{rhythm}' ({name})")
    print(f"    complexity:        {rhythm_complexity(rhythm):.3f}  (subdivision variety)")
    print(f"    rest_ratio:        {rhythm_rest_ratio(rhythm):.3f}  (% rests)")
    print(f"    density:           {rhythm_density(rhythm):.3f}  (notes per beat)")
    print(f"    syncopation:       {rhythm_syncopation(rhythm):.3f}  (subdivision changes)")
    print(f"    groove:            {rhythm_groove(rhythm):.3f}  (strong/weak alternation)")
    print(f"    consistency:       {rhythm_consistency(rhythm):.3f}  (pattern repetition)")
    print(f"    offbeat_emphasis:  {rhythm_offbeat_emphasis(rhythm):.3f}  (offbeat activity)")


def test_drum(name: str, rhythm: str):
    """Test all drum fitness functions on a single pattern."""
    print(f"\n  Pattern: '{rhythm}' ({name})")
    print(f"    strong_beat:   {strong_beat_emphasis(rhythm):.3f}  (beats 1/5)")
    print(f"    backbeat:      {backbeat_emphasis(rhythm):.3f}  (beats 3/7)")
    print(f"    sparsity:      {sparsity(rhythm):.3f}  (inverse density)")
    print(f"    simplicity:    {simplicity(rhythm):.3f}  (single hits)")
    print(f"    offbeat:       {offbeat_pattern(rhythm):.3f}  (offbeat pattern)")


def main():
    print_header("RHYTHM FITNESS TESTS")
    print("\nAll scores range 0.0-1.0. Higher = more of that quality.")

    # Test various rhythm patterns
    test_rhythm("all quarter notes", "11111111")
    test_rhythm("all eighth notes", "22222222")
    test_rhythm("all rests", "00000000")
    test_rhythm("sparse", "10001000")
    test_rhythm("syncopated", "21312240")
    test_rhythm("groovy", "21212121")
    test_rhythm("complex jazz", "31402310")
    test_rhythm("driving rock", "22242224")
    test_rhythm("ambient", "10110101")
    test_rhythm("electronic 4-on-floor", "44444444")

    print_header("DRUM FITNESS TESTS")
    print("\nAll scores range 0.0-1.0. Higher = more of that quality.")

    # Test drum patterns
    print("\n  --- KICK DRUM patterns ---")
    test_drum("four-on-floor", "11111111")
    test_drum("rock kick", "10001000")
    test_drum("sparse kick", "10000000")
    test_drum("busy kick", "12121212")

    print("\n  --- SNARE patterns ---")
    test_drum("backbeat snare", "00100010")
    test_drum("off-snare", "10001000")
    test_drum("busy snare", "11111111")

    print("\n  --- HI-HAT patterns ---")
    test_drum("steady 8ths", "22222222")
    test_drum("offbeat hats", "02020202")
    test_drum("sparse hats", "10101010")

    print_header("CUSTOM FITNESS EXAMPLE")
    print("\nCombine primitives with weights for custom fitness:")
    print("""
    # Example: Groovy bass rhythm fitness
    def bass_fitness(rhythm: str) -> float:
        return (
            0.35 * rhythm_consistency(rhythm) +  # Repetitive
            0.30 * rhythm_groove(rhythm) +       # Groovy
            0.20 * (1 - rhythm_rest_ratio(rhythm)) +  # Few rests
            0.15 * rhythm_density(rhythm)        # Moderate density
        )
    """)

    # Test the custom fitness
    def bass_fitness(rhythm: str) -> float:
        return (
            0.35 * rhythm_consistency(rhythm) +
            0.30 * rhythm_groove(rhythm) +
            0.20 * (1 - rhythm_rest_ratio(rhythm)) +
            0.15 * rhythm_density(rhythm)
        )

    print("  Testing bass_fitness on various patterns:")
    for name, rhythm in [
        ("steady 8ths", "22222222"),
        ("groovy", "21212121"),
        ("sparse", "10001000"),
        ("complex", "31402310"),
    ]:
        print(f"    '{rhythm}' ({name}): {bass_fitness(rhythm):.3f}")

    print_header("DONE")
    print("\nUse these primitives to build your own custom fitness functions!")
    print("See fitness/__init__.py for the full list of available primitives.")


if __name__ == "__main__":
    main()
