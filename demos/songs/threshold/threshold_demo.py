"""Demo showing threshold-based evolution.

This demo evolves until a fitness threshold is reached instead of
using a fixed number of generations. This can result in better music
but may take longer to run.
"""

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness
from fitness.genres import PopFitness
from fitness.chords import PopChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🎯 THRESHOLD-BASED EVOLUTION DEMO 🎯".center(58) + "#")
    print("#" + "    (Evolve until fitness >= 0.75)".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Create composer with FITNESS THRESHOLD instead of fixed generations
    composer = SongComposer(
        population_size=100,
        mutation_rate=0.25,
        # These are now used as fallback if threshold isn't reached
        rhythm_generations=25,
        melody_generations=30,
        chord_generations=20,
        # NEW: Threshold-based stopping
        fitness_threshold=0.75,  # Stop when fitness reaches 0.75
        max_generations=150,     # Safety limit - don't run forever
    )
    
    print("\n⚙️  Settings:")
    print(f"   Fitness threshold: {composer.fitness_threshold}")
    print(f"   Max generations: {composer.max_generations}")
    print(f"   Population size: {composer.population_size}")
    
    # Simple song structure for demo
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.6,
    ))
    
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.8,
    ))
    
    composer.set_song_structure([
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.CHORUS,
        SectionType.CHORUS,
    ])
    
    c_major = [
        NoteName.C, NoteName.D, NoteName.E, NoteName.F,
        NoteName.G, NoteName.A, NoteName.B,
    ]
    
    print("\n📋 Adding instruments...")
    
    # Melody
    composer.add_instrument(InstrumentConfig(
        name="melody",
        instrument="piano",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(4, 6),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
        melody_fitness_fn=MelodicFitness(),
        octave_shift=5,
        gain=0.4,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))
    
    # Chords
    composer.add_instrument(InstrumentConfig(
        name="chords",
        instrument="triangle",
        beats_per_bar=8,
        octave_range=(3, 4),
        scale=c_major,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["major", "minor", "sus4"],
        chord_fitness_fn=PopChordFitness(),
        octave_shift=3,
        gain=0.15,
        lpf=2500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))
    
    # Kick
    composer.add_instrument(InstrumentConfig(
        name="kick",
        instrument="bd",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="bd",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
        gain=0.8,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))
    
    # === EVOLVE ===
    print("\n" + "=" * 60)
    print("🧬 Starting threshold-based evolution...")
    print("   Evolution will stop when fitness >= 0.75 or max 150 generations")
    print("=" * 60)
    
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    
    strudel_link = composer.get_strudel_link(bpm=120)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    
    print("\n✅ Threshold-based evolution complete!")


if __name__ == "__main__":
    main()
