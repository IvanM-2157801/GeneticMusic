"""Demo showcasing all different rhythm fitness functions in one composition."""
import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.genres import PopFitness, JazzFitness, AmbientFitness
from core.music import NoteName


def main():
    print("\n" + "="*60)
    print("MULTI-GENRE RHYTHM DEMONSTRATION")
    print("="*60)
    print("\nThis demo creates 5 layers, each with a different rhythm style:")
    print("  1. Pop rhythm - consistent, groovy")
    print("  2. Jazz rhythm - complex, syncopated")
    print("  3. Funk rhythm - maximum groove")
    print("  4. Ambient rhythm - sparse, meditative")
    print("  5. Rock rhythm - driving, dense")
    print()

    composer = LayeredComposer(
        population_size=15,
        mutation_rate=0.25,
        elitism_count=5,
        rhythm_generations=25,
        melody_generations=20,
    )

    c_major = [NoteName.C, NoteName.D, NoteName.E, NoteName.F,
               NoteName.G, NoteName.A, NoteName.B]

    # 1. Pop layer - consistent, catchy
    composer.add_layer(LayerConfig(
        name="pop_lead",
        instrument="piano",
        bars=2,
        beats_per_bar=4,
        max_subdivision=3,
        octave_range=(4, 5),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=PopFitness(),
    ))

    # 2. Jazz layer - complex, syncopated
    composer.add_layer(LayerConfig(
        name="jazz_lead",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=4,
        octave_range=(5, 6),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["jazz"],
        melody_fitness_fn=JazzFitness(),
    ))

    # 3. Funk layer - groovy, tight
    composer.add_layer(LayerConfig(
        name="funk_bass",
        instrument="square",
        bars=2,
        beats_per_bar=4,
        max_subdivision=4,
        octave_range=(2, 3),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
        melody_fitness_fn=PopFitness(),
    ))

    # 4. Ambient layer - sparse, spacious
    composer.add_layer(LayerConfig(
        name="ambient_pad",
        instrument="triangle",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(3, 4),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
    ))

    # 5. Rock layer - driving, powerful
    composer.add_layer(LayerConfig(
        name="rock_rhythm",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=3,
        octave_range=(3, 4),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["rock"],
        melody_fitness_fn=PopFitness(),
    ))

    # Evolve all layers
    print("Starting evolution...")
    composer.evolve_all_layers(verbose=False)

    # Print detailed summary
    composer.print_summary()

    # Generate Strudel URL
    composition = composer.get_composition(bpm=120)
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')

    print("\n" + "="*60)
    print("RHYTHM COMPARISON")
    print("="*60)

    for config in composer.layer_configs:
        rhythm = composer.evolved_rhythms.get(config.name, "")
        genre = config.name.split('_')[0]
        print(f"\n{genre.upper():8s} rhythm: {rhythm}")

    print("\n" + "="*60)
    print("STRUDEL OUTPUT")
    print("="*60)
    print(f"\n🎵 Strudel URL:\n{f'https://strudel.cc/#{encoded}'}")
    print("\n" + "="*60)
    print("Notice how each layer has a DIFFERENT rhythm character!")
    print("="*60)


if __name__ == "__main__":
    main()
