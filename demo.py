#!/usr/bin/env python3
"""Demo template for creating custom fitness functions and multi-section compositions.

Run with: python demo.py

This template shows how to:
1. Define custom rhythm fitness using primitives
2. Define custom melody fitness using primitives
3. Define custom chord fitness using primitives
4. Use context_group to organize layers into sections (verse, chorus, etc.)
5. Use layer_role for smart inter-layer fitness evaluation
6. Generate a Strudel link to hear the result

Modify the fitness functions and layer configs below to create your own style!
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
# EASY FITNESS BUILDERS
# =============================================================================
# Use these helpers to quickly create custom fitness functions without
# writing full classes.


def make_rhythm_fitness(weights: dict[str, float]):
    """Create a rhythm fitness function from a dictionary of weights.

    Available metrics (all return 0.0-1.0):
        groove       - strong/weak beat alternation (danceable)
        complexity   - variety of subdivisions (interesting)
        density      - notes per beat (busy)
        syncopation  - subdivision changes (off-beat feel)
        consistency  - pattern repetition (predictable)
        offbeat      - offbeat emphasis (funky)
        rests        - ratio of rests (sparse) - use negative to penalize

    Example:
        my_fitness = make_rhythm_fitness({
            'groove': 0.4,
            'density': 0.3,
            'rests': -0.2,  # Negative = penalize rests
        })
    """
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
                # Negative weight means penalize (use 1 - value)
                if weight < 0:
                    score += abs(weight) * (1 - value)
                else:
                    score += weight * value
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5

    return fitness


def make_melody_fitness(weights: dict[str, float], scale=MINOR_SCALE):
    """Create a melody fitness function from a dictionary of weights.

    Available metrics (all return 0.0-1.0):
        variety      - pitch variety (melodic interest)
        smoothness   - small intervals (singable) - use negative for jumps
        scale        - adherence to scale (in-key)
        rests        - ratio of rests (sparse) - use negative to penalize

    Example:
        my_fitness = make_melody_fitness({
            'variety': 0.3,
            'smoothness': 0.4,
            'scale': 0.5,
            'rests': -0.2,
        }, scale=BLUES_SCALE)
    """

    class CustomMelodyFitness(FitnessFunction):
        def evaluate(self, layer: Layer) -> float:
            if not layer.phrases:
                return 0.0

            metric_fns = {
                "variety": note_variety,
                "smoothness": interval_smoothness,
                "scale": lambda p: scale_adherence(p, scale),
                "rests": rest_ratio,
            }

            def score_phrase(phrase: Phrase) -> float:
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
    """Create a chord fitness function from a dictionary of weights.

    Available metrics (all return 0.0-1.0):
        variety      - variety of root notes
        types        - variety of chord qualities (maj, min, etc)
        smooth       - smooth root movement (steps/4ths/5ths)
        functional   - use of I, IV, V chords (tonal)
        resolution   - V-I and ii-V-I patterns
        triads       - simple triads (pop/rock)
        sevenths     - 7th chords (jazz/R&B)

    Example:
        my_fitness = make_chord_fitness({
            'functional': 0.4,
            'resolution': 0.3,
            'smooth': 0.2,
        })
    """

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
    """Create a drum rhythm fitness function from a dictionary of weights.

    Available metrics (all return 0.0-1.0):
        strong_beat  - emphasis on beats 1 & 5 (downbeat, kick-like)
        backbeat     - emphasis on beats 3 & 7 (snare position)
        sparse       - inverse of density (more space)
        simple       - ratio of single hits vs subdivisions
        offbeat      - offbeat emphasis (syncopated hats)
        density      - notes per beat (busy)
        consistency  - pattern repetition (steady)

    Example:
        kick_fitness = make_drum_fitness({
            'strong_beat': 0.5,  # Hit on 1 and 5
            'sparse': 0.3,       # Not too busy
            'simple': 0.2,       # Single hits
        })

        hihat_fitness = make_drum_fitness({
            'density': 0.5,      # Busy
            'consistency': 0.3,  # Steady pattern
            'offbeat': 0.2,      # Some offbeat feel
        })

        snare_fitness = make_drum_fitness({
            'backbeat': 0.6,     # Hit on 2 and 4
            'sparse': 0.3,       # Not too busy
            'simple': 0.1,       # Single hits
        })
    """
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


def make_contextual_weights(weights: dict[str, float]) -> dict[str, float]:
    """Create contextual fitness weights for inter-layer scoring.

    These weights control how a layer is scored against other layers
    in the same context_group during evolution.

    Available metrics (all return 0.0-1.0):
        rhythmic      - How rhythms complement each other (moderate overlap)
        density       - Different busy-ness levels (contrast is good)
        harmonic      - Consonant intervals between melodic layers
        voice_leading - Contrary motion, avoid parallel 5ths/octaves
        call_response - Alternating activity patterns (dialogue)

    Example:
        verse_context = make_contextual_weights({
            'rhythmic': 0.4,      # Emphasize rhythm compatibility
            'harmonic': 0.3,      # Some harmonic awareness
            'density': 0.2,       # Some density contrast
            'voice_leading': 0.1, # Light voice leading
            'call_response': 0.0, # Disable call-response
        })

        # Then use in LayerConfig:
        LayerConfig(
            name="verse_melody",
            contextual_weights=verse_context,
            ...
        )
    """
    return weights


verse_context = make_contextual_weights(
    {
        "rhythmic": 0.65,
        "harmonic": 0.30,
        "density": 0.20,
        "voice_leading": 0.10,
        "call_response": 0.05,
    }
)

verse_rhythm = make_rhythm_fitness(
    {
        "groove": 0.4,
        "density": 0.3,
        "consistency": 0.2,
        "rests": -0.3,
    }
)

# More energetic rhythm for chorus
chorus_rhythm = make_rhythm_fitness(
    {
        "groove": 0.4,
        "density": 0.3,
        "consistency": 0.2,
        "rests": -0.3,
    }
)

# Bass rhythm: sparse but present, groovy
bass_rhythm = make_rhythm_fitness(
    {
        "groove": 0.5,
        "consistency": 0.3,
        "rests": -0.4,  # Penalize rests (need some notes!)
    }
)

# Melody fitness: varied, smooth, in scale
verse_melody = make_melody_fitness(
    {
        "variety": 0.3,
        "smoothness": 0.4,
        "scale": 0.5,
        "rests": -0.2,
    },
    scale=MINOR_SCALE,
)

# More expressive melody for chorus
chorus_melody = make_melody_fitness(
    {
        "variety": 0.8,
        "smoothness": 0.3,
        "scale": 0.4,
        "rests": -0.3,
    },
    scale=MINOR_SCALE,
)

# Chord fitness: functional harmony with resolutions
main_chords = make_chord_fitness(
    {
        "functional": 0.4,
        "resolution": 0.3,
        "smooth": 0.2,
        "triads": 0.1,
    }
)

# =============================================================================
# DRUM FITNESS FUNCTIONS
# =============================================================================

# Kick drum: strong beats (1 & 5), sparse, powerful single hits
kick_fitness = make_drum_fitness(
    {
        "strong_beat": 0.5,  # Hit on beats 1 and 5
        "sparse": 0.3,  # Keep it simple, not too busy
        "simple": 0.2,  # Single hits, no rolls
    }
)

# Hi-hat: busy, consistent, steady groove
hihat_fitness = make_drum_fitness(
    {
        "density": 0.2,  # Keep it busy
        "consistency": 0.1,  # Steady pattern
        "offbeat": 0.4,  # Some offbeat feel
    }
)

# Snare: backbeat emphasis (2 & 4), sparse accents
snare_fitness = make_drum_fitness(
    {
        "backbeat": 0.6,  # Hit on beats 3 and 7 (2 & 4 in 4/4)
        "sparse": 0.3,  # Not too busy
        "simple": 0.1,  # Single hits
    }
)


# Chorus: more emphasis on harmonic richness and voice leading
chorus_context = make_contextual_weights(
    {
        "rhythmic": 0.20,
        "harmonic": 0.35,
        "density": 0.15,
        "voice_leading": 0.20,
        "call_response": 0.10,
    }
)


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 50
BARS = 1
BEATS_PER_BAR = 4

# Evolution settings
POPULATION_SIZE = 20
MUTATION_RATE = 0.25
ELITISM_COUNT = 4
RHYTHM_GENERATIONS = 25
MELODY_GENERATIONS = 30
CHORD_GENERATIONS = 25


def create_layers():
    """Create all layer configurations."""
    layers = []

    layers.append(
        LayerConfig(
            name="chords",
            instrument="saw",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,
            notes_per_chord=4,
            allowed_chord_types=["major", "minor"],
            chord_fitness_fn=main_chords,
            layer_role="verse",
            context_group="",
            gain=0.3,
            lpf=400,
            room=0.5,
            attack=0.01,
            release=0.3,
        )
    )

    layers.append(
        LayerConfig(
            name="verse_melody",
            instrument=["piano", "gm_acoustic_guitar_nylon", "supersaw"],
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 4,  # 16 beats for melody
            max_subdivision=2,
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=verse_rhythm,
            melody_fitness_fn=verse_melody,
            layer_role="melody",
            context_group="verse",
            contextual_weights=verse_context,  # Custom inter-layer scoring
            gain=0.4,
            lpf=400,
            room=0.8,
            postgain=2,
        )
    )

    layers.append(
        LayerConfig(
            name="verse_bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,
            octave_range=(2, 3),
            base_octave=3,
            rhythm_fitness_fn=bass_rhythm,
            melody_fitness_fn=verse_melody,
            layer_role="bass",
            context_group="verse",
            gain=0.35,
            lpf=200,
        )
    )

    # --- DRUM LAYERS ---
    # Drums are global (empty context_group) so they play with all sections
    # Using "RolandTR808" bank for classic drum machine sounds
    # Other good banks: "alesissr16", "RhythmAce", "AkaiLinn"

    layers.append(
        LayerConfig(
            name="kick",
            instrument="bd",  # bass drum
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 beats for more control
            max_subdivision=1,  # Single hits only
            is_drum=True,
            drum_sound="bd",
            rhythm_fitness_fn=kick_fitness,
            layer_role="drums",
            context_group="",  # Global - plays with all sections
            gain=0.8,
            bank="alesissr16",
        )
    )

    layers.append(
        LayerConfig(
            name="hihat",
            instrument="hh",  # hi-hat
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 beats
            max_subdivision=2,  # Allow some subdivisions
            is_drum=True,
            drum_sound="hh",
            rhythm_fitness_fn=hihat_fitness,
            layer_role="drums",
            context_group="",
            gain=0.5,
            bank="alesissr16",
        )
    )

    layers.append(
        LayerConfig(
            name="snare",
            instrument="sd",  # snare drum
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 beats
            max_subdivision=1,  # Single hits
            is_drum=True,
            drum_sound="sd",
            rhythm_fitness_fn=snare_fitness,
            layer_role="drums",
            context_group="",
            gain=0.7,
            bank="alesissr16",
        )
    )

    # # # --- CHORUS SECTION ---
    layers.append(
        LayerConfig(
            name="chorus_melody",
            instrument="supersaw",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 4,
            max_subdivision=2,
            octave_range=(4, 6),  # Higher range for chorus
            base_octave=5,
            rhythm_fitness_fn=chorus_rhythm,
            melody_fitness_fn=chorus_melody,
            layer_role="melody",
            context_group="chorus",
            gain=0.45,
            lpf=600,
            room=0.9,
            postgain=2.5,
        )
    )

    layers.append(
        LayerConfig(
            name="chorus_bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # More active bass in chorus
            octave_range=(2, 3),
            base_octave=3,
            rhythm_fitness_fn=chorus_rhythm,
            melody_fitness_fn=verse_melody,
            layer_role="bass",
            context_group="chorus",
            gain=0.4,
            lpf=250,
        )
    )

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" MULTI-SECTION DEMO WITH CONTEXT GROUPS")
    print("=" * 60)
    print(f"\nBPM: {BPM}")
    print(f"Bars: {BARS}, Beats/bar: {BEATS_PER_BAR}")
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
    layers = create_layers()
    for layer_config in layers:
        composer.add_layer(layer_config)

    # Show context groups
    print("Layer configuration:")
    print("-" * 40)
    for config in layers:
        group = config.context_group if config.context_group else "(global)"
        print(f"  {config.name:<20} role={config.layer_role:<8} group={group}")
    print()

    # Evolve!
    print("Evolving...")
    composer.evolve_all_layers(verbose=True)

    # Show context groups after evolution
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

    # ==========================================================================
    # SONG STRUCTURE WITH ARRANGEMENT
    # ==========================================================================
    # Define layer groups (which layers play together)
    layer_groups = {
        "drums": ["kick", "hihat", "snare"],
        "verse": ["verse_melody", "verse_bass", "chords"],
        "chorus": ["chorus_melody", "chorus_bass", "chords"],
    }

    # Define song arrangement: (bars, group_or_layer_name)
    # This creates a simple verse-chorus structure
    song_arrangement = [
        (4, "stack(drums, verse)"),  # 4 bars verse
        (4, "stack(drums, chorus)"),  # 4 bars chorus
        (4, "stack(drums, verse)"),  # 4 bars verse
        (4, "stack(drums, chorus)"),  # 4 bars chorus
    ]

    # Get song structure with named constants
    song = composer.get_song_structure(
        bpm=BPM,
        random_scale=True,
        groups=layer_groups,
        arrangement=song_arrangement,
    )

    # Generate Strudel link
    print("\n" + "=" * 60)
    print(" STRUDEL LINK (SONG STRUCTURE)")
    print("=" * 60)
    link = song.to_strudel_link()
    print(f"\nOpen this link to hear your composition:")
    print(link)

    print("\n" + "=" * 60)
    print(" STRUDEL CODE (SONG STRUCTURE)")
    print("=" * 60)
    print()
    print(song.to_strudel())
    print()


if __name__ == "__main__":
    main()
