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
    """DnB kick fitness - SPARSE, strategic placement like Amen break.
    
    Amen break: [bd ~ bd ~] ~ [~ ~ bd bd] [bd ~ ~ ~]
    In our 8-beat encoding:
    - Beat 0: YES (the anchor)
    - Beat 1: maybe
    - Beat 2: NO (snare)
    - Beat 3: NO (mostly)
    - Beat 4: maybe
    - Beat 5: maybe (syncopation)
    - Beat 6: NO (snare)
    - Beat 7: NO
    
    Total: 3-5 hits maximum (very sparse!)
    """
    if not rhythm:
        return 0.0

    score = 0.0
    length = len(rhythm)
    if length < 8:
        return 0.0

    # Count total hits
    total_hits = sum(int(c) for c in rhythm)
    
    # 1. CRITICAL: Must be SPARSE (3-5 hits total)
    if total_hits >= 3 and total_hits <= 5:
        score += 0.3
    elif total_hits >= 6 and total_hits <= 7:
        score += 0.1  # Acceptable
    else:
        score += 0.0  # Too few or too many

    # 2. MUST have kick on beat 0
    if rhythm[0] != "0":
        score += 0.3

    # 3. NO kicks on backbeat (2, 6) - that's snare territory
    if rhythm[2] == "0" and rhythm[6] == "0":
        score += 0.2
    else:
        score -= 0.2  # Penalty

    # 4. Reward kicks on offbeats (1, 5) for syncopation
    offbeat_score = 0
    if rhythm[1] != "0":
        offbeat_score += 0.5
    if rhythm[5] != "0":
        offbeat_score += 0.5
    score += 0.2 * min(offbeat_score, 1.0)

    return max(0.0, min(1.0, score))


def dnb_snare_fitness(rhythm: str) -> float:
    """DnB snare fitness - SPARSE backbeat only.
    
    Amen break snare: ~ [sd ~ ~ sd] [~ sd ~ ~] [~ ~ oh ~]
    In our 8-beat encoding:
    - Beat 0: REST (no snare)
    - Beat 1: maybe 1 hit
    - Beat 2: SINGLE hit (backbeat) 
    - Beat 3: maybe 1 hit
    - Beat 4: REST (no snare)
    - Beat 5: REST (no snare) 
    - Beat 6: SINGLE hit (backbeat)
    - Beat 7: maybe 1 hit
    
    Total hits: 2-4 ONLY (very sparse!)
    """
    if not rhythm:
        return 0.0

    score = 0.0
    length = len(rhythm)
    if length < 8:
        return 0.0

    # Count total hits
    total_hits = sum(int(c) for c in rhythm)
    
    # 1. CRITICAL: Must be SPARSE (only 2-4 hits total)
    if total_hits >= 2 and total_hits <= 4:
        score += 0.4
    elif total_hits >= 5 and total_hits <= 6:
        score += 0.2  # Acceptable but busier
    else:
        score += 0.0  # Too sparse or too busy

    # 2. MUST have backbeat on 2 and 6
    backbeat_positions = [2, 6]
    backbeat_hits = sum(1 for i in backbeat_positions if rhythm[i] != "0")
    score += 0.4 * (backbeat_hits / 2.0)

    # 3. Backbeat should be SINGLE hits, not subdivisions
    if rhythm[2] == "1":
        score += 0.1
    if rhythm[6] == "1":
        score += 0.1

    # 4. NO snares on beats 0, 4 (those are kick positions)
    if rhythm[0] == "0" and rhythm[4] == "0":
        score += 0.0  # Good, no penalty needed
    else:
        score -= 0.2  # Penalty

    return max(0.0, min(1.0, score))


def dnb_hihat_fitness(rhythm: str) -> float:
    """DnB hihat/ride fitness - consistent driving 8th notes.
    
    Amen break ride: [rd ~ rd ~] [rd ~ rd ~] (repeated)
    In our encoding: all 2s (8th notes) or all 1s
    Target: "22222222" or "11111111"
    """
    if not rhythm:
        return 0.0

    score = 0.0
    length = len(rhythm)

    # 1. PERFECT CONSISTENCY - same value repeated (critical!)
    unique_vals = len(set(rhythm))
    if unique_vals == 1 and rhythm[0] != "0":  # All same, no rests
        score += 0.5
    elif unique_vals == 2 and "0" in rhythm:  # One value + some rests
        score += 0.2
    elif unique_vals <= 2:  # Two different subdivisions
        score += 0.1

    # 2. Prefer 8th notes (2s) or constant quarter notes (1s)
    if rhythm == "2" * length:
        score += 0.3  # Perfect 8th note groove!
    elif rhythm == "1" * length:
        score += 0.2  # Acceptable quarter note groove

    # 3. No rests (driving timekeeping)
    rest_count = rhythm.count("0")
    score += 0.2 * (1.0 - rest_count / length)

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
            beats_per_bar=BEATS_PER_BAR,  # 4 beats per bar = 8 total beats
            max_subdivision=2,  # Allow pairs and syncopation
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
