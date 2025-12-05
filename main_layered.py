"""Main script for multi-layer genetic music composition."""
import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.genres import PopFitness, JazzFitness, AmbientFitness
from core.music import NoteName


def create_strudel_url(composition, total_cycles: int = 2) -> str:
    """Create a Strudel URL from a composition."""
    # Generate Strudel code
    strudel_code = composition.to_strudel()

    # Encode to base64
    encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')
    url = f"https://strudel.cc/#{encoded}"

    return url


def main():
    print("\n" + "="*60)
    print("GENETIC MUSIC COMPOSER")
    print("="*60)

    # Create composer
    composer = LayeredComposer(
        population_size=15,
        mutation_rate=0.25,
        elitism_count=5,
        rhythm_generations=20,
        melody_generations=30,
    )

    # Define scales
    c_major = [NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B]
    c_minor = [NoteName.C, NoteName.D, NoteName.DS, NoteName.F, NoteName.G, NoteName.GS, NoteName.AS]

    # Add melody layer (pop style)
    composer.add_layer(LayerConfig(
        name="melody",
        instrument="piano",
        bars=2,
        beats_per_bar=4,
        max_subdivision=4,
        octave_range=(4, 5),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=PopFitness(),
    ))

    # Add bass layer (simpler rhythm, lower octave)
    composer.add_layer(LayerConfig(
        name="bass",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,  # Simpler subdivisions for bass
        octave_range=(2, 3),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=PopFitness(),
    ))

    # Add ambient pad layer
    composer.add_layer(LayerConfig(
        name="pad",
        instrument="triangle",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(3, 4),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
    ))

    # Evolve all layers
    print("\nStarting evolution process...")
    composer.evolve_all_layers(verbose=True)

    # Print summary
    composer.print_summary()

    # Get final composition
    composition = composer.get_composition(bpm=120)

    # Generate Strudel URL
    print("\n" + "="*60)
    print("STRUDEL OUTPUT")
    print("="*60)
    url = create_strudel_url(composition)
    print(f"\nStrudel URL:\n{url}")

    # Also print the raw Strudel code
    print("\n" + "-"*60)
    print("Raw Strudel Code:")
    print("-"*60)
    print(composition.to_strudel())
    print()

    return composition


if __name__ == "__main__":
    main()
