#!/usr/bin/env python3
"""Lofi hip-hop demo with chill vibes.

Run with: python lofi_demo.py

Features:
- Jazzy 7th chords with smooth progressions
- Mellow, smooth melodies
- Laid-back drum patterns (boom bap style)
- Vinyl crackle and warm effects
"""

from core.music import NoteName
from fitness.base import (
    FitnessFunction,
    note_variety,
    rest_ratio,
    interval_smoothness,
    scale_adherence,
    MINOR_SCALE,
    PENTATONIC,
)
from fitness.rhythm import (
    rhythm_complexity,
    rhythm_rest_ratio,
    rhythm_density,
    rhythm_syncopation,
    rhythm_groove,
    rhythm_consistency,
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
    root_motion_smoothness,
    functional_harmony_score,
    seventh_chord_bonus,
)
from fitness.contextual import get_context_groups
from core.genome_ops import ChordProgression
from layered_composer import LayeredComposer, LayerConfig


# =============================================================================
# LOFI FITNESS FUNCTIONS
# =============================================================================


def make_lofi_rhythm_fitness(weights: dict[str, float]):
    """Rhythm fitness for lofi - relaxed, groovy, some swing."""
    metric_fns = {
        "groove": rhythm_groove,
        "complexity": rhythm_complexity,
        "density": rhythm_density,
        "syncopation": rhythm_syncopation,
        "consistency": rhythm_consistency,
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


def make_lofi_melody_fitness(weights: dict[str, float], scale=MINOR_SCALE):
    """Melody fitness for lofi - smooth, not too busy, pentatonic friendly."""

    class LofiMelodyFitness(FitnessFunction):
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

    return LofiMelodyFitness()


def make_lofi_drum_fitness(weights: dict[str, float]):
    """Drum fitness for lofi boom-bap style."""
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


def make_lofi_chord_fitness(weights: dict[str, float]):
    """Chord fitness for lofi - jazzy 7ths, smooth motion."""

    class LofiChordFitness(ChordFitnessFunction):
        def evaluate(self, progression: ChordProgression) -> float:
            metric_fns = {
                "variety": chord_variety,
                "smooth": root_motion_smoothness,
                "functional": functional_harmony_score,
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

    return LofiChordFitness()


# =============================================================================
# LOFI STYLE DEFINITIONS
# =============================================================================

# Chords: jazzy 7ths with smooth voice leading
lofi_chords = make_lofi_chord_fitness(
    {
        "variety": 0.3,
        "smooth": 0.4,  # Smooth root motion is key for lofi
        "functional": 0.1,  # Less strict functional harmony
        "sevenths": 0.4,  # Love those 7th chords
    }
)

# Melody: smooth, pentatonic-friendly, with space
lofi_melody = make_lofi_melody_fitness(
    {
        "variety": 0.2,
        "smoothness": 0.5,  # Very smooth intervals
        "scale": 0.3,
        "rests": 0.1,  # Some breathing room
    },
    scale=PENTATONIC,
)

# Rhythm: laid-back, groovy
lofi_rhythm = make_lofi_rhythm_fitness(
    {
        "groove": 0.4,
        "syncopation": 0.3,  # Some swing
        "density": 0.2,
        "rests": -0.2,  # Don't want too sparse
    }
)

# Bass: simple, supportive
lofi_bass_rhythm = make_lofi_rhythm_fitness(
    {
        "groove": 0.5,
        "consistency": 0.3,
        "rests": -0.3,
    }
)

# Kick: boom-bap style, emphasis on 1, some variation
lofi_kick = make_lofi_drum_fitness(
    {
        "strong_beat": 0.4,
        "sparse": 0.2,
        "simple": 0.2,
        "offbeat": 0.2,  # Some offbeat kicks for that lofi feel
    }
)

# Snare: backbeat with ghost notes
lofi_snare = make_lofi_drum_fitness(
    {
        "backbeat": 0.5,
        "sparse": 0.2,
        "simple": 0.3,
    }
)

# Hihat: busy but not overwhelming, offbeat emphasis
lofi_hihat = make_lofi_drum_fitness(
    {
        "density": 0.3,
        "offbeat": 0.4,  # Offbeat hats are classic lofi
        "consistency": 0.2,
    }
)


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 24  # Very slow, chill tempo (setcpm(6) = 24 BPM)
BARS = 2
BEATS_PER_BAR = 4

POPULATION_SIZE = 25
MUTATION_RATE = 0.2
ELITISM_COUNT = 5
RHYTHM_GENERATIONS = 30
MELODY_GENERATIONS = 35
CHORD_GENERATIONS = 30


# =============================================================================
# LAYER CONFIGURATIONS
# =============================================================================


def create_lofi_layers():
    """Create lofi layer configurations."""
    layers = []

    # Jazzy chord pad - piano for that classic lofi feel
    layers.append(
        LayerConfig(
            name="chords",
            instrument="piano",  # Warm piano chords
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,
            notes_per_chord=4,  # 7th chords
            allowed_chord_types=["major7", "minor7", "dom7"],
            chord_fitness_fn=lofi_chords,
            layer_role="chords",
            context_group="",
            gain=0.35,
            lpf=2000,  # Warm, filtered sound
            room=0.4,
            attack=0.05,
            release=0.4,
        )
    )

    # Main melody A - nylon guitar for that cozy lofi vibe
    layers.append(
        LayerConfig(
            name="melody_a",
            instrument="acoustic_guitar_nylon",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 beats for melody
            max_subdivision=2,
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=lofi_rhythm,
            melody_fitness_fn=lofi_melody,
            layer_role="melody",
            context_group="main",
            gain=0.4,
            lpf=3000,
            room=0.5,
            delay=0.3,
            delaytime=0.375,  # Dotted eighth delay
            delayfeedback=0.4,
            bank="gm",  # General MIDI bank for guitar
        )
    )

    # Main melody B - different evolved melody with same fitness
    layers.append(
        LayerConfig(
            name="melody_b",
            instrument="acoustic_guitar_nylon",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 beats for melody
            max_subdivision=2,
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=lofi_rhythm,
            melody_fitness_fn=lofi_melody,
            layer_role="melody",
            context_group="main",
            gain=0.4,
            lpf=3000,
            room=0.5,
            delay=0.3,
            delaytime=0.375,  # Dotted eighth delay
            delayfeedback=0.4,
            bank="gm",  # General MIDI bank for guitar
        )
    )

    # Bass - warm and supportive
    layers.append(
        LayerConfig(
            name="bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=2,  # 8 beats for more movement
            max_subdivision=1,
            octave_range=(1, 2),
            base_octave=3,
            rhythm_fitness_fn=lofi_bass_rhythm,
            melody_fitness_fn=lofi_melody,
            layer_role="bass",
            context_group="main",
            gain=0.25,
            lpf=300,
        )
    )

    # --- DRUMS ---
    # Boom-bap style with vinyl character

    layers.append(
        LayerConfig(
            name="kick",
            instrument="bd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=1,
            is_drum=True,
            drum_sound="bd",
            rhythm_fitness_fn=lofi_kick,
            layer_role="drums",
            context_group="",
            gain=0.7,
            lpf=2000,  # Warm kick
            bank="RolandTR808",
        )
    )

    layers.append(
        LayerConfig(
            name="snare",
            instrument="sd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=1,
            is_drum=True,
            drum_sound="sd",
            rhythm_fitness_fn=lofi_snare,
            layer_role="drums",
            context_group="",
            gain=0.5,
            lpf=4000,
            room=0.3,  # Bit of room on snare
            bank="RolandTR808",
        )
    )

    layers.append(
        LayerConfig(
            name="hihat",
            instrument="hh",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=2,
            is_drum=True,
            drum_sound="hh",
            rhythm_fitness_fn=lofi_hihat,
            layer_role="drums",
            context_group="",
            gain=0.3,
            lpf=6000,
            bank="RolandTR808",
        )
    )

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" LOFI HIP-HOP DEMO")
    print(" Chill beats to relax/study to")
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

    # Add layers
    layers = create_lofi_layers()
    for layer_config in layers:
        composer.add_layer(layer_config)

    # Show configuration
    print("Layer configuration:")
    print("-" * 40)
    for config in layers:
        group = config.context_group if config.context_group else "(global)"
        print(f"  {config.name:<15} role={config.layer_role:<8} group={group}")
    print()

    # Evolve!
    print("Evolving lofi vibes...")
    composer.evolve_all_layers(verbose=True)

    # Print summary
    composer.print_summary()

    # ==========================================================================
    # SONG STRUCTURE
    # ==========================================================================
    layer_groups = {
        "drums": ["kick", "snare", "hihat"],
        "intro": ["bass", "chords"],  # Intro without melody
        "melodic_a": ["melody_a", "bass", "chords"],  # Section with melody A
        "melodic_b": ["melody_b", "bass", "chords"],  # Section with melody B
    }

    # Lofi structure with intro buildup and alternating melodies
    song_arrangement = [
        (2, "stack(intro)"),  # 2 bars - just bass and chords
        (2, "stack(intro, drums)"),  # 2 bars - add drums
        (4, "stack(drums, melodic_a)"),  # 4 bars - melody A
        (4, "stack(drums, melodic_b)"),  # 4 bars - melody B
        (4, "stack(drums, melodic_a)"),  # 4 bars - back to melody A
        (2, "stack(intro, drums)"),  # 2 bars - breakdown
    ]

    # Use a chill minor scale
    song = composer.get_song_structure(
        bpm=BPM,
        random_scale=False,  # We'll set it manually for lofi vibe
        groups=layer_groups,
        arrangement=song_arrangement,
    )

    # Override with a lofi-appropriate scale
    for layer in song.layers.values():
        if hasattr(layer, "scale") and layer.scale:
            layer.scale = "d:minor"  # D minor is very lofi

    # Generate output
    print("\n" + "=" * 60)
    print(" STRUDEL LINK")
    print("=" * 60)
    link = song.to_strudel_link()
    print(f"\nOpen this link to hear your lofi beat:")
    print(link)

    print("\n" + "=" * 60)
    print(" STRUDEL CODE")
    print("=" * 60)
    print()
    print(song.to_strudel())
    print()

    # Bonus: Show how to add vinyl crackle
    print("=" * 60)
    print(" TIP: Add vinyl crackle for authentic lofi!")
    print("=" * 60)
    print()
    print("Add this line to your Strudel code for vinyl texture:")
    print('$: sound("crow").gain(0.05).lpf(3000)')
    print()


if __name__ == "__main__":
    main()
