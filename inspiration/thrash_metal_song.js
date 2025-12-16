// Thrash Metal Song - Inspired by Master of Puppets style
// Simplified version with clearer structure and pacing

// Main palm-muted riff - tight and aggressive
const mainRiff = note("e2*8")
  .s("sawtooth")
  .lpf(500)
  .lpq(4)
  .gain(0.12)
  .distort("1:.5")
  .adsr(".001:.05:.9:.03");

// Power chord hits - heavy and open
const powerChords = note("<[e3,b3] [c3,g3] [d3,a3] [e3,b3]>")
  .s("sawtooth")
  .gain(0.14)
  .lpf(2000)
  .distort("1.5:.5")
  .adsr(".005:.1:.9:.08");

// Bass following the riff
const bass = note("e1*8")
  .s("sawtooth")
  .gain(0.13)
  .lpf(600)
  .distort("0.8:.5");

// Kick drum - double bass pattern
const kicks = s("bd:4")
  .bank("RolandTR909")
  .struct("x*8")
  .gain(0.15)
  .distort("0.4:.6");

// Snare on backbeat
const snare = s("sd:3")
  .bank("RolandTR909")
  .struct("~ x ~ x")
  .gain(0.16);

// Hi-hat keeping time
const hats = s("hh")
  .bank("RolandTR909")
  .struct("x*8")
  .gain(0.08);

// Simple structure: alternate between riff and chords
stack(
  mainRiff,
  powerChords.every(2, x => x), // Play every other cycle
  bass,
  kicks,
  snare,
  hats
)
  .compressor("-30:3:1:.003:.025")
  .gain(0.1)
  .postgain(0.6)
  .cpm(160)
  .orbit(0)
