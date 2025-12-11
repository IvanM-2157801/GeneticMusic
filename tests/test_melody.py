#!/usr/bin/env python3
"""Test melody fitness functions with sample inputs.

Run with: python -m tests.test_melody
Or: python tests/test_melody.py

This script tests melody primitive fitness functions using sample phrases.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.music import Note, NoteName, Phrase, Layer
from fitness.base import (
    note_variety,
    rest_ratio,
    interval_smoothness,
    scale_adherence,
    rhythmic_variety,
    MAJOR_SCALE,
    MINOR_SCALE,
    PENTATONIC,
    BLUES_SCALE,
)


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def make_phrase(notes_data: list[tuple]) -> Phrase:
    """Create a phrase from (pitch, octave, duration) tuples.

    Args:
        notes_data: List of (NoteName, octave, duration) tuples
                   Use NoteName.REST for rests
    """
    notes = [Note(pitch=p, octave=o, duration=d) for p, o, d in notes_data]
    return Phrase(notes=notes)


def test_phrase(name: str, phrase: Phrase):
    """Test all melody fitness functions on a single phrase."""
    print(f"\n  {name}:")
    notes_str = " ".join(
        f"{n.pitch.name}{n.octave}" if n.pitch != NoteName.REST else "REST"
        for n in phrase.notes[:8]
    )
    if len(phrase.notes) > 8:
        notes_str += "..."
    print(f"    Notes: {notes_str}")
    print(f"    note_variety:       {note_variety(phrase):.3f}  (pitch variety)")
    print(f"    rest_ratio:         {rest_ratio(phrase):.3f}  (% rests)")
    print(
        f"    interval_smoothness:{interval_smoothness(phrase):.3f}  (small intervals)"
    )
    print(
        f"    scale_adherence:    {scale_adherence(phrase, MAJOR_SCALE):.3f}  (major scale)"
    )
    print(f"    rhythmic_variety:   {rhythmic_variety(phrase):.3f}  (duration variety)")


def main():
    print_header("MELODY FITNESS TESTS")
    print("\nAll scores range 0.0-1.0. Higher = more of that quality.")

    # Test phrase: C major scale ascending
    scale_ascending = make_phrase(
        [
            (NoteName.C, 4, 1.0),
            (NoteName.D, 4, 1.0),
            (NoteName.E, 4, 1.0),
            (NoteName.F, 4, 1.0),
            (NoteName.G, 4, 1.0),
            (NoteName.A, 4, 1.0),
            (NoteName.B, 4, 1.0),
            (NoteName.C, 5, 1.0),
        ]
    )
    test_phrase("C major scale (ascending)", scale_ascending)

    # Test phrase: Single repeated note
    repeated_note = make_phrase(
        [
            (NoteName.C, 4, 1.0),
            (NoteName.C, 4, 1.0),
            (NoteName.C, 4, 1.0),
            (NoteName.C, 4, 1.0),
        ]
    )
    test_phrase("Single repeated note (drone)", repeated_note)

    # Test phrase: Large jumps
    large_jumps = make_phrase(
        [
            (NoteName.C, 3, 1.0),
            (NoteName.G, 5, 1.0),
            (NoteName.C, 3, 1.0),
            (NoteName.G, 5, 1.0),
        ]
    )
    test_phrase("Large jumps (octave+)", large_jumps)

    # Test phrase: Chromatic line (non-scale)
    chromatic = make_phrase(
        [
            (NoteName.C, 4, 1.0),
            (NoteName.CS, 4, 1.0),
            (NoteName.D, 4, 1.0),
            (NoteName.DS, 4, 1.0),
            (NoteName.E, 4, 1.0),
            (NoteName.F, 4, 1.0),
        ]
    )
    test_phrase("Chromatic line", chromatic)

    # Test phrase: Mostly rests
    mostly_rests = make_phrase(
        [
            (NoteName.C, 4, 1.0),
            (NoteName.REST, 4, 1.0),
            (NoteName.REST, 4, 1.0),
            (NoteName.REST, 4, 1.0),
            (NoteName.G, 4, 1.0),
            (NoteName.REST, 4, 1.0),
        ]
    )
    test_phrase("Mostly rests (sparse)", mostly_rests)

    # Test phrase: Varied durations
    varied_durations = make_phrase(
        [
            (NoteName.C, 4, 0.25),
            (NoteName.D, 4, 0.5),
            (NoteName.E, 4, 1.0),
            (NoteName.F, 4, 2.0),
        ]
    )
    test_phrase("Varied durations", varied_durations)

    # Test phrase: Same duration throughout
    same_duration = make_phrase(
        [
            (NoteName.C, 4, 0.5),
            (NoteName.E, 4, 0.5),
            (NoteName.G, 4, 0.5),
            (NoteName.C, 5, 0.5),
        ]
    )
    test_phrase("Same duration (consistent)", same_duration)

    # Test phrase: Blues scale
    blues_phrase = make_phrase(
        [
            (NoteName.C, 4, 1.0),
            (NoteName.DS, 4, 1.0),
            (NoteName.F, 4, 1.0),
            (NoteName.FS, 4, 1.0),
            (NoteName.G, 4, 1.0),
            (NoteName.AS, 4, 1.0),
        ]
    )

    print_header("SCALE ADHERENCE COMPARISON")
    print("\nSame phrase tested against different scales:")
    print(f"\n  Blues phrase (C, Eb, F, F#, G, Bb):")
    print(f"    vs MAJOR_SCALE:     {scale_adherence(blues_phrase, MAJOR_SCALE):.3f}")
    print(f"    vs MINOR_SCALE:     {scale_adherence(blues_phrase, MINOR_SCALE):.3f}")
    print(f"    vs PENTATONIC:      {scale_adherence(blues_phrase, PENTATONIC):.3f}")
    print(f"    vs BLUES_SCALE:     {scale_adherence(blues_phrase, BLUES_SCALE):.3f}")

    print_header("CUSTOM MELODY FITNESS EXAMPLE")
    print("\nCombine primitives with weights for custom fitness:")
    print(
        """
    # Example: Melodic lead fitness
    def lead_melody_fitness(phrase: Phrase) -> float:
        return (
            0.30 * note_variety(phrase) +
            0.25 * (1 - interval_smoothness(phrase)) +  # Want jumps
            0.25 * scale_adherence(phrase, MAJOR_SCALE) +
            0.20 * (1 - rest_ratio(phrase))
        )

    # Example: Pad/ambient fitness
    def pad_fitness(phrase: Phrase) -> float:
        return (
            0.40 * interval_smoothness(phrase) +  # Smooth
            0.30 * (1 - note_variety(phrase)) +   # Repetitive
            0.30 * scale_adherence(phrase, PENTATONIC)
        )
    """
    )

    # Test the custom fitness functions
    def lead_melody_fitness(phrase: Phrase) -> float:
        return (
            0.30 * note_variety(phrase)
            + 0.25 * (1 - interval_smoothness(phrase))
            + 0.25 * scale_adherence(phrase, MAJOR_SCALE)
            + 0.20 * (1 - rest_ratio(phrase))
        )

    def pad_fitness(phrase: Phrase) -> float:
        return (
            0.40 * interval_smoothness(phrase)
            + 0.30 * (1 - note_variety(phrase))
            + 0.30 * scale_adherence(phrase, PENTATONIC)
        )

    print("  Testing custom fitness functions:")
    test_phrases = [
        ("Scale ascending", scale_ascending),
        ("Repeated note", repeated_note),
        ("Large jumps", large_jumps),
        ("Chromatic", chromatic),
    ]

    print("\n    lead_melody_fitness:")
    for name, phrase in test_phrases:
        print(f"      {name}: {lead_melody_fitness(phrase):.3f}")

    print("\n    pad_fitness:")
    for name, phrase in test_phrases:
        print(f"      {name}: {pad_fitness(phrase):.3f}")

    print_header("DONE")
    print("\nUse these primitives to build your own melody fitness functions!")


if __name__ == "__main__":
    main()
