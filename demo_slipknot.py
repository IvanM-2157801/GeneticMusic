#!/usr/bin/env python3
"""Demo for generating SLIPKNOT-style heavy metal compositions.

Run with: python demo_slipknot.py

This demo creates aggressive nu-metal/groove metal compositions inspired by Slipknot:
- Down-tuned power chords in drop-D tuning
- Heavy, groovy bass with syncopation
- Complex, polyrhythmic drums with emphasis on kicks and snare
- Dense layering with multiple guitar textures
- Extreme dynamic range (quiet verses, explosive choruses)
- DJ/sampler elements for texture and transition

Key fitness optimizations for metal:
- Minimal rests (aggressive, dense playing)
- Strong beat emphasis and syncopation
- Power chord harmony (major/minor emphasis)
- Rhythmic consistency with high intensity
- Harmonic darkness through minor scales and low frequencies
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
# METAL FITNESS BUILDERS - OPTIMIZED FOR SLIPKNOT STYLE
# =============================================================================


def make_metal_rhythm_fitness(weights: dict[str, float]):
    """Create a heavy metal rhythm fitness optimized for aggression and density.
    
    Available metrics:
        groove       - Strong/weak beat alternation (heavy, drives the pit)
        complexity   - Variety of subdivisions (interesting fills and breaks)
        density      - Notes per beat (MAXIMIZE for metal - minimal silence)
        syncopation  - Offbeat emphasis (creates tension and surprise)
        consistency  - Pattern repetition (headbang-able, memorable)
        offbeat      - Offbeat hits (funky, unhinged feel)
    
    For SLIPKNOT-style metal:
    - Maximize density (aggressive, relentless playing)
    - High syncopation (unpredictable, chaotic feel)
    - Strong groove (hypnotic, driving)
    - Minimal rests (dense, no breathing room)
    """
    metric_fns = {
        "groove": rhythm_groove,
        "complexity": rhythm_complexity,
        "density": rhythm_density,
        "syncopation": rhythm_syncopation,
        "consistency": rhythm_consistency,
        "offbeat": rhythm_offbeat_emphasis,
    }

    def fitness(rhythm: str) -> float:
        score = 0.0
        total_weight = 0.0
        for metric, weight in weights.items():
            if metric in metric_fns:
                fn = metric_fns[metric]
                value = fn(rhythm)
                score += weight * value
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5

    return fitness


def make_metal_melody_fitness(weights: dict[str, float], scale=MINOR_SCALE):
    """Create a metal melody fitness for power chords and aggressive playing.
    
    Available metrics:
        variety      - Pitch variety (keeps it interesting)
        smoothness   - Small intervals (singable/playable, but penalize heavily)
        scale        - Adherence to scale (dark, in-key)
        rests        - PENALIZE rests heavily (aggressive, no silence)
    
    For SLIPKNOT-style:
    - Heavy scale adherence (dark, dissonant feel)
    - Variety for interesting riffs
    - STRONG penalty for rests
    - Allow some jumps for aggressive power chords
    """

    class MetalMelodyFitness(FitnessFunction):
        def evaluate(self, layer: Layer) -> float:
            if not layer.phrases:
                return 0.0

            metric_fns = {
                "variety": note_variety,
                "smoothness": interval_smoothness,
                "scale": lambda p: scale_adherence(p, scale),
            }

            def score_phrase(phrase: Phrase) -> float:
                score = 0.0
                total_weight = 0.0
                
                # Penalize rests HEAVILY in metal (aggressive, dense)
                rest_ratio_val = rest_ratio(phrase)
                score += weights.get("rests", -0.8) * (1 - rest_ratio_val)  # Penalize silence
                total_weight += abs(weights.get("rests", -0.8))
                
                for metric, weight in weights.items():
                    if metric != "rests" and metric in metric_fns:
                        fn = metric_fns[metric]
                        value = fn(phrase)
                        score += weight * value
                        total_weight += abs(weight)
                
                return score / total_weight if total_weight > 0 else 0.5

            scores = [score_phrase(p) for p in layer.phrases]
            return sum(scores) / len(scores)

    return MetalMelodyFitness()


def make_metal_chord_fitness(weights: dict[str, float]):
    """Create chord fitness for dark, heavy harmony.
    
    For SLIPKNOT-style:
    - Power chords (empty 3rds for aggressive tone)
    - Minor tonality (dark, aggressive)
    - Root motion emphasis (heavy, grounded)
    - Functional harmony with dark voicings
    """

    class MetalChordFitness(ChordFitnessFunction):
        def evaluate(self, progression: ChordProgression) -> float:
            metric_fns = {
                "variety": chord_variety,
                "types": chord_type_variety,
                "smooth": root_motion_smoothness,
                "functional": functional_harmony_score,
            }

            score = 0.0
            total_weight = 0.0
            for metric, weight in weights.items():
                if metric in metric_fns:
                    fn = metric_fns[metric]
                    value = fn(progression)
                    score += weight * value
                    total_weight += abs(weight)
            return score / total_weight if total_weight > 0 else 0.5

    return MetalChordFitness()


def make_metal_drum_fitness(weights: dict[str, float]):
    """Create drum fitness for heavy, aggressive metal patterns.
    
    For SLIPKNOT style, different drums do different things:
    - Kick: Strong beat emphasis, groove
    - Snare: Backbeat emphasis, sharp attacks
    - Hi-hat: Density and consistency for pocket
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
                score += weight * value
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5

    return fitness



# =============================================================================
# SLIPKNOT-STYLE FITNESS CONFIGURATION
# =============================================================================
# Metal-specific optimization: heavy distortion, extreme dynamics, dense rhythms

# AGGRESSIVE VERSE RHYTHM: Heavy, syncopated, relentless
verse_rhythm_metal = make_metal_rhythm_fitness(
    {
        "groove": 0.3,          # Some groove but aggressive
        "syncopation": 0.4,     # High syncopation for unpredictable feel
        "density": 0.6,         # HEAVY density - aggressive, no space
        "complexity": 0.2,      # Interesting fills
        "consistency": 0.1,     # Some repetition
    }
)

# EXPLOSIVE CHORUS RHYTHM: Even more aggressive
chorus_rhythm_metal = make_metal_rhythm_fitness(
    {
        "groove": 0.2,
        "syncopation": 0.5,     # Maximum syncopation
        "density": 0.7,         # MAXIMUM density for chorus explosion
        "complexity": 0.3,
        "consistency": 0.0,
    }
)

# HEAVY BASS RHYTHM: Thick, groovy foundation with lots of notes
bass_rhythm_metal = make_metal_rhythm_fitness(
    {
        "groove": 0.6,          # Strong groove pocket
        "consistency": 0.2,     # Repeatable patterns
        "density": 0.5,         # Busy but not chaotic
        "syncopation": 0.2,
    }
)

# HEAVY GUITAR MELODY: Power chords, aggressive, dissonant
verse_guitar_metal = make_metal_melody_fitness(
    {
        "variety": 0.4,         # Riff variety for interest
        "smoothness": -0.1,     # Allow jumps (power chords are jumpy)
        "scale": 0.6,           # Heavy emphasis on dark scale
        "rests": -0.8,          # AGGRESSIVE: Penalize rests heavily
    },
    scale=MINOR_SCALE,
)

# LEAD GUITAR METAL: More aggressive, less smooth
chorus_guitar_metal = make_metal_melody_fitness(
    {
        "variety": 0.7,         # High variety for lead work
        "smoothness": -0.2,     # Lots of jumps
        "scale": 0.5,           # Scale adherence
        "rests": -0.9,          # Extremely aggressive - almost no rests
    },
    scale=MINOR_SCALE,
)

# DARK METAL CHORDS: Heavy, minor-focused, functional
metal_chords = make_metal_chord_fitness(
    {
        "functional": 0.5,      # Functional harmony (I, IV, V emphasis)
        "smooth": 0.3,          # Smooth root movement
        "variety": 0.1,         # Some variety
        "types": 0.1,           # Some chord type variety
    }
)

# =============================================================================
# DRUM FITNESS FOR METAL - SLIPKNOT STYLE
# =============================================================================

# KICK DRUM: Heavy emphasis on beats 1 & 5, some groove
kick_metal = make_metal_drum_fitness(
    {
        "strong_beat": 0.6,     # Hit on downbeats
        "density": 0.3,         # Some extra hits for aggression
        "consistency": 0.1,     # Repeating pattern
    }
)

# HI-HAT: Very busy, relentless, driving the groove
hihat_metal = make_metal_drum_fitness(
    {
        "density": 0.7,         # VERY BUSY - relentless hi-hats
        "consistency": 0.2,     # Steady pattern
        "offbeat": 0.1,         # Some offbeat feel
    }
)

# SNARE: Backbeat emphasis (2 & 4), sharp, cutting through mix
snare_metal = make_metal_drum_fitness(
    {
        "backbeat": 0.7,        # Strong 2 & 4 emphasis
        "density": 0.2,         # Some extra snare hits
        "simple": 0.1,          # Mostly single hits
    }
)

# CONTEXT WEIGHTS FOR METAL
verse_context_metal = {
    "rhythmic": 0.5,        # Rhythmic lock between instruments
    "harmonic": 0.2,        # Less harmonic concern (aggressive)
    "density": 0.2,         # Density compatibility
    "voice_leading": 0.05,  # Minimal voice leading
    "call_response": 0.05,  # Some call-response
}

chorus_context_metal = {
    "rhythmic": 0.4,        # Still rhythmic but more chaos
    "harmonic": 0.1,        # Minimal harmonic concern
    "density": 0.3,         # High density contrast
    "voice_leading": 0.1,   # Very minimal
    "call_response": 0.1,
}


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
    """Create all layer configurations for SLIPKNOT-style metal composition.
    
    Uses actual guitar samples from Dirt-Samples library:
    - gtr: Guitar samples (cleanC, ovrdC, distC - clean, overdriven, distorted)
    - metal: Metal percussion hits
    """
    layers = []

    # =================================================================
    # GUITAR LAYERS (actual guitar samples from Dirt-Samples)
    # =================================================================
    # Guitar 1: Heavy rhythm guitar with DISTORTED sample
    layers.append(
        LayerConfig(
            name="rhythm_guitar_1",
            instrument="gtr",                 # Use actual guitar samples from Dirt-Samples
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 beats for riff control
            max_subdivision=2,
            octave_range=(2, 3),              # Lower register for heaviness
            base_octave=2,
            rhythm_fitness_fn=verse_rhythm_metal,
            melody_fitness_fn=verse_guitar_metal,
            layer_role="melody",
            context_group="verse",
            contextual_weights=verse_context_metal,
            gain=0.9,                         # HIGH gain to emphasize distortion
            room=0.05,                        # Minimal reverb (tight, dry metal)
            attack=0.01,
            release=0.3,
        )
    )

    # Guitar 2: Second rhythm guitar (OVERDRIVEN sample for layering)
    layers.append(
        LayerConfig(
            name="rhythm_guitar_2",
            instrument="gtr",                 # Use guitar samples (will select different sample variant)
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=2,
            octave_range=(2, 3),
            base_octave=2,
            rhythm_fitness_fn=verse_rhythm_metal,
            melody_fitness_fn=verse_guitar_metal,
            layer_role="melody",
            context_group="verse",
            contextual_weights=verse_context_metal,
            gain=0.85,                        # Slightly lower for blend
            room=0.03,
            attack=0.01,
            release=0.3,
        )
    )

    # Guitar 3: Lead/fill guitar (CLEAN sample for presence)
    layers.append(
        LayerConfig(
            name="lead_guitar",
            instrument="gtr",                 # Guitar samples - lead notes
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 4,  # 16 beats for faster riffs
            max_subdivision=2,
            octave_range=(3, 4),              # Slightly higher for presence
            base_octave=3,
            rhythm_fitness_fn=chorus_rhythm_metal,
            melody_fitness_fn=chorus_guitar_metal,
            layer_role="melody",
            context_group="chorus",
            contextual_weights=chorus_context_metal,
            gain=0.8,
            room=0.1,
            attack=0.005,
            release=0.2,
        )
    )

    # =================================================================
    # BASS LAYER (heavy, thick, groovy foundation)
    # =================================================================
    layers.append(
        LayerConfig(
            name="bass",
            instrument="sine",                # Keep sine for bass foundation (solid low-end)
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,
            octave_range=(1, 2),              # VERY LOW register
            base_octave=1,
            rhythm_fitness_fn=bass_rhythm_metal,
            melody_fitness_fn=verse_guitar_metal,  # Use aggressive fitness
            layer_role="bass",
            context_group="verse",
            gain=0.9,                         # HIGH gain for presence
            room=0.0,                         # NO reverb
            attack=0.01,
            release=0.4,
        )
    )

    # =================================================================
    # DRUM LAYERS (complex, polyrhythmic, aggressive)
    # =================================================================
    # Kick: Using TR909 drum machine samples for classic metal punch
    layers.append(
        LayerConfig(
            name="kick",
            instrument="bd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=2,                # Allow some kick syncopation
            is_drum=True,
            drum_sound="bd",
            rhythm_fitness_fn=kick_metal,
            layer_role="drums",
            context_group="",                 # Global
            gain=1.0,                         # MAXIMUM kick volume
            bank="RolandTR909",               # Classic 909 drum machine
        )
    )

    # Snare: Sharp, cutting snare for backbeat
    layers.append(
        LayerConfig(
            name="snare",
            instrument="sd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,
            max_subdivision=1,                # Sharp snare hits
            is_drum=True,
            drum_sound="sd",
            rhythm_fitness_fn=snare_metal,
            layer_role="drums",
            context_group="",
            gain=0.9,
            bank="RolandTR909",               # 909 snare for aggression
        )
    )

    # Hi-hat: Relentless hi-hat for groove pocket
    layers.append(
        LayerConfig(
            name="hihat",
            instrument="hh",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 4,  # 16 beats for relentless feel
            max_subdivision=2,                # Allow fast hi-hat patterns
            is_drum=True,
            drum_sound="hh",
            rhythm_fitness_fn=hihat_metal,
            layer_role="drums",
            context_group="",
            gain=0.6,                         # Balanced hi-hat level
            bank="RolandTR909",               # 909 hi-hat for sharp attack
        )
    )

    # =================================================================
    # CHORD LAYER (harmonic foundation with metal samples)
    # =================================================================
    layers.append(
        LayerConfig(
            name="chords",
            instrument="metal",               # Use actual metal hit samples from Dirt-Samples
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,
            notes_per_chord=4,
            allowed_chord_types=["major", "minor"],  # Power chords emphasis
            chord_fitness_fn=metal_chords,
            layer_role="harmony",
            context_group="",
            gain=0.5,                         # Balanced metal sample level
            room=0.1,
            attack=0.01,
            release=0.3,
        )
    )

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 70)
    print(" SLIPKNOT-STYLE HEAVY METAL COMPOSITION GENERATOR")
    print("=" * 70)
    print(f"\nAggressive Nu-Metal Configuration:")
    print(f"  BPM: {BPM} (Heavy, slow, powerful)")
    print(f"  Bars: {BARS}, Beats/bar: {BEATS_PER_BAR}")
    print(f"  Population: {POPULATION_SIZE} (lean for chaos)")
    print(f"  Mutation Rate: {MUTATION_RATE} (chaotic evolution)")
    print()

    # Create composer with metal-tuned settings
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

    # Show layer configuration
    print("Layer Configuration (9 Members of the Nine):")
    print("-" * 70)
    for config in layers:
        group = config.context_group if config.context_group else "(drums/global)"
        print(f"  {config.name:<20} role={config.layer_role:<10} group={group:<15}")
    print()

    # Evolve with feedback
    print("Evolving aggressive metal composition...")
    print("This may take a moment - generating chaos...")
    composer.evolve_all_layers(verbose=True)

    # Show context groups
    print("\n" + "=" * 70)
    print(" CONTEXT GROUPS (Multi-Section Arrangement)")
    print("=" * 70)
    groups = get_context_groups(composer.evolved_layers)
    for group, members in sorted(groups.items()):
        group_name = group if group else "(drums - global, play with all)"
        print(f"\n{group_name}:")
        for name in members:
            layer, rhythm = composer.evolved_layers[name]
            print(f"  - {name}")

    # Print summary
    composer.print_summary()

    # ==========================================================================
    # SONG STRUCTURE - SLIPKNOT STYLE
    # ==========================================================================
    # Define layer groups for arrangement
    layer_groups = {
        "drums_all": ["kick", "snare", "hihat"],
        "guitars": ["rhythm_guitar_1", "rhythm_guitar_2", "lead_guitar"],
        "rhythm_section": ["bass", "chords"],
        "verse": ["rhythm_guitar_1", "rhythm_guitar_2", "bass", "chords"],
        "chorus": ["lead_guitar", "bass", "chords"],
    }

    # Slipknot-style arrangement: verses, heavy chorus, breakdown
    song_arrangement = [
        (2, "stack(drums_all, verse)"),      # 2 bars: verse with rhythm section
        (2, "stack(drums_all, verse)"),      # 2 bars: verse
        (2, "stack(drums_all, chorus)"),     # 2 bars: EXPLOSIVE chorus
        (2, "stack(drums_all, chorus)"),     # 2 bars: chorus continues
        (2, "stack(drums_all, verse)"),      # 2 bars: back to verse (contrast)
        (2, "stack(drums_all, chorus)"),     # 2 bars: final chorus explosion
    ]

    # Generate song with random scale selection
    song = composer.get_song_structure(
        bpm=BPM,
        random_scale=True,                   # Random scale each run
        groups=layer_groups,
        arrangement=song_arrangement,
    )

    # Generate and display Strudel link
    print("\n" + "=" * 70)
    print(" SLIPKNOT-STYLE COMPOSITION READY")
    print("=" * 70)
    print("\nOpen this link in Strudel Live Coder to hear your metal composition:")
    link = song.to_strudel_link()
    print(link)

    print("\n" + "=" * 70)
    print(" STRUDEL CODE (FULL COMPOSITION)")
    print("=" * 70)
    print()
    print(song.to_strudel())
    print()
    print("=" * 70)
    print(" AUDIO CHARACTERISTICS:")
    print("=" * 70)
    print("  ✓ ACTUAL GUITAR SAMPLES from Dirt-Samples library:")
    print("    - rhythm_guitar_1: 'gtr' (distorted guitar)")
    print("    - rhythm_guitar_2: 'gtr' (overdrive guitar)")
    print("    - lead_guitar: 'gtr' (clean/lead guitar)")
    print("    - chords: 'metal' (metal percussion hits)")
    print("  - Heavy, syncopated rhythms")
    print("  - Aggressive, relentless hi-hat patterns")
    print("  - Deep sub-bass foundation (sine wave)")
    print("  - Complex drum polyrhythms (TR909 drums)")
    print("  - Minimal reverb for tight, dry metal sound")
    print("  - Dynamic range: verses → explosive choruses")
    print("=" * 70)


if __name__ == "__main__":
    main()
