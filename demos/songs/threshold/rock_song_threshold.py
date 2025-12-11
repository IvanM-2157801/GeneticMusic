"""Rock Song Demo with Threshold-Based Evolution.

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
from fitness.genres import PopFitness
from fitness.chords import RockChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🎸 ROCK SONG (THRESHOLD-BASED) 🎸".center(58) + "#")
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
        energy_level=0.5,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.65,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.85,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,  # Guitar solo
        bars=2,
        energy_level=0.9,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.7,
    ))
    
    # === SONG STRUCTURE ===
    composer.set_song_structure([
        SectionType.INTRO,
        SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS,
        SectionType.VERSE,
        SectionType.CHORUS,
        SectionType.BRIDGE,
        SectionType.CHORUS,
        SectionType.OUTRO,
    ])
    
    # A minor scale
    a_minor = [NoteName.A, NoteName.B, NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G]
    
    print("\n📋 Adding rock instruments...")
    
    # Power chords
    composer.add_instrument(InstrumentConfig(
        name="power_chords",
        instrument="square",
        beats_per_bar=2,  # 2 chords per bar (half notes)
        octave_range=(2, 3),
        scale=a_minor,
        is_chord_layer=True,
        notes_per_chord=2,
        allowed_chord_types=["power", "major", "minor"],
        chord_fitness_fn=RockChordFitness(),
        octave_shift=2,
        gain=0.3,
        lpf=2500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # Lead guitar
    composer.add_instrument(InstrumentConfig(
        name="lead_guitar",
        instrument="sawtooth",
        beats_per_bar=4,
        max_subdivision=3,
        octave_range=(4, 6),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["rock"],
        melody_fitness_fn=MelodicFitness(),
        octave_shift=5,
        gain=0.4,
        lpf=5000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # Rhythm guitar
    composer.add_instrument(InstrumentConfig(
        name="rhythm_guitar",
        instrument="square",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(3, 5),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["rock"],
        melody_fitness_fn=PopFitness(),
        octave_shift=3,
        gain=0.35,
        lpf=3500,
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
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
        melody_fitness_fn=PopFitness(),
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
        gain=0.85,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
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
        gain=0.75,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
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
    
    # Crash
    composer.add_instrument(InstrumentConfig(
        name="crash",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=1,
        is_drum=True,
        drum_sound="hh:2",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.3,
        play_in_sections=[SectionType.CHORUS],
    ))
    
    # === EVOLVE ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    strudel_link = composer.get_strudel_link(bpm=130)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    print("\n✅ Threshold-based rock song complete!")


if __name__ == "__main__":
    main()
