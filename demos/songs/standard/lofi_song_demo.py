"""Lofi Song Demo - Generates a chill lofi hip-hop track.

This demo creates a relaxing lofi beat with:
- Simple, laid-back drums
- Jazz-influenced chords
- Mellow melodies
- Warm, filtered sounds
- Slow tempo (~75 BPM)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import StableFitness
from fitness.genres import JazzFitness
from fitness.chords import JazzChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🎧 LOFI SONG GENERATOR 🎧".center(58) + "#")
    print("#" + "    (Chill Beats / Lofi Hip-Hop)".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)

    # Create the song composer with fewer generations for simpler patterns
    composer = SongComposer(
        population_size=50,
        mutation_rate=0.2,
        rhythm_generations=20,
        melody_generations=25,
        chord_generations=20,
    )

    # === DEFINE SONG SECTIONS ===

    # Intro - Minimal start
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=4,
        energy_level=0.3,
        rhythm_fitness_modifier=0.7,
        melody_fitness_modifier=0.8,
    ))

    # Main Loop - The core lofi beat
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=4,
        energy_level=0.5,
        rhythm_fitness_modifier=0.9,
        melody_fitness_modifier=1.0,
    ))

    # Variation - Slight change
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=4,
        energy_level=0.6,
        rhythm_fitness_modifier=1.0,
        melody_fitness_modifier=1.0,
    ))

    # Outro - Fade out
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=4,
        energy_level=0.3,
        rhythm_fitness_modifier=0.6,
        melody_fitness_modifier=0.7,
    ))

    # === SET SONG STRUCTURE ===
    # Simple lofi structure: Intro - Loop - Loop - Variation - Loop - Loop - Outro
    composer.set_song_structure([
        # Intro (4 bars)
        SectionType.INTRO,
        # Main loop (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        # Variation (4 bars)
        SectionType.CHORUS,
        # Main loop again (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        # Outro (4 bars)
        SectionType.OUTRO,
    ])

    # === DEFINE INSTRUMENTS ===
    # Use minor scale for that lofi melancholic vibe
    d_minor = [
        NoteName.D, NoteName.E, NoteName.F, NoteName.G,
        NoteName.A, NoteName.AS, NoteName.C,
    ]

    print("\n📋 Adding lofi instruments...")

    # 1. JAZZ CHORDS - Warm, jazzy chords (one per bar)
    print("  🎹 Jazz Chords - Warm harmony")
    composer.add_instrument(InstrumentConfig(
        name="jazz_chords",
        instrument="triangle",  # Soft sound
        beats_per_bar=1,  # Just one chord per bar for simplicity
        octave_range=(3, 4),
        scale=d_minor,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["minor", "major", "minor7", "major7"],
        chord_fitness_fn=JazzChordFitness(),
        octave_shift=3,
        gain=0.25,  # Soft
        lpf=2500,  # Warm, filtered sound
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))

    # 2. MELLOW PAD - Ambient background (very sparse, long notes)
    print("  🎹 Ambient Pad - Atmosphere")
    composer.add_instrument(InstrumentConfig(
        name="pad",
        instrument="sine",  # Very soft sine wave
        beats_per_bar=2,  # Just 2 notes per 4-bar section = super sparse
        max_subdivision=1,
        octave_range=(3, 5),
        scale=d_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=StableFitness(),
        octave_shift=4,
        gain=0.2,  # Quiet
        lpf=2000,  # Heavy filtering
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
    ))

    # 3. SOFT MELODY - Very simple, sparse melody
    print("  🎹 Melody - Chill lead")
    composer.add_instrument(InstrumentConfig(
        name="melody",
        instrument="triangle",
        beats_per_bar=2,  # Only 8 notes for 4 bars = very sparse
        max_subdivision=1,  # No subdivisions, just simple notes
        octave_range=(4, 6),
        scale=d_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],  # Use ambient for sparse patterns
        melody_fitness_fn=JazzFitness(),
        octave_shift=5,
        gain=0.3,
        lpf=4000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))

    # 4. BASS - Very simple, one note per bar
    print("  🎸 Bass - Warm sub-bass")
    composer.add_instrument(InstrumentConfig(
        name="bass",
        instrument="sine",  # Warm sine bass
        beats_per_bar=1,  # One note per bar = 4 notes for 4 bars
        max_subdivision=1,
        octave_range=(2, 3),
        scale=d_minor,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
        melody_fitness_fn=StableFitness(),
        octave_shift=2,
        gain=0.45,
        lpf=400,  # Deep, warm
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
    ))

    # === SIMPLE DRUMS ===

    # === SIMPLE DRUMS - Very minimal ===

    # 5. KICK - Simple, soft kick pattern (just a few kicks per 4 bars)
    print("  🥁 Kick - Soft boom-bap")
    composer.add_instrument(InstrumentConfig(
        name="kick",
        instrument="bd",
        beats_per_bar=2,  # Only 8 kicks max for 4 bars
        max_subdivision=1,  # Just quarter notes
        is_drum=True,
        drum_sound="bd",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
        gain=0.75,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))

    # 6. SNARE - Very simple backbeat (just 2-3 snares per 4 bars)
    print("  🥁 Snare - Laid-back backbeat")
    composer.add_instrument(InstrumentConfig(
        name="snare",
        instrument="sd",
        beats_per_bar=1,  # Only 4 snares max for 4 bars
        max_subdivision=1,  # Simple backbeat
        is_drum=True,
        drum_sound="sd",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
        gain=0.55,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
    ))

    # 7. HI-HAT - Very gentle pattern (sparse)
    print("  🥁 Hi-Hat - Gentle groove")
    composer.add_instrument(InstrumentConfig(
        name="hihat",
        instrument="hh",
        beats_per_bar=2,  # Sparse hi-hats
        max_subdivision=1,  # No double hi-hats
        is_drum=True,
        drum_sound="hh",
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
        gain=0.35,  # Very soft
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
    ))

    # === EVOLVE THE SONG ===
    composer.evolve_song(verbose=True)

    # === OUTPUT ===
    composer.print_summary()

    # Generate Strudel code at 65 BPM (very chill lofi tempo)
    strudel_code = composer.get_strudel_code(bpm=65)
    strudel_link = composer.get_strudel_link(bpm=65)

    print("\n" + "=" * 60)
    print("🎧 STRUDEL CODE")
    print("=" * 60)
    print(strudel_code)

    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)

    print("\n" + "=" * 60)
    print("✅ Lofi song generation complete!")
    print("   Click the link above to hear your chill lofi beat.")
    print("   Perfect for studying, working, or relaxing!")
    print("=" * 60)


if __name__ == "__main__":
    main()
