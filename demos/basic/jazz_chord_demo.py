"""Demo of jazz chord evolution with 7th chords.

This demo shows:
- 4-note chords (7th chords) for jazz
- Jazz-specific chord fitness
- How the chord types affect harmony
"""

from layered_composer import LayeredComposer, LayerConfig
from core.music import NoteName
from fitness.chords import JazzChordFitness
from fitness.genres import JazzFitness
from fitness.rhythm import jazz_rhythm_fitness


def main():
    # Create the composer
    composer = LayeredComposer(
        population_size=40,
        mutation_rate=0.15,
        chord_generations=30,
        melody_generations=25,
        rhythm_generations=20,
    )

    # === Jazz Chord Layer ===
    # Using 7th chords (4 notes) for jazz harmony
    chord_layer = LayerConfig(
        name="jazz_chords",
        instrument="piano",
        is_chord_layer=True,
        num_chords=4,  # ii-V-I-IV style progression
        notes_per_chord=4,  # 7th chords
        allowed_chord_types=["major7", "minor7", "dom7"],  # Jazz chord types
        chord_fitness_fn=JazzChordFitness(),
        gain=0.35,
        octave_shift=0,
        lpf=3500,
    )
    composer.add_layer(chord_layer)

    # === Jazz Melody Layer ===
    jazz_melody = LayerConfig(
        name="jazz_melody",
        instrument="saxophone",
        bars=1,
        beats_per_bar=8,
        max_subdivision=3,  # Allow triplets for jazz feel
        scale=[NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B],
        rhythm_fitness_fn=jazz_rhythm_fitness,
        melody_fitness_fn=JazzFitness(),
        gain=0.5,
        octave_shift=0,
        lpf=4000,
    )
    composer.add_layer(jazz_melody)

    # Evolve all layers
    print("Evolving jazz composition...")
    composer.evolve_all_layers(verbose=True)

    # Get the composition
    composition = composer.get_composition(bpm=110, random_scale=True)

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
