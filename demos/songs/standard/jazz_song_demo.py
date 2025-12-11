"""Jazz Song Demo - Generates a full jazz song with swing and improvisation feel.

This demo creates a complete jazz song structure with multiple sections,
each evolved separately using genetic algorithms.

Jazz characteristics:
- Swing rhythm feel
- Complex chord voicings (7ths, extended chords)
- Chromatic movement and blue notes
- Syncopated rhythms
- Piano, bass, and brush drums
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
    print("#" + "    🎷 JAZZ SONG GENERATOR 🎷".center(58) + "#")
    print("#" + "    (Swing & Improvisation)".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Create the song composer
    composer = SongComposer(
        population_size=120,  # Larger for more exploration
        mutation_rate=0.3,    # Higher mutation for jazz variety
        rhythm_generations=30,
        melody_generations=35,
        chord_generations=25,
    )
    
    # === DEFINE SONG SECTIONS ===
    # Jazz song structure: Head-Solo-Head format (AABA common)
    
    # Head (main theme)
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,
        energy_level=0.5,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))
    
    # A Section (main theme)
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.6,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))
    
    # B Section (bridge/contrast)
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=2,
        energy_level=0.7,
        rhythm_fitness_modifier=1.1,
        melody_fitness_modifier=1.0,
    ))
    
    # Solo section (high energy improvisation)
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.8,
        rhythm_fitness_modifier=1.2,
        melody_fitness_modifier=1.1,
    ))
    
    # Outro (winding down)
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.4,
        rhythm_fitness_modifier=0.8,
        melody_fitness_modifier=0.9,
    ))
    
    # === SET SONG STRUCTURE ===
    # Jazz AABA form with solos
    composer.set_song_structure([
        # Intro (4 bars)
        SectionType.INTRO,
        SectionType.INTRO,
        # Head - A section (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # A section repeat (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # B section - bridge (8 bars)
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        # A section (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Solo chorus 1 (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Solo chorus 2 (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Head out - A section (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Outro (4 bars)
        SectionType.OUTRO,
        SectionType.OUTRO,
    ])
    
    # === DEFINE INSTRUMENTS ===
    # Jazz uses Dorian/Mixolydian modes - using C Dorian for jazz feel
    c_dorian = [
        NoteName.C, NoteName.D, NoteName.DS, NoteName.F,
        NoteName.G, NoteName.A, NoteName.AS,
    ]
    
    print("\n📋 Adding jazz instruments...")
    
    # 1. PIANO - Jazz voicings
    print("  🎹 Jazz Piano - Comping and melody")
    composer.add_instrument(InstrumentConfig(
        name="piano",
        instrument="piano",
        beats_per_bar=4,
        max_subdivision=3,  # Allow triplets for swing
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
    
    # 2. JAZZ CHORDS - Voicings with 7ths
    print("  🎹 Jazz Chords - 7th voicings")
    composer.add_instrument(InstrumentConfig(
        name="chords",
        instrument="triangle",  # Softer than piano
        beats_per_bar=8,  # Longer voicings
        octave_range=(3, 4),  # Lower, sits behind
        scale=c_dorian,
        is_chord_layer=True,
        notes_per_chord=3,  # Simpler voicings
        allowed_chord_types=["maj7", "min7", "dom7"],
        chord_fitness_fn=JazzChordFitness(),
        octave_shift=3,
        gain=0.15,  # Quiet, supportive
        lpf=3000,  # Warmer
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.BRIDGE, SectionType.CHORUS],
    ))
    
    # 3. UPRIGHT BASS - Walking bass
    print("  🎸 Upright Bass - Walking bass lines")
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
    
    # 3. RIDE CYMBAL - Jazz time keeping
    print("  🥁 Ride Cymbal - Swing pattern")
    composer.add_instrument(InstrumentConfig(
        name="ride",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=3,  # Triplets for swing
        is_drum=True,
        drum_sound="hh:3",  # Use ride-like hi-hat
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.3,
        play_in_sections=[SectionType.VERSE, SectionType.BRIDGE, SectionType.CHORUS],
    ))
    
    # 4. KICK - Light jazz kick
    print("  🥁 Kick - Sparse accents")
    composer.add_instrument(InstrumentConfig(
        name="kick",
        instrument="bd",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="bd",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
        gain=0.5,  # Softer for jazz
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # 5. BRUSHES/SNARE - Jazz snare with brushes
    print("  🥁 Snare - Brush hits")
    composer.add_instrument(InstrumentConfig(
        name="snare",
        instrument="sd",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="sd:1",  # Softer snare
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
        gain=0.4,
        play_in_sections=[SectionType.CHORUS],
    ))
    
    # === EVOLVE THE SONG ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    
    # Generate Strudel code at 140 BPM (medium jazz tempo)
    strudel_code = composer.get_strudel_code(bpm=140)
    strudel_link = composer.get_strudel_link(bpm=140)
    
    print("\n" + "=" * 60)
    print("🎷 STRUDEL CODE")
    print("=" * 60)
    print(strudel_code)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    
    print("\n" + "=" * 60)
    print("✅ Jazz song generation complete!")
    print("   Click the link above to hear your jazz composition.")
    print("=" * 60)


if __name__ == "__main__":
    main()
