"""Example: Generate a jazz composition with melody, bass, and chords."""
from music_ga import Composer, LayerConfig, FITNESS_FUNCTIONS


def main():
    composer = Composer(
        population_size=100,
        mutation_rate=0.15,
        crossover_rate=0.7,
        elitism=3,
    )
    
    # Add layers with different fitness functions and instruments
    composer.add_layer(LayerConfig(
        name="melody",
        instrument="piano",
        phrase_count=4,
        phrase_length=8,
        octave_range=(4, 6),
        fitness_fn=FITNESS_FUNCTIONS["jazz"](),
    ))
    
    composer.add_layer(LayerConfig(
        name="bass",
        instrument="bass",
        phrase_count=4,
        phrase_length=4,
        octave_range=(2, 3),
        fitness_fn=FITNESS_FUNCTIONS["jazz"](),
    ))
    
    composer.add_layer(LayerConfig(
        name="pad",
        instrument="pad",
        phrase_count=4,
        phrase_length=4,
        octave_range=(3, 4),
        fitness_fn=FITNESS_FUNCTIONS["ambient"](),  # Ambient pads
    ))
    
    # Evolve
    print("Evolving composition...")
    history = composer.evolve(generations=50)
    
    # Get best composition
    composition = composer.get_best_composition(bpm=100)
    
    # Export to Strudel
    strudel_code = composition.to_strudel()
    print("\n=== Strudel Output ===")
    print(strudel_code)
    
    # Save to file
    with open("output.strudel", "w") as f:
        f.write(strudel_code)
    print("\nSaved to output.strudel")


if __name__ == "__main__":
    main()
