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
    repetitive_pattern_score,
    root_motion_smoothness,
    functional_harmony_score,
    seventh_chord_bonus,
    diminished_chord_score,
    chord_progression_similarity,
    close_voicing_score,
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
                "diminished": diminished_chord_score,
                "progression": chord_progression_similarity,
                "voicing": close_voicing_score,
                "repetitive": repetitive_pattern_score,
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
        "variety": 0.6,
        "smooth": 0.3,  # Lowered slightly
        "functional": 0.1,
        "sevenths": 0.4,
        "diminished": -0.2,
        "voicing": -0.5,
        "repetitive": -0.6,  # Penalize A-B-A-B patterns
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

# =============================================================================
# DnB-SPECIFIC FITNESS FUNCTIONS
# =============================================================================


def dnb_kick_fitness(rhythm: str) -> float:
    """DnB kick fitness - syncopated, punchy with offbeat bounce."""
    if not rhythm:
        return 0.0

    score = 0.0
    length = len(rhythm)

    # 1. Must have kick on beat 1 (strong anchor)
    if rhythm[0] != "0":
        score += 0.2

    # 2. Reward offbeat kicks (the DnB bounce) - positions 1, 3, 5, 7
    offbeat_hits = sum(1 for i in [1, 3, 5, 7] if i < length and rhythm[i] != "0")
    score += 0.25 * (offbeat_hits / min(4, length // 2))

    # 3. Reward syncopation - alternating patterns
    syncopation = sum(
        1 for i in range(length - 1) if rhythm[i] != rhythm[i + 1]
    ) / max(length - 1, 1)
    score += 0.2 * syncopation

    # 4. Moderate density - not too sparse, not too busy (target ~40-60%)
    density = sum(int(c) for c in rhythm) / (length * 4.0)
    density_score = 1.0 - abs(density - 0.35) * 3  # Peak at 35% density
    score += 0.2 * max(0, density_score)

    # 5. Penalize patterns that are too regular (every beat or every other beat)
    if rhythm == "1" * length or rhythm == "10" * (length // 2):
        score -= 0.15

    # 6. Reward some subdivision for that fast DnB feel
    has_subdivision = any(c in "234" for c in rhythm)
    if has_subdivision:
        score += 0.15

    return max(0.0, min(1.0, score))


def dnb_snare_fitness(rhythm: str) -> float:
    """DnB snare fitness - backbeat with ghost notes and rolls."""
    if not rhythm:
        return 0.0

    score = 0.0
    length = len(rhythm)

    # 1. Strong backbeat on beats 3 and 7 (indices 2, 6 in 8-beat)
    backbeat_positions = [2, 6] if length >= 8 else [1, 3]
    backbeat_hits = sum(1 for i in backbeat_positions if i < length and rhythm[i] != "0")
    score += 0.3 * (backbeat_hits / len(backbeat_positions))

    # 2. Reward ghost notes (hits on non-backbeat positions)
    ghost_positions = [i for i in range(length) if i not in backbeat_positions]
    ghost_hits = sum(1 for i in ghost_positions if rhythm[i] != "0")
    ghost_ratio = ghost_hits / max(len(ghost_positions), 1)
    # Want some ghosts but not too many (target 20-40%)
    ghost_score = 1.0 - abs(ghost_ratio - 0.3) * 3
    score += 0.25 * max(0, ghost_score)

    # 3. Reward subdivisions (rolls, fast hits)
    subdivision_count = sum(1 for c in rhythm if c in "234")
    subdivision_ratio = subdivision_count / length
    score += 0.25 * min(subdivision_ratio * 2, 1.0)

    # 4. Syncopation
    syncopation = sum(
        1 for i in range(length - 1) if rhythm[i] != rhythm[i + 1]
    ) / max(length - 1, 1)
    score += 0.2 * syncopation

    return max(0.0, min(1.0, score))


def dnb_hihat_fitness(rhythm: str) -> float:
    """DnB hihat fitness - fast, driving, dense."""
    if not rhythm:
        return 0.0

    score = 0.0
    length = len(rhythm)

    # 1. High density - DnB hats are fast (target 70-90%)
    density = sum(int(c) for c in rhythm) / (length * 4.0)
    density_score = min(density / 0.8, 1.0)  # Reward high density up to 80%
    score += 0.35 * density_score

    # 2. Consistency - steady driving pattern
    unique_vals = len(set(rhythm))
    consistency_score = 1.0 - (unique_vals - 1) / 4.0  # Fewer unique values = more consistent
    score += 0.25 * max(0, consistency_score)

    # 3. Prefer subdivisions (2s, 3s, 4s) over single hits
    subdivision_ratio = sum(1 for c in rhythm if c in "234") / length
    score += 0.25 * subdivision_ratio

    # 4. Penalize too many rests
    rest_ratio = rhythm.count("0") / length
    score += 0.15 * (1.0 - rest_ratio)

    return max(0.0, min(1.0, score))


# Use the new DnB-specific fitness functions
kick = dnb_kick_fitness
snare = dnb_snare_fitness
hihat = dnb_hihat_fitness


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 160  # Very slow, chill tempo (setcpm(6) = 24 BPM)
BARS = 2
BEATS_PER_BAR = 4

POPULATION_SIZE = 100
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
            gain=0.15,
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
            max_subdivision=2,  # Allow 8th notes for syncopated DnB kicks
            is_drum=True,
            drum_sound="bd",
            rhythm_fitness_fn=kick,
            layer_role="drums",
            context_group="",
            gain=0.3,
            lpf=2000,  # Warm kick
            bank="korgddm110",
        )
    )

    layers.append(
        LayerConfig(
            name="snare",
            instrument="sd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=3,  # Allow triplets for ghost notes and rolls
            is_drum=True,
            drum_sound="sd",
            rhythm_fitness_fn=snare,
            layer_role="drums",
            context_group="",
            gain=0.5,
            lpf=4000,
            room=0.15,  # Bit of room on snare
            bank="korgddm110",
        )
    )

    layers.append(
        LayerConfig(
            name="hihat",
            instrument="hh",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=4,  # Allow 16th notes for fast DnB hats
            is_drum=True,
            drum_sound="hh",
            rhythm_fitness_fn=hihat,
            layer_role="drums",
            context_group="",
            gain=0.15,
            lpf=6000,
            bank="korgddm110",
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
        (2, "stack(drums)"),
        # (2, "stack(intro)"),  # 2 bars - just bass and chords
        # (2, "stack(intro, drums)"),  # 2 bars - add drums
        # (4, "stack(drums, melodic_a)"),  # 4 bars - melody A
        # (4, "stack(drums, melodic_b)"),  # 4 bars - melody B
        # (4, "stack(drums, melodic_a)"),  # 4 bars - back to melody A
        # (2, "stack(intro, drums)"),  # 2 bars - breakdown
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
