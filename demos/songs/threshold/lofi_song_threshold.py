"""Lofi Song Threshold Demo - Generates a chill lofi hip-hop track with new features.

This demo showcases the new advanced features:
- Inter-layer fitness: Melody and bass complement each other (30% weight)
- Harmonic context: Melodies respect the underlying chord progression
- Layer role priority: Chords evolve first, then drums, bass, melody, pad

Creates a relaxing lofi beat with:
- Simple, laid-back drums
- Jazz-influenced chords (evolved first for harmonic context)
- Mellow melodies that follow the chord progression
- Warm, filtered sounds
- Slow tempo (~65 BPM)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.drums import DRUM_FITNESS_FUNCTIONS
from fitness.melody_types import StableFitness, MelodicFitness
from fitness.genres import JazzFitness
from fitness.chords import JazzChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "  LOFI SONG (THRESHOLD + NEW FEATURES)".center(58) + "#")
    print("#" + "  Inter-layer fitness + Harmonic context".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)

    # Create the song composer with threshold-based evolution
    composer = SongComposer(
        population_size=80,
        mutation_rate=0.2,
        fitness_threshold=0.90,  # Stop when fitness >= 0.75
        max_generations=100,
        rhythm_generations=25,
        melody_generations=30,
        chord_generations=25,
    )

    # === DEFINE SONG SECTIONS ===
    print("\n[Song Structure]")
    print("  Intro (sparse) -> Verse (main loop) -> Chorus (fuller) -> Outro (fade)")

    # Intro - Minimal start
    composer.add_section(
        SectionConfig(
            section_type=SectionType.INTRO,
            bars=4,
            energy_level=0.3,
            rhythm_fitness_modifier=0.7,
            melody_fitness_modifier=0.8,
        )
    )

    # Main Loop - The core lofi beat
    composer.add_section(
        SectionConfig(
            section_type=SectionType.VERSE,
            bars=4,
            energy_level=0.5,
            rhythm_fitness_modifier=0.9,
            melody_fitness_modifier=1.0,
        )
    )

    # Variation - Slight change, fuller sound
    composer.add_section(
        SectionConfig(
            section_type=SectionType.CHORUS,
            bars=4,
            energy_level=0.6,
            rhythm_fitness_modifier=1.0,
            melody_fitness_modifier=1.0,
        )
    )

    # Outro - Fade out
    composer.add_section(
        SectionConfig(
            section_type=SectionType.OUTRO,
            bars=4,
            energy_level=0.3,
            rhythm_fitness_modifier=0.6,
            melody_fitness_modifier=0.7,
        )
    )

    # === SET SONG STRUCTURE ===
    # Simple lofi structure: Intro - Loop - Loop - Variation - Loop - Outro
    composer.set_song_structure(
        [
            SectionType.INTRO,
            SectionType.VERSE,
            SectionType.VERSE,
            SectionType.CHORUS,
            SectionType.VERSE,
            SectionType.OUTRO,
        ]
    )

    # === DEFINE INSTRUMENTS ===
    # Use minor scale for that lofi melancholic vibe
    d_minor = [
        NoteName.D,
        NoteName.E,
        NoteName.F,
        NoteName.G,
        NoteName.A,
        NoteName.AS,
        NoteName.C,
    ]

    print("\n[New Features Enabled]")
    print("  - Inter-layer fitness: 30% weight (layers complement each other)")
    print("  - Harmonic context: Melodies follow chord progression")
    print("  - Layer role priority: chords -> drums -> bass -> melody -> pad")

    print("\n[Adding instruments...]")

    # 1. JAZZ CHORDS - Evolves FIRST to provide harmonic context
    # layer_role="chords" ensures it's evolved before other melodic layers
    print("  [chords] Jazz Chords - Warm harmony (evolves first)")
    composer.add_instrument(
        InstrumentConfig(
            name="jazz_chords",
            instrument="triangle",
            beats_per_bar=1,  # One chord per bar
            octave_range=(3, 4),
            scale=d_minor,
            is_chord_layer=True,
            notes_per_chord=2,
            allowed_chord_types=["minor", "major", "minor7", "major7"],
            chord_fitness_fn=JazzChordFitness(),
            octave_shift=3,
            gain=0.25,
            lpf=2500,
            use_scale_degrees=True,
            play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
            layer_role="chords",
        )
    )

    composer.add_instrument(
        InstrumentConfig(
            name="jazz_pain",
            instrument="piano",
            beats_per_bar=1,  # One chord per bar
            octave_range=(3, 4),
            scale=d_minor,
            is_chord_layer=True,
            notes_per_chord=3,
            allowed_chord_types=["minor", "major", "minor7", "major7"],
            chord_fitness_fn=JazzChordFitness(),
            octave_shift=3,
            gain=0.25,
            lpf=2500,
            use_scale_degrees=True,
            play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
            layer_role="chords",
        )
    )

    # 2. KICK - Evolves second (drums come after chords)
    print("  [drums] Kick - Soft boom-bap")
    composer.add_instrument(
        InstrumentConfig(
            name="kick",
            instrument="bd",
            beats_per_bar=2,
            max_subdivision=1,
            is_drum=True,
            drum_sound="bd",
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
            gain=0.75,
            play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
            layer_role="drums",
        )
    )

    # 3. SNARE
    print("  [drums] Snare - Laid-back backbeat")
    composer.add_instrument(
        InstrumentConfig(
            name="snare",
            instrument="sd",
            beats_per_bar=1,
            max_subdivision=1,
            is_drum=True,
            drum_sound="sd",
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["snare"],
            gain=0.55,
            play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
            layer_role="drums",
        )
    )

    # 4. HI-HAT
    print("  [drums] Hi-Hat - Gentle groove")
    composer.add_instrument(
        InstrumentConfig(
            name="hihat",
            instrument="hh",
            beats_per_bar=2,
            max_subdivision=1,
            is_drum=True,
            drum_sound="hh",
            rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["hihat"],
            gain=0.35,
            play_in_sections=[
                SectionType.INTRO,
                SectionType.VERSE,
                SectionType.CHORUS,
                SectionType.OUTRO,
            ],
            layer_role="drums",
        )
    )

    # 5. BASS - Evolves after drums, uses inter-layer fitness
    print("  [bass] Bass - Warm sub-bass (inter-layer: 30%)")
    composer.add_instrument(
        InstrumentConfig(
            name="bass",
            instrument="sine",
            beats_per_bar=1,
            max_subdivision=1,
            octave_range=(2, 3),
            scale=d_minor,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
            melody_fitness_fn=StableFitness(),
            octave_shift=2,
            gain=0.45,
            lpf=400,
            use_scale_degrees=True,
            play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.OUTRO],
            # New features
            layer_role="bass",
            use_inter_layer_fitness=True,  # Consider other layers
            inter_layer_weight=0.3,  # 30% weight for inter-layer compatibility
            use_harmonic_context=True,  # Follow chord progression
            genre="jazz",  # Jazz has looser chord-melody relationship
            harmony_weight=0.3,
        )
    )

    # 6. MELLOW PAD - Background atmosphere
    print("  [pad] Ambient Pad - Atmosphere (inter-layer: 30%)")
    composer.add_instrument(
        InstrumentConfig(
            name="pad",
            instrument="sine",
            beats_per_bar=2,
            max_subdivision=1,
            octave_range=(3, 5),
            scale=d_minor,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
            melody_fitness_fn=StableFitness(),
            octave_shift=4,
            gain=0.2,
            lpf=2000,
            use_scale_degrees=True,
            play_in_sections=[
                SectionType.INTRO,
                SectionType.VERSE,
                SectionType.CHORUS,
                SectionType.OUTRO,
            ],
            # New features
            layer_role="pad",
            use_inter_layer_fitness=True,
            inter_layer_weight=0.3,
            use_harmonic_context=True,
            genre="jazz",
            harmony_weight=0.3,
        )
    )

    # 7. SOFT MELODY - Main melody, last to evolve
    print("  [melody] Melody - Chill lead (inter-layer: 30%, harmonic: 40%)")
    composer.add_instrument(
        InstrumentConfig(
            name="melody",
            instrument="triangle",
            beats_per_bar=2,
            max_subdivision=1,
            octave_range=(4, 6),
            scale=d_minor,
            rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
            melody_fitness_fn=MelodicFitness(),  # More expressive for lead
            octave_shift=5,
            gain=0.3,
            lpf=4000,
            use_scale_degrees=True,
            play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
            # New features - melody gets strongest harmonic context
            layer_role="melody",
            use_inter_layer_fitness=True,
            inter_layer_weight=0.3,
            use_harmonic_context=True,
            genre="jazz",  # Jazz allows more chromatic passing tones
            harmony_weight=0.4,  # 40% weight on chord-melody relationship
        )
    )

    # === EVOLVE THE SONG ===
    print("\n" + "=" * 60)
    print("EVOLVING SONG")
    print("Evolution order: chords -> drums -> bass -> pad -> melody")
    print("Threshold: Stop when fitness >= 0.75")
    print("=" * 60)

    composer.evolve_song(verbose=True)

    # === OUTPUT ===
    composer.print_summary()

    # Generate Strudel code at 65 BPM (very chill lofi tempo)
    strudel_code = composer.get_strudel_code(bpm=65)
    strudel_link = composer.get_strudel_link(bpm=65)

    print("\n" + "=" * 60)
    print("STRUDEL CODE")
    print("=" * 60)
    print(strudel_code)

    print("\n" + "=" * 60)
    print("STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)

    print("\n" + "=" * 60)
    print("Lofi song generation complete!")
    print("")
    print("New features used:")
    print("  - Inter-layer fitness: Bass, pad, and melody complement each other")
    print("  - Harmonic context: Melodies follow the jazz chord progression")
    print("  - Layer role priority: Proper evolution order for coherent music")
    print("")
    print("Click the link above to hear your chill lofi beat!")
    print("=" * 60)


if __name__ == "__main__":
    main()
