# Slipknot-Style Metal Composition Guide

## Overview

The `demo_slipknot.py` file has been completely redesigned to generate aggressive nu-metal/groove metal compositions inspired by **Slipknot**. This guide explains the instrumentation, fitness functions, and how to customize the metal sound.

## Slipknot Sound Profile

### Core Instruments
1. **Dual Rhythm Guitars** - Down-tuned power chords (Drop C/D tuning)
2. **Lead Guitar** - Higher register for solos and fills
3. **Bass** - Heavy, groovy, follows chord progression with intensity
4. **Drums** - Complex polyrhythms (kick, snare, hi-hat)
5. **Keyboards/Samples** - DJ elements and texture (in the chord layer)

### Key Characteristics
- **Tuning**: Drop C/D (very low, heavy)
- **BPM**: 50-70 (slow but powerful, creates weight)
- **Dynamics**: Extreme contrasts (quiet verses → explosive choruses)
- **Effects**: High distortion, minimal reverb (tight, dry sound)
- **Rhythm**: Syncopated, polyrhythmic, chaotic but controlled
- **Harmony**: Dark, minor-based, power chords
- **Density**: Aggressive, relentless, minimal silence

## Fitness Functions for Metal

### 1. **Metal Rhythm Fitness** (`make_metal_rhythm_fitness`)

Optimizes rhythms for aggressive metal feel with HIGH density and syncopation.

```python
make_metal_rhythm_fitness({
    "groove": 0.3,          # Some groove but aggressive
    "syncopation": 0.4,     # Unpredictable, chaotic feel
    "density": 0.6,         # HEAVY - aggressive, no space
    "complexity": 0.2,      # Interesting fills
    "consistency": 0.1,     # Some repetition
})
```

**Key Features**:
- **Density**: High (0.5-0.7) = aggressive, relentless playing
- **Syncopation**: High (0.4-0.5) = unpredictable, unhinged
- **Groove**: Lower than dance music but still present for pocket
- **No rest penalty** = aggressive, continuous playing
- **Chorus uses max density** (0.7) for explosion effect

### 2. **Metal Melody Fitness** (`make_metal_melody_fitness`)

Optimizes melodies for power chords and aggressive riffs.

```python
make_metal_melody_fitness({
    "variety": 0.4,         # Riff variety
    "smoothness": -0.1,     # Allow jumps (power chords jump)
    "scale": 0.6,           # Dark, dissonant feel
    "rests": -0.8,          # AGGRESSIVE penalty for silence
}, scale=MINOR_SCALE)
```

**Key Features**:
- **Rest Penalty**: MAXIMUM (-0.8 to -0.9) = almost no silence
- **Scale Adherence**: High (0.5-0.6) = dark, in-key aggression
- **Smoothness**: Negative = allows power chord jumps
- **Variety**: Medium (0.4-0.7) = interesting riffs
- **Dark Scale**: MINOR_SCALE for evil tone

### 3. **Metal Chord Fitness** (`make_metal_chord_fitness`)

Optimizes harmony for dark, heavy power chord progressions.

```python
make_metal_chord_fitness({
    "functional": 0.5,      # Functional harmony (I, IV, V)
    "smooth": 0.3,          # Smooth root movement
    "variety": 0.1,         # Limited variety (simple = heavy)
    "types": 0.1,           # Mostly triads (power chords)
})
```

**Key Features**:
- **Functional Harmony**: High = strong I-IV-V progressions
- **Triads Focus**: Emphasis on simple major/minor triads
- **Root Motion**: Smooth movements for bass following
- **Limited Variety**: Heavy = simple, repeated progressions

### 4. **Metal Drum Fitness** (`make_metal_drum_fitness`)

Separate fitness for kick, snare, and hi-hat with different roles.

**Kick Drum** (downbeat anchor):
```python
{
    "strong_beat": 0.6,     # Hits on beats 1 & 5
    "density": 0.3,         # Some extra aggression
    "consistency": 0.1,     # Repeating pattern
}
```

**Snare** (backbeat crisp):
```python
{
    "backbeat": 0.7,        # Sharp hits on 2 & 4
    "density": 0.2,         # Occasional double hits
    "simple": 0.1,          # Mostly single hits
}
```

**Hi-Hat** (relentless pocket):
```python
{
    "density": 0.7,         # VERY BUSY - relentless
    "consistency": 0.2,     # Steady pattern
    "offbeat": 0.1,         # Some feel
}
```

## Layer Configuration

### Layer Roles and Settings

#### Rhythm Guitars (2x)
```
name: rhythm_guitar_1/2
instrument: square/triangle (aggressive timbres)
octave_range: (2, 3) - LOWER for heaviness
beat_resolution: 8 beats - riff control
rhythm_fn: verse_rhythm_metal (high syncopation)
melody_fn: verse_guitar_metal (power chords, heavy)
gain: 0.75-0.8 - MAXIMUM for aggression
lpf: 300-350 - LOW cutoff for distorted tone
postgain: 1.4-1.5 - crushing
context: verse (rhythmic lock)
```

#### Lead Guitar
```
name: lead_guitar
instrument: sawtooth (presence)
octave_range: (3, 4) - higher for cuts through
beat_resolution: 16 beats - fast riffs
rhythm_fn: chorus_rhythm_metal (maximum density/syncopation)
melody_fn: chorus_guitar_metal (very aggressive)
gain: 0.7 - clear but not dominating
lpf: 400 - slightly higher for presence
context: chorus (explosive)
```

#### Bass
```
name: bass
instrument: sine (pure sub-bass)
octave_range: (1, 2) - EXTREMELY LOW
beat_resolution: 4 beats - groove pocket
rhythm_fn: bass_rhythm_metal (groove + density)
gain: 0.9 - high presence
lpf: 150 - VERY LOW for sub frequencies
postgain: 1.8 - MAXIMUM punch
room: 0.0 - NO reverb (tight)
```

#### Drums
```
kick: bd drum, 8 beats, gain=1.0 (MAXIMUM)
snare: sd drum, 8 beats, gain=0.9
hihat: hh drum, 16 beats, gain=0.6
all: gain values create proper drum mix
```

#### Chords (Harmonic Foundation)
```
name: chords
instrument: pulse (harmonic texture)
is_chord_layer: true
num_chords: 4 - simple progressions
allowed_chord_types: [major, minor] - power chords
gain: 0.4 - background role
lpf: 250 - dark, bassy
```

## Configuration Parameters

### BPM & Timing
```python
BPM = 65                    # Slipknot tempo (50-70 range)
BARS = 1
BEATS_PER_BAR = 4          # Standard 4/4 time
```

### Evolution Settings
```python
POPULATION_SIZE = 16       # Smaller for chaos
MUTATION_RATE = 0.3        # Higher for chaotic feel
ELITISM_COUNT = 2          # Keep best patterns
RHYTHM_GENERATIONS = 20    # Quick evolution
MELODY_GENERATIONS = 20
CHORD_GENERATIONS = 15
```

### Effects Settings

**Gain Strategy**:
- Guitars: 0.7-0.8 (high but not maxed)
- Bass: 0.9 (present and heavy)
- Kick: 1.0 (MAXIMUM punch)
- Snare: 0.9 (loud, cutting)
- Hi-hat: 0.6 (balanced)
- Chords: 0.4 (background)

**Low-Pass Filter (lpf)** - Controls distortion character:
- Kick: Not specified (full range)
- Hi-hat: Not specified (full range)
- Guitars: 300-400 Hz (distorted, aggressive)
- Bass: 150 Hz (sub-bass only)
- Chords: 250 Hz (dark, bassy)

**Reverb (room)**:
- All: 0.0-0.2 (MINIMAL, tight dry sound)
- Vocals would be 0.1-0.3 max
- NO ambient reverb like clean channels

**Post-Gain (postgain)** - Final crushing:
- Bass: 1.8 (maximum punch)
- Guitars: 1.4-1.6 (heavy distortion)
- Chords: default (1.0)

## Song Arrangement

The demo creates a Slipknot-style structure:

```
[VERSE] ──────────── 2 bars
[VERSE] ──────────── 2 bars
[CHORUS EXPLOSION] ─ 2 bars (more syncopated, dense)
[CHORUS EXPLOSION] ─ 2 bars
[VERSE] ──────────── 2 bars (contrast back to groove)
[CHORUS EXPLOSION] ─ 2 bars (final peak)
```

## Customization Guide

### For More Aggressive Sound
```python
# Increase density everywhere
verse_rhythm_metal = make_metal_rhythm_fitness({
    "density": 0.8,         # Was 0.6
    "syncopation": 0.5,     # Was 0.4
})

# Penalize rests MORE
verse_guitar_metal = make_metal_melody_fitness({
    "rests": -0.95,         # Was -0.8 (almost NO silence)
})

# Increase gain/postgain
gain=0.85, postgain=1.7     # Crushing distortion
```

### For More Groovy/Rhythmic
```python
# Increase groove metric
verse_rhythm_metal = make_metal_rhythm_fitness({
    "groove": 0.6,          # Was 0.3
    "density": 0.4,         # Was 0.6 (less dense)
    "syncopation": 0.2,     # Was 0.4 (less chaotic)
})
```

### For Different Tuning (Simulate Drop D)
```python
# Use lower octave ranges
octave_range=(1, 2)         # Was (2, 3) - one octave lower
base_octave=1               # Was 2

# Lower LPF for heavier tone
lpf=250                     # Was 300-350
```

### To Add Clean Sections
```python
# Create a "clean_verse" context group
# Use higher LPF (600+), lower gain (0.4), more reverb (0.5)
# Contrast with heavy chorus
```

## Metal Genre Best Practices

1. **Density Over Clarity**: Metal values relentless playing over note clarity
2. **Syncopation Creates Tension**: Offbeat rhythms keep listeners unsettled
3. **Low Frequencies Are Heavy**: Sub-bass (1-2 octaves) creates weight
4. **Minimal Reverb = Tight**: Professional metal is dry and controlled
5. **Power Chords Are Simple**: Don't overomplicate harmony
6. **Drums Drive Everything**: Complex polyrhythms are essential
7. **Dynamics Matter**: Quiet verses make loud choruses MORE impactful
8. **Rest Penalties**: Silence is the enemy in aggressive metal

## Advanced: Custom Fitness Functions

To create specialized fitness for specific metal subgenres:

```python
# Thrash Metal (extreme density/speed)
def make_thrash_fitness(weights):
    # Maximum syncopation, maximum density
    # Minimal consistency (chaotic)
    
# Doom Metal (slow, heavy)
def make_doom_fitness(weights):
    # Lower syncopation (predictable)
    # MAXIMUM density (note volume)
    # Lower BPM (30-50)
    
# Prog Metal (complex harmony)
def make_prog_fitness(weights):
    # Higher chord variety
    # Complex time signatures
    # Diverse rhythm patterns
```

## References

- **Slipknot Key Albums**: Iowa (2001), All Hope Is Gone (2008), We Are Not Your Kind (2019)
- **Signature Techniques**: 
  - Down-tuned power chords (Mick Thomson, Jim Root)
  - Complex drum polyrhythms (Joey Jordison style)
  - Aggressive hi-hat patterns for pocket
  - Heavy sub-bass foundation (Paul Gray)
  - Syncopated rhythmic tension throughout

## Running the Demo

```bash
python demo_slipknot.py
```

This generates a complete Slipknot-inspired composition and outputs a Strudel live code link that you can open in your browser to hear the result in real-time.

---

**Enjoy creating heavy metal music!** 🤘
