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
    # Advanced primitives
    total_hits,
    hit_count_score,
    hits_at_positions,
    avoid_positions,
    single_hits_at_positions,
    perfect_consistency,
    uniform_subdivision,
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


def test_advanced_drum(name: str, rhythm: str):
    """Test advanced drum fitness primitives on a single pattern."""
    print(f"\n  Pattern: '{rhythm}' ({name})")
    print(f"    total_hits:         {total_hits(rhythm):2d}    (raw count)")
    print(f"    hit_count(3-5):     {hit_count_score(rhythm, 3, 5):.3f}  (sparse kick range)")
    print(f"    hit_count(2-4):     {hit_count_score(rhythm, 2, 4):.3f}  (sparse snare range)")
    print(f"    hits_at[0]:         {hits_at_positions(rhythm, [0]):.3f}  (beat 1 anchor)")
    print(f"    hits_at[2,6]:       {hits_at_positions(rhythm, [2, 6]):.3f}  (backbeat)")
    print(f"    hits_at[1,5]:       {hits_at_positions(rhythm, [1, 5]):.3f}  (offbeats)")
    print(f"    avoid[2,6]:         {avoid_positions(rhythm, [2, 6]):.3f}  (avoid backbeat)")
    print(f"    avoid[0,4]:         {avoid_positions(rhythm, [0, 4]):.3f}  (avoid downbeats)")
    print(f"    single_at[2,6]:     {single_hits_at_positions(rhythm, [2, 6]):.3f}  (punchy backbeat)")
    print(f"    perfect_consist:    {perfect_consistency(rhythm):.3f}  (all same)")
    print(f"    uniform('2'):       {uniform_subdivision(rhythm, '2'):.3f}  (all 8ths)")


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

    print_header("ADVANCED DRUM PRIMITIVES")
    print("\nThese primitives enable fine-grained control for genre-specific patterns.")
    print("Use for DnB, breakbeat, and other styles requiring precise placement.")

    print("\n  --- DnB KICK candidates ---")
    test_advanced_drum("Amen-style kick", "11010100")  # hits on 0, 1, 3, 5
    test_advanced_drum("four-on-floor", "10001000")   # too regular
    test_advanced_drum("busy kick", "11111111")       # too many hits
    test_advanced_drum("sparse syncopated", "10010100")  # good sparse

    print("\n  --- DnB SNARE candidates ---")
    test_advanced_drum("backbeat only", "00100010")   # perfect sparse snare
    test_advanced_drum("busy snare", "11111111")      # too many hits
    test_advanced_drum("ghost notes", "01101010")     # has ghost notes
    test_advanced_drum("no backbeat", "10010001")     # missing backbeat

    print("\n  --- DnB HIHAT candidates ---")
    test_advanced_drum("perfect 8ths", "22222222")    # ideal DnB hihat
    test_advanced_drum("quarters", "11111111")        # acceptable
    test_advanced_drum("mixed", "21212121")           # less consistent
    test_advanced_drum("sparse hats", "20202020")     # has rests

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

    print_header("DnB FITNESS FUNCTIONS")
    print("\nComposed fitness functions using the advanced primitives.")
    print("These show how primitives combine for genre-specific drum patterns.")

    # Import the DnB fitness functions
    from drum_n_ass import dnb_kick_fitness, dnb_snare_fitness, dnb_hihat_fitness

    print("\n  --- DnB KICK fitness (sparse, avoid backbeat, anchor beat 1) ---")
    for name, rhythm in [
        ("Amen-style", "11010100"),
        ("sparse syncopated", "10010100"),
        ("four-on-floor", "10001000"),
        ("busy", "11111111"),
        ("backbeat conflict", "10101010"),
    ]:
        print(f"    '{rhythm}' ({name}): {dnb_kick_fitness(rhythm):.3f}")

    print("\n  --- DnB SNARE fitness (sparse backbeat, single hits, avoid kicks) ---")
    for name, rhythm in [
        ("perfect backbeat", "00100010"),
        ("with ghost", "01100010"),
        ("too busy", "11111111"),
        ("wrong positions", "10001000"),
        ("subdivided", "00200020"),
    ]:
        print(f"    '{rhythm}' ({name}): {dnb_snare_fitness(rhythm):.3f}")

    print("\n  --- DnB HIHAT fitness (consistent 8ths, no rests) ---")
    for name, rhythm in [
        ("perfect 8ths", "22222222"),
        ("quarters", "11111111"),
        ("mixed", "21212121"),
        ("with rests", "20202020"),
        ("complex", "31402310"),
    ]:
        print(f"    '{rhythm}' ({name}): {dnb_hihat_fitness(rhythm):.3f}")

    print_header("DONE")
    print("\nUse these primitives to build your own custom fitness functions!")
    print("See fitness/drums.py for the full list of available primitives.")


if __name__ == "__main__":
    main()
