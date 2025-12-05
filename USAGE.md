# GeneticMusic Usage Guide

## Overview

GeneticMusic uses genetic algorithms to evolve music compositions layer by layer. Each layer independently evolves a rhythm pattern first, then evolves melodic content based on that rhythm.

## Quick Start

### Running the Main Example

```bash
python main_layered.py
```

This will:
1. Evolve a 3-layer composition (melody, bass, pad)
2. Print evolution progress and fitness scores
3. Generate a Strudel URL for instant playback

### Genre Examples

```bash
# Jazz composition with syncopation
python examples/jazz_layered.py

# Funk composition with groove
python examples/funk_example.py
```

## Architecture

### LayeredComposer

The main class that orchestrates multi-layer evolution:

```python
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.genres import PopFitness

composer = LayeredComposer(
    population_size=15,
    mutation_rate=0.25,
    elitism_count=5,
    rhythm_generations=20,
    melody_generations=30,
)
```

### LayerConfig

Defines a single layer with rhythm and melody properties:

```python
composer.add_layer(LayerConfig(
    name="melody",                                    # Layer identifier
    instrument="piano",                               # Strudel instrument
    bars=2,                                           # Number of bars
    beats_per_bar=4,                                  # Beats per bar
    max_subdivision=4,                                # Max notes per beat
    octave_range=(4, 5),                              # Note octave range
    scale=[NoteName.C, NoteName.D, ...],              # Musical scale
    rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"], # Rhythm evolution
    melody_fitness_fn=PopFitness(),                   # Melody evolution
))
```

## Available Fitness Functions

### Rhythm Fitness (evaluates rhythm strings like "33131313")

- `pop_rhythm_fitness`: Consistent, groovy, moderate density
- `jazz_rhythm_fitness`: Complex, syncopated, varied
- `funk_rhythm_fitness`: Highly syncopated, groovy
- `ambient_rhythm_fitness`: Simple, sparse, slow
- `rock_rhythm_fitness`: Driving, dense, consistent

Access via: `RHYTHM_FITNESS_FUNCTIONS["genre_name"]`

### Melody Fitness (evaluates Phrase/Layer objects)

- `PopFitness`: Major scale, smooth intervals, fewer rests
- `JazzFitness`: Note variety, chromatic movement, syncopation
- `BluesFitness`: Blues scale, blue notes (b3, b5, b7)
- `AmbientFitness`: Long notes, slow movement, sparse

Access via: `PopFitness()`, `JazzFitness()`, etc.

## Creating Custom Fitness Functions

### Custom Rhythm Fitness

```python
def custom_rhythm_fitness(rhythm: str) -> float:
    """Your custom rhythm evaluation (returns 0.0-1.0)."""
    # Example: prefer rhythms with exactly 50% rests
    rest_ratio = rhythm.count('0') / len(rhythm)
    return 1.0 - abs(0.5 - rest_ratio)
```

### Custom Melody Fitness

```python
from fitness.base import FitnessFunction
from core.music import Layer

class CustomFitness(FitnessFunction):
    def evaluate(self, layer: Layer) -> float:
        """Evaluate a layer (returns 0.0-1.0)."""
        phrase = layer.phrases[0]
        # Add your evaluation logic here
        score = 0.0
        # ... calculate score based on phrase properties
        return score
```

## Rhythm Genome Format

Rhythm strings encode subdivisions per beat:
- `'0'` = rest (no notes)
- `'1'` = quarter note (1 note per beat)
- `'2'` = eighth notes (2 notes per beat)
- `'3'` = triplets (3 notes per beat)
- `'4'` = sixteenth notes (4 notes per beat)

Example: `"21312240"` = 8 beats with varied subdivisions

## Strudel Output

The system generates URLs for [Strudel.cc](https://strudel.cc), a web-based live coding environment. Click the generated URL to hear your evolved composition instantly!

## Evolution Process

For each layer:

1. **Phase 1: Rhythm Evolution**
   - Generate random rhythm patterns
   - Evaluate using rhythm fitness function
   - Evolve via selection, crossover, mutation
   - Best rhythm selected after N generations

2. **Phase 2: Melody Evolution**
   - Generate random melodies with the fixed rhythm
   - Evaluate using melody fitness function
   - Mutations preserve rhythm structure
   - Best melody selected after M generations

3. **Composition**
   - All evolved layers combined
   - Exported to Strudel format
   - URL generated for playback

## Future Extensions

### Layer Dependencies

The architecture supports adding layer dependencies:

```python
# Future feature (not yet implemented):
composer.add_layer(LayerConfig(
    name="harmony",
    depends_on=["melody"],  # Evolve harmony based on melody
    fitness_fn=HarmonyFitness(melody_layer),
))
```

### Custom Scales

```python
# Blues scale example
blues_scale = [NoteName.C, NoteName.DS, NoteName.F,
               NoteName.FS, NoteName.G, NoteName.AS]

composer.add_layer(LayerConfig(
    name="blues_lead",
    scale=blues_scale,
    # ... other config
))
```

### Adaptive Fitness

Combine multiple fitness functions dynamically:

```python
def adaptive_fitness(rhythm: str, generation: int) -> float:
    """Change fitness criteria over time."""
    if generation < 10:
        return jazz_rhythm_fitness(rhythm)
    else:
        return funk_rhythm_fitness(rhythm)
```

## Tips

- **Population Size**: Larger = better diversity but slower (15-30 recommended)
- **Mutation Rate**: Higher = more exploration (0.2-0.3 recommended)
- **Elitism**: Keep best individuals (20-30% of population)
- **Generations**: More = better evolution but slower (20-50 recommended)
- **Max Subdivision**: Lower for simpler rhythms (bass=2, melody=4)

## Troubleshooting

**Too many rests?**
- Decrease `rest_ratio` weight in fitness function
- Use rhythm fitness with lower rest preference (e.g., rock, pop)

**Too repetitive?**
- Increase mutation rate
- Use fitness with higher complexity (e.g., jazz)

**Too chaotic?**
- Decrease mutation rate
- Use simpler fitness (e.g., pop, ambient)
- Reduce max_subdivision

**Evolution too slow?**
- Reduce population_size
- Reduce number of generations
- Use fewer layers
