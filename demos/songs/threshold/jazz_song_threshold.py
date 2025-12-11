"""Jazz Song Demo with Threshold-Based Evolution.

Evolves until fitness threshold is reached for higher quality results.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness
from fitness.genres import JazzFitness
from fitness.chords import JazzChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🎷 JAZZ SONG (THRESHOLD-BASED) 🎷".center(58) + "#")
    print("#" + "    Evolving until fitness >= 0.80".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    composer = SongComposer(
        population_size=120,
        mutation_rate=0.3,
        fitness_threshold=0.80,
        max_generations=200,
    )
    
    # === SECTIONS (AABA form) ===
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,
        energy_level=0.5,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,  # A section
        bars=2,
        energy_level=0.6,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,  # B section
        bars=2,
        energy_level=0.7,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,  # Solo
        bars=2,
        energy_level=0.8,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.4,
    ))
    
    # === SONG STRUCTURE (AABA with solos) ===
    composer.set_song_structure([
        SectionType.INTRO,
        # Head - AABA
        SectionType.VERSE, SectionType.VERSE,
        SectionType.BRIDGE,
        SectionType.VERSE,
        # Solo
        SectionType.CHORUS, SectionType.CHORUS,
        # Head out
        SectionType.VERSE,
        SectionType.OUTRO,
    ])
    
    # Dorian mode for jazz
    c_dorian = [NoteName.C, NoteName.D, NoteName.DS, NoteName.F, NoteName.G, NoteName.A, NoteName.AS]
    
    print("\n📋 Adding jazz instruments...")
    
    # Piano
    composer.add_instrument(InstrumentConfig(
        name="piano",
        instrument="piano",
        beats_per_bar=4,
        max_subdivision=3,
        octave_range=(3, 6),
        scale=c_dorian,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["jazz"],
        melody_fitness_fn=JazzFitness(),
        octave_shift=4,
        gain=0.4,
        lpf=6000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.BRIDGE, SectionType.CHORUS, SectionType.OUTRO],
    ))
    
    # Jazz chords
    composer.add_instrument(InstrumentConfig(
        name="chords",
        instrument="triangle",
        beats_per_bar=2,  # 2 chords per bar (half notes)
        octave_range=(3, 4),
        scale=c_dorian,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["maj7", "min7", "dom7"],
        chord_fitness_fn=JazzChordFitness(),
        octave_shift=3,
        gain=0.25,
        lpf=3000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.BRIDGE, SectionType.CHORUS],
    ))
    
    # Bass
    composer.add_instrument(InstrumentConfig(
        name="bass",
        instrument="sawtooth",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(2, 4),
        scale=c_dorian,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
        melody_fitness_fn=JazzFitness(),
        octave_shift=2,
        gain=0.5,
        lpf=2000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.BRIDGE, SectionType.CHORUS, SectionType.OUTRO],
    ))
    
    # Ride cymbal
    composer.add_instrument(InstrumentConfig(
        name="ride",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=3,
        is_drum=True,
        drum_sound="hh:3",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.3,
        play_in_sections=[SectionType.VERSE, SectionType.BRIDGE, SectionType.CHORUS],
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
        gain=0.5,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # === EVOLVE ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    strudel_link = composer.get_strudel_link(bpm=140)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    print("\n✅ Threshold-based jazz song complete!")


if __name__ == "__main__":
    main()
