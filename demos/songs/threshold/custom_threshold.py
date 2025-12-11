"""Custom threshold demo - Using simplified instrument presets.

This demo shows how to use the new preset functions for easy song creation.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from song_composer import (
    SongComposer,
    SectionConfig,
    SectionType,
    # Preset functions for easy instrument creation
    create_melody,
    create_bass,
    create_pad,
    create_chords,
    create_kick,
    create_snare,
    create_hihat,
)


def main():
    # Create composer with threshold-based evolution
    composer = SongComposer(
        population_size=50,
        mutation_rate=0.2,
        fitness_threshold=0.65,
        max_generations=80,
    )

    # Define sections
    composer.add_section(SectionConfig(section_type=SectionType.INTRO, bars=4))
    composer.add_section(SectionConfig(section_type=SectionType.VERSE, bars=4))
    composer.add_section(SectionConfig(section_type=SectionType.CHORUS, bars=4))

    composer.set_song_structure([
        SectionType.INTRO,
        SectionType.VERSE,
        SectionType.CHORUS,
        SectionType.VERSE,
        SectionType.CHORUS,
    ])

    # Add instruments using presets - much simpler!
    composer.add_instrument(create_chords(
        scale="c:minor",
        genre="jazz",
        beats_per_bar=2,  # 2 chords per bar
        gain=0.3,
    ))

    composer.add_instrument(create_kick())
    composer.add_instrument(create_snare())
    composer.add_instrument(create_hihat())

    composer.add_instrument(create_bass(scale="c:minor"))

    composer.add_instrument(create_melody(
        scale="c:minor",
        use_variations=True,  # Melody will vary between sections
    ))

    # Evolve and generate
    composer.evolve_song(verbose=True)
    composer.print_summary()

    print("\n" + "=" * 60)
    print("STRUDEL LINK:")
    print(composer.get_strudel_link(bpm=90))


if __name__ == "__main__":
    main()
