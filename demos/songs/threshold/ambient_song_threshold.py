"""Ambient Song Demo with Threshold-Based Evolution.

Evolves until fitness threshold is reached for higher quality results.
"""

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness, StableFitness
from fitness.genres import AmbientFitness
from fitness.chords import AmbientChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🌌 AMBIENT SONG (THRESHOLD-BASED) 🌌".center(58) + "#")
    print("#" + "    Evolving until fitness >= 0.80".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    composer = SongComposer(
        population_size=80,
        mutation_rate=0.2,
        fitness_threshold=0.80,
        max_generations=200,
    )
    
    # === SECTIONS ===
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,
        energy_level=0.2,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.35,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,  # Peak
        bars=2,
        energy_level=0.5,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=2,
        energy_level=0.4,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.15,
    ))
    
    # === SONG STRUCTURE (slow arc) ===
    composer.set_song_structure([
        SectionType.INTRO, SectionType.INTRO, SectionType.INTRO, SectionType.INTRO,
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS,
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE,
        SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS,
        SectionType.VERSE, SectionType.VERSE, SectionType.OUTRO, SectionType.OUTRO,
        SectionType.OUTRO, SectionType.OUTRO, SectionType.OUTRO, SectionType.OUTRO,
    ])
    
    # Pentatonic
    c_pentatonic = [NoteName.C, NoteName.D, NoteName.E, NoteName.G, NoteName.A]
    
    print("\n📋 Adding ambient instruments...")
    
    # Ambient chords
    composer.add_instrument(InstrumentConfig(
        name="ambient_chords",
        instrument="sine",
        beats_per_bar=8,
        octave_range=(3, 4),
        scale=c_pentatonic,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["major", "minor", "sus2", "sus4"],
        chord_fitness_fn=AmbientChordFitness(),
        octave_shift=3,
        gain=0.15,
        lpf=3000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # Low pad
    composer.add_instrument(InstrumentConfig(
        name="low_pad",
        instrument="sawtooth",
        beats_per_bar=8,
        max_subdivision=1,
        octave_range=(2, 4),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=2,
        gain=0.3,
        lpf=1500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # Mid pad
    composer.add_instrument(InstrumentConfig(
        name="mid_pad",
        instrument="sine",
        beats_per_bar=8,
        max_subdivision=1,
        octave_range=(4, 6),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=4,
        gain=0.3,
        lpf=4000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # High shimmer
    composer.add_instrument(InstrumentConfig(
        name="shimmer",
        instrument="triangle",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(5, 7),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=6,
        gain=0.2,
        lpf=8000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # Melodic voice
    composer.add_instrument(InstrumentConfig(
        name="melody",
        instrument="sine",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(4, 6),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=StableFitness(),
        octave_shift=5,
        gain=0.25,
        lpf=5000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))
    
    # No drums for ambient
    
    # === EVOLVE ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    strudel_link = composer.get_strudel_link(bpm=70)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    print("\n✅ Threshold-based ambient song complete!")


if __name__ == "__main__":
    main()
