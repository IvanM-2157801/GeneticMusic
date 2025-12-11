"""Ambient Song Demo - Generates a full ambient/atmospheric piece.

This demo creates a complete ambient composition with flowing sections,
each evolved separately using genetic algorithms.

Ambient characteristics:
- Long, sustained notes
- Sparse textures
- Slow harmonic movement
- Atmospheric pads
- Pentatonic scales for consonance
- Minimal or no drums
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from song_composer import SongComposer, SectionConfig, SectionType, InstrumentConfig
from core.music import NoteName
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness, StableFitness
from fitness.genres import AmbientFitness
from fitness.chords import AmbientChordFitness


def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "    🌌 AMBIENT SONG GENERATOR 🌌".center(58) + "#")
    print("#" + "    (Atmospheric & Ethereal)".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    # Create the song composer
    composer = SongComposer(
        population_size=80,   # Smaller population for ambient
        mutation_rate=0.2,    # Lower mutation for smoother evolution
        rhythm_generations=20,
        melody_generations=25,
        chord_generations=20,
    )
    
    # === DEFINE SONG SECTIONS ===
    # Ambient: flowing sections that blend into each other
    
    # Opening - Emergence
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=2,
        energy_level=0.2,  # Very calm
        rhythm_fitness_modifier=0.6,
        melody_fitness_modifier=1.0,
    ))
    
    # Building - Gradual development
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=2,
        energy_level=0.35,
        rhythm_fitness_modifier=0.7,
        melody_fitness_modifier=1.0,
    ))
    
    # Peak - Maximum texture
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=2,
        energy_level=0.5,
        rhythm_fitness_modifier=0.8,
        melody_fitness_modifier=1.0,
    ))
    
    # Bridge - Different texture
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=2,
        energy_level=0.4,
        rhythm_fitness_modifier=0.7,
        melody_fitness_modifier=1.0,
    ))
    
    # Fade - Dissolving
    composer.add_section(SectionConfig(
        section_type=SectionType.OUTRO,
        bars=2,
        energy_level=0.15,
        rhythm_fitness_modifier=0.5,
        melody_fitness_modifier=0.9,
    ))
    
    # === SET SONG STRUCTURE ===
    # Ambient: slow arc - emergence, development, peak, resolution
    composer.set_song_structure([
        # Emergence (8 bars)
        SectionType.INTRO,
        SectionType.INTRO,
        SectionType.INTRO,
        SectionType.INTRO,
        # Development 1 (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # First peak (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Descent (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.VERSE,
        # New texture (8 bars)
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        SectionType.BRIDGE,
        # Second peak (8 bars)
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        SectionType.CHORUS,
        # Gradual fade (8 bars)
        SectionType.VERSE,
        SectionType.VERSE,
        SectionType.OUTRO,
        SectionType.OUTRO,
        # Final dissolution (8 bars)
        SectionType.OUTRO,
        SectionType.OUTRO,
        SectionType.OUTRO,
        SectionType.OUTRO,
    ])
    
    # === DEFINE INSTRUMENTS ===
    # Pentatonic scale for ambient consonance - very ethereal
    c_pentatonic = [
        NoteName.C, NoteName.D, NoteName.E, NoteName.G, NoteName.A,
    ]

    print("\n📋 Adding ambient instruments...")
    print("   Note: Ambient uses very sparse rhythms with lots of space")

    # 1. AMBIENT CHORDS - Ethereal sustained pads (one chord per 2 bars)
    print("  🎹 Ambient Chords - Ethereal harmony (1 chord per 2 bars)")
    composer.add_instrument(InstrumentConfig(
        name="ambient_chords",
        instrument="sine",
        beats_per_bar=1,  # One chord per bar = very sustained
        octave_range=(3, 4),
        scale=c_pentatonic,
        is_chord_layer=True,
        notes_per_chord=3,
        allowed_chord_types=["major", "minor", "sus2", "sus4"],
        chord_fitness_fn=AmbientChordFitness(),
        octave_shift=3,
        gain=0.18,
        lpf=2500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
        layer_role="chords",
    ))

    # 2. LOW DRONE - Very sparse, sustained foundation
    print("  🎹 Low Drone - Foundation (very sparse)")
    composer.add_instrument(InstrumentConfig(
        name="low_pad",
        instrument="sawtooth",
        beats_per_bar=4,  # 4 beats but sparse rhythm = few notes
        max_subdivision=1,  # Only single hits, no subdivisions
        octave_range=(2, 3),  # Low register
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=2,
        gain=0.35,
        lpf=1200,  # Very warm
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
        layer_role="bass",
        use_inter_layer_fitness=True,
        inter_layer_weight=0.2,
    ))

    # 3. MID PAD - Sparse harmonic texture
    print("  🎹 Mid Pad - Harmonic texture (sparse)")
    composer.add_instrument(InstrumentConfig(
        name="mid_pad",
        instrument="sine",
        beats_per_bar=4,
        max_subdivision=1,
        octave_range=(4, 5),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=4,
        gain=0.25,
        lpf=3500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
        layer_role="pad",
        use_inter_layer_fitness=True,
        inter_layer_weight=0.2,
    ))

    # 4. HIGH SHIMMER - Occasional ethereal high notes
    print("  ✨ High Shimmer - Ethereal accents (very sparse)")
    composer.add_instrument(InstrumentConfig(
        name="shimmer",
        instrument="triangle",
        beats_per_bar=4,
        max_subdivision=1,  # No subdivisions for ambient
        octave_range=(5, 6),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=5,
        gain=0.15,  # Very soft
        lpf=6000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
        layer_role="lead",
    ))

    # 5. MELODIC VOICE - Floating melody with breathing space
    print("  🎵 Melodic Voice - Floating melody (with space)")
    composer.add_instrument(InstrumentConfig(
        name="melody",
        instrument="sine",
        beats_per_bar=4,
        max_subdivision=1,
        octave_range=(4, 5),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=StableFitness(),
        octave_shift=4,
        gain=0.22,
        lpf=4500,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
        layer_role="melody",
        use_inter_layer_fitness=True,
        inter_layer_weight=0.25,
        use_harmonic_context=True,
        genre="ambient",
        harmony_weight=0.3,
    ))
    
    # No drums for pure ambient - just texture
    
    # === EVOLVE THE SONG ===
    composer.evolve_song(verbose=True)
    
    # === OUTPUT ===
    composer.print_summary()
    
    # Generate Strudel code at 70 BPM (very slow, meditative)
    strudel_code = composer.get_strudel_code(bpm=70)
    strudel_link = composer.get_strudel_link(bpm=70)
    
    print("\n" + "=" * 60)
    print("🌌 STRUDEL CODE")
    print("=" * 60)
    print(strudel_code)
    
    print("\n" + "=" * 60)
    print("🔗 STRUDEL LINK")
    print("=" * 60)
    print(strudel_link)
    
    print("\n" + "=" * 60)
    print("✅ Ambient song generation complete!")
    print("   Click the link above to hear your ambient composition.")
    print("=" * 60)


if __name__ == "__main__":
    main()
