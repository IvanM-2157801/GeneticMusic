#!/usr/bin/env python3
"""Ambient music demo - ethereal, atmospheric, spacious.

Run with: python ambient_demo.py

This demo creates ambient music by adjusting weights from the standard
make_xxx_fitness helpers. Ambient characteristics:
- Slow tempo (60 BPM)
- Smooth melodies (high smoothness weight)
- Simple chord progressions with 7th chords
- Sparse rhythms with rests allowed
- Lots of reverb and delay
- No drums (optional soft texture layer)
"""

from core.music import NoteName
from fitness.base import (
    FitnessFunction,
    note_variety,
    rest_ratio,
    interval_smoothness,
    scale_adherence,
    MINOR_SCALE,
    MAJOR_SCALE,
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
from fitness.contextual import get_context_groups
from core.genome_ops import ChordProgression
from layered_composer import LayeredComposer, LayerConfig


# =============================================================================
# FITNESS BUILDERS (same as demo.py)
# =============================================================================


def make_rhythm_fitness(weights: dict[str, float]):
    """Create a rhythm fitness function from a dictionary of weights."""
    metric_fns = {
        "groove": rhythm_groove,
        "complexity": rhythm_complexity,
        "density": rhythm_density,
        "syncopation": rhythm_syncopation,
        "consistency": rhythm_consistency,
        "offbeat": rhythm_offbeat_emphasis,
        "rests": rhythm_rest_ratio,
    }

    def fitness(rhythm: str) -> float:
        score = 0.0
        total_weight = 0.0
        for metric, weight in weights.items():
            if metric in metric_fns:
                fn = metric_fns[metric]
                value = fn(rhythm)
                if weight < 0:
                    score += abs(weight) * (1 - value)
                else:
                    score += weight * value
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5

    return fitness


def make_melody_fitness(weights: dict[str, float], scale=MINOR_SCALE):
    """Create a melody fitness function from a dictionary of weights."""

    class CustomMelodyFitness(FitnessFunction):
        def evaluate(self, layer) -> float:
            if not layer.phrases:
                return 0.0

            metric_fns = {
                "variety": note_variety,
                "smoothness": interval_smoothness,
                "scale": lambda p: scale_adherence(p, scale),
                "rests": rest_ratio,
            }

            def score_phrase(phrase) -> float:
                score = 0.0
                total_weight = 0.0
                for metric, weight in weights.items():
                    if metric in metric_fns:
                        fn = metric_fns[metric]
                        value = fn(phrase)
                        if weight < 0:
                            score += abs(weight) * (1 - value)
                        else:
                            score += weight * value
                        total_weight += abs(weight)
                return score / total_weight if total_weight > 0 else 0.5

            scores = [score_phrase(p) for p in layer.phrases]
            return sum(scores) / len(scores)

    return CustomMelodyFitness()


def make_chord_fitness(weights: dict[str, float]):
    """Create a chord fitness function from a dictionary of weights."""

    class CustomChordFitness(ChordFitnessFunction):
        def evaluate(self, progression: ChordProgression) -> float:
            metric_fns = {
                "variety": chord_variety,
                "types": chord_type_variety,
                "smooth": root_motion_smoothness,
                "functional": functional_harmony_score,
                "resolution": resolution_bonus,
                "triads": triadic_bonus,
                "sevenths": seventh_chord_bonus,
            }

            score = 0.0
            total_weight = 0.0
            for metric, weight in weights.items():
                if metric in metric_fns:
                    fn = metric_fns[metric]
                    value = fn(progression)
                    if weight < 0:
                        score += abs(weight) * (1 - value)
                    else:
                        score += weight * value
                    total_weight += abs(weight)
            return score / total_weight if total_weight > 0 else 0.5

    return CustomChordFitness()


# =============================================================================
# AMBIENT FITNESS WEIGHTS
# =============================================================================
# Key differences from pop/rock:
# - High smoothness (stepwise motion)
# - Moderate groove (on-beat, flowing)
# - Low syncopation (straight rhythms)
# - High consistency (meditative, repetitive)
# - 7th chords for lush harmony

# Ambient context: prioritize harmonic consonance
ambient_context = {
    "rhythmic": 0.3,       # Moderate - not too strict
    "harmonic": 0.5,       # Very important - consonant!
    "density": 0.1,        # Some contrast
    "voice_leading": 0.3,  # Smooth voice leading
    "call_response": 0.1,  # Light interaction
}

# Pad rhythm: simple, flowing, with breathing room
pad_rhythm = make_rhythm_fitness({
    "groove": 0.4,         # Good groove for alternation
    "consistency": 0.3,
    "density": 0.15,       # Moderate density
    "syncopation": -0.2,
    "rests": 0.05,         # Slight reward for rests
})

# Sparse rhythm: fewer notes for slow sections, but not silent
sparse_rhythm = make_rhythm_fitness({
    "groove": 0.5,         # Need groove for alternation
    "consistency": 0.3,
    "density": 0.05,       # Very low - allows many rests
    "syncopation": -0.2,
    "rests": 0.15,         # Slightly reward rests
})

# Minimal rhythm: very few notes, lots of space (but not silent!)
minimal_rhythm = make_rhythm_fitness({
    "groove": 0.4,         # Need some groove
    "consistency": 0.5,    # Consistent pattern
    "density": 0.05,       # Very low
    "syncopation": -0.4,   # No syncopation
    "rests": -0.1,         # Light penalty to ensure some notes
})

# Lead rhythm: similar, slightly sparser for melody
lead_rhythm = make_rhythm_fitness({
    "groove": 0.4,         # Good groove
    "consistency": 0.3,
    "density": 0.2,
    "syncopation": -0.2,
    "rests": -0.1,
})

# Bass rhythm: simple, groovy, not too sparse
bass_rhythm = make_rhythm_fitness({
    "groove": 0.5,         # Strong groove (emphasize beats)
    "consistency": 0.4,    # Very consistent
    "density": 0.1,        # Some density
    "syncopation": -0.3,   # No syncopation
    "rests": -0.3,         # Penalize too many rests
})

# Pad melody: very smooth, in scale, meditative
pad_melody = make_melody_fitness({
    "variety": 0.2,        # Low variety (repetitive is OK)
    "smoothness": 0.6,     # Very smooth (stepwise motion)
    "scale": 0.5,          # Stay in scale
    "rests": -0.1,         # Slight penalty for rests
}, scale=MAJOR_SCALE)

# Lead melody: slightly more varied but still smooth
lead_melody = make_melody_fitness({
    "variety": 0.3,        # Some variety
    "smoothness": 0.5,     # Smooth
    "scale": 0.5,          # Stay in scale
    "rests": -0.1,
}, scale=MAJOR_SCALE)

# Ambient chords: smooth motion, 7th chords, functional
ambient_chords = make_chord_fitness({
    "smooth": 0.4,         # Smooth root motion
    "functional": 0.3,     # Some functional harmony
    "sevenths": 0.3,       # Rich 7th chords
    "resolution": 0.2,     # Some resolution
})


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 55  # Very slow, chill tempo
BARS = 2
BEATS_PER_BAR = 4

# Evolution settings
POPULATION_SIZE = 25
MUTATION_RATE = 0.15
ELITISM_COUNT = 5
RHYTHM_GENERATIONS = 30
MELODY_GENERATIONS = 35
CHORD_GENERATIONS = 25


def create_layers():
    """Create simple ambient layers - just pad + melody."""
    layers = []

    # --- CHORD PAD ---
    # Warm, sustained chords - the background
    layers.append(
        LayerConfig(
            name="pad",
            instrument="sine",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,
            notes_per_chord=4,
            allowed_chord_types=["major7", "minor7"],
            chord_fitness_fn=ambient_chords,
            layer_role="chords",
            context_group="",
            gain=0.05,
            lpf=1500,
            room=0.8,
            roomsize=8.0,
            attack=0.4,
            release=1.0,
        )
    )

    # --- MELODY ---
    # Simple, slow melody on top
    layers.append(
        LayerConfig(
            name="melody",
            instrument="triangle",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,  # Just 4 notes per bar - slow
            max_subdivision=2,  # Allow 0,1,2 for groove patterns
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=pad_rhythm,
            melody_fitness_fn=pad_melody,
            layer_role="melody",
            context_group="main",
            contextual_weights=ambient_context,
            gain=0.25,
            lpf=3000,
            room=0.7,
            roomsize=6.0,
            delay=0.4,
            delaytime=0.5,
            delayfeedback=0.4,
            attack=0.2,
            release=0.6,
        )
    )

    # --- SPARSE MELODY ---
    # Very few notes for slow/quiet sections
    layers.append(
        LayerConfig(
            name="melody_slow",
            instrument="triangle",
            bars=BARS,
            beats_per_bar=2,  # Only 2 beats per bar = 4 total = very sparse
            max_subdivision=2,  # Allow 0,1,2 for groove patterns
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=sparse_rhythm,
            melody_fitness_fn=pad_melody,
            layer_role="melody",
            context_group="slow",
            contextual_weights=ambient_context,
            gain=0.2,
            lpf=2500,
            room=0.8,
            roomsize=8.0,
            delay=0.5,
            delaytime=0.5,
            delayfeedback=0.5,
            attack=0.3,
            release=0.8,
        )
    )

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" AMBIENT DEMO - ETHEREAL & ATMOSPHERIC")
    print("=" * 60)
    print()
    print(f"BPM: {BPM}")
    print(f"Bars: {BARS}, Beats/bar: {BEATS_PER_BAR}")
    print()

    layers = create_layers()

    print("Layer configuration:")
    print("-" * 40)
    for layer in layers:
        group = layer.context_group if layer.context_group else "(global)"
        print(f"  {layer.name:20} role={layer.layer_role:8} group={group}")
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

    # Add all layers
    for layer_config in layers:
        composer.add_layer(layer_config)

    print("Evolving ambient patterns...\n")
    composer.evolve_all_layers(verbose=True)

    # Print context groups
    print("\n" + "=" * 60)
    print(" CONTEXT GROUPS")
    print("=" * 60)
    groups = get_context_groups(composer.evolved_layers)
    for group, members in sorted(groups.items()):
        group_name = group if group else "(global - shared with all)"
        print(f"\n{group_name}:")
        for name in members:
            layer, rhythm = composer.evolved_layers[name]
            print(f"  - {name} ({layer.layer_role}): rhythm={rhythm}")

    # Print summary
    composer.print_summary()

    # Generate Strudel output with slow and full parts
    layer_groups = {
        "full": ["pad", "melody"],
        "slow": ["pad", "melody_slow"],
        "pad_only": ["pad"],
    }

    arrangement = [
        (4, "stack(pad_only)"),   # Intro - just pad
        (4, "stack(slow)"),       # Slow/sparse melody
        (4, "stack(full)"),       # Full melody  
        (4, "stack(slow)"),       # Back to slow
        (4, "stack(full)"),       # Full melody  
        (4, "stack(slow)"),       # Back to slow
        (4, "stack(pad_only)"),   # Outro
    ]

    # Get song structure
    song = composer.get_song_structure(
        bpm=BPM,
        random_scale=False,
        groups=layer_groups,
        arrangement=arrangement,
    )

    # Generate and print Strudel link
    print("\n" + "=" * 60)
    print(" STRUDEL LINK (AMBIENT SONG)")
    print("=" * 60)
    link = song.to_strudel_link()
    print(f"\nOpen this link to hear your ambient composition:\n{link}")

    print("\n" + "=" * 60)
    print(" STRUDEL CODE")
    print("=" * 60)
    print(f"\n{song.to_strudel()}")


if __name__ == "__main__":
    main()
