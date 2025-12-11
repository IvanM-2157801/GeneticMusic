#!/usr/bin/env python3
"""Test script to visualize how inter-layer contextual fitness works.

This script demonstrates:
1. How rhythmic compatibility is scored
2. How density balance affects fitness
3. How harmonic compatibility works between melodic layers
4. How voice leading is evaluated
5. How call-and-response patterns are detected
6. How context_group filters which layers share context

Run with: python test_contextual_fitness.py
"""

from core.music import Note, NoteName, Phrase, Layer
from fitness.contextual import ContextualFitness, create_contextual_fitness, get_context_groups
from fitness.base import FitnessFunction


class DummyFitness(FitnessFunction):
    """Dummy fitness that always returns 0.5 (neutral)."""
    def evaluate(self, layer: Layer) -> float:
        return 0.5


def create_layer_from_rhythm(name: str, rhythm: str, notes: list[tuple[NoteName, int]] = None) -> Layer:
    """Helper to create a layer from rhythm string and optional notes."""
    if notes:
        phrase = Phrase([Note(pitch, octave=oct) for pitch, oct in notes])
    else:
        # Create dummy notes based on rhythm
        note_count = sum(int(c) for c in rhythm if c != '0')
        phrase = Phrase([Note(NoteName.C, octave=4) for _ in range(note_count)])

    return Layer(
        name=name,
        phrases=[phrase],
        instrument="piano",
        rhythm=rhythm,
    )


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def test_rhythmic_compatibility():
    """Test how different rhythm patterns score against each other."""
    print_header("RHYTHMIC COMPATIBILITY")

    # Create a context layer with a specific rhythm
    context_rhythm = "11110000"  # Active first half, rest second half
    context_layer = create_layer_from_rhythm("context", context_rhythm)

    fitness = ContextualFitness(
        intrinsic_fitness=DummyFitness(),
        context_layers=[(context_layer, context_rhythm)],
        intrinsic_weight=0.0,  # Only measure context
        context_weight=1.0,
    )

    test_rhythms = [
        ("11110000", "Identical (same pattern)"),
        ("00001111", "Complementary (opposite pattern)"),
        ("11111111", "All active (no rests)"),
        ("00000000", "All rests"),
        ("10101010", "Alternating"),
        ("11001100", "50% overlap"),
        ("22220000", "Dense first half"),
        ("10100101", "Sparse alternating"),
    ]

    print(f"\nContext rhythm: {context_rhythm}")
    print(f"  (1=active on beats 1-4, rests on beats 5-8)\n")

    print(f"{'Test Rhythm':<15} {'Description':<35} {'Score':>8}")
    print("-" * 60)

    for rhythm, desc in test_rhythms:
        test_layer = create_layer_from_rhythm("test", rhythm)
        score = fitness._rhythmic_compatibility(rhythm, context_rhythm)
        print(f"{rhythm:<15} {desc:<35} {score:>8.3f}")


def test_density_balance():
    """Test how density differences affect fitness."""
    print_header("DENSITY BALANCE")

    context_rhythm = "22222222"  # Medium-high density
    context_layer = create_layer_from_rhythm("context", context_rhythm)

    fitness = ContextualFitness(
        intrinsic_fitness=DummyFitness(),
        context_layers=[(context_layer, context_rhythm)],
        intrinsic_weight=0.0,
        context_weight=1.0,
    )

    test_rhythms = [
        ("22222222", "Same density (all 2s)"),
        ("11111111", "Lower density (all 1s)"),
        ("44444444", "Higher density (all 4s)"),
        ("00000000", "No density (all rests)"),
        ("10101010", "Very sparse"),
        ("33333333", "Slightly higher (all 3s)"),
        ("21212121", "Mixed medium"),
        ("11110000", "Half active"),
    ]

    context_density = sum(int(c) for c in context_rhythm) / (len(context_rhythm) * 4.0)
    print(f"\nContext rhythm: {context_rhythm} (density: {context_density:.2f})")
    print(f"  Target: 0.2-0.5 difference from context for best score\n")

    print(f"{'Test Rhythm':<15} {'Description':<25} {'Density':>8} {'Diff':>8} {'Score':>8}")
    print("-" * 70)

    for rhythm, desc in test_rhythms:
        test_density = sum(int(c) for c in rhythm) / (len(rhythm) * 4.0)
        diff = abs(test_density - context_density)
        score = fitness._density_balance(rhythm, context_rhythm)
        print(f"{rhythm:<15} {desc:<25} {test_density:>8.2f} {diff:>8.2f} {score:>8.3f}")


def test_harmonic_compatibility():
    """Test how different melodic intervals score."""
    print_header("HARMONIC COMPATIBILITY")

    # Context melody: C4 E4 G4 C5 (C major arpeggio)
    context_notes = [
        (NoteName.C, 4), (NoteName.E, 4), (NoteName.G, 4), (NoteName.C, 5)
    ]
    context_layer = create_layer_from_rhythm("context", "1111", context_notes)

    fitness = ContextualFitness(
        intrinsic_fitness=DummyFitness(),
        context_layers=[(context_layer, "1111")],
        intrinsic_weight=0.0,
        context_weight=1.0,
    )

    test_melodies = [
        ([(NoteName.C, 4), (NoteName.E, 4), (NoteName.G, 4), (NoteName.C, 5)],
         "Unison (same notes)"),
        ([(NoteName.E, 4), (NoteName.G, 4), (NoteName.B, 4), (NoteName.E, 5)],
         "Thirds above (consonant)"),
        ([(NoteName.G, 4), (NoteName.B, 4), (NoteName.D, 5), (NoteName.G, 5)],
         "Fifths above (consonant)"),
        ([(NoteName.A, 4), (NoteName.C, 5), (NoteName.E, 5), (NoteName.A, 5)],
         "Sixths above (consonant)"),
        ([(NoteName.D, 4), (NoteName.F, 4), (NoteName.A, 4), (NoteName.D, 5)],
         "Seconds above (mild dissonance)"),
        ([(NoteName.CS, 4), (NoteName.F, 4), (NoteName.GS, 4), (NoteName.CS, 5)],
         "Chromatic clash (dissonant)"),
        ([(NoteName.FS, 4), (NoteName.AS, 4), (NoteName.CS, 5), (NoteName.FS, 5)],
         "Tritone relationship (dissonant)"),
    ]

    print(f"\nContext melody: C4 E4 G4 C5 (C major arpeggio)")
    print(f"  Consonant intervals: unison, 3rds, 5ths, 6ths, octaves")
    print(f"  Mild dissonance: 2nds, 4ths, 7ths")
    print(f"  Strong dissonance: tritones, minor 2nds/9ths\n")

    print(f"{'Test Melody':<35} {'Score':>8}")
    print("-" * 45)

    for notes, desc in test_melodies:
        test_phrase = Phrase([Note(pitch, octave=oct) for pitch, oct in notes])
        score = fitness._harmonic_compatibility(test_phrase, context_layer.phrases[0])
        note_names = " ".join(f"{n.pitch.name}{n.octave}" for n in test_phrase.notes)
        print(f"{desc:<35} {score:>8.3f}")


def test_voice_leading():
    """Test voice leading quality between two melodic lines."""
    print_header("VOICE LEADING QUALITY")

    # Context: ascending line C4 -> D4 -> E4 -> F4
    context_notes = [
        (NoteName.C, 4), (NoteName.D, 4), (NoteName.E, 4), (NoteName.F, 4)
    ]
    context_layer = create_layer_from_rhythm("context", "1111", context_notes)

    fitness = ContextualFitness(
        intrinsic_fitness=DummyFitness(),
        context_layers=[(context_layer, "1111")],
        intrinsic_weight=0.0,
        context_weight=1.0,
    )

    test_lines = [
        ([(NoteName.G, 4), (NoteName.F, 4), (NoteName.E, 4), (NoteName.D, 4)],
         "Contrary motion (descending)"),
        ([(NoteName.C, 4), (NoteName.D, 4), (NoteName.E, 4), (NoteName.F, 4)],
         "Parallel unisons (bad)"),
        ([(NoteName.G, 4), (NoteName.A, 4), (NoteName.B, 4), (NoteName.C, 5)],
         "Parallel fifths (bad)"),
        ([(NoteName.E, 4), (NoteName.F, 4), (NoteName.G, 4), (NoteName.A, 4)],
         "Parallel thirds (acceptable)"),
        ([(NoteName.E, 4), (NoteName.E, 4), (NoteName.E, 4), (NoteName.E, 4)],
         "Oblique motion (one voice static)"),
        ([(NoteName.E, 4), (NoteName.F, 4), (NoteName.E, 4), (NoteName.F, 4)],
         "Mixed motion"),
        ([(NoteName.A, 4), (NoteName.G, 4), (NoteName.A, 4), (NoteName.G, 4)],
         "Contrary oscillation"),
    ]

    print(f"\nContext melody: C4 -> D4 -> E4 -> F4 (ascending)")
    print(f"  Best: Contrary motion (opposite direction)")
    print(f"  Bad: Parallel 5ths/octaves")
    print(f"  OK: Parallel 3rds/6ths, oblique motion\n")

    print(f"{'Test Line':<35} {'Motion Type':<25} {'Score':>8}")
    print("-" * 70)

    for notes, desc in test_lines:
        test_phrase = Phrase([Note(pitch, octave=oct) for pitch, oct in notes])
        score = fitness._voice_leading_quality(test_phrase, context_layer.phrases[0])
        print(f"{desc:<35} {'':<25} {score:>8.3f}")


def test_call_response():
    """Test call-and-response pattern detection."""
    print_header("CALL AND RESPONSE PATTERNS")

    # Context: active-rest-active-rest pattern
    context_rhythm = "11001100"
    context_layer = create_layer_from_rhythm("context", context_rhythm)

    fitness = ContextualFitness(
        intrinsic_fitness=DummyFitness(),
        context_layers=[(context_layer, context_rhythm)],
        intrinsic_weight=0.0,
        context_weight=1.0,
    )

    test_rhythms = [
        ("00110011", "Perfect response (fills gaps)"),
        ("11001100", "Same pattern (no dialogue)"),
        ("10101010", "Constant alternation (too choppy)"),
        ("11111111", "Always active (ignores call)"),
        ("00000000", "Always rest (no response)"),
        ("01100110", "Offset response"),
        ("00111100", "Delayed response"),
        ("10011001", "Partial overlap"),
    ]

    print(f"\nContext rhythm: {context_rhythm}")
    print(f"  (Call pattern: active on 1-2, rest on 3-4, active on 5-6, rest on 7-8)")
    print(f"  Target: 10-30% alternation ratio for good dialogue\n")

    print(f"{'Test Rhythm':<15} {'Description':<30} {'Score':>8}")
    print("-" * 55)

    for rhythm, desc in test_rhythms:
        score = fitness._call_response_pattern(rhythm, context_rhythm)
        print(f"{rhythm:<15} {desc:<30} {score:>8.3f}")


def test_full_contextual_evaluation():
    """Test the complete contextual fitness evaluation."""
    print_header("FULL CONTEXTUAL EVALUATION")

    # Create a "band" context with multiple layers
    drum_layer = create_layer_from_rhythm("drums", "12121212")
    drum_layer.is_drum = True

    bass_notes = [(NoteName.C, 2), (NoteName.G, 2), (NoteName.A, 2), (NoteName.F, 2)]
    bass_layer = create_layer_from_rhythm("bass", "10101010", bass_notes)

    chord_notes = [(NoteName.E, 4), (NoteName.G, 4), (NoteName.C, 5), (NoteName.E, 5)]
    chord_layer = create_layer_from_rhythm("chords", "10001000", chord_notes)

    context_layers = [
        (drum_layer, "12121212"),
        (bass_layer, "10101010"),
        (chord_layer, "10001000"),
    ]

    fitness = ContextualFitness(
        intrinsic_fitness=DummyFitness(),
        context_layers=context_layers,
        intrinsic_weight=0.3,
        context_weight=0.7,
    )

    print("\nContext layers:")
    print(f"  - Drums:  12121212 (steady groove)")
    print(f"  - Bass:   10101010 (quarter notes, C G A F)")
    print(f"  - Chords: 10001000 (sparse hits)")
    print(f"\nWeights: Intrinsic=0.3, Context=0.7")
    print(f"Context metrics: rhythmic=0.25, density=0.15, harmonic=0.25, voice_leading=0.20, call_response=0.15\n")

    # Test different melody candidates
    test_melodies = [
        ("22002200", [(NoteName.G, 4), (NoteName.A, 4), (NoteName.B, 4), (NoteName.C, 5)],
         "Syncopated melody (fills gaps)"),
        ("11111111", [(NoteName.C, 4), (NoteName.D, 4), (NoteName.E, 4), (NoteName.F, 4)],
         "Steady melody (busy)"),
        ("10101010", [(NoteName.C, 4), (NoteName.G, 4), (NoteName.A, 4), (NoteName.F, 4)],
         "Same as bass (parallel)"),
        ("01010101", [(NoteName.E, 5), (NoteName.D, 5), (NoteName.C, 5), (NoteName.B, 4)],
         "Offbeat, contrary to bass"),
        ("20200202", [(NoteName.G, 4), (NoteName.E, 4), (NoteName.A, 4), (NoteName.F, 4)],
         "Complementary rhythm, 3rds with bass"),
    ]

    print(f"{'Rhythm':<12} {'Description':<35} {'Total':>8}")
    print("-" * 60)

    for rhythm, notes, desc in test_melodies:
        melody_layer = create_layer_from_rhythm("melody", rhythm, notes)
        score = fitness.evaluate(melody_layer)
        print(f"{rhythm:<12} {desc:<35} {score:>8.3f}")

    # Show breakdown for one example
    print("\n--- Detailed breakdown for 'Syncopated melody' ---")
    melody_layer = create_layer_from_rhythm("melody", "22002200",
        [(NoteName.G, 4), (NoteName.A, 4), (NoteName.B, 4), (NoteName.C, 5)])

    print(f"\nRhythmic compatibility:")
    for ctx_layer, ctx_rhythm in context_layers:
        if not ctx_layer.is_drum:
            score = fitness._rhythmic_compatibility("22002200", ctx_rhythm)
            print(f"  vs {ctx_layer.name}: {score:.3f}")

    print(f"\nDensity balance:")
    for ctx_layer, ctx_rhythm in context_layers:
        score = fitness._density_balance("22002200", ctx_rhythm)
        print(f"  vs {ctx_layer.name}: {score:.3f}")

    print(f"\nHarmonic compatibility (melodic layers only):")
    for ctx_layer, ctx_rhythm in context_layers:
        if not ctx_layer.is_drum and ctx_layer.phrases:
            score = fitness._harmonic_compatibility(melody_layer.phrases[0], ctx_layer.phrases[0])
            print(f"  vs {ctx_layer.name}: {score:.3f}")


def test_context_groups():
    """Test how context_group filters which layers share context."""
    print_header("CONTEXT GROUPS")

    # Create layers in different context groups
    # Group "verse": drums, bass, melody
    # Group "chorus": drums, bass, melody, lead
    # No group: pad (shares context with everyone)

    verse_drums = Layer(
        name="verse_drums", instrument="drums", rhythm="12121212",
        is_drum=True, layer_role="drums", context_group="verse"
    )
    verse_bass = Layer(
        name="verse_bass", instrument="bass", rhythm="10101010",
        phrases=[Phrase([Note(NoteName.C, 2), Note(NoteName.G, 2)])],
        layer_role="bass", context_group="verse"
    )
    verse_melody = Layer(
        name="verse_melody", instrument="synth", rhythm="11112222",
        phrases=[Phrase([Note(NoteName.E, 4), Note(NoteName.G, 4)])],
        layer_role="melody", context_group="verse"
    )

    chorus_drums = Layer(
        name="chorus_drums", instrument="drums", rhythm="22222222",
        is_drum=True, layer_role="drums", context_group="chorus"
    )
    chorus_bass = Layer(
        name="chorus_bass", instrument="bass", rhythm="11111111",
        phrases=[Phrase([Note(NoteName.C, 2), Note(NoteName.E, 2)])],
        layer_role="bass", context_group="chorus"
    )
    chorus_melody = Layer(
        name="chorus_melody", instrument="synth", rhythm="22221111",
        phrases=[Phrase([Note(NoteName.G, 4), Note(NoteName.A, 4)])],
        layer_role="melody", context_group="chorus"
    )
    chorus_lead = Layer(
        name="chorus_lead", instrument="lead", rhythm="11002200",
        phrases=[Phrase([Note(NoteName.B, 5), Note(NoteName.C, 6)])],
        layer_role="lead", context_group="chorus"
    )

    global_pad = Layer(
        name="global_pad", instrument="pad", rhythm="10001000",
        phrases=[Phrase([Note(NoteName.C, 4), Note(NoteName.E, 4)])],
        layer_role="pad", context_group=""  # Empty = shares with everyone
    )

    # Build evolved_layers dict
    evolved_layers = {
        "verse_drums": (verse_drums, "12121212"),
        "verse_bass": (verse_bass, "10101010"),
        "verse_melody": (verse_melody, "11112222"),
        "chorus_drums": (chorus_drums, "22222222"),
        "chorus_bass": (chorus_bass, "11111111"),
        "chorus_melody": (chorus_melody, "22221111"),
        "chorus_lead": (chorus_lead, "11002200"),
        "global_pad": (global_pad, "10001000"),
    }

    # Show context groups
    groups = get_context_groups(evolved_layers)

    print("\nContext groups defined:")
    for group, members in sorted(groups.items()):
        group_name = group if group else "(no group - shares with all)"
        print(f"  {group_name}: {', '.join(members)}")

    # Demonstrate filtering
    print("\n--- Creating contextual fitness for different groups ---\n")

    # Verse context: should only see verse layers
    print("Layer in 'verse' group sees:")
    verse_fitness = create_contextual_fitness(
        intrinsic_fitness=DummyFitness(),
        evolved_layers=evolved_layers,
        use_context=True,
        context_group="verse",
    )
    if isinstance(verse_fitness, ContextualFitness):
        for layer, rhythm in verse_fitness.context_layers:
            print(f"  - {layer.name} ({layer.layer_role})")
    else:
        print("  (no context layers)")

    # Chorus context: should only see chorus layers
    print("\nLayer in 'chorus' group sees:")
    chorus_fitness = create_contextual_fitness(
        intrinsic_fitness=DummyFitness(),
        evolved_layers=evolved_layers,
        use_context=True,
        context_group="chorus",
    )
    if isinstance(chorus_fitness, ContextualFitness):
        for layer, rhythm in chorus_fitness.context_layers:
            print(f"  - {layer.name} ({layer.layer_role})")
    else:
        print("  (no context layers)")

    # No group context: should see ALL layers
    print("\nLayer with no group (context_group='') sees:")
    all_fitness = create_contextual_fitness(
        intrinsic_fitness=DummyFitness(),
        evolved_layers=evolved_layers,
        use_context=True,
        context_group="",  # Empty = see all
    )
    if isinstance(all_fitness, ContextualFitness):
        for layer, rhythm in all_fitness.context_layers:
            print(f"  - {layer.name} ({layer.layer_role})")
    else:
        print("  (no context layers)")

    # Show role relationships within a group
    print("\n--- Role relationships within 'chorus' group ---")
    chorus_layers = [layer for layer, _ in evolved_layers.values() if layer.context_group == "chorus"]

    # Create a temporary fitness to access the relationship method
    temp_fitness = ContextualFitness(
        intrinsic_fitness=DummyFitness(),
        context_layers=[(l, "") for l in chorus_layers],
    )

    for i, layer1 in enumerate(chorus_layers):
        for layer2 in chorus_layers[i+1:]:
            relationship = temp_fitness._get_role_relationship(layer1, layer2)
            print(f"  {layer1.name} <-> {layer2.name}: {relationship}")


if __name__ == "__main__":
    test_rhythmic_compatibility()
    test_density_balance()
    test_harmonic_compatibility()
    test_voice_leading()
    test_call_response()
    test_full_contextual_evaluation()
    test_context_groups()

    print("\n" + "="*60)
    print(" Tests complete!")
    print("="*60)
