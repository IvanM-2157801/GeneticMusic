"""Example: Funk composition with groovy, syncopated rhythms."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.genres import PopFitness
from core.music import NoteName


def main():
    print("\n🎸 FUNK COMPOSITION GENERATOR 🎸\n")

    composer = LayeredComposer(
        population_size=20,
        mutation_rate=0.3,
        elitism_count=6,
        rhythm_generations=30,
        melody_generations=30,
    )

    # Funk pentatonic scale
    funk_scale = [NoteName.C, NoteName.D, NoteName.DS, NoteName.F,
                  NoteName.G, NoteName.A, NoteName.AS]

    # Lead - funky syncopated melody
    composer.add_layer(LayerConfig(
        name="lead",
        instrument="square",
        bars=2,
        beats_per_bar=4,
        max_subdivision=4,
        octave_range=(4, 5),
        scale=funk_scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
        melody_fitness_fn=PopFitness(),
    ))

    # Bass - groovy bass line
    composer.add_layer(LayerConfig(
        name="bass",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=4,  # More complex for funk bass
        octave_range=(2, 3),
        scale=funk_scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
        melody_fitness_fn=PopFitness(),
    ))

    # Stabs - rhythmic chords
    composer.add_layer(LayerConfig(
        name="stabs",
        instrument="triangle",
        bars=2,
        beats_per_bar=4,
        max_subdivision=3,
        octave_range=(3, 4),
        scale=funk_scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
        melody_fitness_fn=PopFitness(),
    ))

    # Evolve
    composer.evolve_all_layers(verbose=True)
    composer.print_summary()

    # Generate output
    composition = composer.get_composition(bpm=110)
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')

    print("\n" + "="*60)
    print("🎵 Strudel URL:")
    print(f"https://strudel.cc/#{encoded}")
    print("="*60)


if __name__ == "__main__":
    main()
