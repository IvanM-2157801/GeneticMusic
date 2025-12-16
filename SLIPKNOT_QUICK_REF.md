# Slipknot Demo Quick Reference

## Run the Demo
```bash
cd /home/amadeusw/projects/GeneticMusic
python demo_slipknot.py
```

## What You Get
- 7-layer Slipknot-inspired composition
- Dual down-tuned guitars with power chords
- Heavy, groovy bass
- Complex drum patterns (kick, snare, hi-hat)
- Harmonic chord foundation
- Strudel Live Coder link to hear it in your browser

## Key Metal Fitness Metrics

| Metric | Purpose | Metal Value |
|--------|---------|-------------|
| **density** | Notes per beat | 0.6-0.7 (MAXIMIZE) |
| **syncopation** | Offbeat emphasis | 0.4-0.5 (HIGH) |
| **groove** | Beat pocket | 0.3-0.6 (VARY) |
| **rests** | Silence ratio | -0.8 to -0.9 (PENALIZE) |
| **scale** | Dark tone | 0.5-0.6 (MINOR emphasis) |
| **consistency** | Pattern repeat | 0.1-0.2 (LOW, chaotic) |

## Key Parameters Explained

### BPM = 65
- Typical Slipknot range: 50-70
- Slow = HEAVY and POWERFUL
- Too fast = loses heaviness
- Too slow = loses groove

### gain = 0.7-1.0
- Guitars: 0.75-0.8 (aggressive)
- Bass: 0.9 (deep presence)
- Kick: 1.0 (maximum punch)
- Too low = weak metal sound
- Too high = distortion becomes muddy

### lpf (Low-Pass Filter) = 150-400 Hz
- Lower = more distorted, sludgy
- 150 Hz (bass) = sub-bass only
- 300 Hz (guitars) = crushing distortion
- 400 Hz (presence) = lets some high-end through
- Higher lpf = cleaner but less metal

### postgain = 1.4-1.8
- Applies crushing distortion
- Guitar: 1.4-1.6 (heavy)
- Bass: 1.8 (maximum punch)
- Creates that compressed, loud metal sound

### room = 0.0-0.2
- Reverb/ambience
- Metal = TIGHT, DRY (minimal room)
- 0.0 = no reverb (tightest)
- 0.2 = slight space (still dry)
- Clean songs use 0.5-0.8 (NOT metal)

## Layer Roles

```
GUITARS (3x)
├─ rhythm_guitar_1 (square wave, lower octave)
├─ rhythm_guitar_2 (triangle wave, parallel)
└─ lead_guitar (sawtooth, higher octave)

RHYTHM SECTION (2x)
├─ bass (sine, VERY low, pure sub-bass)
└─ chords (pulse, harmonic foundation)

DRUMS (3x)
├─ kick (downbeat anchor)
├─ snare (backbeat crisp)
└─ hihat (relentless pocket, 16-beat density)
```

## Customization Examples

### Make It EVEN MORE AGGRESSIVE
```python
verse_rhythm_metal = make_metal_rhythm_fitness({
    "density": 0.8,         # Was 0.6
    "syncopation": 0.6,     # Was 0.4
})

verse_guitar_metal = make_metal_melody_fitness({
    "rests": -0.99,         # Almost NO silence
    "variety": 0.5,         # More riff variety
})
```

### Add More Bass Presence
```python
layers.append(LayerConfig(
    name="bass",
    gain=1.0,               # Was 0.9 (maximum)
    postgain=2.0,           # Was 1.8 (more crushing)
    lpf=120,                # Was 150 (deeper subs)
))
```

### Increase BPM for Faster Metal
```python
BPM = 80                    # Was 65 (faster but still heavy)
POPULATION_SIZE = 12       # Smaller for tighter evolution
MUTATION_RATE = 0.2        # Lower (less chaotic at speed)
```

### Simulate Different Drop Tuning
```python
# Drop D (1 octave lower than standard)
octave_range=(1, 2)        # Was (2, 3)
base_octave=1              # Was 2
lpf=280                    # Slightly lower for weight
```

## Sound Design Philosophy

### Metal ≠ Clean
- **Distortion**: Yes (use gain + postgain)
- **Reverb**: Minimal (tight, controlled)
- **Clarity**: No (aggressive, crushing)
- **Density**: Maximum (relentless)

### Heavy ≠ Slow
- **BPM 65** = slow enough to feel heavy
- **But fast enough** = maintains groove
- **Density 0.6** = lots of notes per beat
- **Result** = slow but INTENSE

### Chaotic ≠ Random
- **Syncopation** = controlled unpredictability
- **Consistency 0.1** = some patterns repeat
- **Not random** = evolved by fitness
- **Result** = unsettling but musical

## The "Nine" Layer Structure

Slipknot has 9 members (The Nine). This demo uses 9 layers:
1. Shawn Crahan (percussion) → `chords` layer
2. Mick Thomson (guitar) → `rhythm_guitar_1`
3. Corey Taylor (vocals) → represented in lead_guitar expression
4. Sid Wilson (DJ/sampler) → potential 8th layer
5. Jim Root (guitar) → `rhythm_guitar_2`
6. Paul Gray (bass) → `bass` layer
7. Chris Fehn (percussion) → `snare` layer
8. Jay Weinberg (drums) → `kick` layer
9. The crowd/percussion → `hihat` layer

## Output: Strudel Live Code

The demo generates a Strudel live code link with:
- Complete multi-layer arrangement
- BPM and timing synchronized
- All effects parameters baked in
- Ready to play in browser

Just copy the link from output and open in: https://strudel.cc/

## Troubleshooting

**Sound too clean/bright?**
→ Lower lpf values (300 → 250)

**Drums not punchy enough?**
→ Increase kick gain (0.8 → 1.0)

**Bass getting lost?**
→ Increase postgain (1.8 → 2.0)

**Too chaotic/unmusical?**
→ Lower syncopation (0.5 → 0.3)
→ Lower mutation rate (0.3 → 0.2)

**Not aggressive enough?**
→ Maximize density (0.6 → 0.8)
→ Penalize rests more (-0.8 → -0.95)
→ Add more postgain (1.5 → 1.7)

## Next Steps

1. **Run the demo**: `python demo_slipknot.py`
2. **Open the Strudel link** in your browser
3. **Listen** to the generated composition
4. **Modify** fitness values and re-run
5. **Experiment** with layer configurations
6. **Create** custom metal subgenre versions

---

**Rock on!** 🤘
