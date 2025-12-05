## Scale Degrees & Random Scale System

### Overview

The system now uses **scale degrees (0-7)** instead of absolute note names, with random scale selection and proper Strudel effects.

### Key Features

✅ **Scale degrees (0-7)** instead of note names (c4, d5, etc.)
✅ **Random scale selection** (e.g., "b:major", "g:minor")
✅ **Octave transposition** with `.sub(7)`
✅ **Effects**: gain and lpf (low-pass filter)
✅ **Rhythm structure** preserved in output
✅ **Melodic vs Stable** fitness functions

### Output Format

**Before (old system):**
```javascript
$: n("[d2 c3 d2 c2]").s("sawtooth")
```

**After (new system):**
```javascript
$: n("5 [5 1 2] 0 [5 2 4]").sub(7).scale("b:major").s("sawtooth").gain(0.3).lpf(8000)
```

### Breaking Down the Strudel Output

```javascript
$: n("5 [5 1 2] 0 [5 2 4] [2 0 2] 0 [4 4 4] 0")
   .sub(7)                    // Transpose down 7 semitones (1 octave)
   .scale("b:major")          // Use B major scale
   .s("sawtooth")             // Sawtooth wave synth
   .gain(0.3)                 // Volume at 30%
   .lpf(8000)                 // Low-pass filter at 8000 Hz
```

### Scale Degrees Explained

Numbers **0-7** represent scale degrees:
- In **C major**: 0=C, 1=D, 2=E, 3=F, 4=G, 5=A, 6=B, 7=C(octave)
- In **B major**: 0=B, 1=C#, 2=D#, 3=E, 4=F#, 5=G#, 6=A#, 7=B(octave)
- In **G minor**: 0=G, 1=A, 2=Bb, 3=C, 4=D, 5=Eb, 6=F, 7=G(octave)

The `.scale()` function in Strudel automatically maps these degrees to the correct notes!

### Random Scale Selection

Each composition gets a random scale:

**Possible scales:**
- Roots: c, d, e, f, g, a, b
- Modes: major, minor

**Examples:**
- `"c:major"` - C major
- `"g:minor"` - G minor
- `"b:major"` - B major
- `"e:minor"` - E minor

### Octave Transposition

The `.sub(N)` function transposes down by N semitones:
- `.sub(7)` = down 7 semitones (≈ 1 octave in a scale)
- `.sub(0)` = no transposition
- Negative values would use `.add(N)` instead

### Fitness Functions

#### MelodicFitness (for melodic lines)
**Characteristics:**
- Large intervals (jumps, leaps)
- High note variety
- Wide pitch range
- Expressive, attention-grabbing

**Example output:**
```javascript
n("5 [5 1 2] 0 [5 2 4]")  // Notice varied scale degrees
```

#### StableFitness (for synth pads)
**Characteristics:**
- Small intervals (stepwise motion)
- High smoothness
- Narrow pitch range
- Supportive, background

**Example output:**
```javascript
n("[5 0] 0 [2 4] 4")  // Notice smoother progression
```

### Complete Example

**Melody (Melodic):**
```javascript
$: n("5 [5 1 2] 0 [5 2 4] [2 0 2] 0")
   .sub(7)
   .scale("b:major")
   .s("sawtooth")
   .gain(0.3)
   .lpf(8000)
```
- Rhythm: "13133131" → `5` `[5 1 2]` `0` `[5 2 4]` etc.
- Scale degrees: varied (5, 1, 2, 0, 4)
- Transposed up with .sub(7)
- Bright sound (lpf=8000)

**Synth (Stable):**
```javascript
$: n("[5 0] 0 [2 4] 4 [0 6] 2")
   .scale("b:major")
   .s("triangle")
   .gain(0.2)
   .lpf(2000)
```
- Rhythm: "21212121" → `[5 0]` `0` `[2 4]` `4` etc.
- Scale degrees: smoother progression
- No transposition
- Warm sound (lpf=2000)

### Configuration Parameters

In `LayerConfig`:

```python
LayerConfig(
    name="melody",
    instrument="sawtooth",
    # Strudel parameters
    strudel_scale="",          # Empty = use random
    octave_shift=7,            # .sub(7) in Strudel
    gain=0.3,                  # Volume 0.0-1.0
    lpf=8000,                  # Filter frequency in Hz
    use_scale_degrees=True,    # Use 0-7 instead of note names
    # Evolution parameters
    rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],
    melody_fitness_fn=MelodicFitness(),
)
```

### Usage Example

```bash
python melodic_synth_demo.py
```

**Output:**
```javascript
setcpm(30.0)

$: n("5 [5 1 2] 0 [5 2 4] [2 0 2] 0 [4 4 4] 0")
   .sub(7).scale("b:major").s("sawtooth").gain(0.3).lpf(8000)

$: n("[5 0] 0 [2 4] 4 [0 6] 2 [2 0] 0")
   .scale("b:major").s("triangle").gain(0.2).lpf(2000)
```

### Benefits

1. **Harmonic Consistency** - All layers use the same random scale
2. **Clean Notation** - Scale degrees easier to read than absolute notes
3. **Flexible Transposition** - Easy octave shifting with .sub()
4. **Musical Results** - MelodicFitness creates expressive leads
5. **Supportive Background** - StableFitness creates smooth pads
6. **Full Control** - Gain and LPF for sound design

### Layer Types

| Layer Type | Fitness | Characteristics | Use Case |
|-----------|---------|-----------------|----------|
| **Melodic** | MelodicFitness | Varied intervals, wide range | Lead melody, solos |
| **Stable** | StableFitness | Smooth intervals, narrow range | Pads, accompaniment |
| **Drums** | PopFitness | Consistent, dense | Percussion |
| **Bass** | PopFitness | Groovy, moderate | Bass line |

### Testing

**Test scale degree encoding:**
```bash
python test_rhythm_encoding.py
```

**Test melodic + stable:**
```bash
python melodic_synth_demo.py
```

**Test with drums:**
```bash
python band_demo.py
```

### Rhythm Structure Still Preserved!

Even with scale degrees, rhythm structure is maintained:

**Rhythm:** `"2103"`
**Notes:** `[C, D, E, F, G, A]` (scale degrees: `[0, 2, 4, 5, 0, 2]`)
**Output:** `[0 2] 4 ~ [5 0 2]`

- Beat 1 (2 notes): `[0 2]`
- Beat 2 (1 note): `4`
- Beat 3 (rest): `~`
- Beat 4 (3 notes): `[5 0 2]`

Perfect! ✨
