"""Complete band demo with piano, drums, and bass."""
import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.genres import PopFitness
from core.music import NoteName


def main():
    print("\n" + "="*60)
    print("🎹 COMPLETE BAND COMPOSITION 🥁")
    print("="*60)
    print("\nGenerating a full band with:")
    print("  🎹 Piano - Melodic lead")
    print("  🥁 Drums - Steady rhythm")
    print("  🎸 Bass - Groovy foundation")
    print()

    # Create composer with good settings for musical results
    composer = LayeredComposer(
        population_size=20,
        mutation_rate=0.25,
        elitism_count=6,
        rhythm_generations=30,
        melody_generations=35,
    )

    # C major scale for harmony
    c_major = [
        NoteName.C, NoteName.D, NoteName.E, NoteName.F,
        NoteName.G, NoteName.A, NoteName.B
    ]

    # C major pentatonic (simpler, always sounds good)
    c_pentatonic = [NoteName.C, NoteName.D, NoteName.E, NoteName.G, NoteName.A]

    # 1. DRUMS - Steady, driving beat
    print("Adding drums layer...")
    composer.add_layer(LayerConfig(
        name="drums",
        instrument="sawtooth",  # Percussive sound
        bars=2,
        beats_per_bar=4,
        max_subdivision=4,  # Can use sixteenth notes
        octave_range=(2, 3),  # Low octave for percussion
        scale=[NoteName.C, NoteName.D],  # Just two "drum sounds"
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["drum"],
        melody_fitness_fn=PopFitness(),
    ))

    # 2. BASS - Groovy, solid foundation
    print("Adding bass layer...")
    composer.add_layer(LayerConfig(
        name="bass",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,  # Simpler rhythm (quarters and eighths)
        octave_range=(2, 3),  # Bass octave
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
        melody_fitness_fn=PopFitness(),
    ))

    # 3. PIANO - Melodic lead
    print("Adding piano melody...")
    composer.add_layer(LayerConfig(
        name="piano",
        instrument="piano",
        bars=2,
        beats_per_bar=4,
        max_subdivision=3,  # Up to triplets
        octave_range=(4, 5),  # Middle to high octave
        scale=c_pentatonic,  # Pentatonic always sounds good
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=PopFitness(),
    ))

    # Evolve all layers
    print("\n" + "="*60)
    print("Starting evolution process...")
    print("="*60)
    composer.evolve_all_layers(verbose=True)

    # Print detailed summary
    composer.print_summary()

    # Generate composition
    composition = composer.get_composition(bpm=120)

    # Create Strudel URL
    strudel_code = composition.to_strudel()
    encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')
    url = f"https://strudel.cc/#{encoded}"

    # Output
    print("\n" + "="*60)
    print("🎵 STRUDEL OUTPUT")
    print("="*60)
    print(f"\nClick to hear your band:\n{url}")

    print("\n" + "-"*60)
    print("Raw Strudel Code:")
    print("-"*60)
    print(strudel_code)

    print("\n" + "="*60)
    print("✨ COMPOSITION COMPLETE! ✨")
    print("="*60)
    print("\nYour AI band is ready to play!")
    print("The rhythm fitness ensures each instrument has an appropriate pattern:")
    print("  - Drums: Steady, consistent, high density")
    print("  - Bass: Groovy, repetitive, moderate density")
    print("  - Piano: Catchy, melodic, varied but not chaotic")
    print()


if __name__ == "__main__":
    main()
