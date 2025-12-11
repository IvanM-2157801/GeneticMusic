"""Blues Song Demo with Threshold-Based Evolution.

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
from fitness.genres import BluesFitness
from fitness.chords import BluesChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🎸 BLUES SONG (THRESHOLD-BASED) 🎸".center(58) + "#")
    print("#" + "    Evolving until fitness >= 0.80".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    composer = SongComposer(
        population_size=100,
        mutation_rate=0.25,
        fitness_threshold=0.80,
        max_generations=200,
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
        energy_level=0.75,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,  # Solo
        bars=2,
        energy_level=0.8,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.5,
    ))
    
    # === SONG STRUCTURE (12-bar blues) ===
    composer.set_song_structure([
        SectionType.INTRO, SectionType.INTRO,
        # 12-bar verse 1
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS, SectionType.CHORUS,
        # 12-bar verse 2
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS, SectionType.CHORUS,
        # Solo
        SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE,
        # Final verse
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS, SectionType.CHORUS,
        SectionType.OUTRO, SectionType.OUTRO,
    ])
    
    # Blues scale
    blues_scale = [NoteName.C, NoteName.DS, NoteName.F, NoteName.FS, NoteName.G, NoteName.AS]
    
    print("\n📋 Adding blues instruments...")
    
    # Lead guitar
    composer.add_instrument(InstrumentConfig(
        name="lead_guitar",
        instrument="sawtooth",
        beats_per_bar=4,
        max_subdivision=3,
        octave_range=(4, 6),
        scale=blues_scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],
        melody_fitness_fn=BluesFitness(),
        octave_shift=5,
        gain=0.4,
        lpf=4000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # Blues chords
    composer.add_instrument(InstrumentConfig(
        name="chords",
        instrument="triangle",
        beats_per_bar=8,
        octave_range=(3, 4),
        scale=blues_scale,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["dom7", "major", "minor"],
        chord_fitness_fn=BluesChordFitness(),
        octave_shift=3,
        gain=0.15,
        lpf=2000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # Rhythm guitar
    composer.add_instrument(InstrumentConfig(
        name="rhythm_guitar",
        instrument="square",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(3, 5),
        scale=blues_scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["rock"],
        melody_fitness_fn=BluesFitness(),
        octave_shift=4,
        gain=0.25,
        lpf=3000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # Bass
    composer.add_instrument(InstrumentConfig(
        name="bass",
        instrument="sawtooth",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(2, 4),
        scale=blues_scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
        melody_fitness_fn=BluesFitness(),
        octave_shift=2,
        gain=0.5,
        lpf=1500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
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
        gain=0.7,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE],
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
        gain=0.6,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # Hi-hat
    composer.add_instrument(InstrumentConfig(
        name="hihat",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=3,
        is_drum=True,
        drum_sound="hh",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.4,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # === EVOLVE ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    strudel_link = composer.get_strudel_link(bpm=95)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    print("\n✅ Threshold-based blues song complete!")


if __name__ == "__main__":
    main()
