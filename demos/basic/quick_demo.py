"""Quick demo - generates a simple 2-layer composition."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.genres import PopFitness
from core.music import NoteName

# Simple C major scale
c_major = [
    NoteName.C,
    NoteName.D,
    NoteName.E,
    NoteName.F,
    NoteName.G,
    NoteName.A,
    NoteName.B,
]

# Create composer
composer = LayeredComposer(
    population_size=10,
    rhythm_generations=15,
    melody_generations=20,
)

# Add melody layer
composer.add_layer(
    LayerConfig(
        name="melody",
        instrument="piano",
        bars=2,
        beats_per_bar=4,
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=PopFitness(),
    )
)

# Add bass layer
composer.add_layer(
    LayerConfig(
        name="bass",
        instrument="sawtooth",
        bars=2,
        beats_per_bar=4,
        octave_range=(2, 3),
        max_subdivision=2,
        scale=c_major,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
        melody_fitness_fn=PopFitness(),
    )
)

# Evolve
print("Evolving composition...")
composer.evolve_all_layers(verbose=False)
composer.print_summary()

# Generate Strudel URL
composition = composer.get_composition(bpm=120)
encoded = base64.b64encode(composition.to_strudel().encode("utf-8")).decode("utf-8")
print(f"\n🎵 Strudel URL:\nhttps://strudel.cc/#{encoded}\n")
