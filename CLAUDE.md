# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GeneticMusic is a genetic algorithm-based music composition system that evolves musical patterns and melodies. The project uses evolutionary computation to generate complete musical compositions with multiple layers (melody, bass, synth, drums) that adhere to genre-specific fitness criteria.

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
- **Scale Degree System**: Supports both absolute note names and scale degrees (0-7)
- **Drum Support**: Layers can be melodic (using `n()`) or drum (using `sound()`)
- `Phrase.to_strudel_with_rhythm()`: Preserves rhythm structure in output
- `Layer.to_strudel()`: Builds complete Strudel expression with effects (scale, gain, lpf)
- `Composition.random_scale()`: Generates random scales for harmonic consistency

**Genome Operations (`core/genome_ops.py`)**
- Two genome types:
  1. **Rhythm genome**: string where each char = subdivisions per beat ('0'=rest, '1'=quarter, '2'=eighth, '3'=triplet, '4'=sixteenth)
  2. **Phrase genome**: `Phrase` object with list of `Note` objects
- Key functions:
  - `rhythm_to_phrase()`: converts rhythm pattern to Phrase with random pitches
  - `phrase_with_rhythm()`: applies rhythm to existing phrase while preserving pitches
  - Mutation/crossover operations for both rhythm and phrase genomes

**Fitness Functions (`fitness/`)**

*Base Classes:*
- `FitnessFunction`: Abstract base with `evaluate(layer: Layer) -> float` (returns 0.0-1.0)

*Rhythm Fitness (`fitness/rhythm.py`):*
- Genre-specific rhythm evaluation functions
- `RHYTHM_FITNESS_FUNCTIONS` registry: pop, jazz, funk, bass, drum
- Metrics: complexity, density, syncopation, groove, rest_ratio, consistency

*Drum Fitness (`fitness/drums.py`):*
- Specialized fitness for drum patterns
- `DRUM_FITNESS_FUNCTIONS` registry: kick, hihat, snare, percussion
- **kick**: Strong beats (1 & 5), sparse, powerful
- **hihat**: High density, consistent, steady
- **snare**: Backbeat emphasis (3 & 7), sparse accents
- **percussion**: Moderate density, adds texture

*Melody Fitness (`fitness/melody_types.py`):*
- `MelodicFitness`: Varied intervals, wide range, expressive (for lead melodies)
- `StableFitness`: Smooth intervals, narrow range, supportive (for synth pads)

*Genre Fitness (`fitness/genres.py`):*
- `PopFitness`: Major scale adherence, smooth intervals, fewer rests
- `JazzFitness`: Note variety, chromatic movement, syncopation
- `BluesFitness`: Blues scale, "blue note" ratios (b3, b5, b7)
- `AmbientFitness`: Long notes, slow movement, sparse arrangement

### Two-Phase Evolution System (`layered_composer.py`)

The `LayeredComposer` class implements two-phase evolution for each layer:

1. **Phase 1: Rhythm Evolution**
   - Evolves rhythm string genome using genre-specific fitness
   - Uses genetic algorithm to find optimal rhythm patterns
   - For drums: this is the only phase needed
   - For melodic instruments: rhythm becomes fixed for phase 2

2. **Phase 2: Melody Evolution**
   - Takes fixed rhythm from Phase 1
   - Evolves pitch/melody using melody-specific fitness
   - Preserves rhythm structure via `phrase_with_rhythm()`
   - **Skipped for drum layers** (drums only need rhythm)

**LayerConfig**: Defines layer properties
- Basic: name, instrument, bars, beats_per_bar, max_subdivision
- Melodic: octave_range, scale, melody_fitness_fn
- Rhythm: rhythm_fitness_fn
- Strudel: strudel_scale, octave_shift, gain, lpf, use_scale_degrees
- Drum: is_drum, drum_sound

**Key Methods:**
- `add_layer(config)`: Add a layer to the composition
- `evolve_layer_rhythm(config)`: Evolve rhythm for a single layer
- `evolve_layer_melody(config, rhythm)`: Evolve melody with fixed rhythm
- `evolve_all_layers()`: Evolve all layers sequentially
- `get_composition(bpm, random_scale)`: Generate final composition
- `print_summary()`: Display evolved patterns with analysis

### Strudel Integration

- All compositions export to Strudel.cc with base64-encoded URLs
- **Melodic layers** output: `n("5 [5 1 2] 0").sub(7).scale("c:minor").s("sawtooth").gain(0.3).lpf(8000)`
- **Drum layers** output: `sound("bd ~ ~ ~ bd").gain(0.8)`
- Rhythm structure preserved using grouping: `[note1 note2]` for multiple notes per beat
- Random scale selection ensures harmonic consistency across melodic layers

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
# Quick 2-layer demo (melody + bass)
python quick_demo.py

# Drum beat demo (kick, hihat, snare, open hihat)
python drum_demo.py

# Full band demo (melody, synth, bass, 3 drum layers)
python full_band_demo.py

# Melodic synth demo (melodic vs stable fitness)
python melodic_synth_demo.py
```

### Code Formatting

```bash
# Format code with black
black .

# Format specific file
black layered_composer.py
```

## Key Design Patterns

**Generic Genome Types**: The genetic algorithm is genome-agnostic via Python generics. Rhythm phase uses `Individual[str]` for rhythm strings, melody phase uses `Individual[Phrase]` for musical phrases.

**Two-Phase Evolution**: Separating rhythm and pitch evolution reduces search space complexity and allows for more targeted optimization. Drums skip the melody phase entirely.

**Rhythm Preservation**: When evolving melodies, `phrase_with_rhythm()` ensures mutations/crossovers maintain the evolved rhythm structure by re-applying the rhythm pattern after each genetic operation.

**Scale Degree System**: Using scale degrees (0-7) instead of absolute pitches enables harmonic consistency across layers through random scale selection, and produces cleaner Strudel notation.

**Fitness Function Composition**: Genre fitness functions combine multiple weighted metrics (scale adherence, interval smoothness, rhythmic variety, etc.) to guide evolution toward style-specific musical characteristics.

**Drum Sound Notation**: Drum layers use `sound()` notation in Strudel with sound names (bd, hh, sd, oh) instead of `n()` with pitches, providing proper drum machine behavior.

**Strudel Export Pipeline**: All music objects implement `to_strudel()` for seamless export to the Strudel live coding environment, enabling instant preview of evolved music.

## Rhythm Encoding

Rhythm patterns are strings where each character represents subdivisions per beat:
- `'0'` = rest
- `'1'` = quarter note (1 hit per beat)
- `'2'` = eighth notes (2 hits per beat)
- `'3'` = triplets (3 hits per beat)
- `'4'` = sixteenth notes (4 hits per beat)

**Example**: Rhythm `"2103"` with notes `[A, B, C, D, E, F]` becomes:
```
[A B] C ~ [D E F]
```
- Beat 1 (2 notes): `[A B]`
- Beat 2 (1 note): `C`
- Beat 3 (rest): `~`
- Beat 4 (3 notes): `[D E F]`

## Scale Degree System

Instead of absolute note names (c4, d5), the system uses scale degrees (0-7) that map to the current scale:

**Example in C major**: 0=C, 1=D, 2=E, 3=F, 4=G, 5=A, 6=B, 7=C(octave)

**Example in B major**: 0=B, 1=C#, 2=D#, 3=E, 4=F#, 5=G#, 6=A#, 7=B(octave)

**Strudel output**:
```javascript
n("5 [5 1 2] 0 [5 2 4]")
  .sub(7)              // Transpose down 7 semitones
  .scale("b:major")    // Use B major scale
  .s("sawtooth")       // Sawtooth wave synth
  .gain(0.3)          // Volume at 30%
  .lpf(8000)          // Low-pass filter at 8000 Hz
```

See `SCALE_DEGREES_GUIDE.md` for detailed documentation.

## Drum System

Drum layers differ from melodic layers:
- Use `is_drum=True` in LayerConfig
- Specify `drum_sound` (e.g., "bd", "hh", "sd", "oh")
- Only evolve rhythm (skip melody phase)
- Output uses `sound()` instead of `n()`

**Common drum sounds**:
- `bd` = bass drum (kick)
- `hh` = hi-hat (closed)
- `sd` = snare drum
- `oh` = open hi-hat
- `cp` = clap
- `rim` = rim shot

**Example drum output**:
```javascript
sound("bd ~ ~ ~ bd ~ bd ~").gain(0.8)
sound("[hh hh] [hh hh] [hh hh] [hh hh]").gain(0.5)
sound("~ ~ sd ~ ~ ~ sd ~").gain(0.7)
```

## Important Notes

- The project separates rhythm and pitch evolution to reduce search space complexity
- Drum layers only evolve rhythm; melodic layers evolve both rhythm and melody
- All melodic layers in a composition share the same random scale for harmonic consistency
- Rhythm structure is preserved in Strudel output using beat grouping
- Evolution parameters are configurable: `population_size`, `mutation_rate`, `elitism_count`, `rhythm_generations`, `melody_generations`
- Default parameters in demos: population=20, mutation=0.25, elitism=6, rhythm_gens=25, melody_gens=30
