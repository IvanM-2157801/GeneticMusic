"""Example: Jazz composition with syncopated rhythms."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.genres import JazzFitness
from core.music import NoteName


def main():
    print("\n🎷 JAZZ COMPOSITION GENERATOR 🎷\n")

    composer = LayeredComposer(
        population_size=15,
        mutation_rate=0.25,
        elitism_count=5,
        rhythm_generations=25,
        melody_generations=35,
    )

    # Jazz uses more chromatic scales
    chromatic = [NoteName.C, NoteName.CS, NoteName.D, NoteName.DS, NoteName.E,
                 NoteName.F, NoteName.FS, NoteName.G, NoteName.GS,
                 NoteName.A, NoteName.AS, NoteName.B]

    # Melody - high complexity, syncopated
    composer.add_layer(LayerConfig(
        name="lead",
        instrument="piano",
        bars=2,
        beats_per_bar=4,
        max_subdivision=4,
        octave_range=(4, 6),
        scale=chromatic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["jazz"],
        melody_fitness_fn=JazzFitness(),
    ))

    # Bass - walking bass pattern
    composer.add_layer(LayerConfig(
        name="bass",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(2, 3),
        scale=chromatic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["jazz"],
        melody_fitness_fn=JazzFitness(),
    ))

    # Evolve
    composer.evolve_all_layers(verbose=True)
    composer.print_summary()

    # Generate output
    composition = composer.get_composition(bpm=140)
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')

    print("\n" + "="*60)
    print("🎺 Strudel URL:")
    print(f"https://strudel.cc/#{encoded}")
    print("="*60)


if __name__ == "__main__":
    main()
