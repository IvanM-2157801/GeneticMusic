"""Complete band demo with drums and melodic instruments."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness, StableFitness
from fitness.genres import PopFitness
from core.music import NoteName


def main():
    print("\n" + "=" * 60)
    print("🎸 FULL BAND DEMO 🎸")
    print("=" * 60)
    print("\nGenerating complete band with:")
    print("  🎹 Melody - Lead synth")
    print("  🎛️  Synth pad - Stable background")
    print("  🎸 Bass - Groovy foundation")
    print("  🥁 Drums - Kick, hi-hat, snare")
    print()

    composer = LayeredComposer(
        population_size=100,
        mutation_rate=0.25,
        elitism_count=6,
        rhythm_generations=25,
        melody_generations=30,
    )

    # Use C major scale for evolution
    c_major = [
        NoteName.C,
        NoteName.D,
        NoteName.E,
        NoteName.F,
        NoteName.G,
        NoteName.A,
        NoteName.B,
    ]

    # === MELODIC LAYERS ===

    # 1. MELODY - Varied, expressive lead
    print("Adding melody layer...")
    composer.add_layer(
        LayerConfig(
            name="melody",
            instrument="piano",
            bars=1,
            beats_per_bar=4,
            max_subdivision=3,
            octave_range=(4, 6),
            scale=c_major,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
            melody_fitness_fn=MelodicFitness(),
            strudel_scale="",  # Will be set randomly
            octave_shift=7,
            gain=0.3,
            lpf=8000,
            use_scale_degrees=True,
            chord_mode=True,
        )
    )

    # 2. SYNTH PAD - Smooth, supportive background
    print("Adding synth pad layer...")
    composer.add_layer(
        LayerConfig(
            name="piano",
            instrument="piano",
            bars=1,
            beats_per_bar=8,
            max_subdivision=2,
            octave_range=(4, 6),
            scale=c_major,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
            melody_fitness_fn=MelodicFitness(),
            strudel_scale="",  # Will be set randomly
            octave_shift=3,
            gain=0.3,
            lpf=8000,
            use_scale_degrees=True,
        )
    )

    # === DRUM LAYERS ===

    # 4. KICK DRUM
    print("Adding kick drum layer...")
    composer.add_layer(
        LayerConfig(
            name="kick",
            instrument="bd",
            bars=2,
            beats_per_bar=4,
            max_subdivision=2,
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
            is_drum=True,
            drum_sound="bd",
            gain=0.8,
        )
    )

    # 5. HI-HAT
    print("Adding hi-hat layer...")
    composer.add_layer(
        LayerConfig(
            name="hihat",
            instrument="hh",
            bars=2,
            beats_per_bar=4,
            max_subdivision=2,
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
            is_drum=True,
            drum_sound="hh",
            gain=0.5,
        )
    )

    # 6. SNARE DRUM
    print("Adding snare drum layer...")
    composer.add_layer(
        LayerConfig(
            name="snare",
            instrument="sd",
            bars=2,
            beats_per_bar=4,
            max_subdivision=2,
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
            is_drum=True,
            drum_sound="sd",
            gain=0.7,
        )
    )

    # Evolve all layers
    print("\n" + "=" * 60)
    print("Evolving composition...")
    print("=" * 60)
    composer.evolve_all_layers(verbose=True)

    # Print summary
    composer.print_summary()

    # Generate composition with random scale
    composition = composer.get_composition(bpm=120, random_scale=True)

    # Get the random scale that was chosen
    if composition.layers:
        # Find first non-drum layer to get the scale
        for layer in composition.layers:
            if not layer.is_drum:
                chosen_scale = layer.scale
                print(f"\n🎼 Random scale chosen: {chosen_scale}")
                break

    # Create Strudel URL
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode("utf-8")).decode("utf-8")
    url = f"https://strudel.cc/#{encoded}"

    # Output
    print("\n" + "=" * 60)
    print("🎵 STRUDEL OUTPUT")
    print("=" * 60)
    print(f"\nClick to hear your composition:\n{url}")

    print("\n" + "-" * 60)
    print("Raw Strudel Code:")
    print("-" * 60)
    print(strudel_code)


if __name__ == "__main__":
    main()
