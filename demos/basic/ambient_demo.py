"""Ambient demo with sustained melodies and optional chord mode."""
import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import ChordFitness
from core.music import NoteName


def main():
    print("\n" + "=" * 60)
    print("🌌 AMBIENT COMPOSITION DEMO 🌌")
    print("=" * 60)
    print("\nGenerating ambient composition with:")
    print("  🎹 Piano - Sustained chords")
    print("  🎛️  Synth - Simple melody")
    print("  🥁 Drums - Sparse, meditative")
    print()

    composer = LayeredComposer(
        population_size=30,
        mutation_rate=0.2,
        elitism_count=8,
        rhythm_generations=30,
        melody_generations=40,
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

    # 1. PIANO - Sustained chords with comma notation
    print("Adding piano layer (chord mode)...")
    composer.add_layer(
        LayerConfig(
            name="piano",
            instrument="piano",
            bars=1,
            beats_per_bar=8,
            max_subdivision=2,  # Max 2 notes per beat for chords
            octave_range=(3, 5),
            scale=c_major,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
            melody_fitness_fn=ChordFitness(),
            strudel_scale="",  # Will be set randomly
            octave_shift=0,
            gain=0.4,
            lpf=4000,
            use_scale_degrees=True,
            chord_mode=True,  # Use comma-separated notes for chords
        )
    )

    # 2. SYNTH - Simple sustained melody
    print("Adding synth layer...")
    composer.add_layer(
        LayerConfig(
            name="synth",
            instrument="triangle",
            bars=1,
            beats_per_bar=8,
            max_subdivision=1,  # Only single notes per beat
            octave_range=(4, 6),
            scale=c_major,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
            melody_fitness_fn=ChordFitness(),
            strudel_scale="",  # Will be set randomly
            octave_shift=7,
            gain=0.3,
            lpf=6000,
            use_scale_degrees=True,
            chord_mode=False,  # Sequential notes
        )
    )

    # === DRUM LAYERS ===

    # 3. KICK - Sparse, grounding
    print("Adding kick drum layer...")
    composer.add_layer(
        LayerConfig(
            name="kick",
            instrument="bd",
            bars=1,
            beats_per_bar=8,
            max_subdivision=1,
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
            is_drum=True,
            drum_sound="bd",
            gain=0.6,
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
    composition = composer.get_composition(bpm=60, random_scale=True)

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
