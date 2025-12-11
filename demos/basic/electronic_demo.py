"""Electronic music demo showcasing genre-specific drums and inter-layer dependencies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_GENRE_FUNCTIONS
from fitness.melody_types import ChordFitness, StableFitness
from core.music import NoteName


def main():
    print("\n" + "=" * 60)
    print("🎧 ELECTRONIC MUSIC DEMO 🎧")
    print("=" * 60)
    print("\nGenerating electronic composition with:")
    print("  🎹 Pad - Sustained chord progression")
    print("  🎛️  Bass - Deep synth bass")
    print("  🎵 Lead - Melodic synth line")
    print("  🥁 Drums - Electronic genre-specific patterns")
    print()
    print("✨ Features:")
    print("  • Inter-layer dependencies (layers fit together)")
    print("  • Genre-specific drum fitness (electronic style)")
    print("  • Complementary rhythms and densities")
    print()

    composer = LayeredComposer(
        population_size=100,
        mutation_rate=0.25,
        elitism_count=7,
        rhythm_generations=25,
        melody_generations=30,
        use_context=True,  # Enable inter-layer dependencies!
    )

    # Use C minor for that electronic vibe
    c_minor = [
        NoteName.C,
        NoteName.D,
        NoteName.DS,  # Eb
        NoteName.F,
        NoteName.G,
        NoteName.GS,  # Ab
        NoteName.AS,  # Bb
    ]

    # === LAYER 1: DRUMS (evolve first for foundation) ===

    print("Adding electronic drums (genre-specific fitness)...")

    # Electronic kick - four-on-the-floor style
    composer.add_layer(
        LayerConfig(
            name="kick",
            instrument="bd",
            bars=1,
            beats_per_bar=8,
            max_subdivision=1,  # Keep it simple
            rhythm_fitness_fn=DRUM_GENRE_FUNCTIONS["electronic"]["kick"],
            is_drum=True,
            drum_sound="bd",
            gain=0.9,
        )
    )

    # Hi-hat - steady rhythm
    composer.add_layer(
        LayerConfig(
            name="hihat",
            instrument="hh",
            bars=1,
            beats_per_bar=4,
            max_subdivision=3,
            rhythm_fitness_fn=DRUM_GENRE_FUNCTIONS["electronic"]["hihat"],
            is_drum=True,
            drum_sound="hh",
            gain=0.5,
        )
    )

    # # Snare - backbeat
    # composer.add_layer(
    #     LayerConfig(
    #         name="snare",
    #         instrument="sd",
    #         bars=1,
    #         beats_per_bar=8,
    #         max_subdivision=1,
    #         rhythm_fitness_fn=DRUM_GENRE_FUNCTIONS["electronic"]["snare"],
    #         is_drum=True,
    #         drum_sound="sd",
    #         gain=0.7,
    #     )
    # )

    # === LAYER 2: BASS (fits with drums) ===

    print("Adding bass (will fit with drums)...")
    composer.add_layer(
        LayerConfig(
            name="bass",
            instrument="sawtooth",
            bars=1,
            beats_per_bar=16,
            max_subdivision=4,
            octave_range=(2, 3),
            scale=c_minor,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
            melody_fitness_fn=ChordFitness(),
            strudel_scale="",
            octave_shift=-7,  # Very low
            gain=0.6,
            lpf=600,  # Deep bass
            use_scale_degrees=True,
            chord_mode=True,
        )
    )

    # Evolve all layers with dependencies
    print("\n" + "=" * 60)
    print("Evolving composition with inter-layer dependencies...")
    print("=" * 60)
    print("Note: Each layer considers previously evolved layers!")
    print()

    composer.evolve_all_layers(verbose=True)

    # Print summary
    composer.print_summary()

    # Generate composition
    composition = composer.get_composition(bpm=128, random_scale=False)

    # Force C minor
    for layer in composition.layers:
        if not layer.is_drum:
            layer.scale = "c:minor"

    print(f"\n🎼 Scale: C Minor (electronic standard)")

    # Create Strudel URL
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode("utf-8")).decode("utf-8")
    url = f"https://strudel.cc/#{encoded}"

    # Output
    print("\n" + "=" * 60)
    print("🎵 STRUDEL OUTPUT")
    print("=" * 60)
    print(f"\nClick to hear your electronic track:\n{url}")

    print("\n" + "-" * 60)
    print("Raw Strudel Code:")
    print("-" * 60)
    print(strudel_code)

    print("\n" + "=" * 60)
    print("✨ COMPOSITION ANALYSIS ✨")
    print("=" * 60)
    print("\nInter-layer Dependencies:")
    print("  📊 Rhythmic Compatibility:")
    print("      - Each layer's rhythm complements previous layers")
    print("      - Avoids all layers being busy at the same time")
    print("      - Creates space and groove through density balance")
    print("  🎼 Harmonic Compatibility:")
    print("      - Melodic layers use consonant intervals")
    print("      - Bass and pad harmonize naturally")
    print("      - Lead fits within the harmonic context")
    print("  🥁 Density Balance:")
    print("      - Different layers have different densities")
    print("      - Creates dynamic range and interest")
    print("      - No frequency masking or clutter")
    print()
    print("Genre-Specific Drums:")
    print("  🎯 KICK: Four-on-the-floor pattern (electronic style)")
    print("  🎯 HI-HAT: Steady, consistent timekeeping")
    print("  🎯 SNARE: Quantized backbeat")
    print()
    print("⚡ TEMPO: 128 BPM (standard electronic/house tempo)")
    print("🎼 KEY: C Minor")
    print()


if __name__ == "__main__":
    main()
