# Strudel: Comprehensive Technical Reference for LLMs

## Overview

Strudel is a live coding system for creating algorithmic patterns, implemented in JavaScript. It is a port of TidalCycles (Tidal) from Haskell to JavaScript, designed to run entirely in web browsers without requiring any installation.

**Key Facts:**
- Project URL: https://strudel.cc
- License: GNU Affero Public Licence v3 (AGPL-3.0)
- Language: JavaScript (considering TypeScript migration)
- Architecture: Modular package-based system published to npm as @strudel/*
- Main Contributors: Felix Roos (primary), Alex McLean (co-creator)
- First Commit: January 22, 2022

## Core Philosophy

1. **Accessibility**: Runs entirely in browser, no installation needed
2. **Consistency**: Maintains Tidal's approach to pattern representation
3. **Modularity**: Extensible package-based architecture
4. **Simplicity**: Optimized syntax for live coding with minimal keystrokes

## Pattern System Architecture

### What are Patterns?

Patterns are the fundamental abstraction in Strudel. They represent flows of time as pure functions, supporting both:
- **Continuous changes** (like signals/waveforms)
- **Discrete events** (like musical notes)

Patterns use **functional reactive programming** principles from Haskell.

### Key Concept: Querying

**Querying** is the process of asking a Pattern for events within a specific time span.

```javascript
const pattern = sequence('c3', ['e3', 'g3'])
const events = pattern.queryArc(0, 1)  // Query from cycle 0 to 1
```

Output:
```javascript
["[ 0/1 -> 1/2 | c3 ]",   // c3 occupies first half
 "[ 1/2 -> 3/4 | e3 ]",   // e3 occupies first quarter of second half
 "[ 3/4 -> 1/1 | g3 ]"]   // g3 occupies second quarter of second half
```

**Important Properties:**
- Time is represented as **rational numbers** (fractions), not floating point, for precise musical timing
- Time units are measured in **cycles** (default: 1 cycle = 1 second, but configurable via tempo)
- Patterns are **pure functions** - they cannot be mutated, only replaced
- Patterns are **opaque** - you can only interact with them through querying

### Event Structure (Haps)

Events in Strudel are called **Haps** (to avoid conflict with JS built-in Event class).

Each Hap contains:
- **value**: The event data (can be any type - note, number, object, etc.)
- **whole.begin**: Start time as a rational number (Fraction)
- **whole.end**: End time as a rational number (Fraction)
- **part**: The active portion of the event (important for fragments)

### Pattern Transformation Model

Since patterns are immutable pure functions, transformations work by:
1. Creating a **new pattern** that wraps the old one
2. The new pattern can:
   - Manipulate the **query** before passing to old pattern
   - Manipulate the **results** after receiving from old pattern
3. This enables all temporal/structural manipulations in Strudel's library

Example transformation chain:
```javascript
pattern
  .fast(2)      // New pattern that queries old pattern at 2x speed
  .rev()        // New pattern that reverses events from previous
  .slow(3)      // New pattern that queries at 1/3 speed
```

## Time Representation

### Cycles
- The fundamental unit of time in Strudel
- Default: 1 cycle = 1 second
- Configurable via tempo/BPM settings
- All pattern operations are cycle-relative

### Rational Numbers (Fractions)
- Time points represented as ratios of two integers (e.g., 1/3, 5/8)
- Allows perfect representation of musical divisions impossible with floats
- **Performance consideration**: Converting float to rational is expensive
  - This is a known issue when porting to JavaScript
  - Conversions should happen early, not in hot loops
  - TypeScript migration might help catch these issues

## Mini Notation

A Domain Specific Language (DSL) for expressing rhythmic patterns concisely.

### Implementation
- Defined as a PEG (Parsing Expression Grammar) in `krill.pegjs`
- Based on [krill](https://github.com/Mdashdotdashn/krill) by Mdashdotdashn
- Parser generated using [peggy](https://peggyjs.org/)
- Parser transforms mini notation strings into ASTs
- ASTs are converted to Strudel function calls

### Key Syntax Elements

```javascript
// Sequential patterns
"c3 e3 g3"              // Three notes in sequence
sequence('c3', 'e3', 'g3')  // Equivalent JS

// Nested subsequences with brackets
"c3 [e3 g3]"            // c3 in first half, [e3 g3] share second half
seq('c3', seq('e3', 'g3'))  // Equivalent JS

// Rests/silence
"c3 ~ e3"               // c3, silence, e3
seq('c3', silence, 'e3')    // Equivalent JS

// Alternation with angle brackets
"c3 <e3 g3>"            // Alternates e3 and g3 each cycle
seq('c3', slowcat('e3', 'g3'))  // Equivalent JS

// Multiplication/repetition
"c3*4"                  // c3 repeated 4 times in one cycle
"[c3 e3]*2"             // Pattern repeated twice

// Euclidean rhythms
"[bd sd](3,8)"          // 3 pulses distributed over 8 steps
"[bd sd](3,8,1)"        // With offset of 1
.euclid(3, 8, 1)        // Method form
```

### Mini Notation AST Example

Input: `"c3 [e3 g3]"`

AST:
```json
{
  "type_": "pattern",
  "arguments_": { "alignment": "h" },
  "source_": [
    {
      "type_": "element",
      "source_": "c3",
      "location_": { "start": {...}, "end": {...} }
    },
    {
      "type_": "element",
      "source_": {
        "type_": "pattern",
        "source_": [
          { "type_": "element", "source_": "e3", ... },
          { "type_": "element", "source_": "g3", ... }
        ]
      }
    }
  ]
}
```

Transpiles to:
```javascript
seq(
  reify('c3').withLocation([1,1,1], [1,4,4]),
  seq(
    reify('e3').withLocation([1,5,5], [1,8,8]),
    reify('g3').withLocation([1,8,8], [1,10,10])
  )
)
```

## Code Transpilation System

Strudel uses AST manipulation to add syntax sugar for live coding ergonomics.

### Transpilation Pipeline

1. Parse user code with **acorn** (previously used shift-parser) → AST
2. Transform AST to add features
3. Generate code with **escodegen** → transpiled JavaScript
4. Evaluate transpiled code → Pattern instance

### Syntax Sugar Features

#### 1. Double Quotes → Mini Calls

Input:
```javascript
"c3 [e3 g3]*2"
```

Transpiled:
```javascript
mini("c3 [e3 g3]*2").withMiniLocation([1,0,0],[1,14,14])
```

- Double quotes and backticks become `mini()` calls
- Single quotes remain regular strings
- Source locations added for highlighting

#### 2. Pseudo Variables

Input:
```javascript
cat(c3, r, e3)
```

Transpiled:
```javascript
cat("c3", silence, "e3")
```

Common pseudo variables:
- Note-like names (c3, bb2, fs3) → strings
- `r` → `silence`

#### 3. Top Level Await

Input:
```javascript
const p = (await piano()).toDestination()
cat(c3).tone(p)
```

Transpiled:
```javascript
(async()=>{
  const p = (await piano()).toDestination();
  return cat("c3").tone(p);
})()
```

#### 4. Operator Overloading (potential future feature)

Currently Strudel uses method calls instead:
```javascript
// Desired (not yet implemented)
"c3 e3" * 4

// Current approach
cat("c3", "e3").fast(4)
```

### Source Location Tracking

Both JS and mini notation parsers track source locations:

```javascript
// JS transpiler adds location for entire expression
mini("c3 e3").withMiniLocation([1,0,0],[1,7,7])

// Mini parser adds relative locations within the string
seq(
  reify('c3').withLocation([1,1,1], [1,4,4]),
  reify('e3').withLocation([1,5,5], [1,7,7])
)
```

**Purpose**: Enables real-time highlighting of active code during playback

## Scheduling System

The scheduler continuously queries patterns and triggers events.

### Scheduler Algorithm (Simplified)

```javascript
let pattern = seq('c3', ['e3', 'g3']); // Pattern from user
let interval = 0.5;        // Query interval in seconds
let time = 0;              // Current time span start
let minLatency = 0.1;      // Minimum trigger latency

setInterval(() => {
  const haps = pattern.queryArc(time, time + interval);
  time += interval;

  haps.forEach((hap) => {
    const deadline = hap.whole.begin - time + minLatency;
    onTrigger(hap, deadline, duration);
  });
}, interval * 1000);
```

### Scheduler Parameters

**Current Strudel REPL defaults:**
- Query interval: 50ms
- Minimum latency: 100ms
- **Total latency**: Between 100ms and 150ms from code evaluation to audio

**Key Properties:**
- Pure functional querying allows any interval without changing output
- Pattern can be changed mid-playback - next tick uses new pattern
- Actual implementation compensates for `setInterval` imprecision
- See: https://loophole-letters.vercel.app/web-audio-scheduling

## Control Parameters

Control parameters are how you manipulate multiple aspects of sound in parallel.

### How They Work

```javascript
note("c3 e3")
  .cutoff(1000)
  .s('sawtooth')
  .queryArc(0, 1)
  .map(hap => hap.value)

// Results in event values:
[
  { note: 'c3', cutoff: 1000, s: 'sawtooth' },
  { note: 'e3', cutoff: 1000, s: 'sawtooth' }
]
```

### Parameter Input Types

Each control parameter function accepts:
1. **Primitive value**: `cutoff(1000)` - same value for all events
2. **Array/sequence**: `cutoff([500, 1000, 2000])` - creates pattern
3. **Pattern**: `cutoff(sine.range(200, 1000))` - modulation pattern

### Common Audio Control Parameters

**Sound source:**
- `s(name)`: Sound/sample name ('bd', 'sawtooth', etc.)
- `n(index)`: Sample bank index
- `bank(prefix)`: Sample bank prefix
- `note(value)`: Musical note (MIDI number or note name)
- `freq(hz)`: Frequency in Hertz

**Timing:**
- `legato(factor)`: Duration multiplier
- `clip(factor)`: Another duration multiplier
- `begin(0-1)`: Sample start point (normalized)
- `end(0-1)`: Sample end point (normalized)

**Amplitude:**
- `gain(0-1+)`: Main volume control
- `velocity(factor)`: Additional gain multiplier

**Filters:**
- `cutoff(freq)`: Low-pass filter frequency
- `resonance(q)`: Low-pass filter resonance
- `hcutoff(freq)`: High-pass filter frequency
- `hresonance(q)`: High-pass filter resonance
- `bandf(freq)`: Band-pass filter frequency
- `bandq(q)`: Band-pass filter Q/resonance
- `vowel("a"|"e"|"i"|"o"|"u")`: Vowel formant filter

**Effects:**
- `delay(wet)`: Delay mix (0-1)
- `delaytime(seconds)`: Delay time
- `delayfeedback(amount)`: Delay feedback
- `room(wet)`: Reverb mix (0-1)
- `size(amount)`: Reverb room size
- `crush(bits)`: Bit crusher
- `distort(amount)`: Distortion
- `pan(0-1)`: Stereo pan (0=left, 1=right)
- `phaser(speed)`: Phaser speed
- `phaserdepth(amount)`: Phaser depth
- `phasersweep(range)`: Phaser LFO sweep range
- `phasercenter(freq)`: Phaser center frequency

**Envelope:**
- `attack(seconds)`: Attack time
- `decay(seconds)`: Decay time
- `sustain(level)`: Sustain level
- `release(seconds)`: Release time

**Advanced:**
- `orbit(name)`: Effect bus routing (same orbit = shared effects)
- `cut(group)`: Cut group (same group cuts each other)
- `speed(factor)`: Playback speed/pitch multiplier

### Creating Custom Parameters

```javascript
const { x, y } = createParams('x', 'y')
x(sine.range(0, 200)).y(cosine.range(0, 200))
// Creates pattern describing circle coordinates
```

## Pattern Alignment and Combination

One of Strudel's most powerful features is flexible pattern combination.

### Default Alignment: `.in` (implicit)

When combining patterns, the second pattern's values are applied **into** the first pattern's structure:

```javascript
"0 [1 2] 3".add("10 20")
// Equivalent to:
"10 [11 22] 23"

// Same as explicit:
"0 [1 2] 3".add.in("10 20")
```

**How it works:**
1. Cycles align (both start at cycle 0)
2. Events from first pattern are matched with events from second
3. When partial overlap occurs, events become **fragments**

### Fragment Concept

```javascript
"0 1 2".add("10 20")
// Result:
"10 [11 21] 20"
```

- The `1` is split into two fragments
- First fragment (11): active for 1/6 cycle, but "remembers" duration of 1/3
- Second fragment (21): missing its start, so wouldn't trigger sound
- Fragments maintain reference to original event timing

### Alignment Methods

#### `.in` - Into Left Structure (default)
```javascript
"0 1 2".add.in("10 20")
// Values from right applied into left structure
```

#### `.out` - Into Right Structure
```javascript
"0 1 2".add.out("10 20")
// Values from left applied into right structure
// Equivalent to: "10 20".add.in("0 1 2")
```

#### `.mix` - Combine Both Structures
```javascript
"0 1 2".add.mix("10 20")
// New events created at intersections
// No fragments - all events are complete
```

#### `.squeeze` - Squeeze Right into Left Events
```javascript
"0 1 2".add.squeeze("10 20")
// Equivalent to: "[10 20] [11 21] [12 22]"
// Full cycles of right pattern squeezed into each left event
```

#### `.squeezeout` - Squeeze Left into Right Events
```javascript
"0 1 2".add.squeezeout("10 20")
// Equivalent to: "[10 11 12] [20 21 22]"
```

#### `.trig` - Trigger Left Cycles from Right Events
```javascript
"0 1 2 3 4 5 6 7".add.trig("10 [20 30]")
// Equivalent to: "10 11 12 13 20 21 30 31"
// Right events trigger left pattern cycles (truncated to fit)
```

#### `.trigzero` - Trigger from First Cycle
```javascript
// Similar to .trig but always starts from cycle 0
// Only differs when left pattern varies by cycle
```

### Alignment Operators (Haskell vs JavaScript)

**Tidal (Haskell):**
```haskell
"0 1 2" |+ "10 20"   -- .in (into left)
"0 1 2" +| "10 20"   -- .out (into right)
"0 1 2" |+| "10 20"  -- .mix
"0 1 2" ||+ "10 20"  -- .squeeze
```

**Strudel (JavaScript):**
```javascript
"0 1 2".add.in("10 20")
"0 1 2".add.out("10 20")
"0 1 2".add.mix("10 20")
"0 1 2".add.squeeze("10 20")
```

JavaScript lacks custom infix operators, so uses method chaining.

## Sound Output Systems

Strudel supports multiple output targets for maximum flexibility.

### 1. Web Audio API (Default - via superdough)

**Package**: `@strudel/webaudio` + `superdough`

**Approach**: Fire-and-forget - creates new audio graph per event

**Features:**
- Basic oscillators (sine, sawtooth, square, triangle)
- Sample playback with buffers
- Effects chain (filters, delay, reverb, distortion, etc.)
- Experimental soundfont support
- Orbit-based effect buses

**Example:**
```javascript
note("c3 [e3 g3]")
  .s("sawtooth")
  .cutoff(1000)
  .room(0.5)
```

**Simple onTrigger implementation:**
```javascript
function onTrigger(hap, deadline, duration) {
  const { note } = hap.value;
  const time = getAudioContext().currentTime + deadline;
  const o = getAudioContext().createOscillator();
  o.frequency.value = getFreq(note);
  o.start(time);
  o.stop(time + duration);
  o.connect(getAudioContext().destination);
}
```

### 2. OSC (Open Sound Control)

**Package**: `@strudel/osc`

**Use Case**: SuperDirt integration (Tidal's standard synthesis engine)

**Requirements**: Node.js-based OSC proxy server

**Features:**
- Network message transmission
- Compatible with SuperCollider + SuperDirt
- Access to SuperDirt's extensive sample library and effects

**Example:**
```javascript
pattern.osc()  // Route to SuperDirt
```

### 3. MIDI

**Package**: `@strudel/midi`

**Features:**
- Direct MIDI output (no proxy needed)
- Works in Chromium browsers (WebMIDI API)
- Route to external hardware or DAWs

**Example:**
```javascript
pattern.midi()
```

### 4. CSound

**Package**: `@strudel/csound`

**Technology**: CSound WebAssembly build

**Features:**
- Embed CSound "orchestra" synthesizers
- Advanced sound design capabilities
- All processing happens in browser

**Example:**
```javascript
pattern.csound(/* csound instrument */)
```

### 5. Serial (WebSerial)

**Package**: `@strudel/serial`

**Use Case**: Microcontroller/hardware control

**Features:**
- Robot choreography
- Hardware interfacing
- LED control, motor control, etc.

**Example:**
```javascript
pattern.serial()
```

### 6. Deprecated/Experimental Outputs

**Tone.js** (`@strudel/tone`):
- Deprecated due to performance issues
- Creating many Tone.js instruments caused problems
- Fire-and-forget approach of Web Audio better suited

**WebDirt** (`@strudel/webdirt`):
- Deprecated in favor of direct Web Audio
- Originally from Estuary project
- Now integrated into main Web Audio approach

**Speech** (`@strudel/core`):
- Experimental
- Text-to-speech synthesis
- `.speak()` method

## Pattern Library - Common Functions

### Creation Functions

**Sequencing:**
- `sequence(a, b, c)` / `seq(a, b, c)`: Sequential pattern
- `cat(a, b, c)`: Each element lasts one full cycle
- `slowcat(a, b, c)`: Alias for cat
- `fastcat(a, b, c)`: All elements in one cycle

**Stacking:**
- `stack(a, b, c)`: Play patterns simultaneously
- `polymeter(...)`: Polymetric pattern

**From notation:**
- `mini(string)`: Parse mini notation

### Temporal Transformations

**Speed:**
- `.fast(n)`: Speed up by factor n
- `.slow(n)`: Slow down by factor n

**Repetition:**
- `.echo(times, delay, velocity)`: Echo effect
- `.stut(times, feedback, delay)`: Like echo but consistent with Tidal
- `.iter(n)`: Cycle through shifted versions

**Reversal/Symmetry:**
- `.rev()`: Reverse pattern
- `.palindrome()`: Play forward then backward

**Time shifts:**
- `.early(cycles)`: Shift earlier in time
- `.late(cycles)`: Shift later in time
- `.off(time, function)`: Layer pattern on itself with offset

### Structural Transformations

**Selection:**
- `.every(n, function)`: Apply function every n cycles
- `.sometimesBy(probability, function)`: Random application
- `.sometimes(function)`: 50% chance
- `.often(function)`: 75% chance
- `.rarely(function)`: 25% chance

**Chopping:**
- `.chop(n)`: Divide into n equal parts
- `.slice(n, pattern)`: Slice sample into parts
- `.striate(n)`: Granular/glitchy chopping

### Value Transformations

**Arithmetic:**
- `.add(n)`: Add values
- `.sub(n)`: Subtract values
- `.mul(n)`: Multiply values
- `.div(n)`: Divide values

**Musical:**
- `.scale(name)`: Map numbers to scale (e.g., 'D minor')
- `.transpose(n)`: Transpose by semitones

**Continuous patterns:**
- `sine`: Sine wave (0 to 1)
- `cosine`: Cosine wave
- `saw`: Sawtooth wave
- `square`: Square wave
- `tri`: Triangle wave

**Range mapping:**
- `sine.range(min, max)`: Map sine to range
- `sine.slow(n)`: Slow down LFO

## REPL (Live Coding Interface)

The Strudel REPL is the main user interface for live coding.

### REPL Architecture

**Control Flow:**
1. User writes/updates code in CodeMirror editor
2. Code is transpiled (AST transformation)
3. Transpiled code is evaluated → Pattern instance
4. Scheduler queries Pattern at regular intervals
5. Events trigger via selected output
6. Visual feedback highlights active code

### Visual Feedback Features

**Real-time highlighting:**
- Active code sections highlighted during playback
- Uses source location tracking from transpilation
- Shows which mini notation elements are currently playing

**Built-in visualizations:**
- Piano roll view
- Waveform displays
- Custom pattern visualizations

### REPL Setup Example

```javascript
import { repl } from "@strudel/core";
import { webaudioOutput, getAudioContext } from "@strudel/webaudio";

const { scheduler } = repl({
  defaultOutput: webaudioOutput,
  getTime: () => getAudioContext().currentTime
});

scheduler.setPattern(pattern);
scheduler.start();
scheduler.stop();
```

## Package Structure

Strudel is organized into modular npm packages under `@strudel/*`.

### Core Packages

**@strudel/core**
- Bare essence of pattern representation
- Pattern class and combinators
- Querying system
- Fraction (rational number) implementation
- No dependencies on audio/web

**@strudel/mini**
- Mini notation parser
- PEG grammar (krill.pegjs)
- AST generation and processing
- Source location tracking

**@strudel/transpiler**
- JavaScript AST manipulation
- Acorn parser integration
- Escodegen code generation
- Syntax sugar implementation

### Output Packages

**@strudel/webaudio**
- Web Audio API integration
- Thin wrapper around superdough
- `webaudioOutput` function
- Audio context helpers

**superdough** (standalone package)
- Core audio engine
- Sample loading and management
- Synth sound registration
- Effect processing
- Can be used without Strudel

**@strudel/midi**
- WebMIDI integration
- MIDI message generation
- Port selection

**@strudel/osc**
- OSC message formatting
- Proxy server communication
- SuperDirt compatibility

**@strudel/csound**
- CSound WASM integration
- Orchestra file parsing
- Instrument triggering

**@strudel/serial**
- WebSerial API wrapper
- Microcontroller communication

### UI Packages

**@strudel/repl**
- Main REPL application
- Pattern evaluation loop
- Scheduler implementation

**@strudel/codemirror**
- CodeMirror editor integration
- Syntax highlighting
- Code evaluation triggers

**@strudel/draw**
- Visualization utilities
- Pattern drawing
- Visual feedback

**@strudel/hydra**
- Hydra visual synthesis integration
- Pattern-driven visuals

### Utility Packages

**@strudel/tonal**
- Music theory utilities
- Scale definitions
- Chord support
- Voice leading
- Integration with @tonaljs library

**@strudel/xen**
- Xenharmonic/microtonal support
- Alternative tuning systems
- Just intonation

**@strudel/soundfonts**
- SoundFont loading
- Instrument management

**@strudel/sampler**
- Sample loading utilities
- Buffer management

### Integration Packages

**@strudel/embed**
- Embedding Strudel in other sites
- Standalone widget

**@strudel/desktopbridge**
- Desktop application bridge
- Native integration features

**@strudel/gamepad**
- Game controller input
- Pattern control via gamepad

**@strudel/motion**
- Motion sensor input
- Accelerometer patterns

**@strudel/mqtt**
- MQTT protocol support
- IoT integration

## Comparing Strudel to Tidal

### Syntax Philosophy

**Tidal (Haskell):**
- Terse, mathematical notation
- Custom infix operators
- Strong static typing
- `$` operator for precedence

Example:
```haskell
iter 4 $ every 3 (||+ n "10 20") $ (n "0 1 3") # s "triangle" # crush 4
```

**Strudel (JavaScript):**
- Method chaining with `.`
- Spelled-out operations
- Dynamic typing (potential TypeScript migration)
- More parentheses, but more readable

Example:
```javascript
n("0 1 3").every(3, add.squeeze("10 20")).iter(4).s("triangle").crush(4)
```

### Trade-offs

**Tidal advantages:**
- More concise syntax
- Type safety catches errors early
- Cleaner composition with `$` and operators

**Strudel advantages:**
- Easier to learn for beginners
- No installation required (browser-based)
- Access to JavaScript ecosystem
- More approachable method-chaining style

**Hypothesis**: Haskell syntax is cleaner, but Strudel is easier to learn.

### Technical Differences

**Type System:**
- Tidal: Strong static typing, type inference
- Strudel: Dynamic (causes issues with float→rational conversion)

**Time Representation:**
- Both use rational numbers
- Strudel has performance issues with late float→rational conversion
- TypeScript migration could help

**Development:**
- Tidal: Better for core pattern theory development
- Strudel: Better for interface experiments and rapid iteration

**Feature parity:**
- Strudel approaching full parity with Tidal
- Some Tidal functions still being ported
- Mini notation not yet 100% compatible

## Key Implementation Details

### Pattern as Pure Function

```javascript
class Pattern {
  constructor(query) {
    this.query = query;  // Function: TimeSpan → [Hap]
  }

  queryArc(begin, end) {
    return this.query(new TimeSpan(begin, end));
  }

  // All transformations return new Pattern
  fast(factor) {
    return new Pattern(span => {
      // Query the old pattern at faster speed
      const newSpan = span.scale(factor);
      return this.query(newSpan);
    });
  }
}
```

### Hap (Event) Structure

```javascript
class Hap {
  constructor(whole, part, value, context) {
    this.whole = whole;    // TimeSpan of full event
    this.part = part;      // TimeSpan of active portion
    this.value = value;    // Event data (note, params, etc.)
    this.context = context; // Metadata (locations, etc.)
  }

  // Check if event should trigger (has beginning)
  hasOnset() {
    return this.whole.begin.equals(this.part.begin);
  }
}
```

### TimeSpan and Fraction

```javascript
class Fraction {
  constructor(numerator, denominator) {
    this.n = numerator;
    this.d = denominator;
  }

  toFraction() { return `${this.n}/${this.d}`; }
  toFloat() { return this.n / this.d; }
}

class TimeSpan {
  constructor(begin, end) {
    this.begin = Fraction.from(begin);
    this.end = Fraction.from(end);
  }

  duration() {
    return this.end.sub(this.begin);
  }
}
```

## Advanced Pattern Techniques

### Polymeter Example

```javascript
"{c3 e3 g3, c2 g2}"
// First pattern: 3 steps
// Second pattern: 2 steps
// Results in interesting phase relationships
```

### Euclidean Rhythms

Based on Euclidean algorithm for distributing pulses evenly:

```javascript
"bd(3,8)"        // 3 kicks over 8 steps
"bd(3,8,1)"      // With offset of 1
"bd(5,8)"        // 5 over 8 (different pattern)
```

Reference: Toussaint's "The Euclidean Algorithm Generates Traditional Musical Rhythms"

### Continuous Modulation

```javascript
note("c3 e3 g3")
  .cutoff(sine.range(200, 2000).slow(4))  // Slow filter sweep
  .gain(saw.range(0.3, 0.8).fast(8))      // Fast gain modulation
```

### Conditional Transformations

```javascript
note("c3 e3 g3 a3")
  .every(4, rev)                    // Reverse every 4th cycle
  .sometimesBy(0.3, x => x.fast(2)) // 30% chance of doubling speed
  .rarely(x => x.add(12))           // 25% chance of octave up
```

### Layer Offsetting

```javascript
note("c3 e3 g3")
  .off(1/4, x => x.add(7))      // Add fifth, delayed 1/4 cycle
  .off(1/2, x => x.add(12))     // Add octave, delayed 1/2 cycle
  .s("sawtooth")
```

## Performance Considerations

### Rational Number Conversions

**Problem**: Float→Rational conversion is computationally expensive

**Solution**:
- Convert floats to rationals early in pipeline
- Avoid conversions in hot loops (querying/scheduling)
- Consider TypeScript to catch late conversions

### Audio Context Timing

**Web Audio scheduling**: Use `AudioContext.currentTime` for precise timing

```javascript
const deadline = getAudioContext().currentTime + timeUntilEvent;
oscillator.start(deadline);
oscillator.stop(deadline + duration);
```

### Event Query Optimization

**Principle**: Pattern querying is pure and stateless

**Implications:**
- Can cache query results for same time span
- Can query in parallel
- Can change query interval without affecting output

### Browser Compatibility

**WebMIDI**: Chromium browsers only (Chrome, Edge, Opera)
**WebSerial**: Chromium browsers only
**Web Audio**: All modern browsers
**OSC**: Requires Node.js proxy (not browser limitation)

## Future Development Directions

### Planned Features

1. **Sound Engines:**
   - Glicol integration
   - Faust integration
   - WASM-based synthesis

2. **Pattern System:**
   - Tidal 2.0 sequence representation
   - Full mini notation compatibility
   - Improved pattern alignment options

3. **Outputs:**
   - Graphical rendering
   - Choreographic/movement output
   - Video synthesis

4. **Editing:**
   - Multi-user collaborative editing
   - Custom syntax parser (escape JavaScript constraints)
   - Hardware/e-textile interfaces

5. **Type System:**
   - TypeScript migration for better performance
   - Catch rational conversion issues
   - Better IDE support

### Research Areas

1. **Musical Algorithms:**
   - Voice leading
   - Harmonic programming
   - Microtonal/xenharmonic systems

2. **Interfaces:**
   - Alternative notation systems
   - Visual pattern builders
   - Hybrid text/graphical editing

3. **Performance:**
   - Optimize pattern querying
   - Reduce memory allocations
   - Improve real-time responsiveness

## Common Patterns and Idioms

### Basic Pattern Construction

```javascript
// Simple sequence
note("c3 e3 g3 c4")

// Nested rhythms
note("c3 [e3 g3] c4 [g3 e3 c3]")

// With rests
note("c3 ~ e3 ~ g3 ~ c4 ~")

// Alternating values
note("c3 <e3 g3 bb3>")
```

### Adding Parameters

```javascript
// Chain methods
note("c3 e3 g3")
  .s("sawtooth")
  .cutoff(1000)
  .room(0.3)

// Parameters from patterns
note("c3 e3 g3")
  .s("<sawtooth square triangle>")
  .cutoff("1000 2000 500")
```

### Transformations

```javascript
// Speed changes
note("c3 e3 g3").fast(2)
note("c3 e3 g3").slow(0.5)

// Reversal
note("c3 e3 g3").rev()

// Conditionals
note("c3 e3 g3 a3")
  .every(4, x => x.rev())
  .sometimes(x => x.fast(2))
```

### Scales and Harmony

```javascript
// Scale mapping
"0 2 4 7"
  .scale('C major')
  .note()

// Transposition
note("c3 e3 g3")
  .transpose(7)  // Perfect fifth up

// Chord voicings
"<[c3,e3,g3] [f3,a3,c4] [g3,b3,d4]>"
  .note()
```

### Combination

```javascript
// Stack patterns
stack(
  note("c2").s("sawtooth"),
  note("c3 e3 g3").s("square"),
  s("bd sd bd sd")
)

// Combine with alignment
note("c3 e3 g3")
  .add.squeeze("0 7 12")  // Add intervals
  .scale('C minor')
```

## Debugging Tips

### View Events

```javascript
pattern
  .queryArc(0, 1)
  .map(hap => hap.show())
  .forEach(console.log)
```

### Visual Feedback

```javascript
pattern
  .pianoroll()  // Show in piano roll
  .logValues()  // Log values to console
```

### Isolate Issues

```javascript
// Test pattern without audio
pattern.query(0, 4)

// Test small snippets
mini("c3 e3").firstCycle()

// Check transpilation
// (view in browser console during evaluation)
```

## Glossary

**Arc**: A span of time, synonym for TimeSpan

**Cycle**: The fundamental unit of time in patterns (default 1 second)

**Hap**: An event in Strudel (from "happening"). Contains whole, part, value, context

**Mini Notation**: Domain-specific language for expressing rhythms concisely

**Pattern**: Pure function from TimeSpan to array of Haps

**Query/Querying**: Asking a pattern for events within a time span

**REPL**: Read-Eval-Print-Loop, the live coding interface

**Transpilation**: Converting user JavaScript to add syntax sugar

**Whole**: The complete time span of an event (even if only partially active)

**Part**: The active portion of an event's time span

**Fragment**: Partial event created when patterns combine with partial overlap

**Control Parameter**: Function that adds a property to event values (note, cutoff, etc.)

**Alignment**: Method for combining pattern structures (.in, .out, .mix, .squeeze, etc.)

**Orbit**: Effect bus for routing sounds through shared effects

---

# PRACTICAL EXAMPLES AND DETAILED FEATURES

This section provides comprehensive examples from the Strudel documentation, showing practical usage patterns for all major features.

## Mini Notation - Complete Syntax Reference

### String Formats

**Double quotes or backticks**: Parsed as mini notation
```javascript
note("c3 e3 g3")           // Mini notation
note(`c3 e3 g3`)           // Multi-line mini notation
```

**Single quotes**: Regular JavaScript strings (NOT parsed)
```javascript
s('bd')                     // Regular string
```

### Sequential Patterns

**Space-separated events** divide time equally within a cycle:

```javascript
note("c e g b")             // 4 notes, each 1/4 cycle
note("c d e f g a b")       // 7 notes, each 1/7 cycle
```

Key concept: Adding events doesn't increase duration, it divides the cycle into smaller parts.

### Nested Sequences (Brackets)

**Brackets `[]`** create subdivisions:

```javascript
note("e5 [b4 c5] d5 c5 b4")           // b4 and c5 share time of one event
note("e5 [b4 c5] d5 [c5 b4]")         // Two subdivided events
note("e5 [b4 c5] d5 [c5 b4 d5 e5]")   // Subdivision with 4 events
note("e5 [b4 c5] d5 [c5 b4 [d5 e5]]") // Nested subdivisions
```

Subdivisions divide the duration of their parent event equally among children.

### Rests

**Tilde `~`** represents silence:

```javascript
note("bd ~ sd ~")               // Bass drum, rest, snare, rest
note("[b4 [~ c5] d5 e5]")      // Rest within subdivision
```

### Alternation (Angle Brackets)

**Angle brackets `<>`** alternate elements each cycle:

```javascript
note("<e5 b4 d5 c5>")          // e5 in cycle 0, b4 in cycle 1, etc.
note("c3 <e3 g3>")             // c3 constant, second alternates
```

Equivalent to division by number of elements:
```javascript
"<a b c d>" === "[a b c d]/4"
```

With multiplication:
```javascript
note("<e5 b4 d5 c5 a4 c5>*8")  // 8 notes per cycle, cycling through
```

### Multiplication

**Asterisk `*`** repeats patterns:

```javascript
note("[e5 b4 d5 c5]*2")          // Pattern plays twice per cycle
note("[e5 b4 d5 c5]*2.75")       // Decimal multiplication
note("bd*4")                      // 4 bass drums per cycle
note("hh*16")                     // 16 hihats per cycle
```

### Division

**Slash `/`** slows patterns:

```javascript
note("[e5 b4 d5 c5]/2")          // Pattern over 2 cycles
note("[e5 b4 d5 c5]/2.75")       // Decimal division
```

### Polyphony (Chords)

**Commas `,`** play events simultaneously:

```javascript
note("[g3,b3,e4]")                         // Single chord
note("g3,b3,e4")                           // Same thing
note("<[g3,b3,e4] [a3,c3,e4]>*2")         // Chord progression
```

### Elongation

**At sign `@`** sets temporal weight:

```javascript
note("<[g3,b3,e4]@2 [a3,c3,e4]>*2")       // First chord twice as long
```

Default weight is 1.

### Replication

**Exclamation `!`** repeats without speeding up:

```javascript
note("<[g3,b3,e4]!2 [a3,c3,e4]>*2")       // Repeat chord twice
```

### Randomness

**Question mark `?`** adds 50% probability of removal:

```javascript
note("[g3,b3,e4]*8?")                      // Each event has 50% chance
note("[g3,b3,e4]*8?0.1")                   // 10% chance of removal
note("[g3,b3,e4]*8?0.9")                   // 90% chance of removal
```

**Pipe `|`** chooses randomly:

```javascript
note("[g3,b3,e4] | [a3,c3,e4] | [b3,d3,f#4]")  // Random choice each cycle
```

### Euclidean Rhythms

**Parentheses `(beats, steps, offset)`** distribute beats evenly:

```javascript
s("bd(3,8)")              // 3 beats over 8 steps
s("bd(3,8,0)")           // With offset 0 (default)
s("bd(3,8,3)")           // Offset by 3 steps
```

Famous patterns:
```javascript
s("bd(3,8)")             // "Pop Clave" rhythm
s("bd(5,8)")             // Different distribution
s("bd(7,8)")             // Nearly full
```

Parameters:
- **beats**: How many events to play
- **steps**: Total number of positions
- **offset**: Starting position (optional, default 0)

Complex euclidean examples:
```javascript
note("e5(2,8) b4(3,8) d5(2,8) c5(3,8)").slow(2)
s("bd(3,8,0), hh cp")                    // Multiple layers
s("bd(3,8,3), hh cp")                    // With offset
```

### Sample Selection

**Colon `:`** selects sample number:

```javascript
s("hh:0 hh:1 hh:2 hh:3")           // Select from bank
s("bd*4,hh:0 hh:1 hh:2 hh:3")      // In combination
```

### Mini Notation Summary Table

| Syntax | Function | Example |
|--------|----------|---------|
| `a b c` | Sequential | `"c e g"` |
| `[a b]` | Subdivision | `"c [e g]"` |
| `~` | Rest/silence | `"c ~ e ~"` |
| `<a b>` | Alternation | `"<c e g>"` |
| `*n` | Multiply/repeat | `"c*4"` |
| `/n` | Divide/slow | `"[c e g]/2"` |
| `a,b` | Polyphony | `"c,e,g"` |
| `@n` | Elongation | `"c@2 e"` |
| `!n` | Replication | `"c!3"` |
| `?` | Randomness (50%) | `"c?"` |
| `?n` | Randomness (n%) | `"c?0.3"` |
| `a\|b` | Random choice | `"c\|e\|g"` |
| `(b,s)` | Euclidean | `"bd(3,8)"` |
| `(b,s,o)` | Euclidean+offset | `"bd(3,8,2)"` |
| `:n` | Sample select | `"bd:2"` |

## Sample System

### Default Sample Names

Strudel loads samples from [tidal-drum-machines](https://github.com/ritchse/tidal-drum-machines) and [VCSL](https://github.com/sgossner/VCSL) by default.

**Drum Abbreviations:**
- `bd` - Bass drum / Kick
- `sd` - Snare drum
- `rim` - Rimshot
- `cp` - Clap
- `hh` - Closed hi-hat
- `oh` - Open hi-hat
- `cr` - Crash
- `rd` - Ride
- `ht` - High tom
- `mt` - Medium tom
- `lt` - Low tom

**Percussion:**
- `sh` - Shakers, maracas
- `cb` - Cowbell
- `tb` - Tambourine
- `perc` - Other percussion
- `misc` - Miscellaneous
- `fx` - Effects

### Using Sound Banks

Samples are prefixed with drum machine names:

```javascript
s("RolandTR808_bd RolandTR808_sd")
```

Use `bank()` to simplify:

```javascript
s("bd sd,hh*16").bank("RolandTR808")
s("bd sd,hh*16").bank("<RolandTR808 RolandTR909>")  // Pattern banks!
```

### Selecting Samples with `n`

Multiple samples available per sound (e.g., `RolandTR909_hh(4)` has 4 samples):

```javascript
s("hh*8").bank("RolandTR909").n("0 1 2 3")          // Cycle through 4
s("hh*8").bank("RolandTR909").n("0 1 2 3 4 5 6 7")  // Wraps around
```

Numbers that exceed available samples wrap around.

### Loading Custom Samples

**From URLs:**

```javascript
samples({
  bassdrum: 'bd/BT0AADA.wav',
  hihat: 'hh27/000_hh27closedhh.wav',
  snaredrum: ['sd/rytm-01-classic.wav', 'sd/rytm-00-hard.wav'],  // Multiple
}, 'https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/')

s("bassdrum snaredrum:0 bassdrum snaredrum:1, hihat*16")
```

**From strudel.json file:**

```javascript
samples('https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/strudel.json')
s("bd sd bd sd,hh*16")
```

JSON format:
```json
{
  "_base": "https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/",
  "bassdrum": "bd/BT0AADA.wav",
  "snaredrum": ["sd/rytm-01-classic.wav", "sd/rytm-00-hard.wav"],
  "hihat": "hh27/000_hh27closedhh.wav"
}
```

**GitHub shortcut:**

```javascript
samples('github:tidalcycles/dirt-samples')        // Uses main branch
samples('github:user/repo/branch')                 // Specify branch
```

Assumes `strudel.json` at repository root.

**From local disk** (REPL only):
1. Go to `sounds` tab
2. Click "import sounds folder"
3. Select folder with audio files
4. Samples appear in `user` tab

**Via @strudel/sampler** (NodeJS):

```sh
cd samples
npx @strudel/sampler
```

Then load:
```javascript
samples('http://localhost:5432/')
n("<0 1 2>").s("swoop smash")
```

### Pitched Samples

Specify base pitch for tuned playback:

```javascript
samples({
  'gtr': 'gtr/0001_cleanC.wav',
  'moog': { 'g3': 'moog/005_Mighty%20Moog%20G3.wav' },
}, 'github:tidalcycles/dirt-samples')

note("g3 [bb3 c4] <g4 f4 eb4 f3>@2").s("gtr,moog")
```

Multiple pitch regions:

```javascript
samples({
  'moog': {
    'g2': 'moog/004_Mighty%20Moog%20G2.wav',
    'g3': 'moog/005_Mighty%20Moog%20G3.wav',
    'g4': 'moog/006_Mighty%20Moog%20G4.wav',
  }
}, 'github:tidalcycles/dirt-samples')

note("g2!2 <bb2 c3>!2, <c4@3 [<eb4 bb3> g4 f4]>").s('moog')
```

Sampler picks closest pitch automatically.

### Shabda Integration

Query samples from [freesound.org](https://freesound.org/):

```javascript
samples('shabda:bass:4,hihat:4,rimshot:2')

$: n("0 1 2 3 0 1 2 3").s('bass')
$: n("0 1*2 2 3*2").s('hihat').clip(1)
```

Text-to-speech samples:

```javascript
samples('shabda/speech:the_drum,forever')
samples('shabda/speech/fr-FR/m:magnifique')  // Language and gender

$: s("the_drum*2").chop(16)
$: s("forever magnifique").slow(4)
```

### Sample Playback Controls

**begin / end**: Set playback region (0-1)

```javascript
s("bd").begin(0.25)        // Start 25% in
s("bd").end(0.5)          // Stop halfway
s("bd").begin(0.25).end(0.75)  // Play middle section
```

**loop**: Loop sample

```javascript
s("bd").loop(1)           // Loop enabled
```

**loopBegin / loopEnd**: Set loop region

```javascript
s("bd").loopBegin(0.2).loopEnd(0.8)
```

**speed**: Playback speed/pitch

```javascript
s("bd").speed(2)          // Double speed, octave up
s("bd").speed(0.5)        // Half speed, octave down
s("bd").speed("<1 2 0.5 -1>")  // Pattern speed, -1 = reverse
```

**chop**: Granular slicing

```javascript
s("bd").chop(8)           // Divide into 8 slices
s("the_drum*2").chop(16).speed(rand.range(0.85,1.1))
```

**cut**: Cut groups (samples cut each other)

```javascript
s("hh*8").cut(1)          // All hihats in cut group 1
```

**clip / legato**: Duration multiplier

```javascript
note("c e g").clip(0.5)    // Half duration
note("c e g").legato(0.5)  // Same as clip
```

### Sound Aliases

Create custom names:

```javascript
soundAlias('RolandTR808_bd', 'kick')
s("kick")
```

## Synthesizer Engine

### Basic Waveforms

Select with `sound()` or `s()`:

```javascript
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("<sawtooth square triangle sine>")
```

Available waveforms:
- `sine` - Smooth sine wave
- `sawtooth` - Bright, buzzy
- `square` - Hollow, clarinet-like
- `triangle` - Default for note(), softer than saw

Default: If you use `note()` without `sound()`, it defaults to `triangle`.

### Noise Sources

Use as sound source:

```javascript
sound("<white pink brown>")     // Different noise colors
```

Types:
- `white` - Full spectrum, harsh
- `pink` - Softer, reduced highs
- `brown` - Very soft, like wind

Noise hihats example:

```javascript
sound("bd*2,<white pink brown>*8")
  .decay(.04).sustain(0)
```

Add noise to oscillators:

```javascript
note("c3").noise("<0.1 0.25 0.5>")  // Pink noise amount
```

Crackle noise:

```javascript
s("crackle*4").density("<0.01 0.04 0.2 0.5>")
```

### Additive Synthesis

Control individual harmonics:

**partials**: Harmonic magnitudes

```javascript
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("sawtooth")
  .partials([1, 1, "<1 0>", "<1 0>", "<1 0>"])  // Filter harmonics
```

Create custom waveforms with `user` sound:

```javascript
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("user")
  .partials([1, 0, 0.3, 0, 0.1, 0, 0, 0.3])
```

Algorithmic partials:

```javascript
const numHarmonics = 22
note("c2").sound("saw")
  .partials(new Array(numHarmonics).fill(1))  // Spectral filter
```

With patterns:

```javascript
note("c2").sound("user")
  .partials([1, 0, "0 1", "0 1 0.3", rand])  // Pattern per harmonic
```

**phases**: Harmonic phase offsets

```javascript
s("saw").n(irand(12))
  .partials(randL(200))
  .phases(randL(200))  // Random phases add depth
```

### Vibrato

**vib**: Vibrato amount (pitch modulation)

```javascript
note("c3").vib(0.5)              // Vibrato
note("c3").vib("0 0.1 0.5 1")    // Pattern vibrato
```

**vibmod**: Vibrato frequency

```javascript
note("c3").vib(0.5).vibmod(8)    // Faster vibrato
```

### FM Synthesis

Frequency modulation for complex timbres:

**fm**: Modulator amount

```javascript
note("c2 c3").fm(4)              // FM synthesis
note("c2 c3").fm("<0 1 2 4 8>")  // Increasing FM
```

**fmh**: Modulator harmonic ratio

```javascript
note("c2 c3").fm(2).fmh(5)       // Harmonic ratio
```

**FM envelope**: Control FM over time

```javascript
note("c2").fm(8)
  .fmattack(0.5)    // FM attack time
  .fmdecay(1)       // FM decay time
  .fmsustain(0.3)   // FM sustain level
  .fmenv(4)         // FM envelope depth
```

### Wavetable Synthesis

Use the sampler to load single-cycle waveforms:

```javascript
samples('bubo:waveforms')

note("<[g3,b3,e4]!2 [a3,c3,e4] [b3,d3,f#4]>")
  .s('wt_flute')                  // Any sample with wt_ prefix
  .n("<1 2 3 4 5 6 7 8 9 10>/2")  // Scan through wavetables
  .loopBegin(0).loopEnd(1)        // Loop points
```

Over 1000 wavetables available from [AKWF](https://www.adventurekid.se/akrt/waveforms/) set.

### ZZFX Synth

"Zuper Zmall Zound Zynth" - compact synth engine:

```javascript
note("c2 eb2 f2 g2")
  .s("{z_sawtooth z_tan z_noise z_sine z_square}%4")
  .zrand(0)         // Randomization
  .attack(0.001)    // Envelope
  .decay(0.1)
  .sustain(.8)
  .release(.1)
  .curve(1)         // Waveshape 1-3
  .slide(0)         // Pitch slide
  .deltaSlide(0)    // Pitch slide variation
  .noise(0)         // Noise amount
  .zmod(0)          // FM speed
  .zcrush(0)        // Bit crush 0-1
  .zdelay(0)        // Simple delay
  .pitchJump(0)     // Pitch change
  .pitchJumpTime(0) // When pitch jumps
  .lfo(0)           // Tremolo speed
  .tremolo(0.5)     // Tremolo amount
```

Available ZZFX sounds: `z_sawtooth`, `z_tan`, `z_noise`, `z_sine`, `z_square`

## Audio Effects System

### Signal Chain Order

Understanding signal flow:

1. **Sound generation** (sample/synth)
2. **Detune effects** (detune, penv)
3. **Gain** (with ADSR envelope)
4. **Filters** (in order):
   - Low-pass filter (lpf)
   - High-pass filter (hpf)
   - Band-pass filter (bandpass)
   - Vowel filter (vowel)
5. **Waveshaping**:
   - Sample rate reduction (coarse)
   - Bit crushing (crush)
   - Waveshape (shape)
   - Distortion (distort)
6. **Modulation**:
   - Tremolo
   - Phaser
7. **Spatial**:
   - Compressor
   - Panning (pan)
   - Post-gain (post)
8. **Sends**:
   - Dry output (dry)
   - Delay (delay)
   - Reverb (room)
9. **Orbit mixing** (duck, then mixer)

**Important**: Effects can only be used once per chain. Multiple calls override:

```javascript
// This won't work as expected:
s("bd").lpf(100).distort(2).lpf(800)  // Second lpf() is ignored!

// Instead, use separate patterns:
stack(
  s("bd").lpf(100),
  s("sd").lpf(800)
)
```

### Orbits System

**Orbits** are effect buses for grouping sounds.

**Default**: All sounds go to orbit 1

**Set orbit:**
```javascript
s("bd sd").orbit(2)
s("white").orbit("2,3,4")  // Multiple orbits (triples volume!)
```

**Multi-channel mode**: Settings > Multi Channel Orbits
- Orbit `i` maps to channels `2i` and `2i + 1`
- Use with audio routers like Blackhole 16

**Important orbit behavior**: Delay and reverb are shared per orbit:

```javascript
// Problem: kick overrides pluck's reverb
$: s("triangle*4").n(irand(12)).room(1).roomsize(10)
$: s("bd*4").room(0.01).roomsize(0.01)  // Overwrites reverb!

// Solution: Use different orbits
$: s("triangle*4").n(irand(12)).room(1).roomsize(10).orbit(2)
$: s("bd*4").room(0.01).roomsize(0.01).orbit(1)
```

### Continuous vs Discrete Changes

Most parameters are **sampled per event**:

```javascript
// Won't continuously modulate:
s("supersaw").lpf(tri.range(100, 5000).slow(2))
```

**Workaround**: Create more events:

```javascript
// Fake continuous with more events:
s("supersaw").seg(16).lpf(tri.range(100, 5000).slow(2))
```

**Truly continuous parameters:**
- ADSR envelopes (attack, decay, sustain, release)
- Pitch envelope (penv + pitch ADSR)
- FM envelope (fmenv)
- Filter envelopes (lpenv, hpenv, bpenv)
- Tremolo, Phaser, Vibrato
- Ducking

### Filters

**Low-pass filter** (lpf/lpq): Cut high frequencies

```javascript
s("sawtooth").note("c2").lpf(1000)     // Cutoff at 1000 Hz
s("sawtooth").note("c2").lpf(1000).lpq(10)  // High resonance
```

**High-pass filter** (hpf/hpq): Cut low frequencies

```javascript
s("sawtooth").note("c2").hpf(500)      // Cut below 500 Hz
s("sawtooth").note("c2").hpf(500).hpq(5)
```

**Band-pass filter** (bpf/bpq): Only middle frequencies

```javascript
s("white").bpf(1000)                   // Only around 1000 Hz
s("white").bpf(1000).bpq(20)           // Narrow band
```

**Vowel filter**: Formant filter

```javascript
s("sawtooth").note("c2").vowel("a")    // "ah" sound
s("sawtooth").note("c2").vowel("<a e i o u>")  // Pattern vowels
```

**Filter type** (ftype): Choose filter characteristics

```javascript
s("sawtooth").lpf(1000).ftype('24db')  // Steeper filter
```

### Amplitude Envelope (ADSR)

**attack**: Rise time to peak

```javascript
note("c3").attack(0.5)                 // Slow attack (fade in)
note("c3").attack(0.001)               // Instant attack
```

**decay**: Fall time to sustain level

```javascript
note("c3").decay(0.2)                  // Decay to sustain
```

**sustain**: Held level (0-1)

```javascript
note("c3").sustain(0.5)                // 50% level during sustain
note("c3").sustain(0)                  // No sustain (percussive)
```

**release**: Fade out time after note ends

```javascript
note("c3").release(1)                  // Long release tail
note("c3").release(0.05)               // Short release
```

**Combined**:

```javascript
note("c3").adsr(0.01, 0.2, 0.5, 1)    // a, d, s, r
```

Practical examples:

```javascript
// Percussive
note("c3").attack(0.001).decay(0.1).sustain(0).release(0.1)

// Pad
note("c3").attack(1).decay(0.5).sustain(0.7).release(2)

// Pluck
note("c3").attack(0.001).decay(0.3).sustain(0.2).release(0.5)
```

### Filter Envelope

Add movement to filter cutoff:

**Low-pass envelope:**

```javascript
note("c2").s("sawtooth")
  .lpf(200)              // Base cutoff
  .lpenv(2000)           // Envelope depth (goes up to 2200 Hz)
  .lpattack(0.01)        // Filter attack
  .lpdecay(0.3)          // Filter decay
  .lpsustain(0.2)        // Filter sustain
  .lprelease(0.5)        // Filter release
```

Short forms: `lpa`, `lpd`, `lps`, `lpr`, `lpe`

**High-pass envelope**: `hpattack`, `hpdecay`, `hpsustain`, `hprelease`, `hpenv`
Short: `hpa`, `hpd`, `hps`, `hpr`, `hpe`

**Band-pass envelope**: `bpattack`, `bpdecay`, `bpsustain`, `bprelease`, `bpenv`
Short: `bpa`, `bpd`, `bps`, `bpr`, `bpe`

Example with modulation:

```javascript
note("[c eb g <f bb>](3,8,<0 1>)".sub(12))
  .s("sawtooth")
  .lpf(sine.range(300,2000).slow(16))
  .lpa(0.005)
  .lpd(perlin.range(.02,.2))
  .lps(perlin.range(0,.5).slow(3))
  .lpq(sine.range(2,10).slow(32))
  .lpenv(perlin.range(1,8).slow(2))
  .release(.5)
```

### Pitch Envelope

Pitch sweeps controlled by envelope:

**penv**: Pitch envelope depth (in semitones)

```javascript
note("c3").penv(12)              // Sweep up 1 octave
note("c3").penv(-12)             // Sweep down 1 octave
note("c3").penv("<0 7 -7>")      // Pattern pitch sweeps
```

**Pitch envelope ADSR:**

```javascript
note("c3")
  .penv(12)                      // Sweep up octave
  .pattack(0.1)                  // Pitch attack (full name)
  .pdecay(0.2)                   // Pitch decay
  .prelease(0.5)                 // Pitch release
  .panchor(0)                    // Anchor point (0 = start pitch)
  .pcurve(-4)                    // Exponential curve
```

Chiptune example:

```javascript
n(run("<4 8>/16")).jux(rev)
  .chord("<C^7 <Db^7 Fm7>>")
  .voicing()
  .penv("<0 <2 -2>>")
  .patt(.02)
  .dec(.1)
```

### Dynamics

**gain**: Master volume (0-1+)

```javascript
note("c3").gain(0.5)             // Half volume
note("c3").gain("<0.25 0.5 0.75 1>")
```

**velocity**: Additional gain multiplier

```javascript
note("c3").velocity(0.8)         // 80% of full
```

**compressor**: Dynamic range compression

```javascript
note("c3").compressor(-20)       // Threshold in dB
```

**postgain**: Post-effect gain

```javascript
note("c3").postgain(0.5)         // After effects
```

**xfade**: Crossfade between patterns

```javascript
note("c3").xfade(sine.slow(4))   // Fade in/out
```

### Panning

**pan**: Stereo position (0=left, 1=right, 0.5=center)

```javascript
note("c3").pan(0)                // Hard left
note("c3").pan(1)                // Hard right
note("c3").pan(0.5)              // Center
note("c3").pan("<0 0.25 0.75 1>")  // Pattern pan
note("c3").pan(sine.slow(4))     // LFO pan
```

**jux**: Apply function to one channel

```javascript
note("c3 e3 g3").jux(rev)        // Reverse in right channel
```

**juxBy**: Jux with mix amount (0-1)

```javascript
note("c3 e3 g3").juxBy(0.5, rev)  // 50% mix
note("c3 e3 g3").juxBy(0.3, x => x.fast(2))
```

### Waveshaping

**coarse**: Sample rate reduction

```javascript
s("bd").coarse(10)               // Reduce sample rate
s("bd").coarse("<48 24 12 6>")   // Pattern reduction
```

**crush**: Bit crushing

```javascript
s("bd").crush(4)                 // 4-bit resolution
s("bd").crush("<16 8 4 2>")      // Pattern bits
```

**distort**: Distortion

```javascript
s("bd").distort(0.5)             // Mild distortion
s("bd").distort("<0 1 2 5>")     // Increasing distortion
```

**shape**: Waveshaping distortion

```javascript
note("c2").shape(0.5)            // Waveshape
```

### Global Effects (Per-Orbit)

**Delay:**

```javascript
s("bd sd").delay(0.5)            // 50% wet
s("bd sd").delaytime(0.125)      // 1/8 note delay
s("bd sd").delayfeedback(0.6)    // Feedback amount
```

Complete delay:

```javascript
s("bd sd")
  .delay(0.8)                    // Mix
  .delaytime(0.125)              // Time
  .delayfeedback(0.7)            // Feedback
```

**Reverb:**

```javascript
s("bd sd").room(0.5)             // 50% reverb
s("bd sd").roomsize(0.9)         // Large room
s("bd sd").roomfade(10)          // Fade time
s("bd sd").roomlp(5000)          // Low-pass on reverb
s("bd sd").roomdim(0.8)          // Dimension/diffusion
```

Custom impulse response:

```javascript
s("bd sd").iresponse("myIR")     // Custom IR
```

**Phaser:**

```javascript
s("bd").phaser(4)                // Phaser speed
s("bd").phaserdepth(1)           // Depth
s("bd").phasercenter(1000)       // Center frequency
s("bd").phasersweep(2000)        // Sweep range
```

**Duck (sidechain compression):**

```javascript
$: s("supersaw").note("c2").orbit(1)
$: s("bd*4").orbit(2).duckorbit(1)  // Duck orbit 1
   .duckattack(0.01)
   .duckdepth(0.8)                  // How much to duck
```

### Tremolo (Amplitude Modulation)

```javascript
note("c3").tremolo(4)            // Tremolo at 4 Hz (am())
note("c3").tremolodepth(0.8)     // Depth of modulation
note("c3").tremolosync(1)        // Sync to cycle
note("c3").tremoloshape('sine')  // Modulation shape
note("c3").tremoloskew(0.5)      // Waveform skew
note("c3").tremolophase(0)       // Phase offset
```

## Tonal Functions

Integration with [tonaljs](https://github.com/tonaljs/tonal) library.

### Scales

**scale**: Map numbers to scale degrees

```javascript
"0 2 4 7".scale('C major').note()
"0 2 4 7".scale('D minor').note()
"0 2 4 7".scale('C4 bebop major').note()  // With octave
```

Scale names: major, minor, dorian, phrygian, lydian, mixolydian, locrian, harmonic minor, melodic minor, bebop major, pentatonic, etc.

### Chords and Voicings

**chord**: Chord symbols

```javascript
chord("<C^7 A7b13 Dm7 G7>*2")
```

**voicing**: Voice lead chords

```javascript
chord("<C^7 A7b13 Dm7 G7>*2")
  .voicing()                     // Auto voice leading
  .note()
```

Voicing dictionaries:

```javascript
chord("<C^7 Dm7>")
  .dict('ireal')                 // iReal Pro voicings
  .voicing()
```

**mode**: Extract specific chord tones

```javascript
chord("C^7")
  .mode("root:g2")               // Just root note at G2
  .voicing()
```

Full example:

```javascript
chord("<C^7 A7b13 Dm7 G7>*2")
  .dict('ireal')
  .layer(
    x => x.struct("[~ x]*2").voicing(),              // Chords
    x => n("0*4").set(x).mode("root:g2").voicing()   // Bassline
      .s('sawtooth').cutoff("800:4:2")
  )
```

### Transposition

**transpose**: Semitone transposition

```javascript
"[c2 c3]*4".transpose("<0 -2 5 3>").note()
"[c2 c3]*4".transpose("<1P -2M 4P 3m>").note()  // Interval notation
```

**scaleTranspose**: Steps within scale

```javascript
"[-8 [2,4,6]]*2"
  .scale('C4 bebop major')
  .scaleTranspose("<0 -1 -2 -3 -4 -5 -6 -4>*2")
  .note()
```

### Root Notes

**rootNotes**: Extract chord roots

```javascript
"<C^7 A7b13 Dm7 G7>*2".rootNotes(2).note()  // Roots at octave 2
"<C^7 A7b13 Dm7 G7>*2".rootNotes(3).note()  // Roots at octave 3
```

Backing track example:

```javascript
"<C^7 A7b13 Dm7 G7>*2".layer(
  x => x.voicings('lefthand').struct("[~ x]*2").note(),
  x => x.rootNotes(2).note().s('sawtooth').cutoff(800)
)
```

## Continuous Signals (LFOs)

Signals are patterns with theoretically infinite resolution.

### Signal Types

**Sawtooth waves:**
```javascript
saw              // 0 to 1
saw2             // -1 to 1
```

**Sine waves:**
```javascript
sine             // 0 to 1
sine2            // -1 to 1
cosine / cosine2
```

**Triangle waves:**
```javascript
tri              // 0 to 1
tri2             // -1 to 1
```

**Square waves:**
```javascript
square           // 0 to 1
square2          // -1 to 1
```

**Random:**
```javascript
rand             // 0 to 1 (continuous random)
rand2            // -1 to 1
irand(n)         // Random integer 0 to n-1
brand            // Binary random (0 or 1)
brandBy(prob)    // Binary with probability
```

**Perlin noise:**
```javascript
perlin           // Smooth continuous noise
```

**Mouse position:**
```javascript
mousex           // X position 0-1
mousey           // Y position 0-1
```

### Using Signals

Signals can be used anywhere patterns are accepted:

**Range mapping:**
```javascript
sine.range(200, 2000)            // Map 0-1 to 200-2000
saw.range(-12, 12)               // Map for pitch
perlin.range(0, 0.5)             // Perlin noise mapped
```

**Time control:**
```javascript
sine.slow(4)                     // Slow down LFO
sine.fast(2)                     // Speed up LFO
```

**As control parameters:**
```javascript
note("c3").cutoff(sine.range(200, 2000).slow(4))  // Filter LFO
note("c3").gain(saw.range(0.5, 1))                 // Tremolo
note("c3").pan(sine.slow(2))                       // Auto-pan
note("c3 e3 g3").transpose(perlin.range(-7, 7).slow(8))  // Pitch drift
```

**Pattern combinations:**
```javascript
"0 2 4 7"
  .add(sine.mul(12).slow(8))     // Add sine wave to pattern
  .scale('C minor')
```

**Modulation examples:**
```javascript
// Filter sweep
s("sawtooth").note("c2")
  .lpf(sine.range(200, 5000).slow(4))

// Vibrato
note("c3").freq(sine.range(-5, 5).fast(6))

// Tremolo
note("c3").gain(tri.range(0.5, 1).fast(4))

// Complex modulation
note("c2 e2 g2")
  .cutoff(sine.range(200, 2000).slow(4))
  .resonance(cosine.range(1, 20).slow(6))
  .gain(perlin.range(0.6, 1))
```

## Time Modifiers

Functions that alter temporal structure.

### Speed Control

**fast**: Speed up by factor

```javascript
note("c e g").fast(2)            // 2x speed
note("c e g").fast(4)            // 4x speed
note("c e g").fast("<1 2 4 8>")  // Pattern speed
```

Equivalent mini notation: `*`

**slow**: Slow down by factor

```javascript
note("c e g").slow(2)            // Half speed
note("c e g").slow(4)            // Quarter speed
note("c e g").slow("<1 2 4>")    // Pattern tempo
```

Equivalent mini notation: `/`

### Time Shifting

**early**: Shift earlier in time

```javascript
note("c e g").early(0.25)        // 1/4 cycle earlier
note("c e g").early(0.125)       // 1/8 cycle earlier
```

**late**: Shift later in time

```javascript
note("c e g").late(0.25)         // 1/4 cycle later
note("c e g").late(0.125)        // 1/8 cycle later
```

### Euclidean Rhythms

**euclid(beats, steps)**: Distribute beats evenly

```javascript
note("c3").euclid(3, 8)          // 3 beats in 8 steps
note("c3").euclid(5, 8)          // 5 beats in 8 steps
```

**euclidRot(beats, steps, rotation)**: With offset

```javascript
note("c3").euclidRot(3, 8, 2)    // Rotated by 2
```

Equivalent mini notation: `(beats, steps, rotation)`

**euclidLegato(beats, steps)**: Euclidean with legato

```javascript
note("c3").euclidLegato(3, 8)
```

### Structural Transformations

**rev**: Reverse events

```javascript
note("c e g b").rev()            // b g e c
```

**palindrome**: Forward then backward

```javascript
note("c e g").palindrome()       // c e g g e c
```

**iter(n)**: Rotate through shifted versions

```javascript
note("c e g b").iter(4)
// Cycle 0: c e g b
// Cycle 1: e g b c
// Cycle 2: g b c e
// Cycle 3: b c e g
```

**iterBack**: Iter in reverse

```javascript
note("c e g b").iterBack(4)
```

**ply(n)**: Repeat each event

```javascript
note("c e g").ply(2)             // c c e e g g
note("c e g").ply("<1 2 3>")     // Pattern ply
```

**segment(n)**: Resample into n segments

```javascript
note("c e g").segment(8)         // 8 events per cycle
note("c e g").seg(16)            // seg() is alias
```

### Advanced Time Control

**compress(start, end)**: Compress into time span

```javascript
note("c e g b").compress(0, 0.5)      // First half only
note("c e g b").compress(0.25, 0.75)  // Middle section
```

**zoom(start, end)**: Zoom into time span

```javascript
note("c e g b").zoom(0, 0.5)     // See first half, stretched
```

**linger(fraction)**: Hold onto time fraction

```javascript
note("c e g b").linger(0.5)      // Linger on half
```

**fastGap(factor)**: Fast with gaps

```javascript
note("c e g").fastGap(2)         // 2x with gaps
```

**inside(n, fn)**: Apply function at faster rate

```javascript
note("c e g b").inside(2, rev)   // Reverse at 2x speed
```

**outside(n, fn)**: Apply function at slower rate

```javascript
note("c e g b").outside(2, rev)  // Reverse at 1/2x speed
```

**cpm(n)**: Set cycles per minute

```javascript
note("c e g").cpm(120)           // 120 cycles per minute
```

**ribbon(n)**: Temporal ribbon effect

```javascript
note("c e g").ribbon(4)
```

**swing** / **swingBy(n)**: Add swing feel

```javascript
note("c e g b c e g b").swing()          // Default swing
note("c e g b c e g b").swingBy(0.3)     // Custom swing amount
```

## Conditional Modifiers

Pattern transformation based on conditions.

### Cycle-based Conditionals

**every(n, fn)**: Apply function every n cycles

```javascript
note("c e g").every(4, rev)              // Reverse every 4th cycle
note("c e g").every(3, fast(2))          // Double speed every 3rd
note("c e g").every(2, x => x.transpose(12))  // Octave up every 2nd
```

**firstOf(n, fn)**: Apply on first of n cycles

```javascript
note("c e g").firstOf(4, fast(2))        // Fast on 1st of every 4
```

**lastOf(n, fn)**: Apply on last of n cycles

```javascript
note("c e g").lastOf(4, rev)             // Reverse on 4th of every 4
```

**when(test, fn)**: Apply when condition true

```javascript
note("c e g").when(x => x % 2 === 0, rev)  // Reverse on even cycles
```

### Pattern Chunking

**chunk(n, fn)**: Divide into n chunks and apply fn to each

```javascript
note("c d e f g a b c5").chunk(4, rev)    // Reverse in 4 chunks
```

**chunkBack(n, fn)**: Chunk backwards

```javascript
note("c d e f g a b c5").chunkBack(4, rev)
```

**fastChunk(n, fn)**: Fast chunking

```javascript
note("c d e f g a b c5").fastChunk(4, rev)
```

### Arpeggiation

**arp(order)**: Arpeggiate chords

```javascript
note("[c,e,g]").arp("up")                // Up
note("[c,e,g]").arp("down")              // Down
note("[c,e,g]").arp("updown")            // Up then down
note("[c,e,g]").arp("downup")            // Down then up
note("[c,e,g]").arp("diverge")           // From center out
note("[c,e,g]").arp("converge")          // From outside in
```

**arpWith**: Custom arpeggiation

```javascript
note("[c,e,g,b]").arpWith("0 2 1 3")     // Custom order
```

### Structural Control

**struct(pattern)**: Boolean structure from pattern

```javascript
note("c e g").struct("t t f t")          // t=trigger, f=rest
note("c e g").struct("t(3,8)")           // Euclidean structure
```

**mask(pattern)**: Filter events by pattern

```javascript
note("c d e f g a b c5").mask("t f")     // Keep every other
```

**reset**: Reset to beginning

```javascript
note("c e g").reset()                    // Reset pattern
```

**restart**: Restart pattern

```javascript
note("c e g").restart()                  // Restart
```

**hush**: Silence all

```javascript
hush()                                   // Stop everything
```

### Selection Functions

**pick(values)**: Pick from list

```javascript
pick("c e g b")                          // Random choice each cycle
```

**pickmod(values)**: Pick modulo cycle

```javascript
pickmod("c e g b")                       // Cycle through in order
```

**pickF(fn, values)**: Pick with function

```javascript
pickF(x => x % 2, "c e g b")            // Custom selection
```

**inhabit**: Combine patterns with mapping

```javascript
"<0 1 2>".inhabit({0: 'bd', 1: 'sd', 2: 'hh'})  // Map values
```

### Squeezing

**squeeze(pattern)**: Squeeze pattern into structure

```javascript
note("c e g").squeeze("0 1 [2 3]")      // Squeeze into structure
```

## Pattern Factories (Creating Patterns)

Equivalent mini notation reference:

| Function | Mini Notation |
|----------|---------------|
| `cat(x, y)` | `"<x y>"` |
| `seq(x, y)` | `"x y"` |
| `stack(x, y)` | `"x,y"` |
| `stepcat([3,x],[2,y])` | `"x@3 y@2"` |
| `polymeter([a,b,c], [x,y])` | `"{a b c, x y}"` |
| `polymeterSteps(2, x, y, z)` | `"{x y z}%2"` |
| `silence` | `"~"` |

### Basic Constructors

**cat**: Alternate patterns (one per cycle)

```javascript
cat("c3", "e3", "g3")                    // c3 in cycle 0, e3 in cycle 1, etc.
cat("c3", ["e3", "g3"])                  // With arrays
```

**seq / sequence**: Sequential within cycle

```javascript
seq("c3", "e3", "g3")                    // All in one cycle
seq("c3", ["e3", "g3"])                  // Nested sequence
```

**stack**: Layer patterns

```javascript
stack(
  note("c2"),
  note("c3 e3 g3"),
  s("bd sd")
)
```

**stepcat**: Cat with weighted steps

```javascript
stepcat([3, "c3"], [2, "e3"], [1, "g3"])  // c3 for 3, e3 for 2, g3 for 1
```

**arrange**: Arrange patterns by name

```javascript
arrange("a b a c", {
  a: note("c3 e3"),
  b: note("f3 g3"),
  c: note("c4")
})
```

### Polymeter

**polymeter**: Multiple meters simultaneously

```javascript
polymeter(["c3", "e3", "g3"], ["c2", "g2"])  // 3 against 2
polymeter(["bd", "sd"], ["hh", "hh", "oh"])   // 2 against 3
```

Mini notation: `{a b c, x y}`

**polymeterSteps**: Polymeter with step count

```javascript
polymeterSteps(2, "c3", "e3", "g3")      // 3 events over 2 steps
```

Mini notation: `{x y z}%2`

### Utility Patterns

**silence**: Empty pattern

```javascript
silence                                   // No events
seq("c3", silence, "e3")                 // With rests
```

**run(n)**: Ascending numbers

```javascript
run(4)                // 0 1 2 3
run(8)                // 0 1 2 3 4 5 6 7
```

**binary(n)**: Binary representation

```javascript
binary(5)             // 1 0 1
binary(42)            // 1 0 1 0 1 0
```

**binaryN(n, bits)**: Binary with bit count

```javascript
binaryN(5, 8)         // 0 0 0 0 0 1 0 1
```

## Practical Pattern Recipes

### Building Arpeggios

Simple arpeggio:

```javascript
note("c a f e").slow(2)
```

One note per cycle:

```javascript
note("<c a f e>").slow(2)
```

Add offset layer:

```javascript
"<c a f e>"
  .off(1/8, add(7))              // Fifth above
  .note().slow(2)
```

Add structure:

```javascript
"<c*2 a(3,8) f(3,8,2) e*2>"
  .off(1/8, add(7))
  .note().slow(2)
```

Stereo reverse:

```javascript
"<c*2 a(3,8) f(3,8,2) e*2>"
  .off(1/8, add(7))
  .note()
  .jux(rev).slow(2)
```

Multiple layers:

```javascript
"<c*2 a(3,8) f(3,8,2) e*2>"
  .off(1/8, add(7))
  .off(1/8, add(12))             // Octave above
  .note()
  .jux(rev).slow(2)
```

### Building Rhythms

Basic kick-snare:

```javascript
s("bd sd").slow(2)
```

Different sample:

```javascript
s("bd sd:3").slow(2)
```

Add rhythm:

```javascript
s("bd*2 [~ sd:3]").slow(2)
```

Add toms:

```javascript
s("bd*2 [[~ lt] sd:3] lt:1 [ht mt*2]").slow(2)
```

Transform with shifts:

```javascript
s("bd*2 [[~ lt] sd:3] lt:1 [ht mt*2]")
  .every(2, early(.25)).slow(2)
```

Pattern the shift:

```javascript
s("bd*2 [[~ lt] sd:3] lt:1 [ht mt*2]")
  .every(2, early("<.25 .125 .5>")).slow(2)
```

Add effects:

```javascript
s("bd*2 [[~ lt] sd:3] lt:1 [ht mt*2]")
  .every(2, early("<.25 .125 .5>"))
  .shape("<0 .5 .3>")
  .room(saw.range(0,.2).slow(4))
  .slow(2)
```

### Complex Example: Techno Beat

```javascript
stack(
  // Kick
  s("bd*4").gain(1.2),

  // Offbeat hats
  s("~ hh ~ hh").bank("RolandTR909").gain(0.6),

  // Fast hats
  s("hh*16").gain(perlin.range(0.3, 0.6)).bank("RolandTR808"),

  // Snare
  s("~ sd").delay(0.3).delaytime(0.125),

  // Percussion
  s("~ ~ cb ~").gain(0.8).pan(0.7),

  // Bass
  note("c2 ~ [c2 g1] ~")
    .s("sawtooth")
    .lpf(sine.range(300, 1200).slow(4))
    .lpq(10)
    .gain(0.6)
)
```

### Complex Example: Ambient Pad

```javascript
stack(
  // Main pad
  "<[c2,e2,g2,b2] [f2,a2,c3,e3]>"
    .note()
    .s("sawtooth")
    .lpf(800)
    .lpq(5)
    .attack(2)
    .release(3)
    .gain(0.3)
    .room(0.9)
    .roomsize(0.95),

  // Arpeggio
  "<[0,4,7,11] [5,9,0,4]>"
    .scale("C3 minor")
    .off(1/8, add(12))
    .off(1/4, add(7))
    .struct("t*8")
    .note()
    .s("triangle")
    .lpf(2000)
    .release(0.5)
    .gain(0.25)
    .delay(0.5)
    .delaytime(0.375)
    .pan(sine.slow(3))
)
```

### Complex Example: Breakbeat

```javascript
samples('github:tidalcycles/dirt-samples')

stack(
  // Amen break-style pattern
  n("0 [4 0] [2 0] [4 [0 4]]")
    .s("amencutup")
    .speed("<1 0.5 2 -1>/4")
    .chop("<1 8 16 32>"),

  // Bass
  note("<c2 c2 eb2 f2>")
    .s("sawtooth")
    .lpf(600)
    .lpq(15)
    .gain(0.7)
    .shape(0.5),

  // Pads
  "<[c3,eb3,g3] [f3,ab3,c4]>"
    .note()
    .s("square")
    .lpf(sine.range(400, 1200).slow(8))
    .gain(0.3)
    .room(0.8)
    .attack(1)
    .release(2)
)
```

## References and Resources

**Official Sites:**
- Main site: https://strudel.cc
- Tutorial: https://strudel.cc/learn
- Technical blog: https://loophole-letters.vercel.app/strudel

**Code:**
- Repository: https://codeberg.org/uzu/strudel
- npm packages: https://www.npmjs.com/org/strudel

**Community:**
- Discord: https://discord.com/invite/HGEdXmRkzT (#strudel channel)
- Forum: https://club.tidalcycles.org
- Mastodon: https://social.toplap.org/@strudel

**Related Projects:**
- TidalCycles (Haskell): https://tidalcycles.org
- TidalVortex (Python): Port to Python
- SuperDirt: SuperCollider synthesis engine
- Hydra: Visual synthesis
- Estuary: Collaborative live coding

**Academic Papers:**
- "Strudel: live coding patterns on the Web" (ICLC 2023)
- "TidalCycles: live coding algorithmic patterns"
- "Algorithmic Pattern" (McLean 2020)

## License

GNU Affero Public Licence v3 (AGPL-3.0)
- Code must be shared in free/open source projects
- Same license required for derivative works
- See LICENSE file for full terms

Sound samples: See https://github.com/felixroos/dough-samples
