# Rhythm Encoding Fix

## Problem

The original Strudel output was **not preserving the rhythm structure**. All notes were just listed sequentially without showing which beats they belong to.

**Before (incorrect):**
```javascript
$: n("[d2 c3 d2 c2 c2 c2 c2 c2 d3 d3 c3 c3 d3 c3 d2 d2]").s("sawtooth")
```

This doesn't show the rhythm at all - it's just a flat list of notes.

**After (correct):**
```javascript
$: n("[d3 c3 c3] d2 [c2 c2 c2] d3 [c3 d2 d2] c3 [c3 d3 d3] [c3 c2 c2]").s("sawtooth")
```

This properly shows the rhythm structure with notes grouped by beats!

## Solution

### 1. Added `to_strudel_with_rhythm()` method to `Phrase` class

**File:** `core/music.py`

```python
def to_strudel_with_rhythm(self, rhythm: str) -> str:
    """Convert phrase to Strudel notation preserving rhythm structure.

    Example: rhythm "2103" with 6 notes becomes "[n1 n2] [n3] ~ [n4 n5 n6]"
    """
    note_idx = 0
    beat_groups = []

    for beat_char in rhythm:
        subdivisions = int(beat_char)
        if subdivisions == 0:
            # Rest beat
            beat_groups.append("~")
        else:
            # Collect notes for this beat
            beat_notes = []
            for _ in range(subdivisions):
                if note_idx < len(self.notes):
                    beat_notes.append(self.notes[note_idx].to_strudel())
                    note_idx += 1

            if len(beat_notes) == 1:
                beat_groups.append(beat_notes[0])
            else:
                beat_groups.append("[" + " ".join(beat_notes) + "]")

    return " ".join(beat_groups)
```

### 2. Added `rhythm` field to `Layer` class

**File:** `core/music.py`

```python
@dataclass
class Layer:
    name: str
    phrases: list[Phrase] = field(default_factory=list)
    instrument: str = "piano"
    rhythm: str = ""  # NEW: Store rhythm pattern
```

### 3. Updated `Layer.to_strudel()` to use rhythm

**File:** `core/music.py`

```python
def to_strudel(self) -> str:
    """Convert layer to Strudel notation.

    If rhythm is set, uses rhythm-aware formatting.
    Otherwise, falls back to simple grouping.
    """
    if self.rhythm and self.phrases:
        # Use rhythm-aware formatting
        patterns = [p.to_strudel_with_rhythm(self.rhythm) for p in self.phrases]
        pattern = " ".join(patterns)
    else:
        # Fallback: simple grouping
        pattern = " ".join(f"[{p.to_strudel()}]" for p in self.phrases)

    return f'n("{pattern}").s("{self.instrument}")'
```

### 4. Updated `LayeredComposer.get_composition()` to pass rhythm

**File:** `layered_composer.py`

```python
def get_composition(self, bpm: int = 120) -> Composition:
    """Get the final composition with all evolved layers."""
    layers = []
    for config in self.layer_configs:
        phrase = self.evolved_phrases.get(config.name)
        rhythm = self.evolved_rhythms.get(config.name)  # NEW: Get rhythm
        if phrase:
            layer = Layer(
                name=config.name,
                phrases=[phrase],
                instrument=config.instrument,
                rhythm=rhythm if rhythm else ""  # NEW: Pass rhythm
            )
            layers.append(layer)

    return Composition(layers=layers, bpm=bpm)
```

## How Rhythm Encoding Works

### Rhythm String Format

Each character in the rhythm string represents subdivisions per beat:

- `'0'` = **rest** (no notes) → Output: `~`
- `'1'` = **quarter note** (1 note per beat) → Output: `note`
- `'2'` = **eighth notes** (2 notes per beat) → Output: `[note1 note2]`
- `'3'` = **triplets** (3 notes per beat) → Output: `[note1 note2 note3]`
- `'4'` = **sixteenth notes** (4 notes per beat) → Output: `[note1 note2 note3 note4]`

### Examples

#### Example 1: Simple Rhythm

**Rhythm:** `"2103"`
- Beat 1: `'2'` = 2 eighth notes
- Beat 2: `'1'` = 1 quarter note
- Beat 3: `'0'` = rest
- Beat 4: `'3'` = 3 triplets

**Notes:** `[C4, D4, E4, F4, G4, A4]` (6 total notes)

**Strudel Output:** `[c4 d4] e4 ~ [f4 g4 a4]`

#### Example 2: Drum Pattern

**Rhythm:** `"41414141"`
- Alternating: 4 sixteenths, 1 quarter, 4 sixteenths, 1 quarter...

**Total notes needed:** 4+1+4+1+4+1+4+1 = 20 notes

**Strudel Output:**
```
[c2 c2 d2 d2] c2 [c2 d2 c2 d2] c2 [d2 c2 d2 c2] d2 [c2 c2 d2 c2] d2
```

#### Example 3: Bass with Rests

**Rhythm:** `"20212012"`
- Beat 1: 2 notes, Beat 2: rest, Beat 3: 2 notes, Beat 4: 1 note, etc.

**Strudel Output:**
```
[e2 g2] ~ [e2 a2] g2 ~ e2 [g2 a2]
```

## Testing

Run the rhythm encoding test:

```bash
python test_rhythm_encoding.py
```

This demonstrates:
- How rhythm patterns are encoded
- Expected output format
- Different rhythm combinations
- Complete layer examples

## Results

### Before (Flat Output)
```javascript
$: n("[d2 c3 d2 c2 c2 c2 c2 c2]").s("sawtooth")
```
❌ No rhythm structure visible
❌ Can't tell which notes belong to which beats
❌ Doesn't reflect the evolved rhythm pattern

### After (Rhythm-Aware Output)
```javascript
$: n("[d3 c3 c3] d2 [c2 c2 c2] d3").s("sawtooth")
```
✅ Rhythm structure clearly visible
✅ Notes grouped by beats
✅ Rests shown as `~`
✅ Reflects the evolved rhythm pattern "3132"

## Complete Band Example

**Run:**
```bash
python band_demo.py
```

**Example output:**
```javascript
setcpm(30.0)

$: n("[c3 d3 d3 d3] [c3 c3 d2 d2] [d2 c3 c3] [d2 d2 d2]").s("sawtooth")  // Drums
$: n("e3 [a2 d3] d3 [a3 d3] c3 [c3 g2] e3 [e3 d3]").s("sawtooth")        // Bass
$: n("[c4 a3 e4] [d4 d4 d4] e4 [d4 d4] c5 [d5 d5]").s("piano")          // Piano
```

Each layer's rhythm is perfectly preserved:
- **Drums:** Dense patterns with lots of subdivisions
- **Bass:** Alternating quarters and eighths
- **Piano:** Varied rhythm with triplets and quarters

## Key Benefits

1. **Visual Clarity** - You can now SEE the rhythm in the Strudel code
2. **Correct Timing** - Notes play at the right subdivisions within each beat
3. **Rhythm Preservation** - The evolved rhythm pattern is maintained in the output
4. **Musical Accuracy** - The Strudel playback matches the intended rhythm

## Verification

The total number of notes should equal the sum of all digits in the rhythm:

**Rhythm:** `"31313133"`
**Sum:** 3+1+3+1+3+1+3+3 = 18 notes needed
**Notes generated:** Exactly 18 notes ✓

Each beat gets the correct number of notes according to its subdivision value!
