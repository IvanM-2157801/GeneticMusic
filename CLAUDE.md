# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GeneticMusic is a genetic algorithm-based music composition system that evolves musical patterns and melodies. The project uses evolutionary computation to generate music that adheres to different genre-specific fitness criteria.

## Architecture

### Core Components

**Genetic Engine (`core/genetic.py`)**
- Generic genetic algorithm implementation using Python generics (TypeVar `T`)
- `GeneticAlgorithm` class handles evolution with configurable population size, mutation rate, and elitism
- `Individual[T]` dataclass represents genome + fitness score
- Uses tournament selection (size=3) for parent selection

**Music Data Model (`core/music.py`)**
- Musical primitives: `NoteName` (enum), `Note`, `Phrase`, `Layer`, `Composition`
- All classes have `to_strudel()` methods to export to Strudel web-based music notation
- Notes track pitch, octave, and duration (in beats)
- `midi_pitch` property converts Note to MIDI pitch number

**Genome Operations (`core/genome_ops.py`)**
- Two genome types:
  1. **Rhythm genome**: string where each char = subdivisions per beat ('0'=rest, '1'=quarter, '2'=eighth, '3'=triplet, '4'=sixteenth)
  2. **Phrase genome**: `Phrase` object with list of `Note` objects
- Key functions:
  - `rhythm_to_phrase()`: converts rhythm pattern to Phrase with random pitches
  - `phrase_with_rhythm()`: applies rhythm to existing phrase while preserving pitches
  - Mutation/crossover operations for both rhythm and phrase genomes

**Fitness Functions (`fitness/`)**
- Abstract base class `FitnessFunction` with `evaluate(layer: Layer) -> float` (returns 0.0-1.0)
- Genre-specific implementations:
  - `PopFitness`: major scale adherence, smooth intervals, fewer rests
  - `JazzFitness`: note variety, chromatic movement, syncopation
  - `BluesFitness`: blues scale, "blue note" ratios (b3, b5, b7)
  - `AmbientFitness`: long notes, slow movement, sparse arrangement
- Utility functions: `note_variety()`, `interval_smoothness()`, `rest_ratio()`, etc.

### Two-Phase Evolution System (`main.py`)

The main script implements a two-phase interactive evolution:

1. **Phase 1: Rhythm Evolution**
   - User evaluates rhythm patterns (1-6 rating)
   - Evolves rhythm string genome
   - Outputs Strudel preview URLs for listening
   - Continues until fitness ≥ 6

2. **Phase 2: Melody Evolution**
   - Takes fixed rhythm from Phase 1
   - Evolves pitch/melody using `PopFitness` (automated)
   - Preserves rhythm structure via `phrase_with_rhythm()`
   - Continues until fitness ≥ 0.95

### Multi-Layer Composition (`composer.py`)

**Important**: This file is currently stored as binary/encoded data and needs decoding to be used.

The `Composer` class orchestrates parallel evolution of multiple musical layers (melody, bass, pads, etc.) with:
- `LayerConfig`: defines layer properties (instrument, phrase count/length, octave range, fitness function)
- Independent populations per layer, evolved in parallel
- `get_best_composition()`: combines best individual from each layer into a `Composition`

### Strudel Integration (`strudel.py`)

- `create_strudel()`: generates Strudel.cc URLs with base64-encoded music patterns
- Strudel is a web-based live coding environment for music
- URLs allow instant preview/playback of evolved patterns

## Development Commands

### Environment Setup

This project uses Nix flakes for reproducible development environments:

```bash
# Enter development shell (automatically creates/activates venv)
nix develop

# Or use direnv (if .envrc is set up)
direnv allow
```

The Nix flake provides:
- Python 3.11
- libsndfile, pkg-config, portaudio (for audio processing)
- Platform-specific dependencies (pipewire on Linux, gcc/stdenv)

### Running the Project

```bash
# Main two-phase interactive evolution
python main.py

# Example: N-Queens genetic algorithm (unrelated to music)
python aildih.py

# Jazz composition example (requires fixing composer.py encoding first)
python examples/jazz_example.py
```

### Testing

```bash
# Run tests (test.py is currently a stub)
python test.py
```

### Code Formatting

```bash
# Format code with black
black .

# Format specific file
black main.py
```

## Key Design Patterns

**Generic Genome Types**: The genetic algorithm is genome-agnostic via Python generics. Phase 1 uses `Individual[str]` for rhythms, Phase 2 uses `Individual[Phrase]` for melodies.

**Rhythm Preservation**: When evolving melodies in Phase 2, `phrase_with_rhythm()` ensures mutations/crossovers maintain the user-selected rhythm structure by re-applying the rhythm pattern after each genetic operation.

**Fitness Function Composition**: Genre fitness functions combine multiple weighted metrics (scale adherence, interval smoothness, rhythmic variety, etc.) to guide evolution toward style-specific musical characteristics.

**Strudel Export Pipeline**: All music objects implement `to_strudel()` for seamless export to the Strudel live coding environment, enabling instant preview of evolved music.

## Important Notes

- The project separates rhythm and pitch evolution to reduce search space complexity
- User fitness in Phase 1 enables subjective preference, while Phase 2 uses automated genre-specific fitness
- `composer.py` appears corrupted/encoded - decode before using multi-layer composition features
- Constants in `main.py` control evolution parameters: `POPULATION_SIZE=10`, `MUTATION_RATE=0.25`, `ELITISM_COUNT=6`
