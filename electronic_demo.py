#!/usr/bin/env python3
"""Electronic music demo - driving, energetic, danceable.

Run with: python electronic_demo.py

This demo creates electronic/EDM music by adjusting weights from the standard
make_xxx_fitness helpers. Electronic characteristics:
- Fast tempo (128 BPM)
- Driving rhythms with strong groove
- Dense patterns, few rests
- Synth sounds (sawtooth, square)
- Heavy bass
- Sections: intro, buildup, drop, breakdown
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
from fitness.drums import (
    strong_beat_emphasis,
    backbeat_emphasis,
    sparsity,
    simplicity,
    offbeat_pattern,
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


def make_drum_fitness(weights: dict[str, float]):
    """Create a drum rhythm fitness function from a dictionary of weights."""
    metric_fns = {
        "strong_beat": strong_beat_emphasis,
        "backbeat": backbeat_emphasis,
        "sparse": sparsity,
        "simple": simplicity,
        "offbeat": offbeat_pattern,
        "density": rhythm_density,
        "consistency": rhythm_consistency,
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


# =============================================================================
# ELECTRONIC FITNESS WEIGHTS
# =============================================================================
# Key differences from ambient:
# - High groove (danceable)
# - High density (driving, busy)
# - Penalize rests (keep energy up)
# - High consistency (hypnotic, repetitive)
# - Some syncopation for interest

# Electronic context: energy and drive
electronic_context = {
    "rhythmic": 0.5,       # Strong rhythmic alignment
    "harmonic": 0.3,       # Some harmonic interest
    "density": 0.3,        # Similar density across layers
    "voice_leading": 0.2,  # Less important
    "call_response": 0.2,  # Some interaction
}

# Bass rhythm: simple, on-beat, driving
bass_rhythm = make_rhythm_fitness({
    "groove": 0.3,
    "consistency": 0.6,    # Very consistent (hypnotic)
    "density": 0.2,        # Moderate
    "syncopation": -0.4,   # Avoid syncopation - keep it straight
    "rests": -0.3,         # Mostly notes
})

# Lead rhythm: more movement, eighth notes
lead_rhythm = make_rhythm_fitness({
    "groove": 0.5,         # Good groove with alternation
    "consistency": 0.3,
    "density": 0.4,        # Denser
    "syncopation": 0.1,    # Little syncopation
    "rests": -0.3,         # Few rests
})

# Arp rhythm: steady eighth notes
arp_rhythm = make_rhythm_fitness({
    "groove": 0.3,
    "consistency": 0.6,    # Very consistent
    "density": 0.4,        # Dense
    "syncopation": -0.3,   # Steady
    "rests": -0.5,         # No rests
})

# Buildup rhythm: sparser, building tension
buildup_rhythm = make_rhythm_fitness({
    "groove": 0.4,
    "consistency": 0.4,
    "density": 0.2,        # Less dense
    "syncopation": 0.1,
    "rests": -0.2,         # Some rests OK
})

# Bass melody: simple, low, powerful
bass_melody = make_melody_fitness({
    "variety": 0.2,        # Low variety (repetitive bass)
    "smoothness": 0.3,     # Some smoothness
    "scale": 0.6,          # Stay in scale
    "rests": -0.3,         # Few rests
}, scale=MINOR_SCALE)

# Lead melody: more varied, energetic
lead_melody = make_melody_fitness({
    "variety": 0.4,        # More variety
    "smoothness": 0.3,     # Mix of smooth and jumps
    "scale": 0.5,          # Stay in scale
    "rests": -0.2,
}, scale=MINOR_SCALE)

# Arp melody: smooth, flowing, in scale
arp_melody = make_melody_fitness({
    "variety": 0.3,
    "smoothness": 0.5,     # Smooth arpeggios
    "scale": 0.6,          # Very in-scale
    "rests": -0.4,         # No rests
}, scale=MINOR_SCALE)

# Electronic chords: simple, powerful, minor
electronic_chords = make_chord_fitness({
    "smooth": 0.3,         # Some smooth motion
    "functional": 0.3,     # Functional harmony
    "triads": 0.4,         # Simple triads (powerful)
    "resolution": 0.2,
})

# Hook melody: catchy, memorable, stays in scale
hook_rhythm = make_rhythm_fitness({
    "groove": 0.5,         # Good groove
    "consistency": 0.3,    # Some repetition
    "density": 0.3,        # Medium density
    "syncopation": 0.2,    # Bit of syncopation for catchiness
    "rests": 0.1,          # Some rests for rhythm
})

hook_melody = make_melody_fitness({
    "variety": 0.3,        # Some variety but memorable
    "smoothness": 0.5,     # Smooth = singable = catchy
    "scale": 0.6,          # Stay in scale
    "rests": 0.0,          # Neutral on rests
}, scale=MINOR_SCALE)

# Drop bass: heavy, driving, consistent - the foundation of the drop
drop_bass_rhythm = make_rhythm_fitness({
    "groove": 0.4,         # Some groove
    "consistency": 0.6,    # Very consistent - driving
    "density": 0.5,        # Dense
    "syncopation": -0.3,   # Avoid syncopation - keep it solid
    "rests": -0.5,         # No rests - constant drive
})

drop_bass_melody = make_melody_fitness({
    "variety": 0.2,        # Low variety - repetitive is powerful
    "smoothness": 0.4,     # Reasonably smooth
    "scale": 0.6,          # Stay in scale
    "rests": -0.5,         # No rests
}, scale=MINOR_SCALE)


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 128  # Classic EDM tempo
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
    """Create electronic layers - chords, bass, lead, arp, hook."""
    layers = []

    # --- CHORD PAD ---
    # Simple, powerful chords
    layers.append(
        LayerConfig(
            name="chords",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,
            notes_per_chord=3,  # Triads for power
            allowed_chord_types=["major", "minor"],
            chord_fitness_fn=electronic_chords,
            layer_role="chords",
            context_group="",
            gain=0.07,
            lpf=2000,
            room=0.3,
            roomsize=2.0,
            attack=0.01,
            release=0.3,
        )
    )

    # --- BASS ---
    # Simple quarter notes - the foundation
    layers.append(
        LayerConfig(
            name="bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,  # Quarter notes only
            octave_range=(2, 3),
            base_octave=2,
            rhythm_fitness_fn=bass_rhythm,
            melody_fitness_fn=bass_melody,
            layer_role="bass",
            context_group="drop",
            contextual_weights=electronic_context,
            gain=0.35,
            lpf=800,
            room=0.1,
            roomsize=1.0,
            attack=0.01,
            release=0.2,
        )
    )

    # --- LEAD ---
    # Eighth notes for more movement
    layers.append(
        LayerConfig(
            name="lead",
            instrument="square",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes for groove
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=lead_rhythm,
            melody_fitness_fn=lead_melody,
            layer_role="melody",
            context_group="drop",
            contextual_weights=electronic_context,
            gain=0.2,
            lpf=3000,
            room=0.4,
            roomsize=3.0,
            delay=0.25,
            delaytime=0.125,
            delayfeedback=0.25,
            attack=0.01,
            release=0.2,
        )
    )

    # --- ARP ---
    # Steady eighth notes - fills out the sound
    layers.append(
        LayerConfig(
            name="arp",
            instrument="triangle",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=arp_rhythm,
            melody_fitness_fn=arp_melody,
            layer_role="melody",
            context_group="drop",
            contextual_weights=electronic_context,
            gain=0.4,
            lpf=2500,
            room=0.5,
            roomsize=4.0,
            delay=0.3,
            delaytime=0.25,
            delayfeedback=0.35,
            attack=0.01,
            release=0.15,
        )
    )

    # --- HOOK ---
    # Short 1-bar catchy melody that repeats throughout the song
    # This is where the GA shines - evolving the most catchy/memorable pattern
    layers.append(
        LayerConfig(
            name="hook",
            instrument="square",
            bars=1,  # Just 1 bar - will repeat!
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes for interest
            octave_range=(5, 6),  # Higher octave to cut through
            base_octave=5,
            rhythm_fitness_fn=hook_rhythm,
            melody_fitness_fn=hook_melody,
            layer_role="melody",
            context_group="drop",
            contextual_weights=electronic_context,
            gain=0.25,  # Prominent
            lpf=4000,  # Bright
            room=0.3,
            roomsize=2.0,
            delay=0.2,
            delaytime=0.125,  # 1/8 note delay for rhythm
            delayfeedback=0.3,
            attack=0.005,
            release=0.15,
        )
    )

    # --- DROP BASS ---
    # Heavy, aggressive bass that only plays in the drop
    # More rhythmic and punchy than the regular bass
    layers.append(
        LayerConfig(
            name="drop_bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes for punch
            octave_range=(1, 2),  # Very low for weight
            base_octave=1,
            rhythm_fitness_fn=drop_bass_rhythm,
            melody_fitness_fn=drop_bass_melody,
            layer_role="bass",
            context_group="drop",
            contextual_weights=electronic_context,
            gain=0.5,  # Heavy
            lpf=600,   # Sub bass frequencies
            room=0.05,
            roomsize=0.5,
            attack=0.005,
            release=0.1,
        )
    )

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" ELECTRONIC DEMO - DRIVING & ENERGETIC")
    print("=" * 60)
    print()
    print(f"BPM: {BPM}")
    print(f"Bars: {BARS}, Beats/bar: {BEATS_PER_BAR}")
    print()

    layers = create_layers()

    print("Layer configuration:")
    print("-" * 40)
    for layer in layers:
        print(f"  {layer.name:20} role={layer.layer_role:8} group={layer.context_group or '(global)'}")
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

    # Evolve
    print("Evolving electronic patterns...")
    print()
    composer.evolve_all_layers(verbose=True)

    # Print context groups
    print("\n" + "=" * 60)
    print(" CONTEXT GROUPS")
    print("=" * 60)
    context_groups = get_context_groups(composer.evolved_layers)
    for group, members in sorted(context_groups.items()):
        group_name = group if group else "(global - shared with all)"
        print(f"\n{group_name}:")
        for name in members:
            layer, rhythm = composer.evolved_layers[name]
            print(f"  - {name} ({layer.layer_role}): rhythm={rhythm}")

    # Print summary
    composer.print_summary()

    # Generate Strudel output with sections
    # Custom arrangement with smooth transitions
    layer_groups = {
        "drop": ["drop_bass", "lead", "arp", "hook"],
        "breakdown1": ["bass", "lead", "arp", "hook"],
        "breakdown2": ["bass", "arp"],
        "buildup1": ["chords", "arp"],
        "buildup2": ["chords", "bass", "arp"],
        "intro1": ["bass"],
        "intro2": ["chords", "bass"],
        "outro1": ["bass", "hook", "arp"],
        "outro2": ["bass", "hook"],
    }

    arrangement = [
        (2, "stack(intro1)"),
        (2, "stack(intro2)"),
        (4, "stack(buildup1)"),
        (4, "stack(buildup2)"),
        (4, "stack(drop)"),
        (2, "stack(breakdown1)"),
        (2, "stack(breakdown2)"),
        (4, "stack(buildup1)"),
        (4, "stack(buildup2)"),
        (4, "stack(drop)"),
        (2, "stack(breakdown1)"),
        (2, "stack(breakdown2)"),
        (2, "stack(outro1)"),
        (2, "stack(outro2)"),
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
    print(" STRUDEL LINK (ELECTRONIC TRACK)")
    print("=" * 60)
    link = song.to_strudel_link()
    print(f"\nOpen this link to hear your electronic track:\n{link}")

    print("\n" + "=" * 60)
    print(" STRUDEL CODE")
    print("=" * 60)
    print(song.to_strudel())


if __name__ == "__main__":
    main()
