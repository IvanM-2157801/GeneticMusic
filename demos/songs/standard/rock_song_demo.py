"""Rock Song Demo - Generates a full rock song with power and energy.

This demo creates a complete rock song structure with classic rock format,
each section evolved separately using genetic algorithms.

Rock characteristics:
- Power chords and driving rhythms
- Strong backbeat drums
- Distorted guitar sounds
- Simple but powerful progressions
- Verse-Chorus-Verse-Chorus-Solo-Chorus structure
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness
from fitness.genres import PopFitness  # Rock is similar to pop in structure
from fitness.chords import RockChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🎸 ROCK SONG GENERATOR 🎸".center(58) + "#")
    print("#" + "    (Power & Energy)".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Create the song composer
    composer = SongComposer(
        population_size=100,
        mutation_rate=0.25,
        rhythm_generations=25,
        melody_generations=30,
        chord_generations=20,
    )
    
    # === DEFINE SONG SECTIONS ===
    
    # Intro - Building tension
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,
        energy_level=0.5,
        rhythm_fitness_modifier=0.9,
        melody_fitness_modifier=1.0,
    ))
    
    # Verse - Driving rhythm
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.65,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))
    
    # Chorus - Full power
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.85,
        rhythm_fitness_modifier=1.1,
        melody_fitness_modifier=1.0,
    ))
    
    # Bridge/Solo - Guitar solo section
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=2,
        energy_level=0.9,
        rhythm_fitness_modifier=1.2,
        melody_fitness_modifier=1.1,
    ))
    
    # Outro - Ending with power
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.7,
        rhythm_fitness_modifier=0.9,
        melody_fitness_modifier=1.0,
    ))
    
    # === SET SONG STRUCTURE ===
    # Classic rock structure: Intro-Verse-Chorus-Verse-Chorus-Solo-Chorus-Outro
    composer.set_song_structure([
        # Intro (8 bars)
        SectionType.INTRO,
        SectionType.INTRO,
        SectionType.INTRO,
        SectionType.INTRO,
        # Verse 1 (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Chorus 1 (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Verse 2 (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Chorus 2 (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Guitar Solo (8 bars)
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        # Final Chorus - bigger (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Outro (8 bars)
        SectionType.OUTRO,
        SectionType.OUTRO,
        SectionType.OUTRO,
        SectionType.OUTRO,
    ])
    
    # === DEFINE INSTRUMENTS ===
    # Natural minor scale for rock
    a_minor = [
        NoteName.A, NoteName.B, NoteName.C, NoteName.D,
        NoteName.E, NoteName.F, NoteName.G,
    ]
    
    print("\n📋 Adding rock instruments...")
    
    # 1. POWER CHORDS - Rock foundation
    print("  🎸 Power Chords - Rock foundation")
    composer.add_instrument(InstrumentConfig(
        name="power_chords",
        instrument="square",  # Tighter sound
        beats_per_bar=8,  # Longer power chords
        octave_range=(2, 3),  # Lower, foundation
        scale=a_minor,
        is_chord_layer=True,
        notes_per_chord=2,  # Power chords are root + 5th
        allowed_chord_types=["power", "major", "minor"],
        chord_fitness_fn=RockChordFitness(),
        octave_shift=2,
        gain=0.2,  # Reduced volume
        lpf=2500,  # Warmer
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # 2. LEAD GUITAR - Melodic lead
    print("  🎸 Lead Guitar - Melodic lines")
    composer.add_instrument(InstrumentConfig(
        name="lead_guitar",
        instrument="sawtooth",
        beats_per_bar=4,
        max_subdivision=3,  # Allow fast runs
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
    
    # 2. RHYTHM GUITAR - Power chords
    print("  🎸 Rhythm Guitar - Power chords")
    composer.add_instrument(InstrumentConfig(
        name="rhythm_guitar",
        instrument="square",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(3, 5),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["rock"],
        melody_fitness_fn=PopFitness(),  # Simpler patterns
        octave_shift=3,
        gain=0.35,
        lpf=3500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # 3. BASS - Rock bass
    print("  🎸 Bass - Rock foundation")
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
    
    # 4. KICK DRUM - Driving beat
    print("  🥁 Kick Drum - Driving beat")
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
    
    # 5. SNARE - Strong backbeat
    print("  🥁 Snare - Backbeat")
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
    
    # 6. HI-HAT - Driving 8ths
    print("  🥁 Hi-Hat - Driving rhythm")
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
    
    # 7. CRASH - Accents
    print("  🥁 Crash - Section accents")
    composer.add_instrument(InstrumentConfig(
        name="crash",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=1,  # Sparse crashes
        is_drum=True,
        drum_sound="hh:2",  # Different hi-hat for crash-like sound
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.3,
        play_in_sections=[SectionType.CHORUS],
    ))
    
    # === EVOLVE THE SONG ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    
    # Generate Strudel code at 130 BPM (driving rock tempo)
    strudel_code = composer.get_strudel_code(bpm=130)
    strudel_link = composer.get_strudel_link(bpm=130)
    
    print("\n" + "=" * 60)
    print("🎸 STRUDEL CODE")
    print("=" * 60)
    print(strudel_code)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    
    print("\n" + "=" * 60)
    print("✅ Rock song generation complete!")
    print("   Click the link above to hear your rock composition.")
    print("=" * 60)


if __name__ == "__main__":
    main()
