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

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness, StableFitness
from fitness.genres import PopFitness, ElectronicFitness
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
    print("   Note: Electronic uses four-on-the-floor kick, offbeat hats, backbeat clap")

    # 1. SYNTH CHORDS - EDM chord stabs (evolves first for harmonic context)
    print("  🎹 Synth Chords - EDM stabs")
    composer.add_instrument(InstrumentConfig(
        name="synth_chords",
        instrument="triangle",
        beats_per_bar=2,  # 2 chords per bar for movement
        octave_range=(3, 4),
        scale=a_minor,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["minor", "major", "sus2", "sus4"],
        chord_fitness_fn=ElectronicChordFitness(),
        octave_shift=3,
        gain=0.2,
        lpf=3500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
        layer_role="chords",
    ))

    # 2. KICK - Four-on-the-floor (kick on every beat)
    print("  🥁 Kick - Four on the floor (every beat)")
    composer.add_instrument(InstrumentConfig(
        name="kick",
        instrument="bd",
        beats_per_bar=4,
        max_subdivision=1,  # Simple quarter notes
        is_drum=True,
        drum_sound="bd",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["electronic_kick"],  # Four-on-the-floor
        gain=0.85,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
        layer_role="drums",
    ))

    # 3. CLAP - Backbeat (beats 2 and 4)
    print("  🥁 Clap - Backbeat (beats 2 & 4)")
    composer.add_instrument(InstrumentConfig(
        name="clap",
        instrument="sd",
        beats_per_bar=4,
        max_subdivision=1,
        is_drum=True,
        drum_sound="cp",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["electronic_clap"],  # Backbeat pattern
        gain=0.6,
        play_in_sections=[SectionType.CHORUS],
        layer_role="drums",
    ))

    # 4. HI-HAT - Offbeat or steady 8ths
    print("  🥁 Hi-Hat - Offbeat/8ths pattern")
    composer.add_instrument(InstrumentConfig(
        name="hihat",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=2,  # Allow 8th notes
        is_drum=True,
        drum_sound="hh",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["electronic_hihat"],  # Offbeat pattern
        gain=0.4,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
        layer_role="drums",
    ))

    # 5. OPEN HAT - Accent on offbeats
    print("  🥁 Open Hat - Offbeat accents")
    composer.add_instrument(InstrumentConfig(
        name="open_hat",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="oh",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["electronic_hihat"],
        gain=0.35,
        play_in_sections=[SectionType.CHORUS],
        layer_role="drums",
    ))

    # 6. SUB BASS - Low end following chord root
    print("  🎸 Sub Bass - Low end")
    composer.add_instrument(InstrumentConfig(
        name="bass",
        instrument="sine",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(1, 3),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["electronic"],
        melody_fitness_fn=ElectronicFitness(),
        octave_shift=1,
        gain=0.55,
        lpf=400,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
        layer_role="bass",
        use_inter_layer_fitness=True,
        inter_layer_weight=0.25,
        use_harmonic_context=True,
        genre="electronic",
        harmony_weight=0.3,
    ))

    # 7. LEAD SYNTH - Main melody (hypnotic, arpeggiated)
    print("  🎹 Lead Synth - Hypnotic melody")
    composer.add_instrument(InstrumentConfig(
        name="lead_synth",
        instrument="square",
        beats_per_bar=4,
        max_subdivision=4,  # Allow 16th notes for arpeggios
        octave_range=(4, 6),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["electronic"],
        melody_fitness_fn=ElectronicFitness(),  # Repetitive, arpeggiated
        octave_shift=5,
        gain=0.3,
        lpf=5500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
        layer_role="lead",
        use_inter_layer_fitness=True,
        inter_layer_weight=0.3,
        use_harmonic_context=True,
        genre="electronic",
        harmony_weight=0.35,
    ))

    # 8. PLUCK SYNTH - Fast arpeggios
    print("  🎹 Pluck Synth - Fast arpeggios")
    composer.add_instrument(InstrumentConfig(
        name="pluck",
        instrument="triangle",
        beats_per_bar=4,
        max_subdivision=4,  # 16th note arpeggios
        octave_range=(4, 6),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["electronic_arp"],  # Fast arpeggios
        melody_fitness_fn=ElectronicFitness(),
        octave_shift=5,
        gain=0.28,
        lpf=4500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
        layer_role="melody",
        use_inter_layer_fitness=True,
        inter_layer_weight=0.25,
        use_harmonic_context=True,
        genre="electronic",
        harmony_weight=0.3,
    ))

    # 9. PAD - Atmospheric background
    print("  🎹 Synth Pad - Atmosphere")
    composer.add_instrument(InstrumentConfig(
        name="pad",
        instrument="sawtooth",
        beats_per_bar=4,
        max_subdivision=1,
        octave_range=(3, 5),
        scale=a_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["electronic"],
        melody_fitness_fn=StableFitness(),
        octave_shift=4,
        gain=0.22,
        lpf=3000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.BRIDGE, SectionType.OUTRO],
        layer_role="pad",
        use_inter_layer_fitness=True,
        inter_layer_weight=0.2,
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
