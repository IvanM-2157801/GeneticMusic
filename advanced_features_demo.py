"""Advanced Features Demo

This demo showcases all the new features implemented:
1. Harmonic Progression with Chord-Aware Melody Evolution
2. Song Structure with Pre-defined Forms
3. Enhanced Inter-Layer Fitness (30% weight)
4. Dynamic/Expressive Evolution (gain + filter envelopes)
5. Musical Development (theme and variations)

Run this demo to hear the new capabilities in action!
"""

from layered_composer import LayeredComposer, LayerConfig, LAYER_ROLE_PRIORITY
from song_composer import (
    SongComposer, SongForm, SectionType, SectionConfig,
    InstrumentConfig, SONG_FORM_TEMPLATES,
)
from core.music import NoteName
from fitness.genres import PopFitness, JazzFitness
from fitness.melody_types import MelodicFitness, StableFitness
from fitness.rhythm import pop_rhythm_fitness, jazz_rhythm_fitness, bass_rhythm_fitness
from fitness.drums import kick_pattern_fitness, hihat_pattern_fitness, snare_pattern_fitness
from fitness.chords import PopChordFitness, JazzChordFitness
from fitness.development import VariationFitness, create_variation_fitness
from core.genome_ops import create_variation, phrase_similarity


def demo_harmonic_context():
    """Demo 1: Harmonic Context with Chord-Aware Melody Evolution

    This demonstrates how melodies are evolved to fit the underlying
    chord progression, with genre-specific strictness.
    """
    print("\n" + "=" * 70)
    print("DEMO 1: HARMONIC CONTEXT - CHORD-AWARE MELODY EVOLUTION")
    print("=" * 70)
    print("\nThis demo evolves a chord progression first, then evolves melodies")
    print("that respect the underlying harmony with genre-specific strictness.")
    print("\nPop genre uses strict chord-melody relationship (0.8 strictness)")
    print("Jazz genre uses flexible chord-melody relationship (0.4 strictness)")

    # Create composer with harmonic context enabled
    composer = LayeredComposer(
        population_size=15,
        mutation_rate=0.25,
        rhythm_generations=15,
        melody_generations=20,
        chord_generations=15,
        use_context=True,
        use_harmonic_context=True,
    )

    # Add chord layer first (will be evolved first due to role priority)
    composer.add_layer(LayerConfig(
        name="Chords",
        instrument="piano",
        bars=2,
        beats_per_bar=4,
        is_chord_layer=True,
        num_chords=4,
        notes_per_chord=3,
        chord_fitness_fn=PopChordFitness(),
        layer_role="chords",
        gain=0.4,
        lpf=6000,
        octave_shift=0,
    ))

    # Add melody that will be aware of chords
    composer.add_layer(LayerConfig(
        name="Melody",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(4, 6),
        rhythm_fitness_fn=pop_rhythm_fitness,
        melody_fitness_fn=PopFitness(),
        layer_role="melody",
        genre="pop",  # Strict chord-melody relationship
        harmony_weight=0.4,
        use_harmonic_context=True,
        gain=0.5,
        lpf=8000,
    ))

    # Add bass (also chord-aware)
    composer.add_layer(LayerConfig(
        name="Bass",
        instrument="bass",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(2, 3),
        rhythm_fitness_fn=bass_rhythm_fitness,
        melody_fitness_fn=StableFitness(),
        layer_role="bass",
        genre="pop",
        harmony_weight=0.5,  # Bass follows chords closely
        use_harmonic_context=True,
        gain=0.6,
        lpf=3000,
        octave_shift=7,
    ))

    # Evolve all layers
    print("\nEvolving layers with harmonic context...")
    composer.evolve_all_layers(verbose=True)

    # Get composition
    composition = composer.get_composition(bpm=120, random_scale=True)

    print("\n" + "-" * 50)
    print("STRUDEL OUTPUT:")
    print("-" * 50)
    print(composition.to_strudel())
    print("\n" + "-" * 50)
    print("STRUDEL LINK:")
    print(composition.to_strudel_link())

    return composition


def demo_song_structure():
    """Demo 2: Song Structure with Pre-defined Forms

    This demonstrates using pre-defined song forms to create
    complete songs with intro, verse, chorus, bridge, outro.
    """
    print("\n" + "=" * 70)
    print("DEMO 2: SONG STRUCTURE - PRE-DEFINED FORMS")
    print("=" * 70)
    print("\nThis demo uses the POP_STANDARD song form to create a complete song")
    print("with proper section structure: Intro → Verse → Chorus → Bridge → Outro")

    # Show available song forms
    print("\nAvailable song forms:")
    for form in SongForm:
        templates = SONG_FORM_TEMPLATES.get(form)
        if templates:
            sections = [t.section_type.value for t in templates]
            print(f"  {form.value}: {' → '.join(sections)}")

    # Create song composer
    song = SongComposer(
        population_size=12,
        mutation_rate=0.25,
        rhythm_generations=10,
        melody_generations=15,
        chord_generations=10,
    )

    # Use pre-defined pop form (simplified for demo)
    song.use_song_form(SongForm.VERSE_CHORUS)

    # Add instruments
    song.add_instrument(InstrumentConfig(
        name="Lead",
        instrument="sawtooth",
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(4, 5),
        rhythm_fitness_fn=pop_rhythm_fitness,
        melody_fitness_fn=PopFitness(),
        gain=0.5,
        lpf=8000,
    ))

    song.add_instrument(InstrumentConfig(
        name="Kick",
        instrument="bd",
        beats_per_bar=4,
        max_subdivision=2,
        is_drum=True,
        drum_sound="bd",
        rhythm_fitness_fn=kick_pattern_fitness,
        gain=0.8,
    ))

    song.add_instrument(InstrumentConfig(
        name="Hihat",
        instrument="hh",
        beats_per_bar=4,
        max_subdivision=3,
        is_drum=True,
        drum_sound="hh",
        rhythm_fitness_fn=hihat_pattern_fitness,
        gain=0.4,
    ))

    # Evolve the song
    print("\nEvolving song sections...")
    song.evolve_song(verbose=True)

    # Print summary and get code
    song.print_summary()

    strudel_code = song.get_strudel_code(bpm=120)
    print("\n" + "-" * 50)
    print("STRUDEL CODE:")
    print("-" * 50)
    print(strudel_code)
    print("\n" + "-" * 50)
    print("STRUDEL LINK:")
    print(song.get_strudel_link(bpm=120))

    return song


def demo_inter_layer_fitness():
    """Demo 3: Enhanced Inter-Layer Fitness

    This demonstrates how layers are evolved to complement each other
    with 30% weight for inter-layer fitness including:
    - Voice leading (avoid parallel fifths/octaves)
    - Rhythmic compatibility (call-and-response patterns)
    - Bass-melody harmonic support
    """
    print("\n" + "=" * 70)
    print("DEMO 3: INTER-LAYER FITNESS - COORDINATED ARRANGEMENTS")
    print("=" * 70)
    print("\nThis demo shows how layers evolve to complement each other:")
    print("- Voice leading between melodic parts")
    print("- Call-and-response rhythmic patterns")
    print("- Bass supporting melody harmonically")
    print("\nEvolution order: Drums → Bass → Melody → Pad")

    composer = LayeredComposer(
        population_size=15,
        mutation_rate=0.25,
        rhythm_generations=15,
        melody_generations=20,
        use_context=True,  # Enable inter-layer fitness
    )

    # Add layers in any order - they'll be sorted by role priority
    composer.add_layer(LayerConfig(
        name="Melody",
        instrument="piano",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(4, 5),
        rhythm_fitness_fn=pop_rhythm_fitness,
        melody_fitness_fn=MelodicFitness(),
        layer_role="melody",  # Will be evolved 3rd
        gain=0.5,
        lpf=8000,
    ))

    composer.add_layer(LayerConfig(
        name="Bass",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(2, 3),
        rhythm_fitness_fn=bass_rhythm_fitness,
        melody_fitness_fn=StableFitness(),
        layer_role="bass",  # Will be evolved 2nd
        gain=0.6,
        lpf=3000,
        octave_shift=7,
    ))

    composer.add_layer(LayerConfig(
        name="Pad",
        instrument="square",
        bars=2,
        beats_per_bar=4,
        max_subdivision=1,  # Slower moving
        octave_range=(3, 4),
        rhythm_fitness_fn=pop_rhythm_fitness,
        melody_fitness_fn=StableFitness(),
        layer_role="pad",  # Will be evolved 4th
        gain=0.3,
        lpf=5000,
    ))

    composer.add_layer(LayerConfig(
        name="Kick",
        instrument="bd",
        bars=2,
        beats_per_bar=4,
        is_drum=True,
        drum_sound="bd",
        rhythm_fitness_fn=kick_pattern_fitness,
        layer_role="drums",  # Will be evolved 1st
        gain=0.8,
    ))

    # Evolve with inter-layer awareness
    print("\nEvolving with inter-layer fitness (30% weight)...")
    composer.evolve_all_layers(verbose=True)

    composition = composer.get_composition(bpm=110)

    print("\n" + "-" * 50)
    print("STRUDEL OUTPUT:")
    print("-" * 50)
    print(composition.to_strudel())
    print("\n" + "-" * 50)
    print("STRUDEL LINK:")
    print(composition.to_strudel_link())

    return composition


def demo_dynamics():
    """Demo 4: Dynamic Envelopes

    This demonstrates section-based dynamics with different
    gain and filter settings for each section type.
    """
    print("\n" + "=" * 70)
    print("DEMO 4: DYNAMIC ENVELOPES")
    print("=" * 70)
    print("\nThis demo shows how dynamics vary by section:")
    print("- INTRO: Quiet (0.3-0.5 gain), filtered (2000-4000 Hz)")
    print("- VERSE: Moderate (0.5-0.7 gain), open (3000-6000 Hz)")
    print("- CHORUS: Loud (0.8-1.0 gain), bright (6000-10000 Hz)")
    print("- OUTRO: Fade out (0.5→0.2 gain)")

    from core.music import DynamicEnvelope, FilterEnvelope
    from song_composer import SECTION_DYNAMICS

    print("\nDefault section dynamics:")
    for section_type, dynamics in SECTION_DYNAMICS.items():
        gain = dynamics["gain"]
        lpf = dynamics["lpf"]
        print(f"  {section_type.value:12s}: gain={gain[0]:.1f}→{gain[1]:.1f}, lpf={lpf[0]}→{lpf[1]} Hz")

    # Create example envelopes for a buildup section
    print("\nExample: BUILDUP section envelope")
    buildup_gain = DynamicEnvelope(points=[(0.0, 0.4), (0.5, 0.6), (1.0, 0.9)])
    buildup_lpf = FilterEnvelope(points=[(0.0, 2000), (0.5, 5000), (1.0, 10000)])

    print(f"  Gain envelope: {buildup_gain.points}")
    print(f"  Strudel gain: {buildup_gain.to_strudel()}")
    print(f"  Filter envelope: {buildup_lpf.points}")
    print(f"  Strudel lpf: {buildup_lpf.to_strudel()}")


def demo_musical_development():
    """Demo 5: Musical Development (Theme and Variations)

    This demonstrates creating variations of a theme with
    controlled similarity and musical interest.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: MUSICAL DEVELOPMENT - THEME AND VARIATIONS")
    print("=" * 70)
    print("\nThis demo shows how to create variations of a theme:")
    print("- Melodic variation: Keep rhythm, change pitches")
    print("- Rhythmic variation: Keep pitches, change rhythm")
    print("- Ornamental: Add passing tones and embellishments")
    print("- Inversion: Flip intervals around pivot note")
    print("- Retrograde: Reverse note order")

    # Create a simple theme
    from core.music import Phrase, Note

    theme = Phrase([
        Note(NoteName.C, octave=4, duration=1.0),
        Note(NoteName.E, octave=4, duration=0.5),
        Note(NoteName.G, octave=4, duration=0.5),
        Note(NoteName.E, octave=4, duration=1.0),
        Note(NoteName.D, octave=4, duration=0.5),
        Note(NoteName.C, octave=4, duration=1.5),
    ])

    print(f"\nOriginal theme: {theme.to_strudel()}")

    # Create variations
    variation_types = ["melodic", "rhythmic", "ornamental", "inversion", "retrograde"]

    for var_type in variation_types:
        variation = create_variation(theme, variation_type=var_type)
        similarity = phrase_similarity(theme, variation)
        print(f"\n{var_type.capitalize()} variation (similarity: {similarity:.2f}):")
        print(f"  {variation.to_strudel()}")

    # Demonstrate variation fitness
    print("\n" + "-" * 50)
    print("Variation Fitness Evaluation:")
    print("-" * 50)

    from core.music import Layer

    # Create fitness with target similarity of 0.6
    var_fitness = create_variation_fitness(
        theme=theme,
        similarity_target=0.6,
    )

    for var_type in variation_types:
        variation = create_variation(theme, variation_type=var_type)
        layer = Layer(name="test", phrases=[variation])
        fitness = var_fitness.evaluate(layer)
        similarity = phrase_similarity(theme, variation)
        print(f"  {var_type:12s}: similarity={similarity:.2f}, fitness={fitness:.2f}")


def main():
    """Run all demos."""
    print("\n" + "#" * 70)
    print("# GENETICMUSIC ADVANCED FEATURES DEMO")
    print("# " + "-" * 66)
    print("# This demo showcases all new features implemented:")
    print("# 1. Harmonic Progression with Chord-Aware Melody Evolution")
    print("# 2. Song Structure with Pre-defined Forms")
    print("# 3. Enhanced Inter-Layer Fitness (30% weight)")
    print("# 4. Dynamic/Expressive Evolution")
    print("# 5. Musical Development (Theme and Variations)")
    print("#" * 70)

    # Run demos
    demo_harmonic_context()
    demo_song_structure()
    demo_inter_layer_fitness()
    demo_dynamics()
    demo_musical_development()

    print("\n" + "=" * 70)
    print("ALL DEMOS COMPLETE!")
    print("=" * 70)
    print("\nYou can copy any of the Strudel links above and paste them into")
    print("your browser to hear the generated music at https://strudel.cc")


if __name__ == "__main__":
    main()
