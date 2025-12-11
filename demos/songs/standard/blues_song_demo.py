"""Blues Song Demo - Generates a full 12-bar blues song.

This demo creates a complete blues song structure with the classic
12-bar blues form, evolved using genetic algorithms.

Blues characteristics:
- 12-bar blues progression
- Blue notes (b3, b5, b7)
- Shuffle rhythm
- Call and response patterns
- Guitar, bass, and drums
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
    print("#" + "    🎸 BLUES SONG GENERATOR 🎸".center(58) + "#")
    print("#" + "    (12-Bar Blues Style)".center(58) + "#")
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
    # 12-bar blues: I-I-I-I, IV-IV-I-I, V-IV-I-V (turnaround)
    
    # Intro - sparse, setting the mood
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,
        energy_level=0.4,
        rhythm_fitness_modifier=0.8,
        melody_fitness_modifier=1.0,
    ))
    
    # Verse - 12-bar blues verse
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.6,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))
    
    # Chorus/Turnaround - climax
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.75,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))
    
    # Solo section
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=2,
        energy_level=0.8,
        rhythm_fitness_modifier=1.1,
        melody_fitness_modifier=1.1,
    ))
    
    # Outro
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.5,
        rhythm_fitness_modifier=0.8,
        melody_fitness_modifier=0.9,
    ))
    
    # === SET SONG STRUCTURE ===
    # Classic blues: Intro, 12-bar verse x2, solo, 12-bar verse, outro
    composer.set_song_structure([
        # Intro (4 bars)
        SectionType.INTRO,
        SectionType.INTRO,
        # 12-bar blues verse 1 (12 bars = 6 x 2-bar sections)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Turnaround/Chorus (4 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        # 12-bar blues verse 2 (12 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Turnaround/Chorus (4 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Guitar solo (12 bars)
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        # Final verse (12 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Final turnaround (4 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Outro (4 bars)
        SectionType.OUTRO,
        SectionType.OUTRO,
    ])
    
    # === DEFINE INSTRUMENTS ===
    # Blues scale
    blues_scale = [
        NoteName.C, NoteName.DS, NoteName.F, NoteName.FS,
        NoteName.G, NoteName.AS,
    ]
    
    print("\n📋 Adding blues instruments...")
    
    # 1. LEAD GUITAR - Blues licks
    print("  🎸 Lead Guitar - Blues licks")
    composer.add_instrument(InstrumentConfig(
        name="lead_guitar",
        instrument="sawtooth",
        beats_per_bar=4,
        max_subdivision=3,  # Allow triplets for blues feel
        octave_range=(4, 6),
        scale=blues_scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["funk"],  # Good groove
        melody_fitness_fn=BluesFitness(),
        octave_shift=5,
        gain=0.4,
        lpf=4000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # 2. BLUES CHORDS - Dominant 7ths
    print("  🎹 Blues Chords - Dominant 7ths")
    composer.add_instrument(InstrumentConfig(
        name="chords",
        instrument="triangle",  # Softer waveform
        beats_per_bar=8,  # Longer notes, less frequent
        octave_range=(3, 4),  # Lower range to sit behind
        scale=blues_scale,
        is_chord_layer=True,
        notes_per_chord=3,  # Simpler voicings
        allowed_chord_types=["dom7", "major", "minor"],
        chord_fitness_fn=BluesChordFitness(),
        octave_shift=3,
        gain=0.15,  # Quiet, supportive
        lpf=2000,   # Roll off highs
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # 3. RHYTHM GUITAR - Comping
    print("  🎸 Rhythm Guitar - Shuffle comping")
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
    
    # 3. BASS - Boogie bass
    print("  🎸 Bass - Boogie bass line")
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
    
    # 4. KICK DRUM - Shuffle beat
    print("  🥁 Kick Drum")
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
    
    # 5. SNARE - Backbeat
    print("  🥁 Snare - Backbeat")
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
    
    # 6. HI-HAT - Shuffle
    print("  🥁 Hi-Hat - Shuffle pattern")
    composer.add_instrument(InstrumentConfig(
        name="hihat",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=3,  # Triplets for shuffle
        is_drum=True,
        drum_sound="hh",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.4,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # === EVOLVE THE SONG ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    
    # Generate Strudel code at 95 BPM (slow blues tempo)
    strudel_code = composer.get_strudel_code(bpm=95)
    strudel_link = composer.get_strudel_link(bpm=95)
    
    print("\n" + "=" * 60)
    print("🎸 STRUDEL CODE")
    print("=" * 60)
    print(strudel_code)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    
    print("\n" + "=" * 60)
    print("✅ Blues song generation complete!")
    print("   Click the link above to hear your blues composition.")
    print("=" * 60)


if __name__ == "__main__":
    main()
