"""Demo of chord evolution with the genetic music system.

This demo shows how to create a composition with:
- A chord layer (evolved chord progressions)
- A melody layer (that can play over the chords)
- A bass layer (following the chord roots)
"""

from layered_composer import LayeredComposer, LayerConfig
from core.music import NoteName
from fitness.chords import PopChordFitness, JazzChordFitness
from fitness.genres import PopFitness
from fitness.rhythm import pop_rhythm_fitness, bass_rhythm_fitness


def main():
    # Create the composer
    composer = LayeredComposer(
        population_size=30,
        mutation_rate=0.2,
        rhythm_generations=15,
        melody_generations=20,
        chord_generations=25,
    )

    # === Chord Layer ===
    # This layer evolves a chord progression
    chord_layer = LayerConfig(
        name="chords",
        instrument="piano",
        is_chord_layer=True,  # This makes it a chord layer
        num_chords=4,  # 4 chords in the progression
        notes_per_chord=3,  # Triads (3 notes)
        allowed_chord_types=["major", "minor"],  # Only major and minor chords
        chord_fitness_fn=PopChordFitness(),  # Use pop chord fitness
        gain=0.4,
        octave_shift=0,
        lpf=3000,
    )
    composer.add_layer(chord_layer)

    # === Melody Layer ===
    # This layer plays a melody over the chords
    melody_layer = LayerConfig(
        name="melody",
        instrument="sawtooth",
        bars=1,
        beats_per_bar=8,
        max_subdivision=2,
        scale=[NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B],
        rhythm_fitness_fn=pop_rhythm_fitness,
        melody_fitness_fn=PopFitness(),
        gain=0.5,
        octave_shift=0,
        lpf=4000,
    )
    composer.add_layer(melody_layer)

    # === Bass Layer ===
    # This layer provides the bass line
    bass_layer = LayerConfig(
        name="bass",
        instrument="sawtooth",
        bars=1,
        beats_per_bar=8,
        max_subdivision=1,  # Simple bass rhythm
        octave_range=(2, 3),
        scale=[NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B],
        rhythm_fitness_fn=bass_rhythm_fitness,
        melody_fitness_fn=PopFitness(),
        gain=0.6,
        octave_shift=7,  # Lower octave
        lpf=2000,
    )
    composer.add_layer(bass_layer)

    # Evolve all layers
    print("Starting evolution...")
    composer.evolve_all_layers(verbose=True)

    # Get the composition
    composition = composer.get_composition(bpm=120, random_scale=True)

    # Print summary
    composer.print_summary()

    # Print Strudel output
    print("\n" + "=" * 60)
    print("STRUDEL OUTPUT")
    print("=" * 60)
    print(composition.to_strudel())

    # Print Strudel link
    print("\n" + "=" * 60)
    print("STRUDEL LINK")
    print("=" * 60)
    print(composition.to_strudel_link())


if __name__ == "__main__":
    main()
