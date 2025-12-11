"""Electronic Song Demo - Generates a full electronic/EDM track.

This demo creates a complete electronic music track with classic EDM structure,
each section evolved separately using genetic algorithms.

Electronic characteristics:
- Four-on-the-floor kick pattern
- Synth leads and pads
- Build-ups and drops
- Repetitive, hypnotic patterns
- Layered synthesizers
"""

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
    print("#" + "    🎧 ELECTRONIC SONG GENERATOR 🎧".center(58) + "#")
    print("#" + "    (EDM / Synth Wave)".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Create the song composer
    composer = SongComposer(
        population_size=100,
        mutation_rate=0.2,  # Slightly lower for more consistent patterns
        rhythm_generations=25,
        melody_generations=30,
        chord_generations=20,
    )
    
    # === DEFINE SONG SECTIONS ===
    
    # Intro - Minimal, building
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,
        energy_level=0.4,
        rhythm_fitness_modifier=0.8,
        melody_fitness_modifier=1.0,
    ))
    
    # Buildup - Increasing tension
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.6,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))
    
    # Drop - Full energy
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.95,
        rhythm_fitness_modifier=1.2,
        melody_fitness_modifier=1.0,
    ))
    
    # Breakdown - Stripped back
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=2,
        energy_level=0.3,
        rhythm_fitness_modifier=0.6,
        melody_fitness_modifier=1.0,
    ))
    
    # Outro - Fading out
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.4,
        rhythm_fitness_modifier=0.7,
        melody_fitness_modifier=0.9,
    ))
    
    # === SET SONG STRUCTURE ===
    # EDM structure: Intro-Buildup-Drop-Breakdown-Buildup-Drop-Outro
    composer.set_song_structure([
        # Intro (8 bars)
        SectionType.INTRO,
        SectionType.INTRO,
        SectionType.INTRO,
        SectionType.INTRO,
        # Buildup 1 (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Drop 1 (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Extended Drop (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Breakdown (8 bars)
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        # Buildup 2 (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # Drop 2 - Final drop (8 bars)
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
    # Minor scale for darker electronic feel
    a_minor = [
        NoteName.A, NoteName.B, NoteName.C, NoteName.D,
        NoteName.E, NoteName.F, NoteName.G,
    ]
    
    print("\n📋 Adding electronic instruments...")
    
    # 1. SYNTH CHORDS - EDM chord stabs
    print("  🎹 Synth Chords - EDM stabs")
    composer.add_instrument(InstrumentConfig(
        name="synth_chords",
        instrument="triangle",  # Softer
        beats_per_bar=8,  # Longer pads
        octave_range=(3, 4),  # Lower range
        scale=a_minor,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["minor", "major", "sus2", "sus4"],
        chord_fitness_fn=ElectronicChordFitness(),
        octave_shift=3,
        gain=0.18,  # Reduced volume
        lpf=3500,  # Warmer
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))
    
    # 2. LEAD SYNTH - Main melody
    print("  🎹 Lead Synth - Main melody")
    composer.add_instrument(InstrumentConfig(
        name="lead_synth",
        instrument="square",
        beats_per_bar=4,
        max_subdivision=4,  # Allow 16th notes for arpeggios
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
    
    # 2. PLUCK SYNTH - Arpeggiated patterns
    print("  🎹 Pluck Synth - Arpeggios")
    composer.add_instrument(InstrumentConfig(
        name="pluck",
        instrument="triangle",
        beats_per_bar=4,
        max_subdivision=4,  # 16th note arpeggios
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
    
    # 3. PAD - Atmospheric background
    print("  🎹 Synth Pad - Atmosphere")
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
    
    # 4. BASS - Sub bass
    print("  🎸 Sub Bass - Low end")
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
        lpf=500,  # Very low pass for sub
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
    ))
    
    # 5. KICK - Four on the floor
    print("  🥁 Kick - Four on the floor")
    composer.add_instrument(InstrumentConfig(
        name="kick",
        instrument="bd",
        beats_per_bar=4,
        max_subdivision=1,  # Steady quarter notes
        is_drum=True,
        drum_sound="bd",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
        gain=0.9,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
    ))
    
    # 6. CLAP/SNARE - Backbeat
    print("  🥁 Clap - Backbeat")
    composer.add_instrument(InstrumentConfig(
        name="clap",
        instrument="sd",
        beats_per_bar=4,
        max_subdivision=1,
        is_drum=True,
        drum_sound="cp",  # Clap sound
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
        gain=0.6,
        play_in_sections=[SectionType.CHORUS],
    ))
    
    # 7. HI-HAT - Offbeat
    print("  🥁 Hi-Hat - Offbeat pattern")
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
    
    # 8. OPEN HAT - Accent
    print("  🥁 Open Hat - Accents")
    composer.add_instrument(InstrumentConfig(
        name="open_hat",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="oh",  # Open hi-hat
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.35,
        play_in_sections=[SectionType.CHORUS],
    ))
    
    # === EVOLVE THE SONG ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    
    # Generate Strudel code at 128 BPM (classic EDM tempo)
    strudel_code = composer.get_strudel_code(bpm=128)
    strudel_link = composer.get_strudel_link(bpm=128)
    
    print("\n" + "=" * 60)
    print("🎧 STRUDEL CODE")
    print("=" * 60)
    print(strudel_code)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    
    print("\n" + "=" * 60)
    print("✅ Electronic song generation complete!")
    print("   Click the link above to hear your electronic composition.")
    print("=" * 60)


if __name__ == "__main__":
    main()
