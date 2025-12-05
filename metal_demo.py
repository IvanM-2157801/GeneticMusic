"""Heavy metal demo with distorted guitars, power chords, and aggressive drums."""

import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS

# NEW: Importing the improved fitness classes
from fitness.melody_types import (
    MelodicFitness,
    ChordFitness,
    LeadArcFitness,  # For the guitar solo
    RhythmicMotifFitness,  # For the driving bassline
)
from core.music import NoteName


def main():
    print("\n" + "=" * 60)
    print("🤘 HEAVY METAL DEMO 🤘")
    print("=" * 60)
    print("\nGenerating metal composition with:")
    print("  🎸 Rhythm Guitar - Heavy power chords")
    print("  🎸 Lead Guitar - Shredding solo with 'Arc' structure")
    print("  🎸 Bass - Rhythmic motif locking with drums")
    print("  🥁 Drums - Double bass, aggressive snare")
    print()

    composer = LayeredComposer(
        population_size=40,  # Increased for better convergence on complex functions
        mutation_rate=0.3,
        elitism_count=8,
        rhythm_generations=30,
        melody_generations=40,
    )

    # Use minor scale for that dark metal sound
    # E minor pentatonic (common in metal)
    e_minor = [
        NoteName.E,
        NoteName.G,
        NoteName.A,
        NoteName.B,
        NoteName.D,
    ]

    # === GUITAR LAYERS ===

    # 1. RHYTHM GUITAR - Palm-muted power chords
    print("Adding rhythm guitar (power chords)...")
    composer.add_layer(
        LayerConfig(
            name="rhythm_guitar",
            instrument="sawtooth",  # Aggressive, distorted sound
            bars=1,
            beats_per_bar=8,
            max_subdivision=4,  # Allow fast palm-muted patterns
            octave_range=(2, 3),  # Low tuning
            scale=e_minor,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],  # Syncopated, groovy
            melody_fitness_fn=ChordFitness(),  # Power chord intervals (5ths)
            strudel_scale="",
            octave_shift=-12,  # Very low, heavy
            gain=0.6,
            lpf=800,  # Dark, chunky tone
            use_scale_degrees=True,
            chord_mode=True,  # Power chords (root + fifth)
        )
    )

    # 2. LEAD GUITAR - Fast, melodic riffs
    # CHANGED: Using LeadArcFitness to create a "Story" solo
    print("Adding lead guitar (Solo Arc)...")
    composer.add_layer(
        LayerConfig(
            name="lead_guitar",
            instrument="square",  # Sharp, cutting tone
            bars=1,
            beats_per_bar=8,
            max_subdivision=4,  # Fast runs
            octave_range=(4, 6),  # Higher register
            scale=e_minor,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
            # NEW: LeadArcFitness ensures the solo rises and resolves home to E
            melody_fitness_fn=LeadArcFitness(),
            strudel_scale="",
            octave_shift=0,
            gain=0.45,
            lpf=3500,  # Brighter, cutting through
            use_scale_degrees=True,
            chord_mode=False,
        )
    )

    # 3. BASS - Deep, following rhythm
    # CHANGED: Using RhythmicMotifFitness to lock in the groove
    print("Adding bass (Rhythmic Motif)...")
    composer.add_layer(
        LayerConfig(
            name="bass",
            instrument="sawtooth",
            bars=1,
            beats_per_bar=8,
            max_subdivision=4,  # Tight, rhythmic
            octave_range=(1, 2),  # Very low
            scale=e_minor,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
            # NEW: RhythmicMotifFitness prioritizes repetitive, syncopated hooks
            melody_fitness_fn=RhythmicMotifFitness(),
            strudel_scale="",
            octave_shift=-24,  # Extremely low
            gain=0.7,
            lpf=500,  # Deep, rumbling
            use_scale_degrees=True,
            chord_mode=False,
        )
    )

    # === DRUM LAYERS ===

    # 4. KICK - Fast double bass patterns
    print("Adding kick drum (double bass)...")
    composer.add_layer(
        LayerConfig(
            name="kick",
            instrument="bd",
            bars=1,
            beats_per_bar=8,
            max_subdivision=4,  # Allow fast double bass (16th notes)
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS[
                "hihat"
            ],  # Use hihat fitness for high density
            is_drum=True,
            drum_sound="bd",
            gain=0.9,  # Loud and powerful
        )
    )

    # 5. SNARE - Aggressive backbeat
    print("Adding snare drum...")
    composer.add_layer(
        LayerConfig(
            name="snare",
            instrument="sd",
            bars=1,
            beats_per_bar=8,
            max_subdivision=2,
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
            is_drum=True,
            drum_sound="sd",
            gain=0.8,
        )
    )

    # 6. HI-HAT - Fast, steady
    print("Adding hi-hat...")
    composer.add_layer(
        LayerConfig(
            name="hihat",
            instrument="hh",
            bars=1,
            beats_per_bar=8,
            max_subdivision=2,
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
            is_drum=True,
            drum_sound="hh",
            gain=0.5,
        )
    )

    # 7. CRASH CYMBAL - Accents
    print("Adding crash cymbal...")
    composer.add_layer(
        LayerConfig(
            name="crash",
            instrument="cp",
            bars=1,
            beats_per_bar=8,
            max_subdivision=1,  # Sparse accents
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["percussion"],
            is_drum=True,
            drum_sound="cp",
            gain=0.6,
        )
    )

    # Evolve all layers
    print("\n" + "=" * 60)
    print("Evolving metal composition...")
    print("=" * 60)
    composer.evolve_all_layers(verbose=True)

    # Print summary
    composer.print_summary()

    # Generate composition - Force E minor scale
    composition = composer.get_composition(bpm=160, random_scale=False)

    # Override to use E minor for all melodic layers
    for layer in composition.layers:
        if not layer.is_drum:
            layer.scale = "e:minor"

    print(f"\n🎼 Scale: E Minor (metal standard)")

    # Create Strudel URL
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode("utf-8")).decode("utf-8")
    url = f"https://strudel.cc/#{encoded}"

    # Output
    print("\n" + "=" * 60)
    print("🎵 STRUDEL OUTPUT")
    print("=" * 60)
    print(f"\nClick to hear your metal track:\n{url}")

    print("\n" + "-" * 60)
    print("Raw Strudel Code:")
    print("-" * 60)
    print(strudel_code)

    print("\n" + "=" * 60)
    print("✨ METAL COMPOSITION ANALYSIS ✨")
    print("=" * 60)
    print("\nMetal characteristics:")
    print("  🎸 RHYTHM GUITAR:")
    print("      - Power chords with chord_mode (root + fifth)")
    print("      - lpf(800) for chunky, palm-muted tone")
    print("  🎸 LEAD GUITAR:")
    print("      - USES 'LeadArcFitness': Rewards smooth contours and tonic resolution")
    print("      - Attempts to tell a melodic story rather than random shredding")
    print("  🎸 BASS:")
    print("      - USES 'RhythmicMotifFitness': Rewards repetition and syncopation")
    print("      - Locks into a groove pattern")
    print("  🥁 DRUMS:")
    print("      - KICK: High density for double bass patterns")
    print("      - SNARE: Strong backbeat emphasis")
    print("  ⚡ TEMPO: 160 BPM (thrash/speed metal range)")
    print("  🎼 KEY: E Minor (classic metal tonality)")
    print()
    print("🤘 \\m/ METAL! \\m/ 🤘")
    print()


if __name__ == "__main__":
    main()
