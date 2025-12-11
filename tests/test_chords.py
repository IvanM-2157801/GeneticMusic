#!/usr/bin/env python3
"""Test chord fitness functions with sample inputs.

Run with: python -m tests.test_chords
Or: python tests/test_chords.py

This script tests chord primitive fitness functions using sample progressions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dataclasses import dataclass
from core.genome_ops import Chord, ChordProgression, CHORD_TYPES
from fitness.chords import (
    chord_variety,
    chord_type_variety,
    root_motion_smoothness,
    functional_harmony_score,
    resolution_bonus,
    triadic_bonus,
    seventh_chord_bonus,
)


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def make_progression(chords_data: list[tuple]) -> ChordProgression:
    """Create a chord progression from (root_degree, chord_type) tuples.

    Args:
        chords_data: List of (root_degree, chord_type_name) tuples
                    root_degree: 0-6 (I through VII)
                    chord_type_name: "major", "minor", "dom7", etc.
    """
    chords = []
    for root, chord_type in chords_data:
        intervals = CHORD_TYPES.get(chord_type, [0, 4, 7])
        chords.append(Chord(root_degree=root, intervals=intervals))
    return ChordProgression(chords=chords)


def chord_to_numeral(root: int, intervals: list[int]) -> str:
    """Convert chord to Roman numeral notation."""
    numerals = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
    numeral = numerals[root % 7]

    # Determine chord quality
    if intervals == [0, 4, 7]:
        return numeral.upper()  # Major
    elif intervals == [0, 3, 7]:
        return numeral.lower()  # Minor
    elif intervals == [0, 4, 7, 10]:
        return numeral.upper() + "7"  # Dominant 7
    elif intervals == [0, 4, 7, 11]:
        return numeral.upper() + "maj7"  # Major 7
    elif intervals == [0, 3, 7, 10]:
        return numeral.lower() + "7"  # Minor 7
    elif intervals == [0, 3, 6]:
        return numeral.lower() + "°"  # Diminished
    else:
        return f"{numeral}(?)"


def test_progression(name: str, prog: ChordProgression):
    """Test all chord fitness functions on a single progression."""
    print(f"\n  {name}:")
    chord_strs = [chord_to_numeral(c.root_degree, c.intervals) for c in prog.chords]
    print(f"    Chords: {' → '.join(chord_strs)}")
    print(f"    chord_variety:      {chord_variety(prog):.3f}  (root variety)")
    print(f"    chord_type_variety: {chord_type_variety(prog):.3f}  (quality variety)")
    print(
        f"    root_motion:        {root_motion_smoothness(prog):.3f}  (smooth motion)"
    )
    print(
        f"    functional_harmony: {functional_harmony_score(prog):.3f}  (I/IV/V usage)"
    )
    print(f"    resolution_bonus:   {resolution_bonus(prog):.3f}  (V-I patterns)")
    print(f"    triadic_bonus:      {triadic_bonus(prog):.3f}  (simple triads)")
    print(f"    seventh_chord:      {seventh_chord_bonus(prog):.3f}  (7th chords)")


def main():
    print_header("CHORD FITNESS TESTS")
    print("\nAll scores range 0.0-1.0. Higher = more of that quality.")
    print("\nChord types available:", list(CHORD_TYPES.keys()))

    # Classic I-IV-V-I progression
    classic_pop = make_progression(
        [
            (0, "major"),  # I
            (3, "major"),  # IV
            (4, "major"),  # V
            (0, "major"),  # I
        ]
    )
    test_progression("I - IV - V - I (classic pop)", classic_pop)

    # Jazz ii-V-I
    jazz_251 = make_progression(
        [
            (1, "minor7"),  # ii7
            (4, "dom7"),  # V7
            (0, "maj7"),  # Imaj7
        ]
    )
    test_progression("ii7 - V7 - Imaj7 (jazz)", jazz_251)

    # Same chord repeated
    repeated = make_progression(
        [
            (0, "major"),
            (0, "major"),
            (0, "major"),
            (0, "major"),
        ]
    )
    test_progression("I - I - I - I (static)", repeated)

    # Chromatic/unusual root motion
    chromatic_roots = make_progression(
        [
            (0, "major"),  # I
            (1, "major"),  # II (unusual)
            (2, "major"),  # III (unusual)
            (3, "major"),  # IV
        ]
    )
    test_progression("I - II - III - IV (chromatic)", chromatic_roots)

    # Circle of fifths
    circle_fifths = make_progression(
        [
            (0, "major"),  # I
            (3, "major"),  # IV
            (6, "minor"),  # vii
            (2, "minor"),  # iii
        ]
    )
    test_progression("I - IV - vii - iii (circle)", circle_fifths)

    # All 7th chords
    all_sevenths = make_progression(
        [
            (0, "maj7"),
            (1, "minor7"),
            (4, "dom7"),
            (0, "maj7"),
        ]
    )
    test_progression("Imaj7 - ii7 - V7 - Imaj7 (all 7ths)", all_sevenths)

    # Blues I-IV-I-V
    blues = make_progression(
        [
            (0, "dom7"),  # I7
            (3, "dom7"),  # IV7
            (0, "dom7"),  # I7
            (4, "dom7"),  # V7
        ]
    )
    test_progression("I7 - IV7 - I7 - V7 (blues)", blues)

    # Modal/ambient (no resolution)
    modal = make_progression(
        [
            (0, "sus2"),
            (5, "minor"),
            (3, "major"),
            (5, "minor"),
        ]
    )
    test_progression("Isus2 - vi - IV - vi (modal)", modal)

    print_header("CUSTOM CHORD FITNESS EXAMPLE")
    print("\nCombine primitives with weights for custom fitness:")
    print(
        """
    # Example: Pop chord fitness
    def pop_chord_fitness(prog: ChordProgression) -> float:
        return (
            0.35 * functional_harmony_score(prog) +
            0.25 * triadic_bonus(prog) +
            0.20 * resolution_bonus(prog) +
            0.20 * root_motion_smoothness(prog)
        )

    # Example: Jazz chord fitness
    def jazz_chord_fitness(prog: ChordProgression) -> float:
        return (
            0.30 * seventh_chord_bonus(prog) +
            0.25 * chord_type_variety(prog) +
            0.25 * resolution_bonus(prog) +
            0.20 * chord_variety(prog)
        )
    """
    )

    # Test the custom fitness functions
    def pop_chord_fitness(prog: ChordProgression) -> float:
        return (
            0.35 * functional_harmony_score(prog)
            + 0.25 * triadic_bonus(prog)
            + 0.20 * resolution_bonus(prog)
            + 0.20 * root_motion_smoothness(prog)
        )

    def jazz_chord_fitness(prog: ChordProgression) -> float:
        return (
            0.30 * seventh_chord_bonus(prog)
            + 0.25 * chord_type_variety(prog)
            + 0.25 * resolution_bonus(prog)
            + 0.20 * chord_variety(prog)
        )

    print("  Testing custom fitness functions:")
    test_progs = [
        ("I-IV-V-I (pop)", classic_pop),
        ("ii7-V7-I (jazz)", jazz_251),
        ("I-I-I-I (static)", repeated),
        ("Blues", blues),
    ]

    print("\n    pop_chord_fitness:")
    for name, prog in test_progs:
        print(f"      {name}: {pop_chord_fitness(prog):.3f}")

    print("\n    jazz_chord_fitness:")
    for name, prog in test_progs:
        print(f"      {name}: {jazz_chord_fitness(prog):.3f}")

    print_header("CHORD TYPES REFERENCE")
    print("\nAvailable chord types and their intervals:")
    for name, intervals in CHORD_TYPES.items():
        print(f"    {name:12s}: {intervals}")

    print_header("DONE")
    print("\nUse these primitives to build your own chord fitness functions!")


if __name__ == "__main__":
    main()
