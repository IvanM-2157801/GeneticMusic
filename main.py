import asyncio
import supriya
from supriya import Envelope, synthdef
from supriya.ugens import EnvGen, Line, Out, SinOsc

BPM = 128
BARS = 8
NOTES_PER_BAR = 2
NOTES = ["C", "C#", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "B"]


@synthdef()
def simple_sine(frequency=500, amplitude=0.1, duration=1.0):
    sine = SinOsc.ar(frequency=frequency) * amplitude
    # Sustain at full volume, then free the synth when done
    envelope = EnvGen.kr(
        envelope=Envelope(amplitudes=[0, 1, 1, 0], durations=[0.01, duration - 0.02, 0.01]),
        done_action=2
    )
    Out.ar(bus=0, source=[sine * envelope] * 2)


async def main():
    # Use non-realtime rendering to generate audio file
    score = supriya.Score()
    
    with score.at(0):
        score.add_synthdefs(simple_sine)
        score.add_synth(simple_sine, frequency=440, amplitude=0.1, duration=1.0)  # A4
    
    with score.at(1):
        score.add_synth(simple_sine, frequency=550, amplitude=0.1, duration=1.0)  # C#5
    
    with score.at(2):
        score.add_synth(simple_sine, frequency=660, amplitude=0.1, duration=1.0)  # E5
    
    # Render to audio file
    output_path = await score.render(
        output_file_path="output.wav",
        duration=4.0,
        sample_rate=44100,
    )
    
    print(f"Audio rendered to: {output_path}")
    print("Play with: aplay output.wav (or any audio player)")


if __name__ == "__main__":
    asyncio.run(main())