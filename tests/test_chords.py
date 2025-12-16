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
    diminished_chord_score,
    close_voicing_score,
    chord_progression_similarity,
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
    print(f"    diminished_score:   {diminished_chord_score(prog):.3f}  (diminished chords)")
    print(f"    close_voicing:      {close_voicing_score(prog):.3f}  (adjacent degrees)")
    print(f"    prog_similarity:    {chord_progression_similarity(prog):.3f}  (chord similarity)")


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

    # === NEW: Test progressions for diminished and similarity ===

    # All diminished chords
    all_diminished = make_progression(
        [
            (0, "diminished"),  # i°
            (2, "diminished"),  # iii°
            (4, "diminished"),  # v°
            (6, "diminished"),  # vii°
        ]
    )
    test_progression("i° - iii° - v° - vii° (all diminished)", all_diminished)

    # Mixed with some diminished
    mixed_diminished = make_progression(
        [
            (0, "major"),       # I
            (6, "diminished"),  # vii°
            (0, "major"),       # I
            (4, "major"),       # V
        ]
    )
    test_progression("I - vii° - I - V (some diminished)", mixed_diminished)

    # Diminished 7th chords
    dim7_prog = make_progression(
        [
            (0, "dim7"),  # i°7
            (1, "dim7"),  # ii°7
            (0, "dim7"),  # i°7
            (4, "dom7"),  # V7
        ]
    )
    test_progression("i°7 - ii°7 - i°7 - V7 (dim7 chords)", dim7_prog)

    # Very similar progression (same chord type, close roots)
    very_similar = make_progression(
        [
            (0, "major"),  # I
            (0, "major"),  # I
            (1, "major"),  # II
            (0, "major"),  # I
        ]
    )
    test_progression("I - I - II - I (very similar)", very_similar)

    # Contrasting progression (different types, distant roots)
    contrasting = make_progression(
        [
            (0, "major"),       # I
            (4, "minor7"),      # v7
            (1, "diminished"),  # ii°
            (6, "dom7"),        # VII7
        ]
    )
    test_progression("I - v7 - ii° - VII7 (contrasting)", contrasting)

    # === Test cases for close_voicing_score ===

    # All minor7 chords - these have adjacent scale degrees!
    # minor7 = [0, 3, 7, 10] -> degrees [root, root+1, root+3, root+5]
    all_minor7 = make_progression(
        [
            (0, "minor7"),  # degrees: 0, 1, 3, 5
            (1, "minor7"),  # degrees: 1, 2, 4, 6
            (4, "minor7"),  # degrees: 4, 5, 0, 2
            (5, "minor7"),  # degrees: 5, 6, 1, 3
        ]
    )
    test_progression("all minor7 (adjacent degrees)", all_minor7)

    # All major7/dom7 - these DON'T have adjacent degrees
    # major7 = [0, 4, 7, 11] -> degrees [root, root+2, root+3, root+5]
    all_major7 = make_progression(
        [
            (0, "major7"),  # degrees: 0, 2, 3, 5
            (3, "major7"),  # degrees: 3, 5, 6, 1
            (4, "dom7"),    # degrees: 4, 6, 0, 2
            (0, "major7"),  # degrees: 0, 2, 3, 5
        ]
    )
    test_progression("major7/dom7 (no adjacent)", all_major7)

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
