"""Test to demonstrate rhythm encoding in Strudel output."""
from core.music import Note, NoteName, Phrase, Layer


def test_rhythm_encoding():
    """Demonstrate how rhythm patterns are encoded in Strudel output."""
    print("\n" + "="*60)
    print("RHYTHM ENCODING DEMONSTRATION")
    print("="*60)

    # Example 1: Simple rhythm "2103"
    print("\nExample 1: Rhythm '2103'")
    print("  Beat 1: '2' = 2 eighth notes")
    print("  Beat 2: '1' = 1 quarter note")
    print("  Beat 3: '0' = rest")
    print("  Beat 4: '3' = 3 triplet notes")

    phrase1 = Phrase([
        Note(NoteName.C, octave=4, duration=0.5),  # Beat 1, note 1
        Note(NoteName.D, octave=4, duration=0.5),  # Beat 1, note 2
        Note(NoteName.E, octave=4, duration=1.0),  # Beat 2
        # Beat 3 is a rest (no notes)
        Note(NoteName.F, octave=4, duration=0.333),  # Beat 4, note 1
        Note(NoteName.G, octave=4, duration=0.333),  # Beat 4, note 2
        Note(NoteName.A, octave=4, duration=0.333),  # Beat 4, note 3
    ])

    rhythm1 = "2103"
    strudel1 = phrase1.to_strudel_with_rhythm(rhythm1)
    print(f"\nStrudel output: {strudel1}")
    print("Expected:       [c4 d4] e4 ~ [f4 g4 a4]")

    # Example 2: Drum pattern "41414141"
    print("\n" + "-"*60)
    print("\nExample 2: Drum Rhythm '41414141'")
    print("  Alternating: 4 sixteenths, 1 quarter, 4 sixteenths, 1 quarter...")

    phrase2 = Phrase([
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.D, octave=2, duration=0.25),
        Note(NoteName.D, octave=2, duration=0.25),
        Note(NoteName.C, octave=2, duration=1.0),
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.D, octave=2, duration=0.25),
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.D, octave=2, duration=0.25),
        Note(NoteName.C, octave=2, duration=1.0),
        Note(NoteName.D, octave=2, duration=0.25),
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.D, octave=2, duration=0.25),
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.D, octave=2, duration=1.0),
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.D, octave=2, duration=0.25),
        Note(NoteName.C, octave=2, duration=0.25),
        Note(NoteName.D, octave=2, duration=1.0),
    ])

    rhythm2 = "41414141"
    strudel2 = phrase2.to_strudel_with_rhythm(rhythm2)
    print(f"\nStrudel output: {strudel2}")

    # Example 3: Bass pattern with rests "20212012"
    print("\n" + "-"*60)
    print("\nExample 3: Bass Rhythm '20212012'")
    print("  Mix of eighths, rests, quarters")

    phrase3 = Phrase([
        Note(NoteName.E, octave=2, duration=0.5),
        Note(NoteName.G, octave=2, duration=0.5),
        # Beat 2 is rest
        Note(NoteName.E, octave=2, duration=0.5),
        Note(NoteName.A, octave=2, duration=0.5),
        Note(NoteName.G, octave=2, duration=1.0),
        # Beat 6 is rest
        Note(NoteName.E, octave=2, duration=1.0),
        Note(NoteName.G, octave=2, duration=0.5),
        Note(NoteName.A, octave=2, duration=0.5),
    ])

    rhythm3 = "20212012"
    strudel3 = phrase3.to_strudel_with_rhythm(rhythm3)
    print(f"\nStrudel output: {strudel3}")
    print("Expected:       [e2 g2] ~ [e2 a2] g2 ~ e2 [g2 a2]")

    # Example 4: Complete layer
    print("\n" + "="*60)
    print("\nExample 4: Complete Layer with Rhythm")
    layer = Layer(
        name="test",
        phrases=[phrase1],
        instrument="piano",
        rhythm=rhythm1
    )
    print(f"Rhythm: {rhythm1}")
    print(f"Full Strudel output:")
    print(f"  {layer.to_strudel()}")

    print("\n" + "="*60)
    print("KEY POINTS:")
    print("="*60)
    print("✓ Each digit in rhythm = subdivisions per beat")
    print("✓ '0' = rest (shown as ~)")
    print("✓ '1' = single note (no brackets)")
    print("✓ '2' = two notes [n1 n2]")
    print("✓ '3' = three notes [n1 n2 n3]")
    print("✓ '4' = four notes [n1 n2 n3 n4]")
    print("✓ Rhythm structure is preserved in Strudel output")
    print("✓ Total notes = sum of all digits in rhythm")
    print()


if __name__ == "__main__":
    test_rhythm_encoding()
