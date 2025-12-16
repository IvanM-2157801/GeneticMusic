#!/usr/bin/env python3
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
    # Advanced primitives for DnB
    hit_count_score,
    hits_at_positions,
    avoid_positions,
    single_hits_at_positions,
    perfect_consistency,
    uniform_subdivision,
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
        "variety": 0.9,
        "smoothness": 0.5,  # Very smooth intervals
        "scale": 0.3,
        "rests": 0.4,  # Some breathing room
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
# These use the primitive functions from fitness/drums.py for composability


def dnb_kick_fitness(rhythm: str) -> float:
    """DnB kick fitness - Amen break style.

    Amen kick pattern: `10010100` or `11010100`
    - Beat 0: ALWAYS (the anchor)
    - Beat 5: CRITICAL (syncopation before second snare)
    - Beats 2,6: NEVER (snare territory)
    - Total: 3-4 hits (very sparse)
    """
    if not rhythm or len(rhythm) < 8:
        return 0.0

    score = 0.0

    # 1. MUST have kick on beat 0 (the Amen anchor) - highest priority
    score += 0.35 * hits_at_positions(rhythm, [0])

    # 2. Beat 5 syncopation is the Amen signature (before second snare)
    score += 0.25 * hits_at_positions(rhythm, [5])

    # 3. NEVER on backbeat (2, 6) - snare territory, strict avoidance
    score += 0.25 * avoid_positions(rhythm, [2, 6])

    # 4. Sparse: exactly 3-4 hits for authentic Amen feel
    score += 0.15 * hit_count_score(rhythm, 3, 4)

    return max(0.0, min(1.0, score))


def dnb_snare_fitness(rhythm: str) -> float:
    """DnB snare fitness - Amen break style.

    Amen snare pattern: `00100010` (exactly 2 hits on backbeat)
    - Beats 2,6: ALWAYS (clean backbeat)
    - All other beats: NEVER
    - Total: exactly 2 hits
    - Single punchy hits, no rolls
    """
    if not rhythm or len(rhythm) < 8:
        return 0.0

    score = 0.0

    # 1. MUST have backbeat on 2 and 6 - highest priority
    score += 0.4 * hits_at_positions(rhythm, [2, 6])

    # 2. Backbeat should be SINGLE hits (punchy, not subdivided)
    score += 0.25 * single_hits_at_positions(rhythm, [2, 6])

    # 3. Exactly 2 hits for clean Amen snare
    score += 0.2 * hit_count_score(rhythm, 2, 2)

    # 4. NO snares anywhere else (avoid kick positions and offbeats)
    score += 0.15 * avoid_positions(rhythm, [0, 1, 3, 4, 5, 7])

    return max(0.0, min(1.0, score))


def dnb_hihat_fitness(rhythm: str) -> float:
    """DnB hihat/ride fitness - consistent driving 8th notes.

    Uses primitives:
    - perfect_consistency: All same subdivision value
    - uniform_subdivision: Target "2" (8th notes)
    - rhythm_rest_ratio: Penalize rests
    """
    if not rhythm:
        return 0.0

    from fitness.rhythm import rhythm_rest_ratio

    score = 0.0

    # 1. PERFECT CONSISTENCY - same value repeated (critical!)
    score += 0.4 * perfect_consistency(rhythm)

    # 2. Prefer 8th notes (all 2s)
    score += 0.35 * uniform_subdivision(rhythm, "2")

    # 3. No rests (driving timekeeping)
    score += 0.25 * (1.0 - rhythm_rest_ratio(rhythm))

    return max(0.0, min(1.0, score))


# Use the new DnB-specific fitness functions
kick = dnb_kick_fitness
snare = dnb_snare_fitness
hihat = dnb_hihat_fitness


BPM = 160
BARS = 2
BEATS_PER_BAR = 4

POPULATION_SIZE = 100
MUTATION_RATE = 0.2
ELITISM_COUNT = 5
RHYTHM_GENERATIONS = 30
MELODY_GENERATIONS = 35
CHORD_GENERATIONS = 30


def create_lofi_layers():
    """Create lofi layer configurations."""
    layers = []

    # Main melody A
    layers.append(
        LayerConfig(
            name="melody_a",
            instrument="supersaw",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=2,
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=lofi_rhythm,
            melody_fitness_fn=lofi_melody,
            layer_role="melody",
            context_group="main",
            gain=0.4,
            lpf=1000,
            room=0.5,
            delay=0.3,
            delaytime=0.375,  # Dotted eighth delay
            delayfeedback=0.4,
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
            gain=0.35,
            lpf=300,
        )
    )

    layers.append(
        LayerConfig(
            name="kick",
            instrument="bd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,
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
            beats_per_bar=BEATS_PER_BAR,  # 4 beats per bar = 8 total beats
            max_subdivision=2,  # Only allow pairs, no triplets
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
            beats_per_bar=BEATS_PER_BAR,  # 4 beats per bar = 8 total beats
            max_subdivision=2,  # 8th notes for driving pattern
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

    # Lofi structure with intro buildup and alternating melodies
    song_arrangement = [
        (2, "stack(melody_a)"),  # 2 bars - just bass and chords
        # (4, "stack(melodic_a)"),  # 4 bars - melody A
        # (4, "stack(drums, melodic_a)"),  # 4 bars - back to melody A
        # (4, "stack(drums, melodic_b)"),  # 4 bars - melody B
    ]

    # Use a chill minor scale
    song = composer.get_song_structure(
        bpm=BPM,
        random_scale=False,  # We'll set it manually for lofi vibe
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
