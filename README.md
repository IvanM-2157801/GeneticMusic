# GeneticMusic 🎵

A genetic algorithm-based music composition system that evolves musical patterns and melodies. Generate complete musical compositions with drums, melody, bass, and synth layers using evolutionary computation.

## Features

- **Two-Phase Evolution**: Separate rhythm and melody evolution for each layer
- **Genre-Specific Fitness**: Pop, jazz, funk, bass, and drum-specific fitness functions
- **Scale Degree System**: Uses scale degrees (0-7) with random scale selection
- **Drum System**: Multiple drum layers with specialized fitness functions
- **Strudel Export**: Generates playable URLs for the Strudel live coding environment

## Quick Start

```bash
# Enter development environment
nix develop

# Run drum demo
python drum_demo.py

# Run full band demo (drums + melodic instruments)
python full_band_demo.py

# Run ambient demo (sustained chords and simple melodies)
python ambient_demo.py

# Run metal demo (heavy guitars, power chords, double bass)
python metal_demo.py

# Run melodic synth demo (shows melodic vs stable fitness)
python melodic_synth_demo.py

# Run quick demo (simple 2-layer composition)
python quick_demo.py
```

## Architecture

### Core Components

- **`core/genetic.py`**: Generic genetic algorithm implementation
- **`core/music.py`**: Music data model (Note, Phrase, Layer, Composition)
- **`core/genome_ops.py`**: Rhythm and phrase genome operations
- **`layered_composer.py`**: Main composer with two-phase evolution

### Fitness Functions

- **`fitness/rhythm.py`**: Genre-specific rhythm fitness (pop, jazz, funk, bass, drum)
- **`fitness/drums.py`**: Drum-specific fitness (kick, hihat, snare, percussion)
- **`fitness/melody_types.py`**: Melodic vs stable fitness for different instrument roles
- **`fitness/genres.py`**: Genre-specific melody fitness (pop, jazz, blues, ambient)

## Usage

### Creating a Melodic Layer

```python
from layered_composer import LayeredComposer, LayerConfig
from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS
from fitness.melody_types import MelodicFitness
from core.music import NoteName

composer = LayeredComposer(
    population_size=20,
    rhythm_generations=25,
    melody_generations=30,
)

c_major = [NoteName.C, NoteName.D, NoteName.E, NoteName.F,
           NoteName.G, NoteName.A, NoteName.B]

composer.add_layer(LayerConfig(
    name="melody",
    instrument="sawtooth",
    bars=2,
    beats_per_bar=4,
    max_subdivision=3,
    octave_range=(4, 6),
    scale=c_major,
    rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
    melody_fitness_fn=MelodicFitness(),
    octave_shift=7,  # Transpose up (.sub(7) in Strudel)
    gain=0.3,
    lpf=8000,
    use_scale_degrees=True
))
```

### Creating a Drum Layer

```python
from fitness.drums import DRUM_FITNESS_FUNCTIONS

composer.add_layer(LayerConfig(
    name="kick",
    instrument="bd",
    bars=2,
    beats_per_bar=4,
    max_subdivision=2,
    rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS["kick"],
    is_drum=True,
    drum_sound="bd",
    gain=0.8,
))
```

### Evolving and Exporting

```python
import base64

# Evolve all layers
composer.evolve_all_layers(verbose=True)

# Generate composition with random scale
composition = composer.get_composition(bpm=120, random_scale=True)

# Create Strudel URL
strudel_code = composition.to_strudel()
encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')
url = f"https://strudel.cc/#{encoded}"
print(f"🎵 Strudel URL: {url}")
```

## Output Examples

### Melodic Layer (Scale Degrees)

```javascript
$: n("5 [5 1 2] 0 [5 2 4]")
   .sub(7)
   .scale("b:major")
   .s("sawtooth")
   .gain(0.3)
   .lpf(8000)
```

- Uses scale degrees 0-7
- Random scale selection (e.g., "b:major")
- Octave transposition with `.sub(7)`
- Customizable gain and low-pass filter

### Chord Layer (Comma-Separated Notes)

```javascript
$: n("[0, 2] [5, 2] ~ [0, 4]")
   .scale("b:minor")
   .s("piano")
   .gain(0.4)
   .lpf(4000)
```

- Uses comma separation `[0, 2]` for parallel notes (chords)
- Notes play simultaneously in Strudel
- Great for piano, pads, and sustained harmonies
- Enable with `chord_mode=True` in LayerConfig

### Drum Layer (Sound Notation)

```javascript
$: sound("bd ~ ~ ~ bd ~ bd ~").gain(0.8)
$: sound("[hh hh] [hh hh] [hh hh] [hh hh]").gain(0.5)
$: sound("~ ~ sd ~ ~ ~ sd ~").gain(0.7)
```

- Uses `sound()` instead of `n()`
- Drum sound names: bd (kick), hh (hi-hat), sd (snare), oh (open hi-hat)
- Rhythm structure preserved with grouping

## Rhythm Encoding

Rhythm patterns are encoded as strings where each character represents subdivisions per beat:

- `'0'` = rest
- `'1'` = quarter note (1 hit)
- `'2'` = eighth notes (2 hits)
- `'3'` = triplets (3 hits)
- `'4'` = sixteenth notes (4 hits)

**Example**: `"2103"` becomes `[note1 note2] note3 ~ [note4 note5 note6]`

## Fitness Functions

### Rhythm Fitness

| Function | Characteristics | Use Case |
|----------|----------------|----------|
| **pop** | Consistent, catchy, moderate density | Pop/rock music |
| **jazz** | Complex, syncopated, varied | Jazz compositions |
| **funk** | Groovy, syncopated, moderate-high density | Funk/groove music |
| **bass** | Consistent, low complexity, supportive | Bass lines |
| **drum** | High density, consistent, driving | General drums |

### Drum Fitness

| Function | Characteristics | Use Case |
|----------|----------------|----------|
| **kick** | Strong beats (1 & 5), sparse, powerful | Bass drum |
| **hihat** | High density, consistent, steady | Hi-hat |
| **snare** | Backbeat emphasis (3 & 7), sparse | Snare drum |
| **percussion** | Moderate density, adds texture | Shakers, tambourine |

### Melody Fitness

| Function | Characteristics | Use Case |
|----------|----------------|----------|
| **MelodicFitness** | Varied intervals, wide range, expressive | Lead melody |
| **StableFitness** | Smooth intervals, narrow range, supportive | Synth pads |
| **ChordFitness** | Triadic intervals, sustained, harmonious | Piano chords, pads |
| **PopFitness** | Major scale, smooth intervals, consistent | Pop melodies |
| **JazzFitness** | Note variety, chromatic, syncopated | Jazz solos |

## Layer Configuration Parameters

```python
LayerConfig(
    name="layer_name",          # Layer identifier
    instrument="sawtooth",      # Strudel instrument
    bars=2,                     # Number of bars
    beats_per_bar=4,            # Beats per bar (time signature)
    max_subdivision=3,          # Max rhythm subdivision (1-4)
    octave_range=(4, 6),        # Pitch range for melody
    scale=[NoteName.C, ...],    # Scale for evolution
    rhythm_fitness_fn=...,      # Rhythm fitness function
    melody_fitness_fn=...,      # Melody fitness function
    # Strudel output parameters
    strudel_scale="",           # Empty = random scale
    octave_shift=7,             # Octave transposition
    gain=0.3,                   # Volume (0.0-1.0)
    lpf=8000,                   # Low-pass filter (Hz)
    use_scale_degrees=True,     # Use 0-7 degrees
    chord_mode=False,           # True for comma-separated notes (chords)
    # Drum parameters
    is_drum=False,              # True for drum layers
    drum_sound="bd",            # Drum sound name
)
```

## Demos

### drum_demo.py
Complete drum beat with kick, hi-hat, snare, and open hi-hat layers.

### full_band_demo.py
Complete band with melody, synth pad, bass, and three drum layers.

### ambient_demo.py
Ambient composition with sustained chords (using chord_mode) and simple melodies.
Demonstrates ChordFitness and comma-separated note notation.

### metal_demo.py
Heavy metal composition with distorted guitars, power chords, and aggressive drums.
Features drop tuning (.sub), double bass patterns, and low-pass filtering for tone shaping.

### melodic_synth_demo.py
Shows difference between melodic (varied) and stable (smooth) fitness functions.

### quick_demo.py
Simple 2-layer composition (melody + bass) for quick testing.

## Genetic Algorithm Parameters

```python
LayeredComposer(
    population_size=20,      # Size of each population
    mutation_rate=0.25,      # Probability of mutation
    elitism_count=6,         # Number of elite individuals preserved
    rhythm_generations=25,   # Generations for rhythm evolution
    melody_generations=30,   # Generations for melody evolution
)
```

## Tone Shaping with Effects

The system provides several parameters for shaping the tone of each layer:

### Octave Transposition (octave_shift)
- **Positive values**: Transpose down (e.g., `octave_shift=7` → `.sub(7)`)
- **Negative values**: Transpose up (e.g., `octave_shift=-7` → `.add(7)`)
- **Drop tuning**: Use `octave_shift=-12` or `-24` for heavy, low sounds

### Low-Pass Filter (lpf)
Controls the brightness/darkness of the sound:
- **500-800 Hz**: Deep, rumbling bass / chunky rhythm guitar
- **1000-2000 Hz**: Warm, mellow pads / smooth bass
- **3000-4000 Hz**: Balanced, present melodies
- **6000-8000 Hz**: Bright, cutting leads / hi-fi sounds

### Gain (volume)
- **0.2-0.4**: Background elements, pads
- **0.5-0.7**: Normal melodic elements, drums
- **0.8-0.9**: Powerful, upfront sounds (kick drums, lead guitar)

### Instrument Waveforms
- **sawtooth**: Rich, full sound - great for bass, pads, distorted guitar
- **square**: Hollow, aggressive - great for leads, power chords
- **triangle**: Soft, mellow - great for subtle pads, background
- **piano**: Acoustic piano sound
- **sine**: Pure, smooth - great for sub-bass, pads

### Example Configurations

**Heavy Metal Rhythm Guitar:**
```python
instrument="sawtooth"
octave_shift=-12  # Drop tuning
gain=0.6
lpf=800  # Chunky, palm-muted tone
chord_mode=True  # Power chords
```

**Cutting Lead Guitar:**
```python
instrument="square"
octave_shift=0  # Standard pitch
gain=0.4
lpf=3000  # Bright, aggressive
```

**Deep Bass:**
```python
instrument="sawtooth"
octave_shift=-24  # Two octaves down
gain=0.7
lpf=500  # Deep rumble
```

**Ambient Pad:**
```python
instrument="triangle"
octave_shift=0
gain=0.2
lpf=2000  # Warm, mellow
chord_mode=True  # Sustained chords
```

## Strudel Integration

All compositions export to [Strudel](https://strudel.cc/), a web-based live coding environment. The system generates base64-encoded URLs that can be opened directly in a browser to hear the evolved music.

## Documentation

- **CLAUDE.md**: Project architecture and design patterns
- **SCALE_DEGREES_GUIDE.md**: Detailed guide on scale degrees system

## Development

```bash
# Format code
black .

# Enter development shell
nix develop
```

## License

See LICENSE file for details.
