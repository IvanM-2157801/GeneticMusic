"""Quick band demo - faster generation for testing."""
import base64
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.genres import PopFitness
from core.music import NoteName


# Quick settings for fast generation
composer = LayeredComposer(
    population_size=15,
    rhythm_generations=20,
    melody_generations=20,
)

c_major = [NoteName.C, NoteName.D, NoteName.E, NoteName.G, NoteName.A]

# Drums
composer.add_layer(LayerConfig(
    name="drums",
    instrument="sawtooth",
    bars=2,
    beats_per_bar=4,
    max_subdivision=4,
    octave_range=(2, 3),
    scale=[NoteName.C, NoteName.D],
    rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["drum"],
    melody_fitness_fn=PopFitness(),
))

# Bass
composer.add_layer(LayerConfig(
    name="bass",
    instrument="sawtooth",
    bars=2,
    beats_per_bar=4,
    max_subdivision=2,
    octave_range=(2, 3),
    scale=c_major,
    rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["bass"],
    melody_fitness_fn=PopFitness(),
))

# Piano
composer.add_layer(LayerConfig(
    name="piano",
    instrument="piano",
    bars=2,
    beats_per_bar=4,
    max_subdivision=3,
    octave_range=(4, 5),
    scale=c_major,
    rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
    melody_fitness_fn=PopFitness(),
))

print("🎵 Evolving your band...")
composer.evolve_all_layers(verbose=False)
composer.print_summary()

composition = composer.get_composition(bpm=120)
encoded = base64.b64encode(composition.to_strudel().encode('utf-8')).decode('utf-8')
print(f"\n🎹 Strudel URL:\nhttps://strudel.cc/#{encoded}\n")
