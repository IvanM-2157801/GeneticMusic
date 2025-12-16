# Strudel Metal Sounds - Quick Reference Card

## 🎸 GUITAR SOUNDS (Synthesizer Waveforms)

### Primary Distorted Guitar Sound
```javascript
s("note").sound("sawtooth")
  .gain(0.8)
  .lpf(300)        // KEY: Heavy filtering creates distortion
  .postgain(1.5)   // KEY: Crushing compression
```
| Aspect | Value | Purpose |
|--------|-------|---------|
| Waveform | `sawtooth` | Rich harmonics (1,2,3,4,5...) = thick tone |
| Gain | 0.8 | High volume for presence |
| LPF | 300Hz | Cuts above 300Hz (mimics amp rolloff) |
| Postgain | 1.5 | Crushing distortion effect |
| Room | 0.1 | Tight, dry metal sound |

### Secondary Rhythm Guitar (Layering)
```javascript
s("note").sound("triangle")
  .gain(0.75)
  .lpf(350)
  .postgain(1.4)
```
| Aspect | Value | Purpose |
|--------|-------|---------|
| Waveform | `triangle` | Softer harmonics (1,3,5,7...) = less harsh |
| Gain | 0.75 | Slightly quieter for blend |
| LPF | 350Hz | Slightly more body than sawtooth |
| Postgain | 1.4 | Still aggressive but not harsh |

### Lead Guitar (Cutting Presence)
```javascript
s("note").sound("square")
  .gain(0.7)
  .lpf(400)
  .postgain(1.6)
```
| Aspect | Value | Purpose |
|--------|-------|---------|
| Waveform | `square` | Odd harmonics only (1,3,5,7...) = digital, bright |
| Gain | 0.7 | Medium-high presence |
| LPF | 400Hz | Less filtering for brightness |
| Postgain | 1.6 | Aggressive crushing for lead character |

---

## 🎵 BASS SOUNDS

### Heavy Metal Bass (Sub-Bass Foundation)
```javascript
s("note").sound("sine")
  .gain(0.9)
  .lpf(150)        // Cut all high frequencies
  .postgain(1.8)   // Maximum crushing
  .room(0.0)       // No reverb = tight
```
| Aspect | Value | Purpose |
|--------|-------|---------|
| Waveform | `sine` | Pure fundamental, no harmonics = clean sub-bass |
| Gain | 0.9 | Deep presence |
| LPF | 150Hz | Ultra-low frequencies only |
| Postgain | 1.8 | Extreme compression = punchy attack |
| Room | 0.0 | Completely dry/tight |

---

## 🥁 DRUM MACHINE BANKS

### METAL STANDARD: RolandTR909
```javascript
s("bd").bank("RolandTR909")    // Kick drum
s("sd").bank("RolandTR909")    // Snare
s("hh").bank("RolandTR909")    // Closed hi-hat
s("oh").bank("RolandTR909")    // Open hi-hat
```
- **Kick**: Punchy, aggressive attack
- **Snare**: Metallic "crack", no warmth
- **Hi-hat**: Tight, digital, razor-sharp
- **Character**: Iconic in 90s metal, industrial, thrash

### Alternative Banks
| Bank | Character | When to Use |
|------|-----------|------------|
| `RolandTR808` | Warm, classic, iconic 80s | Funk-metal, warmer tone |
| `RolandTR606` | Tight, surgical, precise | Technical metal, digital feel |
| `AlesisSR16` | Modern sampler, realistic | Mixing with other genres |

### Standard Drum Sounds (Work with Any Bank)
```
"bd"  / "kick"  - Bass drum/Kick
"sd"  / "snare" - Snare drum
"hh"  / "hat"   - Closed hi-hat
"oh"  / "ohh"   - Open hi-hat
"cr"  / "crash" - Crash cymbal
"rd"  / "ride"  - Ride cymbal
"ht"            - High tom
"mt"            - Mid tom
"lt"            - Low tom
"cl"  / "clap"  - Handclap
```

---

## 🔩 NOISE TYPES (For Texture & Effects)

```javascript
s("hh").sound("white")   // Harsh, constant = bright hi-hats
s("hh").sound("pink")    // Warmer = more natural hi-hats
s("hh").sound("brown")   // Soft, low-focused = ambient texture
s("perc").sound("crackle") // Subtle crackle = vintage character
```

---

## 🪨 METALLIC/INDUSTRIAL SOUNDS

### From Dirt-Samples "metal" Pack
```javascript
s("metal")                    // Accesses metal0, metal1, metal2...
  .n("[0 1 2 3]")            // Cycle through variations
  .gain(0.6)
  .lpf(800)
```
**Use Case**: Industrial/sci-fi metal textures, metallic percussion hits

---

## 🎼 GUITAR SAMPLES (VCSL - Clean Only)

### Available Guitar Samples
```javascript
s("gtr")        // General guitar
s("guitar")     // Alternative alias
```

**Important**: These are **CLEAN acoustic/electric** samples, NOT distorted.

**VCSL Includes**:
- Acoustic Guitar
- Classical Guitar
- Electric Guitar (clean)
- Nylon Guitar
- Steel Guitar
- 12-String Guitar
- Bass Guitar

---

## ⚡ COMPLETE METAL GUITAR STACK

### Full Example: 3 Layers + Bass + Drums

```javascript
// RHYTHM GUITAR 1 (Sawtooth - Primary)
const gtr1 = s("[c3 c4 c5 c4]*2")
  .sound("sawtooth")
  .gain(0.8)
  .lpf(300)
  .postgain(1.5)
  .room(0.1)
  .pan(0.3);

// RHYTHM GUITAR 2 (Triangle - Blend)
const gtr2 = s("[g2 g3 g4 g3]*2")
  .sound("triangle")
  .gain(0.75)
  .lpf(350)
  .postgain(1.4)
  .room(0.1)
  .pan(-0.3);

// LEAD GUITAR (Square - Cutting)
const lead = s("[c5 g4 e5 d5]")
  .sound("square")
  .gain(0.7)
  .lpf(400)
  .postgain(1.6)
  .room(0.15);

// BASS (Sine - Foundation)
const bass = s("[c1 c1 c2 c1]*2")
  .sound("sine")
  .gain(0.9)
  .lpf(150)
  .postgain(1.8)
  .room(0.0);

// DRUMS (TR909 - Metal Standard)
const kick = s("bd").bank("RolandTR909").gain(1.0).room(0.0);
const snare = s("sd").bank("RolandTR909").gain(0.9).room(0.05);
const hihat = s("hh").bank("RolandTR909").gain(0.8).room(0.0);

// COMBINE
stack(gtr1, gtr2, lead, bass, kick, snare, hihat);
```

---

## 🎛️ PROCESSING PARAMETERS CHEATSHEET

### Distortion Emulation
| Parameter | Value | Effect |
|-----------|-------|--------|
| `gain` | 0.7-0.9 | Volume boost |
| `lpf` | 280-400 | Low-pass filter (amp rolloff) |
| `postgain` | 1.4-1.8 | Compression/crushing |

### Tone Shaping
| Parameter | Value | Effect |
|-----------|-------|--------|
| `lpf` | Lower (250) | Darker, more crushed |
| `lpf` | Higher (400) | Brighter, more sparkle |
| `postgain` | Higher (1.8) | More aggressive |
| `postgain` | Lower (1.2) | Cleaner tone |

### Space/Character
| Parameter | Value | Effect |
|-----------|-------|--------|
| `room` | 0.0 | Tight, dry (metal standard) |
| `room` | 0.1-0.2 | Some space but still tight |
| `room` | 0.3+ | Spacious, less metal-like |

---

## 🔊 SOUND NAMES - METAL CHEAT SHEET

### Synthesizer Waveforms (Metal Use)
```
"sawtooth"   → Distorted rhythm guitar (primary)
"triangle"   → Secondary rhythm guitar (blending)
"square"     → Lead guitar (cutting, bright)
"sine"       → Bass (clean, sub-frequencies)
```

### Noise Types
```
"white"      → Bright hi-hats, effects
"pink"       → Warm hi-hats, natural
"brown"      → Soft ambient texture
"crackle"    → Vintage character
```

### Drum Banks (FOR METAL)
```
"RolandTR909"    → 90s metal standard ⭐ RECOMMENDED
"RolandTR808"    → Classic warm alternative
"RolandTR606"    → Tight, precise alternative
"AlesisSR16"     → Modern sampler alternative
```

### Drum Sounds
```
"bd"  → Kick drum
"sd"  → Snare
"hh"  → Closed hi-hat
"oh"  → Open hi-hat
"cr"  → Crash
"rd"  → Ride
```

### Instrument Samples (VCSL)
```
"gtr" or "guitar" → Guitar (CLEAN, not distorted)
"bass"            → Bass guitar
"moog"            → Synth
"piano"           → Piano
```

### Special Sounds
```
"metal"          → Metallic percussion (from Dirt-Samples)
```

---

## ❌ SOUNDS THAT DON'T EXIST IN STRUDEL

❌ `"distorted_guitar"`  
❌ `"metal_guitar"`  
❌ `"gm_distortion_guitar"`  
❌ Any guitar amp/cabinet simulator  
❌ Pre-recorded distorted guitar samples  

**Why?** Strudel is synthesizer-first. Create distortion through: `sawtooth` + `lpf` + `postgain`

---

## 📚 LOADING SAMPLES

### Default Samples (Already Loaded)
- Dirt-Samples (drum machines, percussion, samples)
- VCSL (instruments, orchestra, chordophones)
- tidal-drum-machines (drum banks)

### Load from GitHub
```javascript
await samples('github:tidalcycles/Dirt-Samples/master');
await samples('github:sgossner/VCSL/master');
```

### Load Custom Samples
```javascript
await samples({
  'heavy_gtr': 'https://example.com/distorted-guitar.wav',
  'metal_kick': 'https://example.com/metal-kick.wav'
});

s("heavy_gtr").note("c3 c4");
```

---

## 🎯 QUICK METAL SETUP (Copy-Paste Ready)

```javascript
// One-line brutal metal riff
s("[c3 c4 c3]*2").sound("sawtooth").gain(0.8).lpf(300).postgain(1.5)
  .stack(s("bd").bank("RolandTR909").gain(1.0))
  .stack(s("hh").bank("RolandTR909").gain(0.8));
```

---

## 📖 REFERENCES

- **Strudel**: https://strudel.cc/
- **GitHub (Codeberg)**: https://codeberg.org/uzu/strudel
- **Dirt-Samples**: https://github.com/tidalcycles/Dirt-Samples
- **VCSL**: https://github.com/sgossner/VCSL
- **Discord**: https://discord.com/invite/HGEdXmRkzT

---

**Key Takeaway**: In Strudel, **distorted guitar = `sawtooth` + `lpf(300)` + `postgain(1.5)`**. No special sound bank needed!
