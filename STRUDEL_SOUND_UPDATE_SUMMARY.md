# Slipknot Demo - Sound Configuration Summary

## Updated Instruments & Sounds

### Guitar Layers

| Layer | Instrument | Character | Purpose |
|-------|-----------|-----------|---------|
| **Rhythm Guitar 1** | `sawtooth` | Rich, aggressive, dense harmonics | Heavy power chords with thick tone |
| **Rhythm Guitar 2** | `triangle` | Softer, layering harmonics | Harmonic complexity, tonal depth |
| **Lead Guitar** | `square` | Bright, harsh, cutting tone | Lead lines, presence, solo fills |

**Sound Design**: Sawtooth + Triangle for rhythm creates a crushing power chord texture. Square for lead cuts through the mix.

### Bass Layer

| Layer | Instrument | Character | Purpose |
|-------|-----------|-----------|---------|
| **Bass** | `sine` | Pure fundamental, sub-bass only | Clean, massive low-end foundation |

**Sound Design**: Pure sine wave with lpf=150Hz creates pure sub-bass. High postgain=1.8 for punchy metal attack.

### Chord Layer

| Layer | Instrument | Character | Purpose |
|-------|-----------|-----------|---------|
| **Chords** | `sawtooth` | Rich, aggressive harmonics | Dark harmonic foundation |

**Sound Design**: Sawtooth for consistency with guitars. Heavy filtering (lpf=250Hz) for dark tone.

### Drum Layers (Roland TR909)

| Layer | Sound | Character | Purpose |
|-------|-------|-----------|---------|
| **Kick** | `bd` (RolandTR909) | Punchy, aggressive thump | Downbeat anchor, groove foundation |
| **Snare** | `sd` (RolandTR909) | Sharp, metallic crack | Backbeat definition (2 & 4) |
| **Hi-Hat** | `hh` (RolandTR909) | Tight, digital precision | Relentless groove pocket |

**Sound Design**: TR909 is the classic metal drum machine. Each sound has sharp, cutting characteristics perfect for heavy metal.

## Key Processing Parameters

All layers use aggressive processing to achieve metal distortion:

```
Gain (0.6-1.0)     → High volume presence
├─ +
LPF (150-400Hz)    → Heavy filtering = distorted tone
├─ +
PostGain (1.4-1.8) → Crushing compression
├─ +
Room (0.0-0.2)     → Minimal reverb = tight sound
└─ = METAL TONE!
```

## Why These Sounds?

### Sawtooth (Guitars & Chords)
✅ Many harmonics = rich, thick tone  
✅ Aggressive character = metal aesthetic  
✅ Distortion-like quality = synthesizer distortion  
✅ Procedural = consistent across all notes  

### Triangle (Rhythm Guitar 2)
✅ Fewer high-end harmonics than sawtooth  
✅ Adds harmonic complexity when layered  
✅ Smoother than square = better blend with sawtooth  
✅ Creates "thickness" without muddiness  

### Square (Lead Guitar)
✅ Harsh, cutting tone = presence in mix  
✅ Digital character = modern metal synth  
✅ Piercing quality = excellent for leads  
✅ Sharp attack = clear definition  

### Sine (Bass)
✅ Pure fundamental = clean, deep bass  
✅ No harmonics = doesn't muddy other frequencies  
✅ Massive sub-bass = metal power  
✅ Best for crushing with postgain  

### Roland TR909 (Drums)
✅ Classic metal standard = iconic sound  
✅ Punchy kick = heavy groove  
✅ Metallic snare = aggressive character  
✅ Tight hi-hat = precise pocket  

## Comparison to Original

### Before (Generic Waveforms)
❌ `square` for all guitars - too harsh  
❌ `pulse` for chords - vague character  
❌ `alesissr16` drums - warm, not aggressive  

### After (Proper Strudel Sounds)
✅ `sawtooth`/`triangle`/`square` - layered aggression  
✅ `sawtooth` chords - consistency with guitars  
✅ `RolandTR909` - classic metal standard  

## Audio Characteristics

The updated demo produces:

🎸 **Guitars**: Thick, heavy power chord texture with crushing distortion  
🎸 **Lead**: Sharp, cutting lead lines that pierce the mix  
🎸 **Bass**: Massive sub-bass punch with aggressive attack  
🥁 **Drums**: Classic metal groove with TR909 character  
🎼 **Overall**: Authentic Slipknot-style nu-metal sound  

## Customization Ideas

### For Different Metal Subgenres

**Doom Metal** (slow, heavy, fuzzy)
- Lower BPM: 30-40
- Reduce all LPF values by 50Hz
- Increase postgain: 1.8 → 2.0
- Use double sawtooth guitars (remove triangle)

**Thrash Metal** (fast, chaotic, precise)
- Increase BPM: 50 → 120+
- Increase square wave usage
- Reduce postgain slightly: 1.5 → 1.3
- TR808 drums for tighter sound

**Metalcore** (modern, cleaner, melodic)
- Increase all LPF values by 100Hz
- Decrease postgain: 1.5 → 1.2
- Add more triangle wave
- Increase room: 0.1 → 0.3

**Death Metal** (ultra-aggressive, distorted)
- Use all sawtooth (no triangle/square)
- Lower all LPF: 300 → 200, 400 → 300
- Increase postgain: 1.5 → 2.0
- RolandTR808 for darker drums

## Testing

✅ **Syntax validated**: No errors in demo_slipknot.py  
✅ **Sound selection**: Based on Strudel documentation  
✅ **Metal appropriate**: Classic TR909 + aggressive waveforms  
✅ **Customizable**: Easy to adjust for different metal styles  

## Next Steps

1. Run: `python demo_slipknot.py`
2. Open Strudel link in browser
3. Listen for:
   - Thick guitar tone
   - Punchy TR909 drums
   - Clean bass foundation
   - Overall metal aggression

Happy metal generating! 🤘
