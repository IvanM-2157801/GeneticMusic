"""Simple demo - The easiest way to generate music.

Just a few lines to create a complete song!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from song_composer import quick_composer


def main():
    # Create a full song with sensible defaults
    composer = quick_composer(
        scale="d:minor",
        include_melody=True,
        include_bass=True,
        include_chords=True,
        include_drums=True,
        genre="ambient",  # pop has better chord variety than ambient
        fitness_threshold=0.90,  # Higher threshold = better quality
    )

    # Evolve the song
    composer.evolve_song(verbose=True)

    # Print results
    composer.print_summary()
    print("\n" + "=" * 60)
    print("STRUDEL LINK:")
    print(composer.get_strudel_link(bpm=110))


if __name__ == "__main__":
    main()
