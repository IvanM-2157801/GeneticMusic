"""Demo with melodic line (varied intervals) and stable synth (smooth intervals)."""
import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness, StableFitness
from core.music import NoteName


def main():
    print("\n" + "="*60)
    print("🎵 MELODIC + STABLE SYNTH DEMO 🎵")
    print("="*60)
    print("\nGenerating:")
    print("  🎹 Melodic Line - Varied intervals, expressive")
    print("  🎛️  Stable Synth - Smooth intervals, supportive")
    print()

    composer = LayeredComposer(
        population_size=20,
        mutation_rate=0.25,
        elitism_count=6,
        rhythm_generations=25,
        melody_generations=30,
    )

    # Use C major scale for evolution
    c_major = [
        NoteName.C, NoteName.D, NoteName.E, NoteName.F,
        NoteName.G, NoteName.A, NoteName.B
    ]

    # 1. MELODIC LINE - Varied, expressive, attention-grabbing
    print("Adding melodic line layer...")
    composer.add_layer(LayerConfig(
        name="melody",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=3,  # Up to triplets
        octave_range=(4, 6),  # Wide range for melodic expression
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=MelodicFitness(),  # Favors varied intervals
        # Strudel parameters
        strudel_scale="",  # Will be set randomly
        octave_shift=7,  # Transpose up (.sub(7) in Strudel)
        gain=0.3,
        lpf=8000,  # Higher cutoff for brightness
        use_scale_degrees=True
    ))

    # 2. STABLE SYNTH - Smooth, consistent, supportive
    print("Adding stable synth layer...")
    composer.add_layer(LayerConfig(
        name="synth",
        instrument="triangle",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,  # Simpler rhythm
        octave_range=(3, 4),  # Narrower range
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],  # Consistent rhythm
        melody_fitness_fn=StableFitness(),  # Favors smooth intervals
        # Strudel parameters
        strudel_scale="",  # Will be set randomly (same as melody)
        octave_shift=0,  # No transposition
        gain=0.2,
        lpf=2000,  # Lower cutoff for warmth
        use_scale_degrees=True
    ))

    # Evolve all layers
    print("\n" + "="*60)
    print("Evolving composition...")
    print("="*60)
    composer.evolve_all_layers(verbose=True)

    # Print summary
    composer.print_summary()

    # Generate composition with random scale
    composition = composer.get_composition(bpm=120, random_scale=True)

    # Get the random scale that was chosen
    if composition.layers:
        chosen_scale = composition.layers[0].scale
        print(f"\n🎼 Random scale chosen: {chosen_scale}")

    # Create Strudel URL
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')
    url = f"https://strudel.cc/#{encoded}"

    # Output
    print("\n" + "="*60)
    print("🎵 STRUDEL OUTPUT")
    print("="*60)
    print(f"\nClick to hear your composition:\n{url}")

    print("\n" + "-"*60)
    print("Raw Strudel Code:")
    print("-"*60)
    print(strudel_code)

    print("\n" + "="*60)
    print("✨ COMPOSITION ANALYSIS ✨")
    print("="*60)
    print("\nNotice the difference:")
    print("  - MELODY: Uses scale degrees 0-7 with .sub(7) for transposition")
    print("  - MELODY: Larger intervals, more varied (melodic)")
    print("  - SYNTH:  Smoother intervals, more stable (supportive)")
    print("  - Both use the same random scale")
    print("  - Different gain and lpf settings for distinct sounds")
    print()


if __name__ == "__main__":
    main()
