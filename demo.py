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
    weights = [0.02, 0.02, 0.20, 0.80, 0.40]
    total = sum(weights)
    weights = [w / total for w in weights]

    fitness_fns = [
        rhythm_groove,
        rhythm_complexity,
        lambda r: 1 - rhythm_rest_ratio(r),
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

        weights = [0.20, 0.55, 0.50, 0.105]
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
# EVOLUTION PARAMETERS
# =============================================================================

# Layer settings
INSTRUMENT = "sawtooth"  # Try: "sawtooth", "square", "triangle", "sine", "piano"
BARS = 1  # Number of bars (more = longer pattern)
BEATS_PER_BAR = 8  # Beats per bar
MAX_SUBDIVISION = 2  # Max notes per beat (1=quarter, 2=eighth, 3=triplet, 4=16th)
OCTAVE_RANGE = (4, 5)  # Pitch range (octaves)
BPM = 50  # Tempo

# Post-gain (after effects)
POSTGAIN = 0.0  # Volume after effects (0.0 = disabled)

# Evolution settings
POPULATION_SIZE = 20  # Larger = more variety, slower
MUTATION_RATE = 0.25  # Higher = more random changes
ELITISM_COUNT = 4  # Keep top N individuals each generation
RHYTHM_GENERATIONS = 25  # More = better rhythm
MELODY_GENERATIONS = 30  # More = better melody


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" CUSTOM FITNESS DEMO")
    print("=" * 60)
    print(f"\nInstrument: {INSTRUMENT}")
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
    )

    # Configure layer with custom fitness functions
    layer_config = LayerConfig(
        name="melody",
        instrument="supersaw",
        bars=BARS,
        beats_per_bar=BEATS_PER_BAR,
        max_subdivision=MAX_SUBDIVISION,
        octave_range=OCTAVE_RANGE,
        rhythm_fitness_fn=my_rhythm_fitness,
        melody_fitness_fn=MyMelodyFitness(),
        gain=0.4,
        lpf=400,
        room=0.8,
        postgain=2,
        use_scale_degrees=True,
    )

    composer.add_layer(layer_config)

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
