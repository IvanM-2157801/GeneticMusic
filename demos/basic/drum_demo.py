"""Demo of drum system with multiple drum layers."""
import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.drums import DRUM_FITNESS_FUNCTIONS


def main():
    print("\n" + "="*60)
    print("🥁 DRUM BEAT DEMO 🥁")
    print("="*60)
    print("\nGenerating drum beat with:")
    print("  🎵 Kick (bass drum) - bd")
    print("  🎵 Hi-hat - hh")
    print("  🎵 Snare drum - sd")
    print("  🎵 Open hi-hat - oh")
    print()

    composer = LayeredComposer(
        population_size=20,
        mutation_rate=0.25,
        elitism_count=6,
        rhythm_generations=30,
        melody_generations=0,  # Not used for drums
    )

    # 1. KICK DRUM - Strong beats, sparse, powerful
    print("Adding kick drum layer...")
    composer.add_layer(LayerConfig(
        name="kick",
        instrument="bd",  # Not used in drum mode, but kept for consistency
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
        is_drum=True,
        drum_sound="bd",
        gain=0.8,
    ))

    # 2. HI-HAT - Consistent, high density, steady
    print("Adding hi-hat layer...")
    composer.add_layer(LayerConfig(
        name="hihat",
        instrument="hh",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        is_drum=True,
        drum_sound="hh",
        gain=0.5,
    ))

    # 3. SNARE DRUM - Backbeat emphasis, sparse accents
    print("Adding snare drum layer...")
    composer.add_layer(LayerConfig(
        name="snare",
        instrument="sd",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
        is_drum=True,
        drum_sound="sd",
        gain=0.7,
    ))

    # 4. OPEN HI-HAT - Adds texture and accents
    print("Adding open hi-hat layer...")
    composer.add_layer(LayerConfig(
        name="openhat",
        instrument="oh",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["percussion"],
        is_drum=True,
        drum_sound="oh",
        gain=0.4,
    ))

    # Evolve all drum layers
    print("\n" + "="*60)
    print("Evolving drum patterns...")
    print("="*60)
    composer.evolve_all_layers(verbose=True)

    # Print summary
    composer.print_summary()

    # Generate composition (no scale needed for drums)
    composition = composer.get_composition(bpm=120, random_scale=False)

    # Create Strudel URL
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')
    url = f"https://strudel.cc/#{encoded}"

    # Output
    print("\n" + "="*60)
    print("🎵 STRUDEL OUTPUT")
    print("="*60)
    print(f"\nClick to hear your drum beat:\n{url}")

    print("\n" + "-"*60)
    print("Raw Strudel Code:")
    print("-"*60)
    print(strudel_code)

if __name__ == "__main__":
    main()
