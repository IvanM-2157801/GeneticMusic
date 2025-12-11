"""Full features demo - Showcasing all new capabilities.

This demo demonstrates:
1. Theme variations (melody varies between sections)
2. Dynamic envelope evolution (gain/filter automation)
3. Inter-layer fitness (instruments complement each other)
4. Simplified preset functions
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from song_composer import (
    SongComposer,
    SectionConfig,
    SectionType,
    InstrumentConfig,
    create_melody,
    create_bass,
    create_pad,
    create_chords,
    create_kick,
    create_snare,
    create_hihat,
    create_open_hihat,
)
from fitness.melody_types import MelodicFitness
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS


def main():
    print("=" * 60)
    print("FULL FEATURES DEMO")
    print("Demonstrating: variations, dynamics, inter-layer fitness")
    print("=" * 60)

    composer = SongComposer(
        population_size=40,
        mutation_rate=0.25,
        fitness_threshold=0.62,
        max_generations=60,
    )

    # Song structure with varied energy
    composer.add_section(SectionConfig(
        section_type=SectionType.INTRO,
        bars=4,
        energy_level=0.3,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.VERSE,
        bars=8,
        energy_level=0.5,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.CHORUS,
        bars=8,
        energy_level=0.8,
    ))
    composer.add_section(SectionConfig(
        section_type=SectionType.BRIDGE,
        bars=4,
        energy_level=0.4,
    ))

    composer.set_song_structure([
        SectionType.INTRO,
        SectionType.VERSE,
        SectionType.CHORUS,
        SectionType.VERSE,
        SectionType.CHORUS,
        SectionType.BRIDGE,
        SectionType.CHORUS,
    ])

    # Chords - foundation for harmony
    composer.add_instrument(create_chords(
        scale="a:minor",
        genre="pop",
        beats_per_bar=1,  # Whole note chords
        notes_per_chord=4,
        gain=0.35,
    ))

    # Drums - full kit
    composer.add_instrument(create_kick(gain=0.65))
    composer.add_instrument(create_snare(gain=0.55))
    composer.add_instrument(create_hihat(gain=0.35))
    composer.add_instrument(create_open_hihat(
        gain=0.25,
        play_in_sections=[SectionType.CHORUS],  # Only in chorus
    ))

    # Bass - supportive
    composer.add_instrument(create_bass(
        scale="a:minor",
        gain=0.5,
    ))

    # Pad - atmospheric, with variations
    composer.add_instrument(create_pad(
        scale="a:minor",
        gain=0.2,
        use_variations=True,  # Will vary between sections
        play_in_sections=[SectionType.VERSE, SectionType.CHORUS, SectionType.BRIDGE],
    ))

    # Lead melody - with variations and dynamic evolution
    composer.add_instrument(InstrumentConfig(
        name="lead",
        instrument="square",
        beats_per_bar=4,
        max_subdivision=3,
        octave_range=(5, 7),
        scale="a:minor",
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS.get("pop"),
        melody_fitness_fn=MelodicFitness(),
        gain=0.4,
        lpf=8000,
        layer_role="lead",
        use_variations=True,  # Melody varies between sections
        variation_similarity=0.55,  # 55% similar to theme
        evolve_dynamics=True,  # Evolve gain/filter envelopes
        play_in_sections=[SectionType.CHORUS, SectionType.BRIDGE],
    ))

    # Evolve!
    composer.evolve_song(verbose=True)
    composer.print_summary()

    print("\n" + "=" * 60)
    print("STRUDEL LINK:")
    print(composer.get_strudel_link(bpm=128))


if __name__ == "__main__":
    main()
