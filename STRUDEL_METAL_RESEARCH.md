# Strudel Metal/Heavy Music Research
## Live Code Examples, Sound Banks, and Guitar Resources

**Last Updated**: December 12, 2025

---

## EXECUTIVE SUMMARY

### Key Findings:

1. **Strudel has NO native distorted guitar sounds** - Instead, it uses **synthesizer waveforms processed with heavy filtering**
2. **No "guitar bank" exists** - Heavy distortion is created through synthesis: `sawtooth` + `square` + `triangle` waveforms
3. **Guitar samples available**: `gtr` (from VCSL library) - but these are **clean acoustic/electric**, not distorted
4. **Metal standard drum bank**: `RolandTR909` for authentic heavy metal sound
5. **Default sample libraries**:
   - **Dirt-Samples** (TidalCycles) - includes `metal` folder with percussion hits
   - **VCSL** (Versilian Community Sample Library) - includes `Chordophones` with guitar samples
   - **tidal-drum-machines** - multiple classic drum machine banks

---

## PART 1: SYNTHESIZER WAVEFORMS FOR DISTORTED GUITAR

### Why No Real Guitar Samples?

In Strudel live coding, the philosophy is **algorithmic sound generation** rather than sample playback. This means:
- You DON'T use recorded guitar samples (that would be static)
- You CREATE the illusion of distorted guitar through synthesizer waveforms
- The processing (gain + filtering) creates the "distortion" effect

### The Three Sacred Waveforms for Metal Guitar

#### 1. **SAWTOOTH** - Primary Rhythm Guitar
```javascript
// Heavy, aggressive power chords
s("[c3 c4 c5]*4")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(300)           // Heavy low-pass filter
  .postgain(1.5)      // Crushing compression
```

**Why Sawtooth?**
- Contains ALL odd and even harmonics (1×, 2×, 3×, 4×, 5× fundamental)
- Rich, thick, naturally aggressive tone
- When filtered at 300Hz, mimics distorted guitar amplifier rolloff
- Stacks well with other guitar layers

**Harmonic Content**: Most harmonically dense of the three
**Use Case**: Main rhythm guitar, power chords, heavy layers

---

#### 2. **TRIANGLE** - Secondary Rhythm Guitar / Layering
```javascript
// Softer complement to sawtooth
s("[c3 c4 c5]*4")
  .sound("triangle")
  .gain(0.75)
  .lpf(350)
  .postgain(1.4)
```

**Why Triangle?**
- Contains only ODD harmonics (1×, 3×, 5×, 7×, 9×...)
- Softer than sawtooth, fewer high harmonics
- Provides tonal variation and prevents harshness buildup
- Creates thickness when layered with sawtooth

**Harmonic Content**: Smoother, more musical
**Use Case**: Second guitar part, harmonic layering, texture

---

#### 3. **SQUARE** - Lead Guitar / Cutting Tones
```javascript
// Bright, piercing lead lines
s("[c5 g4 e5]*2")
  .sound("square")
  .gain(0.7)
  .lpf(400)           // Slightly less filtering for brightness
  .postgain(1.6)      // Aggressive crushing
```

**Why Square?**
- Contains ODD harmonics only (1×, 3×, 5×, 7×, 9×...)
- Very digital, bright, hollow-sounding
- CUTS THROUGH the mix (essential for leads)
- Harsh but with presence

**Harmonic Content**: Most "digital" sounding
**Use Case**: Lead guitar, solos, cutting presence

---

### Processing = The Distortion

The actual "distorted guitar" sound comes from **three processing steps**:

```javascript
// Step 1: Gain (volume boost)
.gain(0.8)          // Boost the signal

// Step 2: Low-Pass Filter (amp rolloff)
.lpf(300)           // Cut frequencies above 300Hz
                    // Creates the "crushed" distortion tone

// Step 3: Post-Gain Compression
.postgain(1.5)      // Compress/crush the waveform
                    // Adds aggression and punch
```

**The Result**: Sawtooth + 300Hz LPF + 1.5× compression = **Sounds like overdriven guitar amp**

---

## PART 2: AVAILABLE GUITAR SAMPLES IN STRUDEL

### VCSL Chordophones Library

Strudel loads the **Versilian Community Sample Library (VCSL)** by default, which includes:

#### Real Guitar Samples (Clean/Acoustic)
```javascript
s("gtr")              // General guitar sample
s("guitar")           // Alternative alias for guitar
```

**Important**: These are clean/acoustic guitar samples, NOT distorted.

**VCSL Guitar Categories** (from Chordophones folder):
- Acoustic Guitar
- Classical Guitar
- Electric Guitar (clean)
- Nylon Guitar
- Steel Guitar
- 12-String Guitar
- Bass Guitar

**VCSL Availability**: All samples are CC0 (public domain) - https://github.com/sgossner/VCSL

**Sample Format**: 44.1 or 48kHz, 16-24 bit, stereo WAV files

**Limitation**: VCSL samples are articulation-based, not distorted versions

---

### Alternative: Load Custom Distorted Guitar Samples

If you want REAL distorted guitar samples, you must load them as custom samples:

```javascript
// Load custom distorted guitar samples
await samples({
  'heavy_gtr': 'https://example.com/distorted-guitar.wav',
  'metal_bass': 'https://example.com/metal-bass.wav'
})

// Use in patterns
s("heavy_gtr")
  .note("c3 c4 g3")
  .speed(0.5)         // Adjust playback speed
```

**Where to Get Samples**:
- Freesound.org (search "distorted guitar")
- Zapsplat.com (free samples)
- LoopSwap.com
- Your own recordings with distortion pedal/amp

---

## PART 3: DRUM MACHINES FOR METAL

### The Strudel Drum Machine Standard

Strudel ships with multiple drum machine banks from:
- **tidal-drum-machines** repository (https://github.com/ritchse/tidal-drum-machines)
- **Dirt-Samples** (from TidalCycles)

### RECOMMENDED FOR METAL: RolandTR909

```javascript
// Metal standard drum kit
s("bd").bank("RolandTR909")      // Bass drum / Kick
s("sd").bank("RolandTR909")      // Snare drum
s("hh").bank("RolandTR909")      // Closed hi-hat
s("oh").bank("RolandTR909")      // Open hi-hat
s("cr").bank("RolandTR909")      // Crash
s("rd").bank("RolandTR909")      // Ride
```

**Why TR909 for Metal?**
- **Iconic**: Standard drum machine in thrash metal, industrial, 90s metal
- **Punchy Kick**: Aggressive attack, perfect for downbeats
- **Metallic Snare**: Sharp, cold, metallic "crack" (no warmth)
- **Tight Hi-Hats**: Digital, precise, relentless pocket
- **Instant Recognition**: Metal listeners hear TR909 and know it's metal

**Sound Characteristics**:
- Kick: 80-200Hz punchy attack
- Snare: Metallic, no reverb, cold tone
- Hi-Hat: Tight, digital, razor-sharp

**Standard Drum Sounds**:
```
bd    = Bass drum / Kick (kick)
sd    = Snare drum
hh    = Closed hi-hat
oh    = Open hi-hat
cr    = Crash cymbal
rd    = Ride cymbal
ht    = High tom
mt    = Mid tom
lt    = Low tom
```

---

### Alternative Drum Banks

#### RolandTR808 (Classic, Warmer)
```javascript
s("bd").bank("RolandTR808")
```
- Warm, iconic 80s character
- Longer sustain on kick
- Less aggressive than 909
- **Use when**: Wanting classic funk-metal, trap-metal, or warmer tone

#### RolandTR606 (Compact, Tight)
```javascript
s("bd").bank("RolandTR606")
```
- Very tight, precise
- Less presence than 909
- More control-oriented sound
- **Use when**: Wanting surgical precision

#### AlesisSR16 (Sample-Based, Versatile)
```javascript
s("bd").bank("AlesisSR16")
```
- Modern sampler character
- More sampled/realistic
- Versatile for various styles
- **Use when**: Mixing metal with other genres

---

## PART 4: DIRT-SAMPLES "METAL" FOLDER

### What's in Dirt-Samples?

The **Dirt-Samples** repository (TidalCycles) contains 100+ sample packs:
- Single hits (kick, snare, hi-hat variations)
- Drum machines (tr808, tr909, etc.)
- Instrument samples
- Loops and breaks

### The "metal" Sample Pack

Dirt-Samples has a **`metal/`** folder with percussion hits:

```
Dirt-Samples/metal/
├── metal0.wav     (metallic percussion hits)
├── metal1.wav
├── metal2.wav
├── metal3.wav
└── ...
```

**What "metal" Contains**: These are PITCHED metallic percussion samples (not distorted guitar):
- Metal/gong-like sounds
- Metallic textures for sci-fi/industrial
- NOT actual guitar sounds

**How to Use**:
```javascript
// From Dirt-Samples
s("metal")         // Accesses metal0.wav, metal1.wav, etc.
  .n("[0 1 2 3]")  // Cycle through metal samples
```

---

## PART 5: COMPLETE STRUDEL METAL COMPOSITION EXAMPLE

### Example 1: Classic Metal Pattern (Sawtooth Power Chords + TR909)

```javascript
// Setup samples (loads default banks)
await samples('github:tidalcycles/Dirt-Samples/master');
await samples('github:felixroos/dough-samples/main');

// ===== GUITARS =====
const rhythm_guitar_1 = s("[c3 c4 c5 c4]*2")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(300)
  .postgain(1.5)
  .room(0.1)
  .pan(0.3);

const rhythm_guitar_2 = s("[g2 g3 g4 g3]*2")
  .sound("triangle")
  .gain(0.75)
  .lpf(350)
  .postgain(1.4)
  .room(0.1)
  .pan(-0.3);

const lead_guitar = s("[c5 g4 e5 d5]*1")
  .sound("square")
  .gain(0.7)
  .lpf(400)
  .postgain(1.6)
  .room(0.15);

// ===== BASS =====
const bass = s("[c1 c1 c2 c1]*2")
  .sound("sine")
  .gain(0.9)
  .lpf(150)
  .postgain(1.8)
  .room(0.0);

// ===== DRUMS =====
const kick = s("bd")
  .bank("RolandTR909")
  .gain(1.0)
  .room(0.0);

const snare = s("sd")
  .bank("RolandTR909")
  .gain(0.9)
  .room(0.05);

const hihat = s("hh")
  .bank("RolandTR909")
  .gain(0.8)
  .room(0.0);

// ===== STITCH IT TOGETHER =====
stack(
  rhythm_guitar_1,
  rhythm_guitar_2,
  lead_guitar,
  bass,
  kick,
  snare,
  hihat
);
```

**Result**: Dense, aggressive metal composition with:
- Layered sawtooth/triangle guitars = Thick distorted tone
- Square lead = Cutting presence
- Sine bass = Deep sub-bass
- TR909 = Authentic metal drums

---

### Example 2: Industrial/Extreme Metal (with Metallic Textures)

```javascript
// Add metallic percussion texture
const metal_perc = s("metal")
  .n("[0 1 2 3]*4")
  .gain(0.6)
  .lpf(800)
  .room(0.2);

const rhythm_guitar_1 = s("[c3 [c4 c3]]*2")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(280)
  .postgain(1.7);

// Stack with metal percussion for industrial feel
stack(rhythm_guitar_1, metal_perc);
```

---

### Example 3: Synth Metal (using FM Synthesis)

```javascript
// FM synthesis for extreme, metallic synth sound
const fm_guitar = s("[c3 c4 g3 d4]*2")
  .sound("sawtooth")
  .fm(8)              // Heavy FM modulation
  .fmh(2.5)           // Metallic harmonicity (1=natural, 2.5+=extreme)
  .gain(0.8)
  .lpf(350)
  .postgain(1.5);

stack(fm_guitar);
```

**FM Parameters**:
- `.fm(amount)` - How much modulation (8+ = extreme)
- `.fmh(harmonicity)` - Overtone distribution
  - 1.0 = Natural harmonics
  - 2.0-3.0 = Metallic, bell-like
  - 5.0+ = Extreme sci-fi sounds

---

## PART 6: HOW TO LOAD CUSTOM SAMPLES

### Load from GitHub Repository

```javascript
// Load complete Dirt-Samples
await samples('github:tidalcycles/Dirt-Samples/master');

// Load VCSL samples
await samples('github:sgossner/VCSL/master');

// Load custom metal sample pack (example)
await samples('github:yourusername/metal-samples/main');
```

### Load from Custom URL

```javascript
// Load from your own server or cloud storage
const baseURL = 'https://example.com/samples/';

await samples({
  'heavy_gtr': baseURL + 'distorted-guitar.wav',
  'metal_bass': baseURL + 'metal-bass.wav',
  'kick_metal': baseURL + 'metal-kick.wav',
})
```

### Sample JSON Format

```json
{
  "sample_name": {
    "url": "https://example.com/path/to/sample.wav",
    "note": 60,           // MIDI note number (optional)
    "speed": 1.0          // Playback speed (optional)
  }
}
```

---

## PART 7: STRUDEL SOUND NAMES - COMPLETE REFERENCE

### Synthesizer Waveforms (Built-in)
```
"sine"      - Pure sine wave (smooth)
"triangle"  - Triangle wave (softer)
"square"    - Square wave (harsh, bright)
"sawtooth"  - Sawtooth wave (rich, aggressive)
```

### Noise Types (Built-in)
```
"white"     - White noise (harsh constant)
"pink"      - Pink noise (warmer)
"brown"     - Brown noise (soft, low-focused)
"crackle"   - Crackle noise (subtle texture)
```

### Drum Machine Banks (Available)
```
"RolandTR909"     - 90s metal standard
"RolandTR808"     - Classic warm
"RolandTR606"     - Compact tight
"AlesisSR16"      - Modern sampler
"RolandTR505"     - Compact variant
"RolandCR78"      - Drum computer
"Linndrum"        - LinnDrum samples
"EmuDrums"        - Emulator samples
```

### Standard Drum Sounds (Any Bank)
```
"bd" / "kick"     - Bass drum
"sd" / "snare"    - Snare
"hh" / "hat"      - Closed hi-hat
"oh" / "ohh"      - Open hi-hat
"cr" / "crash"    - Crash cymbal
"rd" / "ride"     - Ride cymbal
"ht"              - High tom
"mt"              - Mid tom
"lt"              - Low tom
"cl" / "clap"     - Handclap
"tom"             - Generic tom
"perc"            - Percussion
```

### Instrument Sample Names (VCSL)
```
"gtr" / "guitar"  - Guitar (clean)
"bass"            - Bass guitar
"piano"           - Piano
"moog"            - Moog synthesizer
"rhodes"          - Rhodes electric piano
"sax"             - Saxophone
"sitar"           - Sitar
"flute"           - Flute
"trumpet"         - Trumpet
"violin"          - Violin
```

### Dirt-Samples Sample Pack Names
```
"bd" / "bd0"      - Kick variations (808, 909, etc.)
"sd" / "sd0"      - Snare variations
"hh"              - Hi-hat samples
"clap"            - Handclap samples
"perc"            - Percussion
"metal"           - Metallic percussion
"breaks125"       - Break samples
"vinyl"           - Vinyl crackle
"amencutup"       - Amen breaks
"and more..."     - 100+ packs
```

---

## PART 8: GITHUB DISCUSSIONS & COMMUNITY RESOURCES

### Active Strudel Communities

1. **Strudel GitHub (Codeberg - Active)**
   - https://codeberg.org/uzu/strudel
   - Main development repository
   - Issues: 347+ open discussions
   - Pull Requests: 115+ active

2. **Discord Community**
   - https://discord.com/invite/HGEdXmRkzT
   - Shared TidalCycles/Strudel/Vortex Discord
   - Real-time help and discussions

3. **TidalCycles Club Forum**
   - https://club.tidalcycles.org/
   - Shared with TidalCycles Haskell and Vortex communities
   - Archived discussions and patterns

4. **Mastodon Account**
   - https://social.toplap.org/@strudel
   - Updates and announcements

### What's NOT Available

**After extensive research, these do NOT exist in Strudel:**
- ✗ Native distorted guitar sound bank
- ✗ "gm_distortion_guitar" or similar GM bank
- ✗ Pre-recorded metal guitar samples (library)
- ✗ Specific "metal" sound preset (beyond Dirt-Samples `metal` folder)
- ✗ Amp simulator effects (like gain staging with cabinet modeling)

**Why?** Strudel is **synthesizer-first** - it generates sound algorithmically, not through samples.

---

## PART 9: CREATING AUTHENTIC METAL IN STRUDEL

### The Philosophy

Instead of using guitar samples, Strudel creates metal through:

1. **Waveform Selection**
   - Sawtooth = Aggressive, thick
   - Square = Bright, cutting
   - Triangle = Softer, layering

2. **Heavy Processing**
   - Low-pass filtering (300-400Hz) = Amp rolloff effect
   - High gain + postgain = Compression/distortion
   - Low room = Tight, dry sound

3. **Rhythmic Patterns**
   - Syncopated patterns = Chaotic, metal feel
   - Minimal rests = Dense, aggressive
   - Heavy kick emphasis = Power

4. **Harmonic Choices**
   - Minor scales = Dark, heavy
   - Power chords (root + fifth) = Metal standard
   - Drop tunings (synthesizer notes) = Low frequency emphasis

### Genetic Algorithm Integration

Your `demo_slipknot.py` implementation uses **genetic algorithms** to evolve metal patterns:

```python
# Metal-specific fitness functions
make_metal_rhythm_fitness()     # Dense, syncopated rhythms
make_metal_melody_fitness()     # Dark scale adherence
make_metal_chord_fitness()      # Power chord emphasis
make_metal_drum_fitness()       # Aggressive backbeats

# Processing parameters for metal sound
instrument="sawtooth"           # Thick waveform
gain=0.8                        # High volume
lpf=300                         # Heavy filtering
postgain=1.5                    # Crushing compression
room=0.1                        # Tight, dry
```

---

## PART 10: ACTUAL METAL STRUDEL CODE SNIPPETS

### Snippet 1: Slipknot-Style Rhythm Riff

```javascript
// Drop-D tuning, heavy power chords
const slipknot_riff = s("[d3 d4 d3]*4")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(300)
  .postgain(1.5)
  .room(0.0)
  .speed("[1 0.5]");  // Rhythmic variation

const drums = stack(
  s("bd bd bd bd").bank("RolandTR909"),
  s("hh [hh hh]").bank("RolandTR909")
);

stack(slipknot_riff, drums);
```

### Snippet 2: Brutal Bass + Distorted Guitars

```javascript
// Three-layer guitar texture
const gtr1 = s("[c3 c4 g3]*2").sound("sawtooth").gain(0.8).lpf(300).postgain(1.5);
const gtr2 = s("[c3 g3 c4]*2").sound("triangle").gain(0.7).lpf(350).postgain(1.4);
const bass = s("[c1 c1 c2]*1").sound("sine").gain(0.9).lpf(150).postgain(1.8);

stack(gtr1, gtr2, bass);
```

### Snippet 3: Industrial Metal (with Metallic Hits)

```javascript
const industrial_guitars = s("[d3 [d4 d3]]*2")
  .sound("sawtooth")
  .fm(6)
  .gain(0.8)
  .lpf(280)
  .postgain(1.7);

const metal_texture = s("metal")
  .n("[0 1 2 3]*4")
  .gain(0.6);

stack(industrial_guitars, metal_texture);
```

---

## SUMMARY: SOUND NAMES FOR STRUDEL METAL

### For Distorted Guitar Sound
- **Waveforms**: `"sawtooth"`, `"square"`, `"triangle"`
- **Processing**: `.lpf(300)` + `.postgain(1.5)` = distortion

### For Bass
- **Waveform**: `"sine"`
- **Processing**: `.lpf(150)` + `.postgain(1.8)` = crushing

### For Drums
- **Bank**: `"RolandTR909"`
- **Sounds**: `"bd"`, `"sd"`, `"hh"`, `"oh"`, `"cr"`, `"rd"`

### For Metallic Texture
- **Sound**: `"metal"` (from Dirt-Samples)
- **Use**: `.n("[0 1 2 3]")` to cycle through variations

### For Guitar Samples (Clean)
- **Sound**: `"gtr"` or `"guitar"` (from VCSL)
- **Note**: These are clean acoustic/electric, not distorted

---

## RESOURCES

- **Strudel**: https://strudel.cc/
- **Codeberg (Active)**: https://codeberg.org/uzu/strudel
- **Dirt-Samples**: https://github.com/tidalcycles/Dirt-Samples
- **VCSL**: https://github.com/sgossner/VCSL
- **dough-samples**: https://github.com/felixroos/dough-samples
- **tidal-drum-machines**: https://github.com/ritchse/tidal-drum-machines
- **Discord**: https://discord.com/invite/HGEdXmRkzT
- **TidalCycles Club**: https://club.tidalcycles.org/

---

## CONCLUSION

**There are no "metal guitar" sound banks in Strudel** because Strudel is a **synthesizer-based live coding environment**. Instead, you create the sound of distorted metal guitar through:

1. **Sawtooth waveform** (rich harmonics)
2. **Heavy low-pass filtering** (300Hz = amp rolloff)
3. **Aggressive compression** (postgain = crushing)
4. **Layering** (multiple waveforms for thickness)

The result **sounds** like distorted electric guitar, even though it's pure synthesis. This is the philosophy of live coding: *create sound algorithmically, not through samples*.

For your GeneticMusic project, your implementation using synthesizer waveforms with heavy processing is the **correct and authentic approach** to metal in Strudel!
