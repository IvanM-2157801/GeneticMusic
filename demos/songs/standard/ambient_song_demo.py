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
    # Pentatonic scale for ambient consonance
    c_pentatonic = [
        NoteName.C, NoteName.D, NoteName.E, NoteName.G, NoteName.A,
    ]
    
    print("\n📋 Adding ambient instruments...")
    
    # 1. AMBIENT CHORDS - Ethereal pads
    print("  🎹 Ambient Chords - Ethereal harmony")
    composer.add_instrument(InstrumentConfig(
        name="ambient_chords",
        instrument="sine",
        beats_per_bar=8,
        octave_range=(3, 4),  # Lower, warmer
        scale=c_pentatonic,
        is_chord_layer=True,
        notes_per_chord=3,  # Simpler voicings
        allowed_chord_types=["major", "minor", "sus2", "sus4"],
        chord_fitness_fn=AmbientChordFitness(),
        octave_shift=3,
        gain=0.15,  # Very quiet, atmospheric
        lpf=3000,  # Warmer
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # 2. PAD 1 - Low drone
    print("  🎹 Low Pad - Foundation drone")
    composer.add_instrument(InstrumentConfig(
        name="low_pad",
        instrument="sawtooth",
        beats_per_bar=8,  # Long notes
        max_subdivision=1,  # Very simple rhythms
        octave_range=(2, 4),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=2,
        gain=0.3,
        lpf=1500,  # Low pass for warmth
        use_scale_degrees=True,
        play_in_sections=[SectionType.INTRO, SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # 2. PAD 2 - Mid-range texture
    print("  🎹 Mid Pad - Harmonic texture")
    composer.add_instrument(InstrumentConfig(
        name="mid_pad",
        instrument="sine",
        beats_per_bar=8,
        max_subdivision=1,
        octave_range=(4, 6),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=4,
        gain=0.3,
        lpf=4000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE, SectionType.OUTRO],
    ))
    
    # 3. HIGH SHIMMER - Ethereal high notes
    print("  ✨ High Shimmer - Ethereal tones")
    composer.add_instrument(InstrumentConfig(
        name="shimmer",
        instrument="triangle",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(5, 7),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=AmbientFitness(),
        octave_shift=6,
        gain=0.2,  # Very soft
        lpf=8000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))
    
    # 4. MELODIC VOICE - Occasional melody
    print("  🎵 Melodic Voice - Floating melody")
    composer.add_instrument(InstrumentConfig(
        name="melody",
        instrument="sine",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(4, 6),
        scale=c_pentatonic,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["ambient"],
        melody_fitness_fn=StableFitness(),  # Smooth movement
        octave_shift=5,
        gain=0.25,
        lpf=5000,
        use_scale_degrees=True,
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS],
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
