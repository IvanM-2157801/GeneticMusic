#!/usr/bin/env python3
"""Modern Pop demo - singable, catchy, radio-ready.

Run with: python pop_demo.py

This demo creates modern pop music suitable for vocals (Bruno Mars, Sabrina Carpenter style).
Pop characteristics:
- Moderate tempo (110 BPM)
- Clear, memorable melodies in vocal range
- I-V-vi-IV or similar progressions
- Space for vocals (not too busy)
- Piano/keys, clean bass, bright synths
- Sections: intro, verse, pre-chorus, chorus, bridge, outro
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
                fn = metric_fns[metric]
                value = fn(rhythm)
                if weight < 0:
                    score += abs(weight) * (1 - value)
                else:
                    score += weight * value
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5

    return fitness


def make_melody_fitness(weights: dict[str, float], scale=MAJOR_SCALE):
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
# POP FITNESS WEIGHTS
# =============================================================================
# Key differences for pop:
# - Major scale for upbeat feel
# - Space for vocals (more rests, less dense)
# - Very smooth melodies (singable)
# - Strong functional harmony
# - Catchy, memorable patterns

# Pop context: leave room for vocals, support but don't compete
verse_context = {
    "rhythmic": 0.4,       # Moderate rhythmic alignment
    "harmonic": 0.5,       # Strong harmonic support
    "density": 0.3,        # Don't get too busy
    "voice_leading": 0.3,  # Smooth transitions
    "call_response": 0.2,  # Some interaction
}

# Chorus context: more energy, tighter rhythmic alignment
chorus_context = {
    "rhythmic": 0.5,       # Tighter rhythmic alignment
    "harmonic": 0.4,       # Good harmonic support
    "density": 0.3,        # Can be a bit busier
    "voice_leading": 0.3,  # Smooth transitions
    "call_response": 0.2,  # Some interaction
}

# Piano/keys rhythm: steady, supportive, not too busy
keys_rhythm = make_rhythm_fitness({
    "groove": 0.3,
    "consistency": 0.5,    # Steady pattern
    "density": 0.2,        # Not too dense - leave room for vocals
    "syncopation": 0.1,    # Little syncopation
    "rests": 0.2,          # Some rests OK
})

# Bass rhythm: simple, solid foundation - must play notes!
bass_rhythm = make_rhythm_fitness({
    "groove": 0.4,
    "consistency": 0.5,    # Steady
    "density": 0.3,        # Need some notes
    "syncopation": -0.2,   # Avoid syncopation
    "rests": -0.4,         # Penalize rests - bass must be present
})

# Chorus bass rhythm: more active, driving
chorus_bass_rhythm = make_rhythm_fitness({
    "groove": 0.5,         # Good groove
    "consistency": 0.4,    # Consistent but can vary
    "density": 0.4,        # More active in chorus
    "syncopation": 0.1,    # Little bit of syncopation
    "rests": -0.5,         # No rests - drive it!
})

# Lead/topline rhythm: singable, with breathing room - NOT too syncopated
lead_rhythm = make_rhythm_fitness({
    "groove": 0.3,
    "consistency": 0.4,    # More consistent = less random
    "density": 0.4,        # Good density - needs actual notes!
    "syncopation": -0.2,   # REDUCE syncopation - was making it sound goofy
    "rests": -0.3,         # Penalize rests - lead should play notes
})

# Pad rhythm: simple but present, sustained
pad_rhythm = make_rhythm_fitness({
    "groove": 0.2,
    "consistency": 0.6,    # Very consistent
    "density": 0.2,        # Some notes
    "syncopation": -0.3,   # No syncopation
    "rests": -0.2,         # Don't want all rests
})

# Hook rhythm: catchy, memorable - needs to be a real melody!
hook_rhythm = make_rhythm_fitness({
    "groove": 0.5,         # Good groove
    "consistency": 0.3,    # Some repetition but not too much
    "density": 0.4,        # Dense - real melody needs notes!
    "syncopation": 0.2,    # Some syncopation for pop feel
    "rests": -0.3,         # Penalize rests - hook should be full
})

# Bass melody: simple, root-focused
bass_melody = make_melody_fitness({
    "variety": 0.2,        # Low variety - simple bass
    "smoothness": 0.4,     # Reasonably smooth
    "scale": 0.6,          # Stay in scale
    "rests": 0.1,          # Some rests OK
}, scale=MAJOR_SCALE)

# Lead melody: very smooth, singable, in scale - supportive not distracting
lead_melody = make_melody_fitness({
    "variety": 0.2,        # Less variety = more coherent
    "smoothness": 0.7,     # VERY smooth = natural sounding
    "scale": 0.7,          # Strongly in major scale
    "rests": 0.1,          # Some rests OK
}, scale=MAJOR_SCALE)

# Pad melody: smooth, ambient
pad_melody = make_melody_fitness({
    "variety": 0.2,
    "smoothness": 0.6,     # Very smooth
    "scale": 0.6,
    "rests": 0.2,
}, scale=MAJOR_SCALE)

# Hook melody: catchy, singable, memorable - this IS the chorus!
hook_melody = make_melody_fitness({
    "variety": 0.4,        # Good variety for interesting melody
    "smoothness": 0.7,     # VERY smooth = super singable
    "scale": 0.6,          # Stay in scale
    "rests": -0.2,         # Avoid rests - hook should sing
}, scale=MAJOR_SCALE)

# Pop chords: strong functional harmony, satisfying progressions
pop_chords = make_chord_fitness({
    "smooth": 0.4,         # Smooth voice leading
    "functional": 0.5,     # Strong functional harmony (I-V-vi-IV)
    "triads": 0.4,         # Simple triads
    "resolution": 0.3,     # Strong resolutions
    "variety": 0.2,        # Some variety
})

# Kick drum: four on the floor
kick_rhythm = make_drum_fitness({
    "strong_beat": 0.8,    # Hit beats 1 and 3
    "simple": 0.4,         # Keep it simple
    "sparse": 0.3,         # Not too busy
    "consistency": 0.4,
})

# Snare/clap: backbeat emphasis (2 and 4)
snare_rhythm = make_drum_fitness({
    "backbeat": 0.9,       # Strongly reward 2 and 4
    "simple": 0.4,
    "sparse": 0.4,         # Sparse - just the backbeat
    "strong_beat": -0.3,   # Avoid hitting 1 and 3
})

# Hihat: steady eighth notes
hihat_rhythm = make_drum_fitness({
    "consistency": 0.6,    # Very consistent
    "density": 0.5,        # Steady eighth notes
    "offbeat": 0.3,        # Some offbeat hits for groove
})


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 110  # Modern pop tempo
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
    """Create pop layers - piano, bass, pad, lead, hook, drums."""
    layers = []

    # --- PIANO/KEYS CHORDS (slow - 2 chords) ---
    # Clean, bright piano chords - slower for verse/intro/outro
    layers.append(
        LayerConfig(
            name="piano",
            instrument="piano",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=2,  # 2 chords for slower sections
            notes_per_chord=3,  # Triads
            allowed_chord_types=["major", "minor"],
            chord_fitness_fn=pop_chords,
            layer_role="chords",
            context_group="verse",  # Verse context
            gain=0.25,
            lpf=4000,
            room=0.3,
            roomsize=2.0,
            attack=0.01,
            release=0.4,
        )
    )

    # --- PIANO/KEYS CHORDS (fast - 4 chords) ---
    # More active piano for prechorus/chorus
    layers.append(
        LayerConfig(
            name="piano2",
            instrument="piano",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,  # 4 chords for chorus energy
            notes_per_chord=3,  # Triads
            allowed_chord_types=["major", "minor"],
            chord_fitness_fn=pop_chords,
            layer_role="chords",
            context_group="chorus",  # Chorus context
            gain=0.25,
            lpf=4000,
            room=0.3,
            roomsize=2.0,
            attack=0.01,
            release=0.4,
        )
    )

    # --- VERSE BASS ---
    # Simple, steady bass for verse sections
    layers.append(
        LayerConfig(
            name="verse_bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,  # Quarter notes
            octave_range=(2, 3),
            base_octave=2,
            rhythm_fitness_fn=bass_rhythm,
            melody_fitness_fn=bass_melody,
            layer_role="bass",
            context_group="verse",
            contextual_weights=verse_context,
            gain=0.3,
            lpf=800,
            room=0.1,
            roomsize=1.0,
            attack=0.01,
            release=0.2,
        )
    )

    # --- CHORUS BASS ---
    # More active, driving bass for chorus sections
    layers.append(
        LayerConfig(
            name="chorus_bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes for more movement
            octave_range=(2, 3),
            base_octave=2,
            rhythm_fitness_fn=chorus_bass_rhythm,
            melody_fitness_fn=bass_melody,
            layer_role="bass",
            context_group="chorus",
            contextual_weights=chorus_context,
            gain=0.35,  # Slightly louder in chorus
            lpf=900,    # Slightly brighter
            room=0.1,
            roomsize=1.0,
            attack=0.01,
            release=0.15,
        )
    )

    # --- PAD ---
    # Soft pad for atmosphere
    layers.append(
        LayerConfig(
            name="pad",
            instrument="triangle",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,  # Quarter notes - sustained feel
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=pad_rhythm,
            melody_fitness_fn=pad_melody,
            layer_role="melody",
            context_group="",  # Global - plays in all sections
            contextual_weights=verse_context,
            gain=0.12,
            lpf=2000,
            room=0.5,
            roomsize=4.0,
            attack=0.1,  # Slow attack for pad
            release=0.5,
        )
    )

    # --- LEAD/TOPLINE ---
    # Main melody that could be sung
    layers.append(
        LayerConfig(
            name="lead",
            instrument="sine",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes
            octave_range=(4, 5),  # Vocal range
            base_octave=4,
            rhythm_fitness_fn=lead_rhythm,
            melody_fitness_fn=lead_melody,
            layer_role="melody",
            context_group="verse",  # Used in prechorus/bridge
            contextual_weights=verse_context,
            gain=0.3,
            lpf=3500,
            room=0.35,
            roomsize=2.5,
            delay=0.15,
            delaytime=0.125,
            delayfeedback=0.2,
            attack=0.01,
            release=0.25,
        )
    )

    # --- HOOK 1 ---
    # First half of the catchy chorus melody (2 bars)
    layers.append(
        LayerConfig(
            name="hook1",
            instrument="square",
            bars=BARS,  # 2 bars
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes for real melody
            octave_range=(4, 5),  # Vocal range - singable
            base_octave=4,
            rhythm_fitness_fn=hook_rhythm,
            melody_fitness_fn=hook_melody,
            layer_role="melody",
            context_group="chorus",  # Chorus context
            contextual_weights=chorus_context,
            gain=0.25,
            lpf=3500,
            room=0.3,
            roomsize=2.0,
            delay=0.15,
            delaytime=0.125,
            delayfeedback=0.2,
            attack=0.01,
            release=0.2,
        )
    )

    # --- HOOK 2 ---
    # Second half of the catchy chorus melody (2 bars)
    # Together with hook1 forms the complete 4-bar chorus hook
    layers.append(
        LayerConfig(
            name="hook2",
            instrument="square",
            bars=BARS,  # 2 bars
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes for real melody
            octave_range=(4, 5),  # Vocal range - singable
            base_octave=4,
            rhythm_fitness_fn=hook_rhythm,
            melody_fitness_fn=hook_melody,
            layer_role="melody",
            context_group="chorus",  # Chorus context
            contextual_weights=chorus_context,
            gain=0.25,
            lpf=3500,
            room=0.3,
            roomsize=2.0,
            delay=0.15,
            delaytime=0.125,
            delayfeedback=0.2,
            attack=0.01,
            release=0.2,
        )
    )

    # --- KICK ---
    layers.append(
        LayerConfig(
            name="kick",
            instrument="bd",
            drum_sound="bd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,  # Quarter notes
            is_drum=True,
            rhythm_fitness_fn=kick_rhythm,
            layer_role="drums",
            context_group="drums",
            gain=0.25,
        )
    )

    # --- SNARE ---
    layers.append(
        LayerConfig(
            name="snare",
            instrument="sd",
            drum_sound="sd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,  # Quarter notes - backbeat
            is_drum=True,
            rhythm_fitness_fn=snare_rhythm,
            layer_role="drums",
            context_group="drums",
            gain=0.35,
        )
    )

    # --- HIHAT ---
    layers.append(
        LayerConfig(
            name="hihat",
            instrument="hh",
            drum_sound="hh",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,  # Eighth notes
            is_drum=True,
            rhythm_fitness_fn=hihat_rhythm,
            layer_role="drums",
            context_group="drums",
            gain=0.2,
        )
    )

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print(" MODERN POP DEMO - SINGABLE & CATCHY")
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
    print("Evolving pop patterns...")
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

    # Pop song structure - matching user's custom arrangement
    # piano = 2 chords (slow), piano2 = 4 chords (fast)
    layer_groups = {
        # Intro - two parts for build (verse bass for intro)
        "intro1": ["piano"],  # Just slow piano
        "intro2": ["piano", "verse_bass"],
        
        # Verse - verse bass, pad and drums (leave room for vocals)
        "verse": ["piano", "verse_bass", "pad", "kick", "snare", "hihat"],
        
        # Pre-chorus - 4 chords piano2, add lead melody, still verse bass
        "prechorus": ["piano2", "verse_bass", "pad", "lead", "kick", "snare", "hihat"],
        
        # Chorus part 1 - piano2 + chorus_bass + hook1!
        "chorus1": ["piano2", "chorus_bass", "pad", "hook1", "kick", "snare", "hihat"],
        
        # Chorus part 2 - piano2 + chorus_bass + hook2!
        "chorus2": ["piano2", "chorus_bass", "pad", "hook2", "kick", "snare", "hihat"],
        
        # Bridge - stripped back, emotional (slow piano)
        "bridge": ["piano", "pad", "lead"],
        
        # Outro - wind down (slow piano + verse bass)
        "outro": ["piano", "verse_bass", "pad"],
    }

    # User's custom arrangement with repeating hook sections
    arrangement = [
        (2, "stack(intro1)"),      # 2 bars - bass only
        (2, "stack(intro2)"),      # 2 bars - piano joins
        (8, "stack(verse)"),       # 8 bars verse 1
        (4, "stack(prechorus)"),   # 4 bars pre-chorus
        (2, "stack(chorus1)"),     # hook1
        (2, "stack(chorus2)"),     # hook2
        (2, "stack(chorus1)"),     # hook1 again
        (2, "stack(chorus2)"),     # hook2 again
        (8, "stack(verse)"),       # 8 bars verse 2
        (4, "stack(prechorus)"),   # 4 bars pre-chorus
        (2, "stack(chorus1)"),     # hook1
        (2, "stack(chorus2)"),     # hook2
        (2, "stack(chorus1)"),     # hook1 again
        (2, "stack(chorus2)"),     # hook2 again
        (4, "stack(bridge)"),      # 4 bars bridge
        (2, "stack(chorus1)"),     # final chorus - hook1
        (2, "stack(chorus2)"),     # hook2
        (2, "stack(chorus1)"),     # hook1 again
        (2, "stack(chorus2)"),     # hook2 again
        (4, "stack(outro)"),       # 4 bars outro
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
    print(" STRUDEL LINK (POP TRACK)")
    print("=" * 60)
    link = song.to_strudel_link()
    print(f"\nOpen this link to hear your pop track:\n{link}")

    print("\n" + "=" * 60)
    print(" STRUDEL CODE")
    print("=" * 60)
    print(song.to_strudel())


if __name__ == "__main__":
    main()
