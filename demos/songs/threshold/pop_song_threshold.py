"""Pop Song Demo with Threshold-Based Evolution.

Evolves until fitness threshold is reached for higher quality results.
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
    print("#" + "    🎵 POP SONG (THRESHOLD-BASED) 🎵".center(58) + "#")
    print("#" + "    Evolving until fitness >= 0.80".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    composer = SongComposer(
        population_size=100,
        mutation_rate=0.25,
        fitness_threshold=0.80,  # Higher quality threshold
        max_generations=200,     # Safety limit
    )
    
    # === SECTIONS ===
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,
        energy_level=0.4,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.6,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.7,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=2,
        energy_level=0.5,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.4,
    ))
    
    # === SONG STRUCTURE ===
    composer.set_song_structure([
        SectionType.INTRO, SectionType.INTRO, SectionType.INTRO, SectionType.INTRO,
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS,
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS,
        SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE,
        SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS,
        SectionType.OUTRO, SectionType.OUTRO, SectionType.OUTRO, SectionType.OUTRO,
    ])
    
    c_major = [NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B]
    
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
        octave_shift=7,
        gain=0.3,
        lpf=8000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # Piano pad
    composer.add_instrument(InstrumentConfig(
        name="piano_pad",
        instrument="piano",
        beats_per_bar=8,
        max_subdivision=2,
        octave_range=(4, 6),
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
        melody_fitness_fn=MelodicFitness(),
        octave_shift=3,
        gain=0.3,
        lpf=8000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
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
        allowed_chord_types=["major", "minor", "sus2", "sus4"],
        chord_fitness_fn=PopChordFitness(),
        octave_shift=3,
        gain=0.15,
        lpf=2500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
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
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # Hi-hat
    composer.add_instrument(InstrumentConfig(
        name="hihat",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="hh",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.5,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # Snare
    composer.add_instrument(InstrumentConfig(
        name="snare",
        instrument="sd",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="sd",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
        gain=0.7,
        play_in_sections=[SectionType.CHORUS],
    ))
    
    # === EVOLVE ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    strudel_link = composer.get_strudel_link(bpm=120)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    print("\n✅ Threshold-based pop song complete!")


if __name__ == "__main__":
    main()
