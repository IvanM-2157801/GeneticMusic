# Strudel Metal Examples - Copy-Paste Code Snippets

This document contains working Strudel code snippets for creating metal and heavy music. Copy these directly into https://strudel.cc/ and modify as needed.

---

## EXAMPLE 1: Basic Heavy Metal Riff (Sawtooth + TR909)

```javascript
// Simple brutal metal pattern
s("[c3 c4 c3]*2")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(300)
  .postgain(1.5)
  .stack(
    s("bd bd bd bd").bank("RolandTR909").gain(1.0)
  );
```

**What This Does**:
- `[c3 c4 c3]*2` = Power chord pattern (C note, 2 octaves)
- `sawtooth` = Aggressive, distorted sound
- `lpf(300)` = Heavy filtering (distortion effect)
- `postgain(1.5)` = Crushing compression
- `bd` = TR909 kick drum on every beat

**Customize**:
```javascript
// Change notes for different riff
s("[d3 d4 d3]*2")           // Drop-D tuning
s("[c3 g2 c3]*2")           // Power chord (root + 5th)
s("[c3 c3 c4 c3]*2")        // Faster rhythm
s("[c3 c4 c3]*1")           // Slower tempo
```

---

## EXAMPLE 2: Full Metal Composition (3 Guitars + Bass + Drums)

```javascript
// Complete metal setup
const gtr1 = s("[c3 c4 c5 c4]*2")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(300)
  .postgain(1.5)
  .room(0.1)
  .pan(0.3);

const gtr2 = s("[g2 g3 g4 g3]*2")
  .sound("triangle")
  .gain(0.75)
  .lpf(350)
  .postgain(1.4)
  .room(0.1)
  .pan(-0.3);

const lead = s("[c5 g4 e5 d5]*1")
  .sound("square")
  .gain(0.7)
  .lpf(400)
  .postgain(1.6)
  .room(0.15);

const bass = s("[c1 c1 c2 c1]*2")
  .sound("sine")
  .gain(0.9)
  .lpf(150)
  .postgain(1.8)
  .room(0.0);

const drums = stack(
  s("bd bd bd bd").bank("RolandTR909").gain(1.0).room(0.0),
  s("sd . sd .").bank("RolandTR909").gain(0.9).room(0.05),
  s("hh [hh hh] hh [hh hh]").bank("RolandTR909").gain(0.8).room(0.0)
);

stack(gtr1, gtr2, lead, bass, drums);
```

**What This Does**:
1. **Guitar 1 (Sawtooth)**: Main rhythm, thick and aggressive
2. **Guitar 2 (Triangle)**: Second layer for texture and thickness
3. **Lead Guitar (Square)**: Cutting presence, solos, fills
4. **Bass (Sine)**: Deep sub-bass foundation
5. **Drums**: TR909 kick, snare backbeat, relentless hi-hats

**Customize**:
```javascript
// Change guitar rhythm patterns
const gtr1 = s("[c3 [c4 c3]]*2")           // Syncopated
const gtr2 = s("[g2 . g3 .]*2")            // Sparse
const lead = s("[c5 . g4 . e5]*1")         // Staccato lead

// Change drum pattern
s("bd bd . bd")           // Kick off-beat
s("sd . sd . sd . sd .")  // Double snare hits
s("hh*8")                 // Fast hi-hat rolls

// Adjust metal intensity
.postgain(1.8)  // More aggressive
.postgain(1.3)  // Less aggressive
.lpf(250)       // Darker tone
.lpf(400)       // Brighter tone
```

---

## EXAMPLE 3: Slipknot-Style Groove Metal

```javascript
// Drop-D tuning, groovy syncopation
const main_riff = s("[d3 [d4 d3 d4] d3]*1")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(300)
  .postgain(1.6)
  .room(0.05);

const rhythmic_layer = s("[d3 . . . [d4 d3] . d4]*1")
  .sound("triangle")
  .gain(0.7)
  .lpf(320)
  .postgain(1.4);

const bass_groove = s("[d1 d1 . d1 d1 . d2]*1")
  .sound("sine")
  .gain(0.95)
  .lpf(120)
  .postgain(1.8);

const drum_groove = stack(
  s("[bd bd . bd]").bank("RolandTR909").gain(1.0),
  s("[. . sd .]").bank("RolandTR909").gain(0.95),
  s("[hh [hh hh] hh [hh hh]]").bank("RolandTR909").gain(0.85)
);

stack(main_riff, rhythmic_layer, bass_groove, drum_groove);
```

**Groove Elements**:
- `[d3 [d4 d3 d4] d3]` = Syncopated, chaotic feel
- Kick-snare on different beats = Polyrhythmic pocket
- Hi-hat fills = Busy, aggressive texture

---

## EXAMPLE 4: Industrial/Extreme Metal (with Metallic Textures)

```javascript
// Extreme metal with sci-fi metallic elements
const industrial_gtr = s("[c3 [c4 c3]]*2")
  .sound("sawtooth")
  .fm(6)                  // FM synthesis for metallic character
  .fmh(2.5)               // Metallic harmonicity
  .gain(0.85)
  .lpf(280)
  .postgain(1.7)
  .room(0.0);

const metal_texture = s("metal")
  .n("[0 1 2 3]*4")       // Cycle through metallic samples
  .gain(0.5)
  .lpf(800)
  .room(0.2);

const brutal_bass = s("[c1 c1 . c1]*1")
  .sound("sine")
  .gain(1.0)
  .lpf(100)
  .postgain(1.9);

const extreme_drums = stack(
  s("bd bd bd bd").bank("RolandTR909").gain(1.0),
  s("[sd . sd sd]").bank("RolandTR909").gain(1.0),
  s("cr . . cr").bank("RolandTR909").gain(0.8)
);

stack(industrial_gtr, metal_texture, brutal_bass, extreme_drums);
```

**Features**:
- **FM Synthesis** (`.fm(6)`) = Extra metallic character
- **metal sample** = Sci-fi/industrial texture
- **Maximum gain** on bass = Crushing sub-frequencies
- **Crash cymbals** = Industrial percussion

**FM Parameters**:
```javascript
.fm(4)           // Subtle FM
.fm(8)           // Heavy FM
.fmh(1.0)        // Natural harmonics
.fmh(2.5)        // Metallic bell-like
.fmh(5.0)        // Extreme sci-fi
```

---

## EXAMPLE 5: Synth Metal (Waveform FM Synthesis)

```javascript
// Extreme synthesizer metal using FM modulation
const fm_power = s("[c3 c4 g3 d4]*2")
  .sound("sawtooth")
  .fm(8)                  // Heavy FM modulation
  .fmh(2.5)               // Metallic overtones
  .gain(0.8)
  .lpf(350)
  .postgain(1.5);

const fm_lead = s("[c5 [g4 e5] d5]*1")
  .sound("square")
  .fm(10)                 // EXTREME FM for lead
  .fmh(3.0)               // Ultra-metallic
  .gain(0.75)
  .lpf(400)
  .postgain(1.7);

const bass = s("[c1 c1 c2]*1")
  .sound("sine")
  .gain(0.9)
  .lpf(150)
  .postgain(1.8);

const drums = stack(
  s("bd bd bd bd").bank("RolandTR909").gain(1.0),
  s("hh [hh hh hh hh]").bank("RolandTR909").gain(0.9)
);

stack(fm_power, fm_lead, bass, drums);
```

**FM Synthesis for Metal**:
- Creates "bell-like", "metallic" tones
- Perfect for extreme/symphonic metal
- Combines aggression with otherworldly character

---

## EXAMPLE 6: Thrash Metal (Fast, Tight, Precise)

```javascript
// Fast thrash metal pattern - technical and dense
const thrash_main = s("[e3 e4 [e3 e4]*2]*1")
  .sound("sawtooth")
  .gain(0.85)
  .lpf(300)
  .postgain(1.6)
  .room(0.0);

const thrash_harmony = s("[e3 b2 [e3 b2]*2]*1")
  .sound("triangle")
  .gain(0.75)
  .lpf(320)
  .postgain(1.5);

const bass = s("[e1 [e1 e2] e1]*1")
  .sound("sine")
  .gain(1.0)
  .lpf(130)
  .postgain(1.8);

const thrash_drums = stack(
  s("bd bd [bd bd] bd").bank("RolandTR909").gain(1.0),
  s("sd . [sd sd] .").bank("RolandTR909").gain(1.0),
  s("hh*16").bank("RolandTR909").gain(0.85)  // 16th note hi-hats
);

stack(thrash_main, thrash_harmony, bass, thrash_drums);
```

**Thrash Elements**:
- **Tight, minimal rests** = Relentless attack
- **16th note patterns** = Fast, technical
- **Synchronized guitars + bass** = Power
- **Kick on every beat** = Driving force

---

## EXAMPLE 7: Slower Doom/Sludge Metal

```javascript
// Slow, heavy, crushing doom metal
const doom_riff = s("[c2 [c3 c2]]*1")
  .sound("sawtooth")
  .gain(0.9)
  .lpf(250)              // LOWER filter = darker
  .postgain(1.8)         // HIGHER postgain = more crushing
  .room(0.1);

const doom_harmony = s("[c2 g1 [c3 g2]]*1")
  .sound("triangle")
  .gain(0.85)
  .lpf(280)
  .postgain(1.7);

const doom_bass = s("[c1 [c1 c0] c1]*1")
  .sound("sine")
  .gain(1.0)
  .lpf(100)              // ULTRA low = sub-bass
  .postgain(1.9);

const doom_drums = stack(
  s("[bd . . .]").bank("RolandTR808").gain(1.0),    // TR808 = warmer
  s("[. . . sd]").bank("RolandTR808").gain(0.9),
  s("[. hh . .]").bank("RolandTR808").gain(0.7)
);

stack(doom_riff, doom_harmony, doom_bass, doom_drums);
```

**Doom Characteristics**:
- **Slower tempo** (whole note beats)
- **Lower frequencies** (C2, C1, C0)
- **Heavy filtering** (lpf=250, lpf=100)
- **Maximum crushing** (postgain=1.9)
- **TR808 drums** = Warmer than 909, more ominous
- **Sparse rhythm** = Brooding, patient

---

## EXAMPLE 8: Noise/Drone Metal (Experimental)

```javascript
// Experimental metal with noise layers
const drone_guitar = s("[c2]*1")
  .sound("sawtooth")
  .gain(0.9)
  .lpf(200)
  .postgain(1.8)
  .room(0.3);              // More room for drone effect

const drone_noise = s("[c2]*1")
  .sound("white")          // White noise instead of sine
  .gain(0.4)
  .lpf(400)
  .room(0.4);

const sub_bass = s("[c1]*1")
  .sound("sine")
  .gain(1.0)
  .lpf(80)                 // EXTREME sub-bass
  .postgain(1.9)
  .room(0.0);

const sparse_drums = stack(
  s("[bd . . .]").bank("RolandTR909").gain(1.0),
  s("[. . . sd]").bank("RolandTR909").gain(0.9)
);

stack(drone_guitar, drone_noise, sub_bass, sparse_drums);
```

**Drone Elements**:
- **Sustained notes** `[c2]*1` = Held long
- **White noise** = Texture and air
- **Room/reverb** = Spacious, atmospheric
- **Sparse drums** = Barely there rhythm

---

## EXAMPLE 9: Alternative/Nu-Metal (Groovy, Syncopated)

```javascript
// Nu-metal style - groovy but heavy
const nu_riff = s("[f3 [f4 f3 f4]*2 f3]*1")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(320)
  .postgain(1.4)
  .room(0.08);

const nu_layer2 = s("[f3 . [f4 f3] .]*1")
  .sound("triangle")
  .gain(0.7)
  .lpf(350)
  .postgain(1.3);

const groove_bass = s("[f1 f1 [f2 f1] f1]*1")
  .sound("sine")
  .gain(0.95)
  .lpf(140)
  .postgain(1.7);

const groove_drums = stack(
  s("[bd bd . [bd bd] bd]*1").bank("RolandTR909").gain(1.0),
  s("[. . sd . . sd sd .]").bank("RolandTR909").gain(0.9),
  s("[hh hh [hh hh] hh]*1").bank("RolandTR909").gain(0.8)
);

stack(nu_riff, nu_layer2, groove_bass, groove_drums);
```

**Nu-Metal Characteristics**:
- **Syncopated rhythms** = Chaotic, energetic
- **Groovy but aggressive** = Bouncy heaviness
- **Layered guitars** = Thick texture
- **Syncopated drums** = Pocket-heavy

---

## EXAMPLE 10: Minimal Metal (Post-Metal/Ambient Metal)

```javascript
// Minimal, atmospheric metal
const ambient_gtr = s("[c4]*2")
  .sound("sine")
  .gain(0.6)
  .lpf(800)
  .room(0.5)
  .delay(0.5);

const subtle_rhythm = s("[c3 . . .]")
  .sound("triangle")
  .gain(0.5)
  .lpf(400)
  .room(0.3);

const deep_bass = s("[c1]*1")
  .sound("sine")
  .gain(0.8)
  .lpf(60)
  .room(0.2);

const minimal_drums = stack(
  s("[bd . . .]").bank("RolandTR909").gain(0.8),
  s("[. . . .]").bank("RolandTR909")  // No snare
);

stack(ambient_gtr, subtle_rhythm, deep_bass, minimal_drums);
```

**Post-Metal/Ambient Characteristics**:
- **Sustained notes** = Atmosphere
- **Sparse rhythm** = Spacious, patient
- **High room values** = Reverb and space
- **Lower gains** = Subtle, not aggressive
- **Sine wave** = Smooth, meditative

---

## QUICK MODIFICATION GUIDE

### Make It Heavier
```javascript
.lpf(250)           // Lower cutoff
.postgain(1.8)      // More crushing
.gain(0.9)          // Higher volume
```

### Make It Lighter
```javascript
.lpf(400)           // Higher cutoff
.postgain(1.3)      // Less crushing
.gain(0.7)          // Lower volume
```

### Add More Aggression
```javascript
.sound("sawtooth")  // Switch to sawtooth
.gain(0.85)         // +0.05
.fm(8)              // Add FM modulation
.postgain(1.7)      // +0.2
```

### Darken Tone
```javascript
.lpf(250)           // Cut high frequencies
.lpf(200)           // ULTRA dark
```

### Brighten Tone
```javascript
.lpf(400)           // Keep high frequencies
.sound("square")    // Switch to square (brighter)
```

### Change Timing/Groove
```javascript
// Faster
s("[c3 c4]*4")      // Play notes 4 times per measure

// Slower
s("[c3 c4]*1")      // Play notes 1 time per measure

// Syncopated
s("[c3 [c4 c3]]*2") // Nested brackets = syncopation

// Sparse
s("[c3 . . .]")     // Dots = rests
```

### Change Drum Feel
```javascript
// Tight (no reverb)
.room(0.0)

// Some space
.room(0.1)

// Spacious
.room(0.3)
```

---

## RESOURCES

- **Strudel REPL**: https://strudel.cc/
- **Strudel Docs**: https://strudel.cc/learn
- **Discord**: https://discord.com/invite/HGEdXmRkzT
- **GitHub (Codeberg)**: https://codeberg.org/uzu/strudel
- **Dirt-Samples**: https://github.com/tidalcycles/Dirt-Samples
- **VCSL**: https://github.com/sgossner/VCSL

---

**Note**: All code is ready to copy-paste directly into https://strudel.cc/. Just select all code, paste into the editor, and click "Play"!
