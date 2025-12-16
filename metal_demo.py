#!/usr/bin/env python3
"""Metal Music Demo using Genetic Algorithm.

Run with: python metal_demo.py

This demo creates aggressive metal music with:
- Palm-muted rhythm guitar with ROOT-FOCUSED chugging patterns
- Power chord progressions (E minor based)
- Screaming lead guitar lines
- Heavy distorted bass (root note emphasis)
- Double bass drum patterns (blast beats)
- Punchy backbeat snare
- Cymbal accents

Based on the metal_song.js Strudel reference.

KEY INSIGHT: Metal requires REPETITIVE, ROOT-FOCUSED patterns.
Unlike pop/jazz that wants variety, metal wants:
- Same note repeated (especially the root)
- Minimal pitch variety
- Relentless rhythm patterns
"""

from core.music import Phrase, Layer, NoteName
from fitness.base import (
    FitnessFunction,
    note_variety,
    rest_ratio,
    interval_smoothness,
    scale_adherence,
    rhythmic_variety,
    MINOR_SCALE,
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
# METAL-SPECIFIC SCALES
# =============================================================================

# E minor scale for metal
E_MINOR_SCALE = [
    NoteName.E,
    NoteName.FS,  # F#
    NoteName.G,
    NoteName.A,
    NoteName.B,
    NoteName.C,
    NoteName.D,
]


# =============================================================================
# METAL-SPECIFIC MELODY FITNESS FUNCTIONS
# =============================================================================
# Metal melodies need to be REPETITIVE and ROOT-FOCUSED, not varied!


def root_note_emphasis(phrase: Phrase, root: NoteName = NoteName.E) -> float:
    """Measure how often the root note appears (0-1). Higher = more root notes.
    
    Metal riffs should emphasize the root note (E in E minor).
    """
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if not notes:
        return 0.0
    
    root_count = sum(1 for n in notes if n.pitch == root)
    return root_count / len(notes)


def note_repetition(phrase: Phrase) -> float:
    """Measure consecutive note repetition (0-1). Higher = more repetition.
    
    Metal chugging should repeat the same note many times.
    """
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if len(notes) < 2:
        return 0.5
    
    repetitions = 0
    for i in range(len(notes) - 1):
        if notes[i].pitch == notes[i + 1].pitch and notes[i].octave == notes[i + 1].octave:
            repetitions += 1
    
    return repetitions / (len(notes) - 1)


def low_pitch_bias(phrase: Phrase, max_octave: int = 3) -> float:
    """Measure how many notes are in low octaves (0-1). Higher = more low notes.
    
    Metal riffs should be in low octaves for heaviness.
    """
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if not notes:
        return 0.0
    
    low_count = sum(1 for n in notes if n.octave <= max_octave)
    return low_count / len(notes)


def pitch_uniformity(phrase: Phrase) -> float:
    """Inverse of variety - rewards using few unique pitches (0-1).
    
    Metal chugging should use only 1-3 different pitches.
    """
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if not notes:
        return 0.0
    
    unique_pitches = len(set((n.pitch, n.octave) for n in notes))
    
    # 1 unique pitch = 1.0, 2 = 0.8, 3 = 0.6, 4+ = lower
    if unique_pitches == 1:
        return 1.0
    elif unique_pitches == 2:
        return 0.8
    elif unique_pitches == 3:
        return 0.6
    else:
        return max(0.0, 1.0 - (unique_pitches - 1) * 0.15)


# =============================================================================
# FITNESS BUILDERS
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
                value = metric_fns[metric](rhythm)
                if weight < 0:
                    score += abs(weight) * (1 - value)
                else:
                    score += weight * value
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5

    return fitness


def make_metal_riff_fitness(root: NoteName = NoteName.E, scale=E_MINOR_SCALE):
    """Create a melody fitness for metal riffs - ROOT FOCUSED, REPETITIVE.
    
    This is the key difference from pop/jazz fitness!
    Metal riffs should:
    - Play the root note most of the time
    - Repeat notes consecutively
    - Stay in low octaves
    - Have minimal pitch variety
    """

    class MetalRiffFitness(FitnessFunction):
        def evaluate(self, layer: Layer) -> float:
            if not layer.phrases:
                return 0.0

            scores = []
            for phrase in layer.phrases:
                # Penalize rests heavily - metal is relentless
                rest_penalty = rest_ratio(phrase)
                if rest_penalty > 0.5:
                    scores.append(0.1)
                    continue
                
                score = (
                    0.35 * root_note_emphasis(phrase, root) +  # Root note focus
                    0.25 * note_repetition(phrase) +            # Repeat same note
                    0.20 * pitch_uniformity(phrase) +           # Few unique pitches
                    0.10 * scale_adherence(phrase, scale) +     # Stay in scale
                    0.10 * (1 - rest_penalty)                   # Minimize rests
                )
                scores.append(score)

            return sum(scores) / len(scores)

    return MetalRiffFitness()


def make_metal_bass_fitness(root: NoteName = NoteName.E, scale=E_MINOR_SCALE):
    """Create a melody fitness for metal bass - EXTREMELY root focused."""

    class MetalBassFitness(FitnessFunction):
        def evaluate(self, layer: Layer) -> float:
            if not layer.phrases:
                return 0.0

            scores = []
            for phrase in layer.phrases:
                rest_penalty = rest_ratio(phrase)
                if rest_penalty > 0.3:
                    scores.append(0.1)
                    continue
                
                score = (
                    0.45 * root_note_emphasis(phrase, root) +  # Heavy root focus
                    0.25 * note_repetition(phrase) +            # Repeat notes
                    0.15 * low_pitch_bias(phrase, max_octave=2) +  # Stay low
                    0.15 * (1 - rest_penalty)                   # No rests
                )
                scores.append(score)

            return sum(scores) / len(scores)

    return MetalBassFitness()


def make_metal_lead_fitness(scale=E_MINOR_SCALE):
    """Create a melody fitness for metal lead guitar - more expressive but still in scale."""

    class MetalLeadFitness(FitnessFunction):
        def evaluate(self, layer: Layer) -> float:
            if not layer.phrases:
                return 0.0

            scores = []
            for phrase in layer.phrases:
                score = (
                    0.35 * scale_adherence(phrase, scale) +     # Stay in scale
                    0.25 * note_variety(phrase) +               # Some variety for leads
                    0.20 * (1 - rest_ratio(phrase)) +           # Some notes
                    0.20 * interval_smoothness(phrase)          # Melodic movement
                )
                scores.append(score)

            return sum(scores) / len(scores)

    return MetalLeadFitness()


def make_chord_fitness(weights: dict[str, float]):
    """Create a chord fitness function from a dictionary of weights."""

    class CustomChordFitness(ChordFitnessFunction):
        def evaluate(self, progression: ChordProgression) -> float:
            metrics = {
                "variety": chord_variety(progression),
                "types": chord_type_variety(progression),
                "smooth": root_motion_smoothness(progression),
                "functional": functional_harmony_score(progression),
                "resolution": resolution_bonus(progression),
                "triads": triadic_bonus(progression),
                "sevenths": seventh_chord_bonus(progression),
            }

            score = 0.0
            total_weight = 0.0
            for metric, weight in weights.items():
                if metric in metrics:
                    score += weight * metrics[metric]
                    total_weight += weight

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
                value = metric_fns[metric](rhythm)
                if weight < 0:
                    score += abs(weight) * (1 - value)
                else:
                    score += weight * value
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5

    return fitness


# =============================================================================
# METAL-SPECIFIC FITNESS FUNCTIONS
# =============================================================================

# Palm-muted rhythm: aggressive, chugging, HIGH DENSITY, VERY consistent
palm_mute_rhythm = make_rhythm_fitness({
    "density": 0.4,        # High density for chugging
    "consistency": 0.5,    # VERY repetitive patterns (metal key!)
    "rests": -0.6,         # HEAVILY penalize rests - metal is relentless
})

# Bass rhythm: lock with kick drum, no rests, consistent
bass_rhythm = make_rhythm_fitness({
    "consistency": 0.5,    # Lock with drums
    "density": 0.3,        # Steady 8th notes
    "rests": -0.7,         # NO rests for bass
})

# Lead guitar rhythm: more varied but still driving
lead_rhythm = make_rhythm_fitness({
    "groove": 0.3,
    "density": 0.3,
    "rests": -0.2,         # Some rests ok for phrasing
    "syncopation": 0.2,
})

# Double bass drum: VERY high density for blast beats
double_bass_drum_fitness = make_drum_fitness({
    "density": 0.7,        # Maximum density
    "consistency": 0.3,    # Steady pattern
})

# Metal snare: clean backbeat, sparse
snare_fitness = make_drum_fitness({
    "backbeat": 0.7,       # Classic 2 and 4
    "sparse": 0.2,         # Not too busy
    "simple": 0.1,         # Clean single hits
})

# Hi-hat: steady 8ths or 16ths, very consistent
hihat_fitness = make_drum_fitness({
    "density": 0.5,        # Steady pattern
    "consistency": 0.4,    # Very consistent
    "simple": 0.1,         # Clean hits
})

# Crash: sparse, on downbeats
crash_fitness = make_drum_fitness({
    "sparse": 0.6,         # Very sparse
    "strong_beat": 0.4,    # On downbeats
})

# Metal riff melody: ROOT FOCUSED
palm_mute_melody = make_metal_riff_fitness(root=NoteName.E, scale=E_MINOR_SCALE)

# Metal bass melody: VERY root focused
metal_bass_melody = make_metal_bass_fitness(root=NoteName.E, scale=E_MINOR_SCALE)

# Metal lead melody: more expressive
metal_lead_melody = make_metal_lead_fitness(scale=E_MINOR_SCALE)

# Power chord fitness: simple triads, strong root motion
metal_chord_fitness = make_chord_fitness({
    "triads": 0.5,         # Power chords (dyads/triads)
    "smooth": 0.3,         # Some smooth motion (4ths, 5ths)
    "functional": 0.2,     # Basic functionality
})


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 140  # Metal tempo (140 BPM as in metal_song.js)
BARS = 1
BEATS_PER_BAR = 4

# Evolution settings - more generations for better convergence
POPULATION_SIZE = 30
MUTATION_RATE = 0.2       # Lower mutation to preserve good patterns
ELITISM_COUNT = 8         # Keep more elite individuals
RHYTHM_GENERATIONS = 40   # More generations for rhythm
MELODY_GENERATIONS = 50   # More generations for melody convergence
CHORD_GENERATIONS = 30


def create_layers():
    """Create all layer configurations for metal music."""
    layers = []

    # === POWER CHORDS ===
    # Heavy power chord progression - foundation of metal
    # Uses note() notation for absolute pitches like metal_song.js:
    # note("<[e3,b3,e4] [c3,g3,c4] [d3,a3,d4] [a2,e3,a3]>").slow(2).struct("x@3 [x x]")
    layers.append(
        LayerConfig(
            name="power_chords",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,
            notes_per_chord=3,  # Power chord (root, 5th, octave)
            allowed_chord_types=["major", "minor"],
            chord_fitness_fn=metal_chord_fitness,
            strudel_scale="e:minor",
            base_octave=3,  # Power chords in octave 3
            layer_role="chords",
            context_group="",
            # Metal-style output
            use_note_notation=True,  # Use note("e3") instead of n("0")
            slow_factor=2.0,         # .slow(2) like reference
            struct_pattern="x@3 [x x]",  # Rhythm pattern from reference
            # Effects
            gain=0.15,
            lpf=2000,
            distort=2.0,
            room=0.15,
            adsr=".005:.1:.9:.1",
        )
    )

    # === PALM MUTED RHYTHM GUITAR ===
    # Aggressive chugging on low notes - THE KEY METAL ELEMENT
    # Reference uses: note("<[e2 e2 e2] [e2 g2] [e2 e2 e2] [e2 f2]>")
    # with low lpf for palm mute effect and stack for thickness
    layers.append(
        LayerConfig(
            name="palm_mute",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 subdivisions for chugging
            max_subdivision=2,                 # Allow 8th notes max
            octave_range=(2, 3),              # Low octave for heavy sound
            base_octave=2,
            scale=E_MINOR_SCALE,
            strudel_scale="e:minor",
            rhythm_fitness_fn=palm_mute_rhythm,
            melody_fitness_fn=palm_mute_melody,
            layer_role="melody",
            context_group="riff",
            # Metal-style output
            use_note_notation=True,  # Use absolute pitches
            # Effects (palm mute simulation)
            gain=0.15,
            lpf=400,            # VERY low pass for palm mute effect
            lpq=3.0,            # Resonance for punch
            distort=2.0,
            room=0.1,
            adsr=".001:.1:.8:.05",
        )
    )

    # === LEAD GUITAR ===
    # Screaming high notes, expressive
    # Reference: note("<[e5 g5 f5 e5] ~ [g5 a5 g5 f5] [e5 d5 c5 b4]>").slow(4)
    layers.append(
        LayerConfig(
            name="lead_guitar",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 subdivisions
            max_subdivision=2,
            octave_range=(4, 5),  # High octave for screaming leads
            base_octave=5,
            scale=E_MINOR_SCALE,
            strudel_scale="e:minor",
            rhythm_fitness_fn=lead_rhythm,
            melody_fitness_fn=metal_lead_melody,
            layer_role="lead",
            context_group="lead",
            # Metal-style output
            use_note_notation=True,
            slow_factor=4.0,  # .slow(4) for longer phrases
            # Effects
            gain=0.12,
            lpf=4000,
            distort=1.5,
            delay=0.3,
            delaytime=0.125,
            delayfeedback=0.4,
            room=0.3,
        )
    )

    # === METAL BASS ===
    # Heavy, distorted, follows root notes
    # Reference: note("<e1 c1 d1 a0>").slow(2).struct("x*8")
    layers.append(
        LayerConfig(
            name="metal_bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,      # 4 root notes per phrase
            max_subdivision=1,                 # Single notes only
            octave_range=(1, 2),              # Very low
            base_octave=1,
            scale=E_MINOR_SCALE,
            strudel_scale="e:minor",
            rhythm_fitness_fn=bass_rhythm,
            melody_fitness_fn=metal_bass_melody,
            layer_role="bass",
            context_group="riff",
            # Metal-style output
            use_note_notation=True,
            slow_factor=2.0,     # .slow(2) to stretch across 2 bars
            struct_pattern="x*8", # Repeat each note 8 times for driving bass
            # Effects
            gain=0.15,
            lpf=800,
            distort=1.0,
            adsr=".001:.05:.9:.05",
        )
    )

    # === DRUMS ===
    
    # Double bass drum - fast kick pattern (blast beats)
    # Reference: s("bd:4").struct("x(7,16)") - euclidean pattern
    layers.append(
        LayerConfig(
            name="double_bass",
            instrument="bd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 4,  # 16 subdivisions for blast beats
            max_subdivision=2,
            is_drum=True,
            drum_sound="bd:4",
            rhythm_fitness_fn=double_bass_drum_fitness,
            layer_role="drums",
            context_group="",
            # Use struct pattern for euclidean rhythm
            struct_pattern="x(7,16)",
            gain=0.16,
            distort=0.5,
            bank="RolandTR909",
        )
    )

    # Snare - punchy backbeat
    # Reference: s("sd:3").struct("~ x ~ x") - classic 2 and 4
    layers.append(
        LayerConfig(
            name="snare",
            instrument="sd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,  # 4 beats - clean backbeat
            max_subdivision=1,
            is_drum=True,
            drum_sound="sd:3",
            rhythm_fitness_fn=snare_fitness,
            layer_role="drums",
            context_group="",
            struct_pattern="~ x ~ x",  # Backbeat pattern
            gain=0.18,
            room=0.1,
            bank="RolandTR909",
        )
    )

    # Hi-hat - driving rhythm
    layers.append(
        LayerConfig(
            name="hihat",
            instrument="hh",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR * 2,  # 8 subdivisions
            max_subdivision=2,
            is_drum=True,
            drum_sound="hh",
            rhythm_fitness_fn=hihat_fitness,
            layer_role="drums",
            context_group="",
            gain=0.06,
            bank="RolandTR909",
        )
    )

    # Crash cymbal - sparse accents on downbeats
    # Reference: s("cr").struct("<x ~ ~ ~>/2") - one crash every 2 bars
    layers.append(
        LayerConfig(
            name="crash",
            instrument="cr",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,  # 4 subdivisions only
            max_subdivision=1,
            is_drum=True,
            drum_sound="cr",
            rhythm_fitness_fn=crash_fitness,
            layer_role="drums",
            context_group="",
            struct_pattern="<x ~ ~ ~>/2",  # Very sparse
            gain=0.12,
            room=0.3,
            bank="RolandTR909",
        )
    )

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" METAL MUSIC GENERATOR - GENETIC ALGORITHM")
    print("=" * 60)
    print(f"\nBPM: {BPM}")
    print(f"Bars: {BARS}, Beats/bar: {BEATS_PER_BAR}")
    print("\nMetal-specific optimizations:")
    print("  - Root note emphasis (E) for riffs and bass")
    print("  - Note repetition rewards (chugging patterns)")
    print("  - Low pitch bias for heaviness")
    print("  - High rhythm consistency")
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
    print("Evolving metal layers...")
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
    # SONG STRUCTURE
    # ==========================================================================
    layer_groups = {
        "drums": ["double_bass", "snare", "hihat", "crash"],
        "riff": ["palm_mute", "metal_bass", "power_chords"],
        "lead_section": ["lead_guitar", "power_chords"],
    }

    # Metal song arrangement: intro -> verse riff -> lead break -> outro
    song_arrangement = [
        (2, "stack(drums, riff)"),           # 2 bars - main riff
        (2, "stack(drums, riff)"),           # 2 bars - repeat
        (2, "stack(drums, lead_section)"),   # 2 bars - lead guitar solo
        (2, "stack(drums, riff)"),           # 2 bars - back to riff
    ]

    # Get song structure
    song = composer.get_song_structure(
        bpm=BPM,
        random_scale=False,  # We use E minor
        groups=layer_groups,
        arrangement=song_arrangement,
    )

    # Generate Strudel link
    print("\n" + "=" * 60)
    print(" STRUDEL LINK (METAL SONG)")
    print("=" * 60)
    link = song.to_strudel_link()
    print(f"\nOpen this link to hear your metal composition:")
    print(link)

    print("\n" + "=" * 60)
    print(" STRUDEL CODE")
    print("=" * 60)
    print()
    print(song.to_strudel())
    print()


if __name__ == "__main__":
    main()
