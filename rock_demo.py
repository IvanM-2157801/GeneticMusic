#!/usr/bin/env python3
"""AC/DC-style Rock demo with driving rhythms and powerful riffs.

Run with: python rock_demo.py

Features:
- Power chords and triads (I-IV-V progressions)
- Straight, driving 4/4 drum patterns (no syncopation!)
- FM synthesis with distortion for guitar-like tones
- Pentatonic riffs (AC/DC style)
- Strong backbeat emphasis (kick on 1&3, snare on 2&4)
- Uses dirt-samples for realistic guitar sounds
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
    BLUES_SCALE,
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
    chord_type_variety,
    root_motion_smoothness,
    functional_harmony_score,
    resolution_bonus,
    triadic_bonus,
)
from fitness.contextual import get_context_groups
from core.genome_ops import ChordProgression
from layered_composer import LayeredComposer, LayerConfig


# =============================================================================
# AC/DC-STYLE ROCK FITNESS FUNCTIONS
# =============================================================================
# The key to AC/DC rock is SIMPLICITY and POWER:
# - Straight rhythms (NO syncopation - penalize it!)
# - High consistency (same pattern repeating)
# - Strong on-the-beat playing
# - Dense eighth-note patterns


def make_rock_rhythm_fitness(weights: dict[str, float]):
    """Rhythm fitness for AC/DC-style rock - STRAIGHT, driving, no syncopation.
    
    AC/DC rock characteristics:
    - NO syncopation (straight on-the-beat playing)
    - High consistency (same pattern over and over)
    - High density (driving eighth notes)
    - Strong groove (locked to the beat)
    """
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


def make_rock_melody_fitness(weights: dict[str, float], scale=PENTATONIC):
    """Melody fitness for AC/DC rock - pentatonic riffs, simple but powerful.
    
    AC/DC riff characteristics:
    - Pentatonic scale (blues-influenced)
    - Moderate variety (riffs repeat but have some movement)
    - Not too smooth, not too angular
    - Minimal rests (keep it driving!)
    """

    class RockMelodyFitness(FitnessFunction):
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

    return RockMelodyFitness()


def make_rock_drum_fitness(weights: dict[str, float]):
    """Drum fitness for AC/DC rock - simple, powerful, NO fills."""
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


def make_rock_chord_fitness(weights: dict[str, float]):
    """Chord fitness for AC/DC rock - power chords, I-IV-V only.
    
    AC/DC harmony:
    - Simple major triads (power chords in reality)
    - Strong I, IV, V (functional)
    - Very simple progressions
    - Root motion by 4ths and 5ths
    """

    class RockChordFitness(ChordFitnessFunction):
        def evaluate(self, progression: ChordProgression) -> float:
            metric_fns = {
                "variety": chord_variety,
                "types": chord_type_variety,
                "smooth": root_motion_smoothness,
                "functional": functional_harmony_score,
                "resolution": resolution_bonus,
                "triads": triadic_bonus,
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

    return RockChordFitness()


# =============================================================================
# AC/DC ROCK STYLE DEFINITIONS
# =============================================================================

# Chords: simple I-IV-V, major triads only
rock_chords = make_rock_chord_fitness(
    {
        "variety": 0.1,       # Low variety - keep it simple!
        "smooth": 0.3,        # Smooth root motion (4ths/5ths)
        "functional": 0.5,    # STRONG I-IV-V emphasis
        "triads": 0.4,        # Simple triads (power chords)
        "resolution": 0.1,    # Some resolution
    }
)

# Verse riff: pentatonic, driving, simple
verse_melody = make_rock_melody_fitness(
    {
        "variety": 0.2,       # Low variety (riff-based)
        "smoothness": 0.3,    # Moderate smoothness
        "scale": 0.5,         # Strong pentatonic adherence
        "rests": -0.4,        # Penalize rests
    },
    scale=PENTATONIC,
)

# Chorus riff: same as verse but slightly more variety
chorus_melody = make_rock_melody_fitness(
    {
        "variety": 0.3,       # Slightly more variety
        "smoothness": 0.2,    # Can be more angular
        "scale": 0.5,         # Strong pentatonic
        "rests": -0.5,        # Strongly penalize rests
    },
    scale=PENTATONIC,
)

# Verse rhythm: STRAIGHT eighth notes, no syncopation!
verse_rhythm = make_rock_rhythm_fitness(
    {
        "groove": 0.2,        # Good groove
        "density": 0.4,       # Very dense (eighth notes)
        "consistency": 0.4,   # VERY consistent (same pattern)
        "syncopation": -0.3,  # PENALIZE syncopation!
        "rests": -0.5,        # Strongly penalize rests
    }
)

# Chorus rhythm: same straight feel
chorus_rhythm = make_rock_rhythm_fitness(
    {
        "groove": 0.2,        # Good groove
        "density": 0.4,       # Very dense
        "consistency": 0.4,   # VERY consistent
        "syncopation": -0.3,  # PENALIZE syncopation!
        "rests": -0.5,        # Strongly penalize rests
    }
)

# Bass rhythm: lock with kick drum, simple root notes
bass_rhythm = make_rock_rhythm_fitness(
    {
        "groove": 0.3,        # Lock with drums
        "density": 0.3,       # Moderate-high density
        "consistency": 0.5,   # VERY consistent
        "syncopation": -0.4,  # NO syncopation
        "rests": -0.4,        # Penalize rests
    }
)

# =============================================================================
# AC/DC DRUM FITNESS - Simple and POWERFUL
# =============================================================================

# Kick drum: ONLY on beats 1 and 3 (strong beats)
# Custom fitness that penalizes hitting on beats 2 and 4
def kick_strong_beats_only(rhythm: str) -> float:
    """Kick fitness that ONLY allows hits on beats 1 and 3."""
    if not rhythm or len(rhythm) < 4:
        return 0.0
    
    score = 0.0
    
    # Reward: hits on beat 1 (index 0) and beat 3 (index 2)
    if rhythm[0] != "0":  # Beat 1
        score += 0.4
    if len(rhythm) > 2 and rhythm[2] != "0":  # Beat 3
        score += 0.4
    
    # Penalty: hits on beat 2 (index 1) and beat 4 (index 3)
    if rhythm[1] != "0":  # Beat 2 - should NOT hit
        score -= 0.3
    if len(rhythm) > 3 and rhythm[3] != "0":  # Beat 4 - should NOT hit
        score -= 0.3
    
    # Reward simplicity (single hits, no subdivisions)
    simple_count = sum(1 for c in rhythm if c == "1")
    active_count = sum(1 for c in rhythm if c != "0")
    if active_count > 0:
        score += 0.2 * (simple_count / active_count)
    
    return max(0.0, min(1.0, score))

kick_fitness = kick_strong_beats_only

# Snare drum: ONLY on beats 2 and 4 (backbeat) - the AC/DC signature
# Custom fitness that penalizes hitting on beats 1 and 3
def snare_backbeat_only(rhythm: str) -> float:
    """Snare fitness that ONLY allows hits on beats 2 and 4."""
    if not rhythm or len(rhythm) < 4:
        return 0.0
    
    score = 0.0
    
    # Reward: hits on beat 2 (index 1) and beat 4 (index 3)
    if rhythm[1] != "0":  # Beat 2
        score += 0.4
    if len(rhythm) > 3 and rhythm[3] != "0":  # Beat 4
        score += 0.4
    
    # Penalty: hits on beat 1 (index 0) and beat 3 (index 2)
    if rhythm[0] != "0":  # Beat 1 - should NOT hit
        score -= 0.3
    if len(rhythm) > 2 and rhythm[2] != "0":  # Beat 3 - should NOT hit
        score -= 0.3
    
    # Reward simplicity (single hits, no subdivisions)
    simple_count = sum(1 for c in rhythm if c == "1")
    active_count = sum(1 for c in rhythm if c != "0")
    if active_count > 0:
        score += 0.2 * (simple_count / active_count)
    
    return max(0.0, min(1.0, score))

snare_fitness = snare_backbeat_only

# Hi-hat: steady eighth notes, closed, driving
hihat_fitness = make_rock_drum_fitness(
    {
        "density": 0.5,       # Dense, driving eighths
        "consistency": 0.5,   # VERY consistent
        "simple": 0.2,        # Simple pattern
        "offbeat": -0.2,      # Minimal offbeat
    }
)


# =============================================================================
# CONTEXTUAL WEIGHTS
# =============================================================================

# Rock context: focus on rhythmic lock
verse_context = {
    "rhythmic": 0.6,       # Very important - lock together
    "harmonic": 0.2,
    "density": 0.1,
    "voice_leading": 0.1,
}

# Chorus context: same feel
chorus_context = {
    "rhythmic": 0.6,
    "harmonic": 0.2,
    "density": 0.1,
    "voice_leading": 0.1,
}


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 135  # AC/DC tempo (Back in Black = 94, Highway to Hell = 116, TNT = 126)
BARS = 1
BEATS_PER_BAR = 4

# Evolution settings
POPULATION_SIZE = 30  # Larger population for better results
MUTATION_RATE = 0.15  # Lower mutation for more stable patterns
ELITISM_COUNT = 6
RHYTHM_GENERATIONS = 35
MELODY_GENERATIONS = 40
CHORD_GENERATIONS = 30


def create_layers():
    """Create AC/DC-style rock layer configurations.
    
    Key changes from generic rock:
    - Use 'gm' bank for more realistic General MIDI sounds
    - Simpler rhythms with fewer subdivisions
    - Lower max_subdivision to prevent syncopated patterns
    - Heavier distortion with shape for gritty rock tone
    """
    layers = []

    # --- CHORD LAYER ---
    # Power chords - use sawtooth with heavy distortion for that crunch
    # In AC/DC, power chords are the foundation!
    layers.append(
        LayerConfig(
            name="power_chords",
            instrument="sawtooth",  # Sawtooth sounds more guitar-like than square
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,
            notes_per_chord=2,  # DYADS for power chords (root + 5th feel)
            allowed_chord_types=["major"],  # Major chords only for AC/DC
            chord_fitness_fn=rock_chords,
            layer_role="chords",
            context_group="",  # Global - shared across sections
            gain=0.4,
            lpf=1200,          # Keep some high end for crunch
            hpf=80,            # Cut sub-bass rumble
            distort=1.5,       # Heavy distortion for rock crunch
            room=0.2,          # Small room, tight sound
            attack=0.005,
            release=0.15,
        )
    )

    # --- VERSE SECTION ---
    # Lead riff (verse) - sawtooth with distortion for guitar sound
    # AC/DC riffs are simple, repetitive, driving eighth notes
    layers.append(
        LayerConfig(
            name="verse_riff",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # Only 8 beats - simpler, straighter
            max_subdivision=1,  # NO subdivisions - straight eighth notes only!
            octave_range=(3, 4),  # Lower register for power riffs
            base_octave=3,
            rhythm_fitness_fn=verse_rhythm,
            melody_fitness_fn=verse_melody,
            layer_role="melody",
            context_group="verse",
            contextual_weights=verse_context,
            gain=0.45,
            lpf=1500,
            hpf=100,
            distort=1.2,       # Rock distortion
            room=0.25,
        )
    )

    # Bass guitar (verse) - simple root notes, lock with kick
    # AC/DC bass is very simple - follows the root notes
    layers.append(
        LayerConfig(
            name="verse_bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,  # Only 4 beats - very simple
            max_subdivision=1,  # NO subdivisions!
            octave_range=(2, 2),  # Low and consistent
            base_octave=2,
            rhythm_fitness_fn=bass_rhythm,
            melody_fitness_fn=verse_melody,
            layer_role="bass",
            context_group="verse",
            gain=0.55,
            lpf=250,           # Very low pass for bass
            hpf=40,
            distort=0.3,       # Slight grit
        )
    )

    # --- DRUM LAYERS ---
    # AC/DC drums are SIMPLE: kick on 1-3, snare on 2-4, straight hi-hats
    # Using a harder-hitting bank for rock drums

    # Kick drum - ONLY on beats 1 and 3 (the "four on the floor" feel)
    layers.append(
        LayerConfig(
            name="kick",
            instrument="bd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,  # Only 4 positions - keeps it simple
            max_subdivision=1,  # Single hits only!
            is_drum=True,
            drum_sound="bd",
            rhythm_fitness_fn=kick_fitness,
            layer_role="drums",
            context_group="",
            gain=0.95,         # Very loud kick for rock!
            bank="RolandTR909",  # 909 has a harder hit
        )
    )

    # Snare - ONLY on beats 2 and 4 (pure backbeat)
    layers.append(
        LayerConfig(
            name="snare",
            instrument="sd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,  # Only 4 positions
            max_subdivision=1,  # Single hits only!
            is_drum=True,
            drum_sound="sd",
            rhythm_fitness_fn=snare_fitness,
            layer_role="drums",
            context_group="",
            gain=0.85,
            bank="RolandTR909",
        )
    )

    # Hi-hat - steady eighth notes, no variation
    layers.append(
        LayerConfig(
            name="hihat",
            instrument="hh",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,  # 4 positions
            max_subdivision=2,  # Allow eighth notes (2 per beat)
            is_drum=True,
            drum_sound="hh",
            rhythm_fitness_fn=hihat_fitness,
            layer_role="drums",
            context_group="",
            gain=0.4,          # Hi-hats quieter, drums dominate
            bank="RolandTR909",
        )
    )

    # --- CHORUS SECTION ---
    # Chorus riff - same as verse but higher energy
    layers.append(
        LayerConfig(
            name="chorus_riff",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 beats
            max_subdivision=1,  # NO subdivisions!
            octave_range=(4, 5),  # Higher for chorus impact
            base_octave=4,
            rhythm_fitness_fn=chorus_rhythm,
            melody_fitness_fn=chorus_melody,
            layer_role="melody",
            context_group="chorus",
            contextual_weights=chorus_context,
            gain=0.5,
            lpf=2000,
            hpf=100,
            distort=1.5,       # More distortion for chorus
            room=0.3,
        )
    )

    # Bass guitar (chorus) - same simple pattern
    layers.append(
        LayerConfig(
            name="chorus_bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,  # 4 beats only
            max_subdivision=1,
            octave_range=(2, 2),
            base_octave=2,
            rhythm_fitness_fn=bass_rhythm,
            melody_fitness_fn=verse_melody,
            layer_role="bass",
            context_group="chorus",
            gain=0.6,
            lpf=280,
            hpf=40,
            distort=0.35,
        )
    )

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" AC/DC-STYLE ROCK DEMO")
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
    print("Evolving rock patterns...")
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
    # AC/DC-STYLE ROCK SONG STRUCTURE
    # ==========================================================================
    # Define layer groups - AC/DC songs are simple: verse, chorus, repeat!
    layer_groups = {
        "drums": ["kick", "hihat", "snare"],
        "verse": ["verse_riff", "verse_bass", "power_chords"],
        "chorus": ["chorus_riff", "chorus_bass", "power_chords"],
        "intro": ["power_chords", "kick"],  # Drums start with intro
        "breakdown": ["verse_bass", "power_chords"],  # Quiet section
        "outro": ["chorus_riff", "power_chords", "kick"],
    }

    # AC/DC-style song arrangement: simple, driving, repetitive
    song_arrangement = [
        (2, "stack(intro)"),              # 2 bars intro
        (2, "stack(drums, verse)"),       # 2 bars verse intro with drums
        (4, "stack(drums, verse)"),       # 4 bars main verse
        (4, "stack(drums, chorus)"),      # 4 bars chorus - ENERGY!
        (4, "stack(drums, verse)"),       # 4 bars verse
        (4, "stack(drums, chorus)"),      # 4 bars chorus
        (2, "stack(breakdown)"),          # 2 bars breakdown (no drums)
        (4, "stack(drums, chorus)"),      # 4 bars final chorus - BIG!
        (2, "stack(outro)"),              # 2 bars outro
    ]

    # Get song structure
    song = composer.get_song_structure(
        bpm=BPM,
        random_scale=True,
        groups=layer_groups,
        arrangement=song_arrangement,
    )

    # Generate Strudel link
    print("\n" + "=" * 60)
    print(" STRUDEL LINK (ROCK SONG)")
    print("=" * 60)
    link = song.to_strudel_link()
    print(f"\nOpen this link to hear your rock composition:")
    print(link)

    print("\n" + "=" * 60)
    print(" STRUDEL CODE")
    print("=" * 60)
    print()
    print(song.to_strudel())
    print()


if __name__ == "__main__":
    main()
