"""Complete Song Demo - Generates a full song with intro, verse, chorus, and outro.

This demo creates a complete song structure with multiple sections,
each evolved separately using genetic algorithms.

Based on the full_band_demo.py style - funk rhythms, groovy feel.
"""

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness, StableFitness
from fitness.genres import PopFitness
from fitness.chords import PopChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🎵 COMPLETE SONG GENERATOR 🎵".center(58) + "#")
    print("#" + "    (Full Band Style)".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Create the song composer - using same settings as full_band_demo
    composer = SongComposer(
        population_size=100,  # Same as full_band_demo
        mutation_rate=0.25,   # Same as full_band_demo
        rhythm_generations=25,  # Same as full_band_demo
        melody_generations=30,  # Same as full_band_demo
        chord_generations=20,
    )
    
    # === DEFINE SONG SECTIONS ===
    # Using 2 bars per section like full_band_demo for the right vibe
    
    # Intro: Building up, sparse
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,  # Same as full_band_demo
        energy_level=0.4,
        rhythm_fitness_modifier=0.8,
        melody_fitness_modifier=1.0,
    ))
    
    # Verse: Medium energy, groovy
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.6,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))
    
    # Chorus: Full energy, catchy
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.7,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))
    
    # Bridge: Different feel
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=2,
        energy_level=0.5,
        rhythm_fitness_modifier=0.9,
        melody_fitness_modifier=1.0,
    ))
    
    # Outro: Winding down
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.4,
        rhythm_fitness_modifier=0.7,
        melody_fitness_modifier=0.9,
    ))
    
    # === SET SONG STRUCTURE ===
    # More repetitions of 2-bar sections for a longer song with the right vibe
    composer.set_song_structure([
        # Intro (8 bars = 4 repetitions)
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
        # Bridge (8 bars)
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        # Final Chorus (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Outro (8 bars)
        SectionType.OUTRO,
        SectionType.OUTRO,
        SectionType.OUTRO,
        SectionType.OUTRO,      # Outro
    ])
    
    # === DEFINE INSTRUMENTS ===
    # Same as full_band_demo
    c_major = [
        NoteName.C, NoteName.D, NoteName.E, NoteName.F,
        NoteName.G, NoteName.A, NoteName.B,
    ]
    
    print("\n📋 Adding instruments (Full Band Style)...")
    
    # 1. MELODY - Lead synth (same as full_band_demo)
    print("  🎹 Melody - Lead piano")
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
    
    # 2. PIANO PAD - Background (same as full_band_demo)
    print("  🎛️  Piano pad - Background")
    composer.add_instrument(InstrumentConfig(
        name="piano_pad",
        instrument="piano",
        beats_per_bar=8,  # Same as full_band_demo
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
    
    # 3. CHORD PAD - Harmonic foundation
    print("  🎹 Chord pad - Harmonic foundation")
    composer.add_instrument(InstrumentConfig(
        name="chords",
        instrument="triangle",  # Softer waveform
        beats_per_bar=8,  # Longer, sustained chords
        octave_range=(3, 4),  # Lower range to sit behind
        scale=c_major,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["major", "minor", "sus2", "sus4"],
        chord_fitness_fn=PopChordFitness(),
        octave_shift=3,
        gain=0.15,  # Quiet, supportive
        lpf=2500,  # Roll off highs
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # 4. KICK DRUM (same as full_band_demo)
    print("  🥁 Kick drum")
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
    
    # 4. HI-HAT (same as full_band_demo)
    print("  🥁 Hi-hat")
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
    
    # 5. SNARE (same as full_band_demo)
    print("  🥁 Snare")
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
    
    # === EVOLVE THE SONG ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    
    # Generate Strudel code at 120 BPM (same as full_band_demo)
    strudel_code = composer.get_strudel_code(bpm=120)
    strudel_link = composer.get_strudel_link(bpm=120)
    
    print("\n" + "=" * 60)
    print("🎵 STRUDEL CODE")
    print("=" * 60)
    print(strudel_code)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    
    print("\n" + "=" * 60)
    print("✅ Song generation complete!")
    print("   Click the link above to hear your composition.")
    print("=" * 60)


if __name__ == "__main__":
    main()
