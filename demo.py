#!/usr/bin/env python3
"""Demo template for creating custom fitness functions.

Run with: python demo.py

This template shows how to:
1. Define custom rhythm fitness using primitives
2. Define custom melody fitness using primitives
3. Evolve a single instrument layer
4. Generate a Strudel link to hear the result

Modify the fitness functions below to create your own style!
"""

from core.music import Phrase, Layer, NoteName
from fitness.base import (
    FitnessFunction,
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
from fitness.rhythm import (
    rhythm_complexity,
    rhythm_rest_ratio,
    rhythm_density,
    rhythm_syncopation,
    rhythm_groove,
    rhythm_consistency,
    rhythm_offbeat_emphasis,
)
from fitness.chords import (
    ChordFitnessFunction,
    chord_variety,
    chord_type_variety,
    root_motion_smoothness,
    functional_harmony_score,
    resolution_bonus,
    triadic_bonus,
    seventh_chord_bonus,
)
from core.genome_ops import ChordProgression
from layered_composer import LayeredComposer, LayerConfig


# =============================================================================
# CUSTOM RHYTHM FITNESS
# =============================================================================
# Modify the weights below to change how rhythms evolve.
# All primitives return 0.0-1.0. Higher = more of that quality.
#
# Available primitives:
#   rhythm_complexity(r)     - variety of subdivisions
#   rhythm_rest_ratio(r)     - ratio of rests (use 1-x to penalize rests)
#   rhythm_density(r)        - notes per beat
#   rhythm_syncopation(r)    - subdivision changes
#   rhythm_groove(r)         - strong/weak alternation
#   rhythm_consistency(r)    - pattern repetition
#   rhythm_offbeat_emphasis(r) - offbeat activity


def my_rhythm_fitness(rhythm: str) -> float:
    """Custom rhythm fitness function."""
    weights = [0.15, 0.15, 0.40, 0.25, 0.30]
    total = sum(weights)
    weights = [w / total for w in weights]

    fitness_fns = [
        rhythm_groove,
        rhythm_complexity,
        lambda r: 1 - rhythm_rest_ratio(r),  # Penalize rests
        rhythm_consistency,
        rhythm_density,
    ]

    return sum(w * fn(rhythm) for w, fn in zip(weights, fitness_fns))


# =============================================================================
# CUSTOM MELODY FITNESS
# =============================================================================
# Modify the weights below to change how melodies evolve.
# All primitives return 0.0-1.0. Higher = more of that quality.
#
# Available primitives:
#   note_variety(p)           - pitch variety
#   rest_ratio(p)             - ratio of rests
#   interval_smoothness(p)    - small intervals (use 1-x for jumps)
#   scale_adherence(p, scale) - how well notes fit a scale
#   rhythmic_variety(p)       - duration variety
#
# Available scales: MAJOR_SCALE, MINOR_SCALE, PENTATONIC, BLUES_SCALE


class MyMelodyFitness(FitnessFunction):
    """Custom melody fitness function."""

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        weights = [0.30, 0.55, 0.50, 0.105]
        total = sum(weights)
        weights = [w / total for w in weights]

        fitness_fns = [
            note_variety,
            interval_smoothness,
            lambda p: scale_adherence(p, MINOR_SCALE),
            lambda p: 1 - rest_ratio(p),
        ]

        scores = [
            sum(w * fn(phrase) for w, fn in zip(weights, fitness_fns))
            for phrase in layer.phrases
        ]
        return sum(scores) / len(scores)


# =============================================================================
# CUSTOM CHORD FITNESS
# =============================================================================
# Modify the weights below to change how chord progressions evolve.
# All primitives return 0.0-1.0. Higher = more of that quality.
#
# Available primitives:
#   chord_variety(prog)           - variety of root notes
#   chord_type_variety(prog)      - variety of chord qualities (maj, min, etc)
#   root_motion_smoothness(prog)  - smooth root movement (steps/4ths/5ths)
#   functional_harmony_score(prog)- use of I, IV, V chords (tonal)
#   resolution_bonus(prog)        - V-I and ii-V-I resolution patterns
#   triadic_bonus(prog)           - simple triads (pop/rock)
#   seventh_chord_bonus(prog)     - 7th chords (jazz/R&B)


class MyChordFitness(ChordFitnessFunction):
    """Custom chord fitness function."""

    def evaluate(self, progression: ChordProgression) -> float:
        weights = [0.35, 0.25, 0.20, 0.20]
        total = sum(weights)
        weights = [w / total for w in weights]

        fitness_fns = [
            functional_harmony_score,  # Favor I, IV, V chords
            triadic_bonus,  # Simple triads
            resolution_bonus,  # V-I patterns
            root_motion_smoothness,  # Smooth voice leading
        ]

        return sum(w * fn(progression) for w, fn in zip(weights, fitness_fns))


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

# Melody layer settings
INSTRUMENT = "supersaw"  # Try: "sawtooth", "square", "triangle", "sine", "piano"
BARS = 1  # Number of bars (more = longer pattern)
BEATS_PER_BAR = 8  # Beats per bar
MAX_SUBDIVISION = 2  # Max notes per beat (1=quarter, 2=eighth, 3=triplet, 4=16th)
OCTAVE_RANGE = (4, 5)  # Pitch range (octaves)
BPM = 50  # Tempo

# Chord layer settings
CHORD_INSTRUMENT = "piano"  # Try: "piano", "organ", "pad"
NUM_CHORDS = 4  # Number of chords in the progression
NOTES_PER_CHORD = 3  # Notes per chord (2=dyad, 3=triad, 4=7th)
ALLOWED_CHORD_TYPES = [
    "major",
    "minor",
]  # None = all types, or ["major", "minor", "dom7", etc.]

# Post-gain (after effects)
POSTGAIN = 0.0  # Volume after effects (0.0 = disabled)

# Evolution settings
POPULATION_SIZE = 20  # Larger = more variety, slower
MUTATION_RATE = 0.25  # Higher = more random changes
ELITISM_COUNT = 4  # Keep top N individuals each generation
RHYTHM_GENERATIONS = 25  # More = better rhythm
MELODY_GENERATIONS = 30  # More = better melody
CHORD_GENERATIONS = 25  # More = better chord progressions


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" CUSTOM FITNESS DEMO (Melody + Chords)")
    print("=" * 60)
    print(f"\nMelody Instrument: {INSTRUMENT}")
    print(f"Chord Instrument: {CHORD_INSTRUMENT}")
    print(f"Bars: {BARS}, Beats/bar: {BEATS_PER_BAR}")
    print(f"BPM: {BPM}")
    print()

    # Create composer
    composer = LayeredComposer(
        population_size=POPULATION_SIZE,
        mutation_rate=MUTATION_RATE,
        elitism_count=ELITISM_COUNT,
        rhythm_generations=RHYTHM_GENERATIONS,
        melody_generations=MELODY_GENERATIONS,
        chord_generations=CHORD_GENERATIONS,
    )

    # Configure chord layer (evolves first to provide harmonic context)
    chord_config = LayerConfig(
        name="chords",
        instrument="saw",
        bars=BARS,
        beats_per_bar=BEATS_PER_BAR,
        is_chord_layer=True,
        num_chords=NUM_CHORDS,
        notes_per_chord=NOTES_PER_CHORD,
        allowed_chord_types=ALLOWED_CHORD_TYPES,
        chord_fitness_fn=MyChordFitness(),
        layer_role="chords",  # Evolves first
        lpf=400,
        gain=0.3,
        room=0.5,
        attack=0.01,
        release=0.3,
    )
    composer.add_layer(chord_config)

    # Configure melody layer with custom fitness functions
    melody_config = LayerConfig(
        name="melody",
        instrument="supersaw",
        bars=BARS,
        beats_per_bar=16,
        max_subdivision=2,
        octave_range=OCTAVE_RANGE,
        rhythm_fitness_fn=my_rhythm_fitness,
        melody_fitness_fn=MyMelodyFitness(),
        layer_role="melody",
        gain=0.4,
        lpf=400,
        room=0.8,
        postgain=2,
        use_scale_degrees=True,
    )
    composer.add_layer(melody_config)

    melody_config = LayerConfig(
        name="bassline",
        instrument="supersaw",
        bars=BARS,
        beats_per_bar=4,
        max_subdivision=1,
        octave_range=(2, 4),
        rhythm_fitness_fn=my_rhythm_fitness,
        melody_fitness_fn=MyMelodyFitness(),
        layer_role="melody",
        gain=0.3,
        lpf=150,
        room=0.8,
        postgain=2,
        use_scale_degrees=True,
    )

    composer.add_layer(melody_config)

    # Evolve!
    print("Evolving...")
    composer.evolve_all_layers(verbose=True)

    # Get composition
    composition = composer.get_composition(bpm=BPM, random_scale=True)

    # Print results
    composer.print_summary()

    # Generate Strudel link
    print("\n" + "=" * 60)
    print(" STRUDEL LINK")
    print("=" * 60)
    link = composition.to_strudel_link()
    print(f"\nOpen this link to hear your composition:")
    print(link)

    print("\n" + "=" * 60)
    print(" STRUDEL CODE")
    print("=" * 60)
    print()
    print(composition.to_strudel())
    print()


if __name__ == "__main__":
    main()
