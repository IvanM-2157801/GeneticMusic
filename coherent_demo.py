#!/usr/bin/env python3
"""Enhanced demo showcasing inter-layer coherence through contextual fitness.

Run with: python coherent_demo.py

This demo demonstrates how layers consider each other during evolution to create
a more coherent musical composition. Key features:

1. **Chord-Melody Coherence**: Melodies are evolved to fit the chord progression
   - Chord tones on strong beats
   - Scale tones on weak beats
   - Voice leading considerations

2. **Bass-Melody Support**: Bass is evolved to harmonically support the melody
   - Bass plays roots/fifths when melody has thirds/sevenths
   - Complementary rhythm patterns

3. **Rhythm Complementarity**: All layers consider each other's rhythms
   - Balanced density (not all busy at once)
   - Moderate overlap (good groove, not clashing)
   - Call-and-response patterns

4. **Voice Leading Between Parts**: Melodic layers avoid parallel fifths/octaves
   - Contrary motion rewarded
   - Voice crossing penalized

The contextual fitness system wraps each layer's intrinsic fitness and adds
inter-layer compatibility scoring. Layers in the same context_group are evaluated
against each other during evolution.
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
)
from fitness.contextual import get_context_groups
from core.genome_ops import ChordProgression
from layered_composer import LayeredComposer, LayerConfig


# =============================================================================
# FITNESS HELPER BUILDERS
# =============================================================================


def make_rhythm_fitness(weights: dict[str, float]):
    """Create a rhythm fitness function from weights."""
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
    """Create a melody fitness function from weights."""

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
    """Create a chord fitness function from weights."""

    class CustomChordFitness(ChordFitnessFunction):
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

    return CustomChordFitness()


def make_drum_fitness(weights: dict[str, float]):
    """Create a drum rhythm fitness function from weights."""
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
# COHERENCE-FOCUSED CONTEXTUAL WEIGHTS
# =============================================================================
# These weights define how each layer considers other layers during evolution.
# Higher weights = more emphasis on that inter-layer relationship.

# Melody contextual weights: strong emphasis on harmonic fit with chords
# and voice leading with other melodic parts
melody_context = {
    "rhythmic": 0.2,       # Some rhythm complementarity
    "density": 0.15,       # Some density contrast
    "harmonic": 0.35,      # STRONG: fit with chords and other melodies
    "voice_leading": 0.2,  # Contrary motion, avoid parallels
    "call_response": 0.1,  # Light call-response patterns
}

# Bass contextual weights: support the melody harmonically
bass_context = {
    "rhythmic": 0.3,       # Lock with drums and provide groove
    "density": 0.15,       # Contrast with busy melody
    "harmonic": 0.35,      # STRONG: support melody with good bass notes
    "voice_leading": 0.15, # Contrary motion with melody
    "call_response": 0.05, # Light alternation
}

# Pad contextual weights: fill space, don't clash
pad_context = {
    "rhythmic": 0.15,      # Light rhythm consideration
    "density": 0.3,        # STRONG: contrast with melody/bass
    "harmonic": 0.35,      # STRONG: consonant with everything
    "voice_leading": 0.15, # Avoid parallels
    "call_response": 0.05, # Very light alternation
}


# =============================================================================
# INTRINSIC FITNESS FUNCTIONS
# =============================================================================
# These define what makes a layer good on its own (before context is considered)

# Chord progression: functional harmony with smooth voice leading
chords_fitness = make_chord_fitness({
    "functional": 0.4,     # Use I, IV, V, vi etc.
    "resolution": 0.25,    # V-I resolutions
    "smooth": 0.25,        # Smooth root movement
    "triads": 0.1,         # Simple triads
})

# Melody: varied, smooth, in scale
melody_rhythm = make_rhythm_fitness({
    "groove": 0.3,
    "density": 0.3,
    "syncopation": 0.1,
    "rests": -0.3,         # Penalize too many rests
})

melody_fitness = make_melody_fitness({
    "variety": 0.3,
    "smoothness": 0.4,
    "scale": 0.5,
    "rests": -0.2,
}, scale=MINOR_SCALE)

# Bass: simple, root-focused, supportive
bass_rhythm = make_rhythm_fitness({
    "groove": 0.5,
    "consistency": 0.3,
    "rests": -0.4,         # Bass needs to play!
})

bass_fitness = make_melody_fitness({
    "variety": 0.2,        # Less variety (more repetitive)
    "smoothness": 0.3,
    "scale": 0.6,
    "rests": -0.1,
}, scale=MINOR_SCALE)

# Pad: sustained, smooth, ambient
pad_rhythm = make_rhythm_fitness({
    "consistency": 0.5,
    "density": 0.2,
    "rests": -0.3,
})

pad_fitness = make_melody_fitness({
    "variety": 0.2,
    "smoothness": 0.6,     # Very smooth for pad
    "scale": 0.5,
    "rests": 0.1,          # Some rests OK for pads
}, scale=MINOR_SCALE)

# Drums
kick_fitness = make_drum_fitness({
    "strong_beat": 0.5,
    "sparse": 0.3,
    "simple": 0.2,
})

snare_fitness = make_drum_fitness({
    "backbeat": 0.6,
    "sparse": 0.3,
    "simple": 0.1,
})

hihat_fitness = make_drum_fitness({
    "density": 0.3,
    "consistency": 0.4,
    "offbeat": 0.3,
})


# =============================================================================
# EVOLUTION PARAMETERS
# =============================================================================

BPM = 85
BARS = 2
BEATS_PER_BAR = 4

POPULATION_SIZE = 30     # Larger population for better exploration
MUTATION_RATE = 0.15
ELITISM_COUNT = 6
RHYTHM_GENERATIONS = 30
MELODY_GENERATIONS = 40  # More generations for melody coherence
CHORD_GENERATIONS = 30


# =============================================================================
# LAYER CONFIGURATION
# =============================================================================


def create_layers():
    """Create all layer configurations with coherence settings."""
    layers = []

    # --- CHORDS ---
    # Chords evolve first and establish harmonic context for all other layers
    layers.append(
        LayerConfig(
            name="chords",
            instrument="piano",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            is_chord_layer=True,
            num_chords=4,
            notes_per_chord=3,
            allowed_chord_types=["major", "minor"],
            chord_fitness_fn=chords_fitness,
            layer_role="chords",
            context_group="",  # Global - provides harmonic context to all
            gain=0.3,
            lpf=3000,
            room=0.4,
            roomsize=2.0,
            attack=0.02,
            release=0.5,
        )
    )

    # --- KICK ---
    # Kick establishes rhythmic foundation
    layers.append(
        LayerConfig(
            name="kick",
            instrument="bd",
            drum_sound="bd",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,
            is_drum=True,
            rhythm_fitness_fn=kick_fitness,
            layer_role="drums",
            context_group="drums",
            gain=0.4,
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
            max_subdivision=1,
            is_drum=True,
            rhythm_fitness_fn=snare_fitness,
            layer_role="drums",
            context_group="drums",
            gain=0.35,
        )
    )

    # --- HI-HAT ---
    layers.append(
        LayerConfig(
            name="hihat",
            instrument="hh",
            drum_sound="hh",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,
            is_drum=True,
            rhythm_fitness_fn=hihat_fitness,
            layer_role="drums",
            context_group="drums",
            gain=0.2,
        )
    )

    # --- BASS ---
    # Bass evolves after drums, considers kick rhythm and supports melody
    # harmonically. Uses bass_context to weigh harmonic support heavily.
    layers.append(
        LayerConfig(
            name="bass",
            instrument="sawtooth",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,
            octave_range=(2, 3),
            base_octave=2,
            rhythm_fitness_fn=bass_rhythm,
            melody_fitness_fn=bass_fitness,
            layer_role="bass",
            context_group="melodic",        # In melodic group
            contextual_weights=bass_context, # Heavy harmonic support
            use_harmonic_context=True,       # Consider chord progression
            harmony_weight=0.35,             # How much to weigh chord fit
            genre="electronic",
            gain=0.35,
            lpf=800,
            room=0.2,
            roomsize=1.0,
            attack=0.01,
            release=0.2,
        )
    )

    # --- PAD ---
    # Pad fills harmonic space, considers bass and melody to not clash
    layers.append(
        LayerConfig(
            name="pad",
            instrument="triangle",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=1,
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=pad_rhythm,
            melody_fitness_fn=pad_fitness,
            layer_role="melody",
            context_group="melodic",
            contextual_weights=pad_context,
            use_harmonic_context=True,
            harmony_weight=0.4,
            genre="ambient",
            gain=0.15,
            lpf=2000,
            room=0.6,
            roomsize=4.0,
            attack=0.1,
            release=0.5,
        )
    )

    # --- LEAD MELODY ---
    # Lead melody is the main melodic focus. Evolves last with full context
    # of all other layers. Strong harmonic and voice leading considerations.
    layers.append(
        LayerConfig(
            name="melody",
            instrument="sine",
            bars=BARS,
            beats_per_bar=BEATS_PER_BAR,
            max_subdivision=2,
            octave_range=(4, 5),
            base_octave=4,
            rhythm_fitness_fn=melody_rhythm,
            melody_fitness_fn=melody_fitness,
            layer_role="melody",
            context_group="melodic",          # In melodic group
            contextual_weights=melody_context, # Strong harmonic/voice leading
            use_harmonic_context=True,         # Consider chord progression
            harmony_weight=0.4,                # Strong chord awareness
            genre="pop",                       # Strict chord-melody rules
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

    return layers


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 70)
    print(" COHERENT COMPOSITION DEMO - Inter-Layer Awareness")
    print("=" * 70)
    print()
    print("This demo shows how layers consider each other during evolution:")
    print("  • Melodies fit the chord progression (chord tones on strong beats)")
    print("  • Bass harmonically supports the melody (roots/fifths vs thirds)")
    print("  • Rhythms complement each other (balanced density, good overlap)")
    print("  • Voice leading avoids parallel fifths/octaves")
    print()
    print(f"BPM: {BPM}")
    print(f"Bars: {BARS}, Beats/bar: {BEATS_PER_BAR}")
    print()

    layers = create_layers()

    print("Layer configuration:")
    print("-" * 70)
    print(f"{'Name':<12} {'Role':<8} {'Context Group':<12} {'Harmonic Ctx':<12} {'Context Weights'}")
    print("-" * 70)
    for layer in layers:
        harmonic = "Yes" if layer.use_harmonic_context else "No"
        weights = ""
        if layer.contextual_weights:
            top_weights = sorted(
                layer.contextual_weights.items(),
                key=lambda x: x[1],
                reverse=True
            )[:2]
            weights = ", ".join(f"{k}={v:.1f}" for k, v in top_weights)
        print(f"{layer.name:<12} {layer.layer_role:<8} {layer.context_group or '(global)':<12} {harmonic:<12} {weights}")
    print()

    # Create composer with context enabled
    composer = LayeredComposer(
        population_size=POPULATION_SIZE,
        mutation_rate=MUTATION_RATE,
        elitism_count=ELITISM_COUNT,
        rhythm_generations=RHYTHM_GENERATIONS,
        melody_generations=MELODY_GENERATIONS,
        chord_generations=CHORD_GENERATIONS,
        use_context=True,              # Enable inter-layer fitness!
        use_harmonic_context=True,     # Enable chord-aware melodies!
    )

    # Add all layers
    for layer_config in layers:
        composer.add_layer(layer_config)

    # Evolve with full coherence
    print("Evolving with inter-layer coherence...\n")
    composer.evolve_all_layers(verbose=True)

    # Print context groups
    print("\n" + "=" * 70)
    print(" CONTEXT GROUPS (layers that consider each other)")
    print("=" * 70)
    context_groups = get_context_groups(composer.evolved_layers)
    for group, members in sorted(context_groups.items()):
        group_name = group if group else "(global - shared with all)"
        print(f"\n{group_name}:")
        for name in members:
            layer, rhythm = composer.evolved_layers[name]
            print(f"  - {name} ({layer.layer_role}): rhythm={rhythm}")

    # Print summary
    composer.print_summary()

    # Song structure
    layer_groups = {
        "full": ["chords", "bass", "pad", "melody", "kick", "snare", "hihat"],
        "intro": ["chords", "pad"],
        "verse": ["chords", "bass", "pad", "kick", "hihat"],
        "chorus": ["chords", "bass", "pad", "melody", "kick", "snare", "hihat"],
        "bridge": ["chords", "pad", "melody"],
        "outro": ["chords", "pad", "bass"],
    }

    arrangement = [
        (4, "stack(intro)"),
        (8, "stack(verse)"),
        (8, "stack(chorus)"),
        (8, "stack(verse)"),
        (8, "stack(chorus)"),
        (4, "stack(bridge)"),
        (8, "stack(chorus)"),
        (4, "stack(outro)"),
    ]

    song = composer.get_song_structure(
        bpm=BPM,
        random_scale=False,
        groups=layer_groups,
        arrangement=arrangement,
    )

    print("\n" + "=" * 70)
    print(" STRUDEL LINK")
    print("=" * 70)
    link = song.to_strudel_link()
    print(f"\nOpen this link to hear your coherent composition:\n{link}")

    print("\n" + "=" * 70)
    print(" STRUDEL CODE")
    print("=" * 70)
    print(song.to_strudel())

    print("\n" + "=" * 70)
    print(" HOW COHERENCE WAS ACHIEVED")
    print("=" * 70)
    print("""
1. CHORD-MELODY COHERENCE (use_harmonic_context=True):
   - Melodies are scored against the chord progression
   - Chord tones (root, 3rd, 5th) score highest on strong beats
   - Scale tones are acceptable, chromatic notes penalized
   - The 'genre' parameter controls strictness (pop=strict, jazz=loose)

2. INTER-LAYER RHYTHM (contextual_weights with 'rhythmic'):
   - Layers in the same context_group consider each other's rhythms
   - Moderate overlap (30-70%) scores highest for good groove
   - Too much overlap = clashing; too little = disconnected

3. DENSITY BALANCE (contextual_weights with 'density'):
   - Layers are rewarded for different busy-ness levels
   - Creates dynamic range: some layers busy, others sparse

4. HARMONIC COMPATIBILITY (contextual_weights with 'harmonic'):
   - Non-drum layers check interval consonance with each other
   - Thirds, sixths, fifths = good; seconds, tritones = penalized
   - Bass-melody pairs get special scoring for harmonic support

5. VOICE LEADING (contextual_weights with 'voice_leading'):
   - Contrary motion between melodic parts is rewarded
   - Parallel fifths and octaves are penalized
   - Voice crossing is discouraged

6. EVOLUTION ORDER MATTERS:
   - Chords evolve first → establish harmonic foundation
   - Drums evolve next → establish rhythmic foundation
   - Bass evolves with chord/drum context
   - Melody evolves last with full awareness of all layers
""")


if __name__ == "__main__":
    main()
