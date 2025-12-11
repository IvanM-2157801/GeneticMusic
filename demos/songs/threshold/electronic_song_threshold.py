"""Electronic Song Demo with Threshold-Based Evolution.

Evolves until fitness threshold is reached for higher quality results.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness, StableFitness
from fitness.genres import PopFitness
from fitness.chords import ElectronicChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🎧 ELECTRONIC SONG (THRESHOLD-BASED) 🎧".center(58) + "#")
    print("#" + "    Evolving until fitness >= 0.80".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    composer = SongComposer(
        population_size=100,
        mutation_rate=0.2,
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
        section_type=SectionType.VERSE,  # Buildup
        bars=2,
        energy_level=0.6,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,  # Drop
        bars=2,
        energy_level=0.95,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,  # Breakdown
        bars=2,
        energy_level=0.3,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.4,
    ))
    
    # === SONG STRUCTURE (EDM build-drop) ===
    composer.set_song_structure([
        SectionType.INTRO, SectionType.INTRO, SectionType.INTRO, SectionType.INTRO,
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS,
        SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS,
        SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE, SectionType.BRIDGE,
        SectionType.VERSE, SectionType.VERSE, SectionType.VERSE, SectionType.VERSE,
        SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS, SectionType.CHORUS,
        SectionType.OUTRO, SectionType.OUTRO, SectionType.OUTRO, SectionType.OUTRO,
    ])
    
    # A minor
    a_minor = [NoteName.A, NoteName.B, NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G]
    
    print("\n📋 Adding electronic instruments...")
    
    # Synth chords
    composer.add_instrument(InstrumentConfig(
        name="synth_chords",
        instrument="triangle",
        beats_per_bar=8,
        octave_range=(3, 4),
        scale=a_minor,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["minor", "major", "sus2", "sus4"],
        chord_fitness_fn=ElectronicChordFitness(),
        octave_shift=3,
        gain=0.18,
        lpf=3500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))
    
    # Lead synth
    composer.add_instrument(InstrumentConfig(
        name="lead_synth",
        instrument="square",
        beats_per_bar=4,
        max_subdivision=4,
        octave_range=(4, 6),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=MelodicFitness(),
        octave_shift=5,
        gain=0.3,
        lpf=6000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # Pluck synth
    composer.add_instrument(InstrumentConfig(
        name="pluck",
        instrument="triangle",
        beats_per_bar=4,
        max_subdivision=4,
        octave_range=(4, 6),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=StableFitness(),
        octave_shift=5,
        gain=0.3,
        lpf=5000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))
    
    # Pad
    composer.add_instrument(InstrumentConfig(
        name="pad",
        instrument="sawtooth",
        beats_per_bar=8,
        max_subdivision=1,
        octave_range=(3, 5),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=StableFitness(),
        octave_shift=4,
        gain=0.25,
        lpf=3000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # Sub bass
    composer.add_instrument(InstrumentConfig(
        name="bass",
        instrument="sine",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(1, 3),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
        melody_fitness_fn=PopFitness(),
        octave_shift=1,
        gain=0.6,
        lpf=500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
    ))
    
    # Kick
    composer.add_instrument(InstrumentConfig(
        name="kick",
        instrument="bd",
        beats_per_bar=4,
        max_subdivision=1,
        is_drum=True,
        drum_sound="bd",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
        gain=0.9,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
    ))
    
    # Clap
    composer.add_instrument(InstrumentConfig(
        name="clap",
        instrument="sd",
        beats_per_bar=4,
        max_subdivision=1,
        is_drum=True,
        drum_sound="cp",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
        gain=0.6,
        play_in_sections=[SectionType.CHORUS],
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
        gain=0.4,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))
    
    # Open hat
    composer.add_instrument(InstrumentConfig(
        name="open_hat",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="oh",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.35,
        play_in_sections=[SectionType.CHORUS],
    ))
    
    # === EVOLVE ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    strudel_link = composer.get_strudel_link(bpm=128)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    print("\n✅ Threshold-based electronic song complete!")


if __name__ == "__main__":
    main()
