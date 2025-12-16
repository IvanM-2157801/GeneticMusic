// Metal Song in Strudel
// Aggressive, heavy sound with palm-muted chugging rhythms, power chords, and blast beats

// Heavy palm-muted guitar riff - the foundation of metal
const palmMutedRiff = note("<[e2 e2 e2] [e2 g2] [e2 e2 e2] [e2 f2]>")
  .s("sawtooth")
  .lpf("<400 500 400 600>") // Low-pass for palm-mute effect
  .lpq(3)
  .gain(0.15)
  .distort("2:.5")
  .room(0.1)
  .stack(
    note("<[e3 e3 e3] [e3 g3] [e3 e3 e3] [e3 f3]>")
      .s("sawtooth")
      .lpf("<400 500 400 600>")
      .lpq(3)
      .detune(3) // Slight detuning for thickness
  )
  .adsr(".001:.1:.8:.05");

// Power chord progression - open chords for heavy sections
const powerChords = note("<[e3,b3,e4] [c3,g3,c4] [d3,a3,d4] [a2,e3,a3]>")
  .s("sawtooth")
  .slow(2)
  .struct("x@3 [x x]")
  .gain(0.15)
  .lpf(2000)
  .distort("2:.5")
  .room(0.15)
  .adsr(".005:.1:.9:.1");

// Lead guitar - screaming high notes with vibrato
const leadGuitar = note("<[e5 g5 f5 e5] ~ [g5 a5 g5 f5] [e5 d5 c5 b4]>")
  .s("sawtooth")
  .slow(4)
  .gain(0.12)
  .vib("8:0.5")
  .distort("1.5:.5")
  .delay(0.3)
  .delaytime(0.125)
  .delayfeedback(0.4)
  .lpf(4000)
  .room(0.3);

// Aggressive bass - following the root notes
const metalBass = note("<e1 c1 d1 a0>")
  .s("sawtooth")
  .slow(2)
  .struct("x*8")
  .gain(0.15)
  .lpf(800)
  .distort("1:.5")
  .adsr(".001:.05:.9:.05");

// Double bass drum pedal - fast kick pattern
const doubleBassDrum = s("bd:4")
  .bank("RolandTR909")
  .struct("x(7,16)")
  .gain("<0.15 0.18 0.12 0.18>")
  .distort("0.5:.6");

// Snare - punchy and aggressive
const snare = s("sd:3")
  .bank("RolandTR909")
  .struct("~ x ~ x")
  .gain(0.18)
  .room(0.1);

// Crash cymbals - accents on transitions
const crashes = s("cr")
  .struct("<x ~ ~ ~>/2")
  .gain(0.12)
  .room(0.3);

// Ride for intensity building
const ride = s("rd")
  .struct("~ ~ x(5,8) ~")
  .gain(0.08)
  .sometimes(x => x.speed(1.2));

// China cymbal hits for dramatic effect
const china = s("oh:4")
  .bank("RolandTR909")
  .struct("<~ ~ x ~>/4")
  .gain(0.12)
  .distort("0.3:.6");

// Combine everything with different sections
stack(
  palmMutedRiff.every(4, x => x.fast(2)), // Occasionally speed up riff
  powerChords.every(8, rev), // Reverse progression occasionally
  leadGuitar.sometimes(x => x.add(12)), // Octave jumps
  metalBass,
  doubleBassDrum,
  snare,
  crashes,
  ride.often(x => x.gain(0.1)),
  china
)
  .compressor("-30:3:1:.003:.025") // Gentle compression to control peaks
  .gain(0.12) // Master volume control
  .postgain(0.8) // Additional final gain control
  .cpm(140) // 140 BPM - typical metal tempo
  .orbit(0)
