# Strudel Comprehensive Guide

**A Complete Reference for Live Coding Music with Strudel**

This document provides detailed information about Strudel, a web-based live coding environment implementing the Tidal Cycles algorithmic pattern language in JavaScript.

---

## Table of Contents

1. [What is Strudel?](#what-is-strudel)
2. [Mini-Notation Reference](#mini-notation-reference)
3. [Samples and Sound Sources](#samples-and-sound-sources)
4. [Synthesizers](#synthesizers)
5. [Audio Effects](#audio-effects)
6. [Pattern Creation](#pattern-creation)
7. [Time Modifiers](#time-modifiers)
8. [Signals and Continuous Patterns](#signals-and-continuous-patterns)
9. [Random Modifiers](#random-modifiers)
10. [Conditional Modifiers](#conditional-modifiers)
11. [Tonal Functions](#tonal-functions)
12. [Signal Chain and Architecture](#signal-chain-and-architecture)
13. [Advanced Techniques](#advanced-techniques)

---

## What is Strudel?

**Strudel** is a web-based implementation of [Tidal Cycles](https://tidalcycles.org/) written in JavaScript by Alex McLean and Felix Roos (initiated in 2022). Unlike the original Haskell-based Tidal Cycles which requires installation of multiple components (Haskell, SuperCollider, SuperDirt), Strudel runs entirely in your web browser with no installation required.

### Key Features:
- **Browser-based**: Runs at https://strudel.cc/ with no installation
- **Live coding**: Edit patterns in real-time while they play
- **Algorithmic patterns**: Powerful mini-notation for creating complex rhythms
- **Built-in sounds**: Comprehensive sample library and synthesizers
- **Export friendly**: Generate shareable URLs

### Basic Concepts:

**Cycles**: The fundamental unit of time in Strudel. By default, one cycle = 1 second. Patterns repeat every cycle.

**Events**: Individual sound triggers within a pattern. The duration of each event depends on how many events fit in one cycle.

**Pattern**: A sequence of events that repeats cyclically.

---

## Mini-Notation Reference

The mini-notation is Strudel's compact language for describing rhythmic patterns. It uses special characters to control timing and structure.

### Basic Syntax

#### Sequences (Space-Separated)
```javascript
note("c e g b")  // 4 notes, each 1/4 cycle long
s("bd sd hh cp") // 4 drum sounds
```

#### Multiplication (`*`)
Speed up a pattern by repeating it:
```javascript
s("bd*4")        // bd bd bd bd (4 times per cycle)
s("[bd sd]*2")   // bd sd bd sd (pattern repeated twice)
```

#### Division (`/`)
Slow down a pattern over multiple cycles:
```javascript
s("bd/2")        // bd plays every 2 cycles
s("[bd sd]/3")   // pattern plays over 3 cycles
```

#### Angle Brackets (`<>`)
Alternate between values (one per cycle):
```javascript
note("<c e g>")  // c on cycle 1, e on cycle 2, g on cycle 3, then repeat
s("bd <sd cp>")  // bd always plays, alternates sd/cp
```

#### Square Brackets (`[]`)
Group events into subdivisions:
```javascript
s("bd [sd cp]")     // bd takes 1/2 cycle, [sd cp] share the other 1/2
s("bd [sd [cp hh]]") // Nested subdivisions
```

### Advanced Mini-Notation

#### Rests (`~`)
Silence/rest:
```javascript
s("bd ~ sd ~")   // bd, silence, sd, silence
```

#### Polyphony (`,`)
Play multiple things simultaneously:
```javascript
s("bd, hh*4")           // bd and 4 hi-hats at same time
note("c,e,g")           // C major chord
note("[c,e,g] [d,f,a]") // Two chords in sequence
```

#### Elongation (`@`)
Give events different durations (weight):
```javascript
s("bd@3 sd")     // bd is 3x as long as sd
s("<bd@2 sd cp>") // bd lasts 2 cycles
```

#### Replication (`!`)
Repeat without speeding up:
```javascript
s("bd!3 sd")     // bd bd bd sd (same speed)
note("c!4")      // c c c c
```

#### Randomness (`?`)
50% chance of playing:
```javascript
s("bd*8?")       // Each bd has 50% chance
s("bd*8?0.3")    // 30% chance for each bd
```

#### Choice (`|`)
Choose randomly between options:
```javascript
s("bd | sd | cp") // Picks one randomly each time
```

#### Euclidean Rhythms (`()`)
Distribute beats evenly:
```javascript
s("bd(3,8)")     // 3 beats distributed over 8 steps
s("bd(5,8)")     // 5 beats over 8 steps
s("bd(3,8,2)")   // 3 beats over 8 steps, offset by 2
```

#### Sample Selection (`:`)
Choose specific sample variant:
```javascript
s("bd:0 bd:1 bd:2") // Different bd samples
s("hh:0 hh:1")      // Different hi-hat samples
```

### Mini-Notation String Formats

- **Backticks** (`` ` ``): Multi-line mini-notation
- **Double quotes** (`"`): Single-line mini-notation (parsed)
- **Single quotes** (`'`): Plain strings (not parsed as pattern)

---

## Samples and Sound Sources

### Default Sample Names

Strudel includes comprehensive drum machine samples from the [tidal-drum-machines](https://github.com/ritchse/tidal-drum-machines) library:

#### Core Drum Sounds
| Sound | Code | Description |
|-------|------|-------------|
| Bass drum / Kick | `bd` | Low frequency drum |
| Snare drum | `sd` | Mid-high crack sound |
| Rimshot | `rim` | Sharp click |
| Clap | `cp` | Hand clap sound |
| Closed hi-hat | `hh` | Short metallic sound |
| Open hi-hat | `oh` | Sustained metallic sound |
| Crash cymbal | `cr` | Loud sustained crash |
| Ride cymbal | `rd` | Sustained ping |
| High tom | `ht` | High pitched drum |
| Medium tom | `mt` | Mid pitched drum |
| Low tom | `lt` | Low pitched drum |

#### Additional Percussion
| Sound | Code |
|-------|------|
| Shakers/maracas | `sh` |
| Cowbell | `cb` |
| Tambourine | `tb` |
| Percussion | `perc` |
| Miscellaneous | `misc` |
| Effects | `fx` |

### Using the `s()` Function

```javascript
s("bd sd")           // Play bass drum, then snare
s("bd*4, hh*8")      // 4 kicks + 8 hi-hats simultaneously
s("bd sd [~ bd] sd") // Rhythm with a rest
```

### Sound Banks

Sound banks group related samples. Use `.bank()` to select:

```javascript
s("bd sd hh").bank("RolandTR808")
s("bd sd hh").bank("RolandTR909")
s("bd sd,hh*16").bank("<RolandTR808 RolandTR909>") // Alternate banks
```

### Selecting Sample Variants

Use `.n()` for numeric selection or `:` in mini-notation:

```javascript
s("hh*8").bank("RolandTR909").n("0 1 2 3") // Select variants 0-3
s("bd:0 bd:1 bd:2 bd:3")                    // Mini-notation version
```

Numbers wrap around if they exceed available samples.

### Loading Custom Samples

#### From URLs
```javascript
samples({
  bassdrum: 'bd/BT0AADA.wav',
  hihat: 'hh27/000_hh27closedhh.wav',
  snaredrum: ['sd/rytm-01-classic.wav', 'sd/rytm-00-hard.wav']
}, 'https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/');

s("bassdrum snaredrum:0 snaredrum:1, hihat*16")
```

#### From strudel.json
```javascript
samples('https://path/to/strudel.json')
s("bd sd bd sd,hh*16")
```

#### GitHub Shortcut
```javascript
samples('github:tidalcycles/dirt-samples')
s("bd sd bd sd,hh*16")
```

#### Local Files via Import
Use the REPL's "Import Sounds Folder" button in the sounds tab.

#### Local Server (@strudel/sampler)
```bash
cd samples
npx @strudel/sampler
```
Then in Strudel:
```javascript
samples('http://localhost:5432/');
n("<0 1 2>").s("swoop smash")
```

### Pitched Samples

Specify base pitch for tuned samples:

```javascript
samples({
  'gtr': 'gtr/0001_cleanC.wav',
  'moog': { 
    'g2': 'moog/004_Mighty%20Moog%20G2.wav',
    'g3': 'moog/005_Mighty%20Moog%20G3.wav',
    'g4': 'moog/006_Mighty%20Moog%20G4.wav'
  }
}, 'github:tidalcycles/dirt-samples');

note("g3 [bb3 c4] <g4 f4 eb4 f3>").s("moog")
```

### Shabda (AI Sample Search)

Query samples from freesound.org:
```javascript
samples('shabda:bass:4,hihat:4,rimshot:2')
s("bass*2, hihat*8")
```

Generate speech synthesis:
```javascript
samples('shabda/speech:hello,goodbye')
samples('shabda/speech/fr-FR/m:magnifique') // French, male voice
s("hello goodbye")
```

### Sample Effects

#### begin / end
Cut portions of samples:
```javascript
s("rave").begin("<0 .25 .5 .75>")  // Skip beginning
s("bd*2,oh*4").end("<.1 .2 .5 1>") // Cut ending
```

#### loop / loopBegin / loopEnd
Loop samples:
```javascript
s("casio").loop(1)
s("space").loop(1).loopBegin("<0 .125 .25>").loopEnd("<1 .75 .5>")
```

#### cut
Stop previous sample in same cut group:
```javascript
s("[oh hh]*4").cut(1) // Realistic hi-hat behavior
```

#### clip / legato
Limit sample duration:
```javascript
note("c a f e").s("piano").clip("<.5 1 2>")
```

#### loopAt
Fit sample to cycle count:
```javascript
s("rhodes").loopAt(2) // Stretch/compress to 2 cycles
```

#### chop
Granular synthesis:
```javascript
s("rhodes").chop(4).rev().loopAt(2)
```

#### slice / splice
Slice and rearrange:
```javascript
s("breaks165").slice(8, "0 1 <2 2*2> 3 [4 0] 5 6 7")
s("breaks165").splice(8, "0 1 [2 3 0]@2 3 0@2 7")
```

#### speed
Change playback speed (affects pitch):
```javascript
s("bd*6").speed("1 2 4 1 -2 -4") // Negative = reverse
speed("1 1.5*2 [2 1.1]").s("piano").clip(1)
```

---

## Synthesizers

Strudel includes built-in synthesizers for generating sounds programmatically.

### Basic Waveforms

Available via `.sound()` or `.s()`:

```javascript
note("c2 <eb2 <g2 g1>>").sound("<sawtooth square triangle sine>")
```

- `sine` - Pure smooth tone
- `sawtooth` - Bright, buzzy (default for many sounds)
- `square` - Hollow, video-game like
- `triangle` - Default if only `note()` is specified

### Noise Generators

```javascript
sound("<white pink brown>") // Different noise colors
s("bd*2,<white pink brown>*8").decay(.04).sustain(0) // Hi-hat style

// Add noise to oscillators
note("c3").noise("<0.1 0.25 0.5>")

// Crackle noise
s("crackle*4").density("<0.01 0.04 0.2 0.5>")
```

### Additive Synthesis

#### partials
Control harmonic content:
```javascript
note("c2 <eb2 <g2 g1>>")
  .sound("sawtooth")
  .partials([1, 1, "<1 0>", "<1 0>", "<1 0>"]) // Filter harmonics

// Create custom waveforms
note("c2").sound("user").partials([1, 0, 0.3, 0, 0.1, 0, 0, 0.3])
```

#### phases
Control harmonic phases:
```javascript
s("saw").n(irand(12))
  .partials(randL(200))
  .phases(randL(200))
```

### Vibrato

```javascript
note("a e").vib("<.5 1 2 4 8 16>")        // Frequency
note("a e").vib("<.5 1 2 4 8 16>:12")     // Freq:depth
note("a e").vib(4).vibmod("<.25 .5 1 2>") // Control depth separately
```

### FM Synthesis

Frequency Modulation for complex timbres:

```javascript
note("c e g b g e").fm("<0 1 2 8 32>")  // Brightness (modulation index)
note("c e g b g e").fm(4).fmh("<1 2 1.5 1.61>") // Harmonicity

// FM Envelope controls
note("c e g").fm(4)
  .fmattack("<0 .05 .1>")   // Attack time
  .fmdecay("<.01 .05 .1>")  // Decay time
  .fmsustain("<1 .75 .5>")  // Sustain level
  .fmenv("<exp lin>")       // Envelope curve
```

### Wavetable Synthesis

Use custom waveforms (1000+ available from AKWF set):

```javascript
samples('bubo:waveforms');
note("<[g3,b3,e4]!2 [a3,c3,e4] [b3,d3,f#4]>")
  .s('wt_flute')
  .n("<1 2 3 4 5 6 7 8 9 10>")
```

Any sample with `wt_` prefix loops automatically.

### ZZFX Synth

Compact synth with 20 parameters for game-style sounds:

```javascript
note("c2 eb2 f2 g2")
  .s("{z_sawtooth z_tan z_noise z_sine z_square}%4")
  .attack(0.001).decay(0.1).sustain(.8).release(.1)
  .curve(1)        // Waveshape 1-3
  .slide(0)        // Pitch slide
  .noise(0)        // Dirt amount
  .zmod(0)         // FM speed
  .zcrush(0)       // Bit crush 0-1
  .zdelay(0)       // Simple delay
  .pitchJump(0)    // Pitch change
  .lfo(0)          // Tremolo speed
  .tremolo(0.5)    // Tremolo amount
```

---

## Audio Effects

### Filters

Fundamental for subtractive synthesis.

#### Low-Pass Filter (lpf/cutoff)
Allows low frequencies, cuts high:
```javascript
s("bd sd [~ bd] sd,hh*6").lpf("<4000 2000 1000 500>")
s("bd*16").lpf("1000:0 1000:10 1000:20 1000:30") // lpf:resonance

// Separate resonance control
s("bd sd,hh*8").lpf(2000).lpq("<0 10 20 30>")
```

#### High-Pass Filter (hpf)
Allows high frequencies, cuts low:
```javascript
s("bd sd,hh*8").hpf("<4000 2000 1000 500>")
s("bd sd,hh*8").hpf(2000).hpq("<0 10 20 30>")
```

#### Band-Pass Filter (bpf)
Allows middle frequencies:
```javascript
s("bd sd,hh*6").bpf("<1000 2000 4000 8000>")
s("bd sd").bpf(500).bpq("<0 1 2 3>")
```

#### Filter Type (ftype)
```javascript
note("c").s("sawtooth").lpf(500)
  .ftype("<0 1 2>") // 0=12db, 1=ladder, 2=24db
```

#### Vowel Filter
```javascript
note("c2").s('sawtooth').vowel("<a e i o u>")
// Available vowels: a e i o u ae aa oe ue y uh un en an on
```

### Amplitude Envelope (ADSR)

Controls volume over time:

```javascript
note("c3 e3 f3 g3")
  .attack("<0 .1 .5>")    // Time to reach peak
  .decay("<.1 .2 .3>")    // Time to reach sustain
  .sustain("<0 .5 1>")    // Level to hold (0-1)
  .release("<0 .1 .5>")   // Time to fade out

// Shorthand ADSR
note("c3 bb2 f3 eb3").s("sawtooth").adsr(".1:.1:.5:.2")
```

### Filter Envelope

Apply ADSR envelope to filter cutoff:

```javascript
note("c2 e2 f2 g2").s('sawtooth')
  .lpf(300)
  .lpattack(.5)    // or lpa
  .lpdecay(.5)     // or lpd
  .lpsustain(.5)   // or lps
  .lprelease(.5)   // or lpr
  .lpenv(4)        // or lpe (modulation depth)

// Also available: hpattack/hpdecay/etc, bpattack/bpdecay/etc
```

### Pitch Envelope

Animate pitch over time:

```javascript
note("c").penv("<12 7 1 .5 0 -1 -7 -12>") // Semitones
note("c").penv(12)
  .pattack("<0 .1 .25>")   // Attack time
  .pdecay("<0 .1 .25>")    // Decay time
  .prelease("<0 .1 .25>")  // Release time
  .pcurve("<0 1>")         // 0=linear, 1=exponential
  .panchor("<0 .5 1>")     // Range anchor
```

### Dynamics

```javascript
s("hh*8").gain(".4!2 1 .4!2 1")  // Volume control
s("hh*8").velocity(".4 1")        // Multiplied with gain

// Compression
s("bd sd,hh*8").compressor("-20:20:10:.002:.02")
  .postgain(1.5) // Gain after all effects
```

### Distortion & Waveshaping

```javascript
s("bd sd,hh*3").crush("<16 8 7 6 5 4 3 2>") // Bit crusher
s("bd sd,hh*8").coarse("<1 4 8 16 32>")     // Sample rate reduction

s("bd sd,hh*8").distort("<0 2 3 10:.5>")
// distort:"amount:postgain:type"
note("d1!8").s("sine").distort("8:.4:diode")
```

### Panning

```javascript
s("[bd hh]*2").pan("<.5 1 .5 0>")     // 0=left, 1=right
s("bd rim sd").pan(sine.slow(2))      // Autopan

// Jux: apply function only to right channel
s("bd lt [~ ht] mt cp").jux(rev)
s("bd lt [~ ht] mt cp").juxBy("<0 .5 1>", rev) // Control width
```

### Global Effects (Per Orbit)

These are shared across all events in the same orbit.

#### Delay
```javascript
s("bd bd").delay("<0 .25 .5 1>")
s("bd bd").delay("0.65:0.25:0.9") // level:time:feedback
s("bd").delay(.25).delaytime(.125).delayfeedback("<.25 .5 .75>")
```

#### Reverb
```javascript
s("bd sd").room("<0 .2 .4 .6 .8 1>")
s("bd sd").room("<0.9:1 0.9:4>") // level:size

s("bd sd").room(.8)
  .roomsize(4)    // 0-10 (recalculates reverb)
  .roomfade(2)    // Fade time in seconds
  .roomlp(5000)   // Lowpass frequency
  .roomdim(400)   // Lowpass at -60dB
```

#### Phaser
```javascript
n(run(8)).scale("D:pentatonic").s("sawtooth")
  .phaser("<1 2 4 8>")        // Speed
  .phaserdepth("<0 .5 .75>")  // Depth 0-1
  .phasercenter("<800 2000>") // Center freq
  .phasersweep("<800 2000>")  // Sweep range
```

#### Duck (Sidechain)
```javascript
// Pattern 1: sound to duck
n(run(16)).scale("c:minor:pentatonic").s("sawtooth").orbit(2)

// Pattern 2: trigger that ducks orbit 2
s("bd:4!4").duckorbit(2)
  .duckattack(0.2)  // Return time
  .duckdepth(1)     // Amount 0-1
```

### Amplitude Modulation

```javascript
note("f a c e").s("sawtooth")
  .tremolosync(4)              // Speed in cycles
  .tremolodepth("<1 2 .7>")    // Depth
  .tremoloskew("<.5 0 1>")     // Waveform shape
  .tremolophase("<0 .25 .66>") // Phase offset
  .tremoloshape("<sine tri square>") // Waveform
```

---

## Pattern Creation

Functions to create and combine patterns.

### cat / slowcat
Concatenate patterns (one per cycle):
```javascript
cat("e5", "b4", ["d5", "c5"]).note()
// Same as: "<e5 b4 [d5 c5]>".note()
```

### seq / fastcat
Concatenate into one cycle:
```javascript
seq("e5", "b4", ["d5", "c5"]).note()
// Same as: "e5 b4 [d5 c5]".note()
```

### stack
Play simultaneously:
```javascript
stack("g3", "b3", ["e4", "d4"]).note()
// Same as: "g3,b3,[e4 d4]".note()
```

### stepcat / timecat
Proportional concatenation:
```javascript
stepcat([3,"e3"], [1,"g3"]).note()
// Same as: "e3@3 g3".note()
```

### arrange
Arrange patterns over multiple cycles:
```javascript
arrange(
  [4, "<c a f e>(3,8)"],
  [2, "<g a>(5,8)"]
).note()
```

### polymeter
Create polymeters:
```javascript
polymeter("c eb g", "c2 g2").note()
// Same as: "{c eb g, c2 g2}%6".note()
```

### run
Numeric sequence:
```javascript
n(run(4)).scale("C4:pentatonic")
// Same as: n("0 1 2 3")
```

### binary / binaryN
Convert numbers to binary patterns:
```javascript
"hh".s().struct(binary(5))      // "1 0 1"
"hh".s().struct(binaryN(55532, 16)) // 16-bit binary
```

---

## Time Modifiers

Functions that manipulate temporal structure.

### slow / fast
```javascript
s("bd hh sd hh").slow(2)  // Half speed
s("bd hh sd hh").fast(2)  // Double speed
```

### early / late
Nudge timing:
```javascript
"bd ~".stack("hh ~".early(.1)).s()
"bd ~".stack("hh ~".late(.1)).s()
```

### euclid
Euclidean rhythms:
```javascript
note("c3").euclid(3,8)          // 3 beats in 8 steps
note("c3").euclidRot(3,8,2)     // With rotation
note("c3").euclidLegato(3,8)    // Sustained notes
```

### rev / palindrome
```javascript
note("c d e g").rev()        // Reverse pattern
note("c d e g").palindrome() // Forwards/backwards alternating
```

### iter / iterBack
Rotate subdivisions each cycle:
```javascript
note("0 1 2 3".scale('A minor')).iter(4)
note("0 1 2 3".scale('A minor')).iterBack(4)
```

### ply
Repeat each event:
```javascript
s("bd ~ sd cp").ply("<1 2 3>")
```

### segment
Sample continuous patterns:
```javascript
note(saw.range(40,52).segment(24))
```

### compress / zoom
Select portion of pattern:
```javascript
s("bd sd").compress(.25,.75)      // Compress into timespan
s("bd*2 hh*3 [sd bd]*2").zoom(0.25, 0.75)
```

### linger
Repeat fraction of pattern:
```javascript
s("lt ht mt cp, [hh oh]*2").linger("<1 .5 .25>")
```

### fastGap
Speed up with gap:
```javascript
s("bd sd").fastGap(2) // Plays in first half, silent in second
```

### inside / outside
Transform at different speeds:
```javascript
"0 1 2 3 4 3 2 1".inside(4, rev).note()
// Same as: .slow(4).rev().fast(4)

"<[0 1] 2 [3 4] 5>".outside(4, rev).note()
// Same as: .fast(4).rev().slow(4)
```

### cpm
Cycles per minute:
```javascript
s("<bd sd>,hh*2").cpm(90) // 90 BPM
```

### ribbon
Loop portion of pattern:
```javascript
note("<c d e f>").ribbon(1, 2) // Loop cycles 1-3
n(irand(8).segment(4)).ribbon(1337, 2) // Loop random seed
```

### swingBy / swing
Add shuffle/swing:
```javascript
s("hh*8").swingBy(1/3, 4) // swing amount, subdivision
s("hh*8").swing(4)        // Default swing (1/3)
```

---

## Signals and Continuous Patterns

Continuous functions that can be sampled.

### Waveforms (0 to 1)
```javascript
saw.slow(2)         // Sawtooth 0→1
sine.slow(2)        // Sine wave
cosine.slow(2)      // Cosine wave
tri.slow(2)         // Triangle
square.slow(2)      // Square wave

// Usage
note("c3 [eb3,g3]").clip(saw.slow(2))
n(sine.segment(16).range(0,15)).scale("C:minor")
```

### Waveforms (-1 to 1)
Also available: `saw2`, `sine2`, `cosine2`, `tri2`, `square2`, `rand2`

### Random Signals
```javascript
rand             // Random 0-1
s("bd*4,hh*8").cutoff(rand.range(500,8000))

irand(8)         // Random integers 0 to 7
n(irand(8)).scale("C:minor")

brand            // Binary random (0 or 1)
brandBy(0.3)     // Binary with 30% probability of 1
s("hh*10").pan(brand)

perlin           // Perlin noise (smoother than rand)
s("bd*4").cutoff(perlin.range(500,8000))
```

### Mouse Input
```javascript
mousex.segment(4).range(0,7) // X position
mousey.segment(4).range(0,7) // Y position
n(mousex.segment(4).range(0,7)).scale("C:minor")
```

### Signal Methods

All signals support:
```javascript
.range(min, max)  // Map to range
.segment(n)       // Sample n times per cycle
.slow(n)          // Slow down
.fast(n)          // Speed up
```

---

## Random Modifiers

Add probabilistic behavior.

### choose / wchoose
```javascript
note("c2 g2").s(choose("sine", "triangle", "bd:6"))

// Weighted choice
note("c2").s(wchoose(["sine",10], ["triangle",1], ["bd:6",1]))
```

### chooseCycles / wchooseCycles
Pick per cycle:
```javascript
chooseCycles("bd", "hh", "sd").s().fast(8)
wchooseCycles(["bd",10], ["hh",1], ["sd",1]).s().fast(8)
```

### degradeBy / degrade
Remove events randomly:
```javascript
s("hh*8").degradeBy(0.2)  // 20% removal chance
s("hh*8").degrade()       // 50% removal (shorthand)
s("[hh?0.2]*8")           // Mini-notation version
```

### undegradeBy / undegrade
Inverse of degrade:
```javascript
s("hh*8").undegradeBy(0.2) // Keep only 20%
s("hh*8").undegrade()      // Keep only 50%
```

### sometimesBy family
Apply function randomly:
```javascript
s("hh*8").sometimesBy(.4, x=>x.speed("0.5"))  // 40% chance
s("hh*8").sometimes(x=>x.speed("0.5"))        // 50% chance (default)
s("hh*8").often(x=>x.speed("0.5"))            // 75% chance
s("hh*8").rarely(x=>x.speed("0.5"))           // 25% chance
s("hh*8").almostNever(x=>x.speed("0.5"))      // 10% chance
s("hh*8").almostAlways(x=>x.speed("0.5"))     // 90% chance
s("hh*8").never(x=>x.speed("0.5"))            // 0% chance
s("hh*8").always(x=>x.speed("0.5"))           // 100% chance
```

### someCyclesBy / someCycles
Per-cycle randomization:
```javascript
s("bd,hh*8").someCyclesBy(.3, x=>x.speed("0.5"))
s("bd,hh*8").someCycles(x=>x.speed("0.5"))
```

---

## Conditional Modifiers

Apply functions conditionally.

### when
Apply when condition is true:
```javascript
"c3 eb3 g3".when("<0 1>/2", x=>x.sub("5")).note()
```

### lastOf / firstOf
Apply on specific cycles:
```javascript
note("c3 d3 e3 g3").lastOf(4, x=>x.rev())  // Every 4th cycle
note("c3 d3 e3 g3").firstOf(4, x=>x.rev()) // 1st of every 4
```

### chunk / chunkBack / fastChunk
Divide and process:
```javascript
"0 1 2 3".chunk(4, x=>x.add(7)).scale("A:minor").note()
"0 1 2 3".chunkBack(4, x=>x.add(7)).scale("A:minor").note()
```

### struct
Apply rhythmic structure:
```javascript
note("c,eb,g").struct("x ~ x ~ ~ x ~ x")
```

### mask
Silence when mask is 0:
```javascript
note("c [eb,g] d [eb,g]").mask("<1 [0 1]>")
```

### reset / restart
Reset pattern on events:
```javascript
s("[<bd lt> sd]*2, hh*8").reset("<x@3 x(5,8)>")
s("[<bd lt> sd]*2, hh*8").restart("<x@3 x(5,8)>")
```

### pick / pickmod
Select from list/table:
```javascript
note("<0 1 2!2 3>".pick(["g a", "e f", "f g f g", "g c d"]))
s("<a!2 [a,b] b>".pick({a: "bd(3,8)", b: "sd sd"}))
```

### inhabit / squeeze
Pattern substitution:
```javascript
"<a b [a,b]>".inhabit({
  a: s("bd(3,8)"),
  b: s("cp sd")
})

note(squeeze("<0@2 [1!2] 2>", ["g a", "f g f g", "g a c d"]))
```

### arp / arpWith
Arpeggiate stacked notes:
```javascript
note("<[c,eb,g]!2 [c,f,ab] [d,f,ab]>").arp("0 [0,2] 1 [0,2]")
```

---

## Tonal Functions

Musical theory operations using [tonaljs](https://github.com/tonaljs/tonal).

### scale(name)
Map numbers to scale degrees:

```javascript
n("0 2 4 6 4 2").scale("C:major")
n("0 2 4 6").scale("C:<major minor>/2")
n(rand.range(0,12).segment(8)).scale("C:ritusen")

// Scale format: "root:type"
// Root: c, c4, f#, bb4 (default octave 3)
// Types: major, minor, dorian, phrygian, etc.
// See: https://github.com/tonaljs/tonal/blob/main/packages/scale-type/data.ts
```

Available scales include:
- Major/minor and modes: `major`, `minor`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `locrian`
- Pentatonic: `pentatonic`, `minor:pentatonic`
- World scales: `ritusen`, `egyptian`, `kumoi`, `hirajoshi`
- Jazz: `bebop`, `bebop:major`, `altered`
- And many more...

### voicing()
Turn chord symbols into voicings:

```javascript
n("0 1 2 3").chord("<C Am F G>").voicing()

// With controls
chord("<C^7 A7b13 Dm7 G7>").voicing()
  .dict('ireal')     // Voicing dictionary
  .anchor('c4')      // Alignment note
  .mode('below')     // below/duck/above
  .offset(0)         // Octave shift

// Chord + bass example
chord("<C^7 A7b13 Dm7 G7>*2").dict('ireal').layer(
  x => x.struct("[~ x]*2").voicing(),
  x => n("0*4").set(x).mode("root:g2").voicing()
    .s('sawtooth').cutoff("800:4:2")
)
```

Chord symbols:
- Triads: `C`, `Cm`, `C+`, `Cdim`
- Sevenths: `C7`, `Cm7`, `C^7` (major 7), `Cm7b5` (half-dim)
- Extensions: `C9`, `C11`, `C13`
- Alterations: `C7#5`, `C7b9`, `A7b13`

### transpose(semitones)
Transpose by semitones:
```javascript
note("c e g").transpose(7)        // Up 7 semitones (perfect 5th)
note("c e g").transpose("<0 3 7>") // Pattern transposition
```

### scaleTranspose(steps)
Transpose within scale:
```javascript
"[-8 [2,4,6]]*2"
  .scale('C4:bebop:major')
  .scaleTranspose("<0 -1 -2 -3>")
  .note()
```

### rootNotes(octave)
Extract root notes from chords:
```javascript
"<C^7 A7b13 Dm7 G7>*2".layer(
  x => x.voicing('lefthand').struct("[~ x]*2").note(),
  x => x.rootNotes(2).note().s('sawtooth')
)
```

---

## Signal Chain and Architecture

Understanding the signal flow in Strudel.

### Signal Flow Order

1. **Event Generation**: Pattern triggers sound event
2. **Sound Source**: Sample or oscillator
   - Detune, pitch envelope, vibrato
3. **Gain**: Volume applied (with ADSR envelope)
4. **Filters** (single-use, in order):
   - Low-pass filter (`lpf`)
   - High-pass filter (`hpf`)
   - Band-pass filter (`bandpass`)
   - Vowel filter (`vowel`)
5. **Waveshaping**:
   - Sample rate reduction (`coarse`)
   - Bit crushing (`crush`)
   - Waveshape distortion (`shape`)
   - Distortion (`distort`)
6. **Modulation Effects**:
   - Tremolo (`tremolo`)
7. **Dynamics**:
   - Compressor (`compressor`)
8. **Spatial**:
   - Panning (`pan`)
   - Phaser (`phaser`)
   - Post-gain (`postgain`)
9. **Send to Orbit**:
   - Dry signal
   - Delay send
   - Reverb send
10. **Orbit Processing**:
    - Duck (sidechain)
    - Mix to output

### Orbits

Orbits are independent audio busses:

```javascript
// Default orbit is 1
s("bd sd").orbit(1)

// Use multiple orbits for separate effects
stack(
  s("hh*6").delay(.5).delaytime(.25).orbit(1),
  s("~ sd ~ sd").delay(.5).delaytime(.125).orbit(2)
)
```

**Important**: Each orbit has one delay and one reverb. Multiple patterns on same orbit share these effects, which can cause conflicts.

### Continuous vs Discrete Parameters

Most parameters are **sampled per event** (when sound triggers):
```javascript
s("supersaw").lpf(tri.range(100, 5000).slow(2))
// Triangle only sampled once per note
```

These parameters update **continuously** (smooth):
- ADSR envelopes (`attack`, `decay`, `sustain`, `release`)
- Pitch envelope (`penv` + ADSR)
- FM envelope (`fmenv`)
- Filter envelopes (`lpenv`, `hpenv`, `bpenv`)
- Tremolo (`tremolo`)
- Phaser (`phaser`)
- Vibrato (`vib`)
- Ducking (`duckorbit`)

Workaround for continuous modulation:
```javascript
s("supersaw").seg(16).lpf(tri.range(100, 5000).slow(2))
// More events = smoother modulation
```

---

## Advanced Techniques

### Multi-Line Patterns

Use backticks for complex patterns:

```javascript
note(`<
  [e5 [b4 c5] d5 [c5 b4]]
  [a4 [a4 c5] e5 [d5 c5]]
  [b4 [~ c5] d5 e5]
  [c5 a4 a4 ~]
>`)
```

### Layering

```javascript
// With stack()
stack(
  s("bd*4"),
  s("hh*8"),
  note("c e g").s("piano")
)

// With layer() - apply variations
s("bd hh sd hh").layer(
  x => x,                    // Original
  x => x.fast(2).gain(0.5),  // Double speed, quieter
  x => x.rev()               // Reversed
)
```

### Pattern Arithmetic

```javascript
note("c e g").add(7)      // Transpose up 7
note("c e g").sub(2)      // Transpose down 2
note("c e g").mul(2)      // Multiply values
note("c e g").div(2)      // Divide values
```

### Function Chaining

Strudel uses method chaining extensively:

```javascript
note("c d e f")
  .scale("C:major")
  .slow(2)
  .rev()
  .sometimes(x => x.add(7))
  .s("piano")
  .room(0.5)
  .lpf(2000)
```

### Creating Generative Patterns

```javascript
// Random note selection
n(irand(8).segment(8))
  .scale("C:minor:pentatonic")
  .s("piano")
  .sometimes(x => x.add(12))

// Euclidean rhythm generator
s("bd").segment(16).degradeBy(.5)

// Evolving patterns
note("c d e f")
  .iter(4)
  .every(4, rev)
  .sometimes(x => x.fast(2))
```

### Multiple Patterns ($:)

Run multiple patterns simultaneously in the REPL:

```javascript
$: s("bd*4").bank("RolandTR909")
$: s("hh*8").gain(0.6)
$: note("c a f e").s("piano").slow(2)
```

### Storing Patterns

```javascript
// Define reusable patterns
const drums = s("bd sd, hh*8")
const bass = note("c3*4").s("sawtooth")

stack(drums, bass)
```

### Pattern Modifiers with Functions

```javascript
const addReverb = x => x.room(0.8).roomsize(4)
const makeQuiet = x => x.gain(0.5)

s("bd sd cp hh")
  .sometimes(addReverb)
  .often(makeQuiet)
```

### Combining Mini-Notation with Functions

```javascript
"<c a f e>(3,8)"           // Euclidean rhythm
  .add(note("<0 7 12>"))   // Varying transposition
  .scale("C:major")
  .s("piano")
  .room(sine.slow(4).range(0, 0.5))
  .lpf(perlin.range(500, 5000))
```

### Complex Rhythmic Structures

```javascript
// Polyrhythms
s("{bd bd bd, sd sd, hh hh hh hh}")

// Nested euclidean patterns
s("bd(3,8), sd(5,16), hh(11,16)")

// Randomized structures
s("bd*<4 6 8>").struct(binary(irand(256)))
```

### Strudel URL Generation

When you create patterns, the REPL can generate shareable URLs. The pattern code is encoded in the URL hash.

### Custom Sample Packs

Create a `strudel.json` file:
```json
{
  "_base": "https://yoursite.com/samples/",
  "kick": "kicks/kick1.wav",
  "snare": ["snares/snare1.wav", "snares/snare2.wav"],
  "hihat": {
    "c3": "hihats/hihat_c3.wav",
    "c4": "hihats/hihat_c4.wav"
  }
}
```

Load it:
```javascript
samples('https://yoursite.com/samples/strudel.json')
s("kick snare:1 hihat")
```

### Performance Tips

1. **Limit polyphony**: Too many simultaneous sounds can cause glitches
2. **Use orbits wisely**: Separate reverb/delay needs into different orbits
3. **Optimize effects**: Heavy effects (reverb, phaser) can impact performance
4. **Sample caching**: Samples load on first play (might miss initial hit)
5. **Segment continuous signals**: Balance smoothness vs performance

---

## Quick Reference Tables

### Mini-Notation Symbols

| Symbol | Meaning | Example |
|--------|---------|---------|
| `space` | Sequence | `"bd sd"` |
| `*` | Multiply/speed up | `"bd*4"` |
| `/` | Divide/slow down | `"bd/2"` |
| `< >` | Alternate per cycle | `"<bd sd cp>"` |
| `[ ]` | Subdivide | `"bd [sd cp]"` |
| `~` | Rest/silence | `"bd ~ sd ~"` |
| `,` | Polyphony/stack | `"bd,hh*4"` |
| `@` | Elongate | `"bd@3 sd"` |
| `!` | Replicate | `"bd!4"` |
| `?` | Random (50%) | `"bd*8?"` |
| `?n` | Random (n%) | `"bd*8?0.3"` |
| `\|` | Random choice | `"bd \| sd"` |
| `( )` | Euclidean | `"bd(3,8)"` |
| `:` | Sample select | `"bd:2"` |

### Common Functions

| Category | Functions |
|----------|-----------|
| **Sound** | `s()`, `note()`, `sound()`, `n()`, `bank()` |
| **Time** | `slow()`, `fast()`, `early()`, `late()`, `euclid()` |
| **Structure** | `cat()`, `seq()`, `stack()`, `layer()` |
| **Random** | `choose()`, `degrade()`, `sometimes()`, `often()` |
| **Filters** | `lpf()`, `hpf()`, `bpf()`, `lpq()`, `vowel()` |
| **Envelope** | `attack()`, `decay()`, `sustain()`, `release()` |
| **Effects** | `room()`, `delay()`, `distort()`, `crush()` |
| **Spatial** | `pan()`, `jux()` |
| **Tonal** | `scale()`, `transpose()`, `voicing()`, `chord()` |

### Default Drum Sounds

```
bd, sd, rim, cp, hh, oh, cr, rd, ht, mt, lt
sh, cb, tb, perc, misc, fx
```

### Basic Waveforms

```
sine, sawtooth, square, triangle
white, pink, brown (noise)
```

### Common Banks

```
RolandTR808, RolandTR909, RolandTR707
LinnDrum, OberheimDMX, AkaiLinn9000
```

---

## Resources & Links

- **Strudel REPL**: https://strudel.cc/
- **Tutorial/Workshop**: https://strudel.cc/workshop/getting-started/
- **Discord Community**: https://discord.com/invite/HGEdXmRkzT
- **GitHub/Codeberg**: https://codeberg.org/uzu/strudel
- **TidalCycles**: https://tidalcycles.org/
- **Tonal.js** (music theory): https://github.com/tonaljs/tonal

### Example Patterns

Browse examples at: https://strudel.cc/examples/

### Learn More

- Mini-Notation: https://strudel.cc/learn/mini-notation/
- Samples: https://strudel.cc/learn/samples/
- Synths: https://strudel.cc/learn/synths/
- Effects: https://strudel.cc/learn/effects/
- Tonal Functions: https://strudel.cc/learn/tonal/

---

**End of Comprehensive Guide**

*This document covers the core functionality of Strudel. For the most up-to-date information, always refer to the official documentation at https://strudel.cc/*
