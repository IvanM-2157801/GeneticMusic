import platform
import subprocess
import time

import supriya
from supriya import Envelope, synthdef
from supriya.ugens import EnvGen, Out, SinOsc

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


def main():
    # Boot realtime server
    server = supriya.Server().boot()
    server.add_synthdefs(simple_sine)
    server.sync()
    
    # Auto-connect SuperCollider to default audio output (Linux/PipeWire only)
    if platform.system() == "Linux":
        time.sleep(0.5)
        default_sink = subprocess.run(
            ['pactl', 'get-default-sink'],
            capture_output=True, text=True
        ).stdout.strip()
        subprocess.run(['pw-link', 'SuperCollider:out_1', f'{default_sink}:playback_FL'], stderr=subprocess.DEVNULL)
        subprocess.run(['pw-link', 'SuperCollider:out_2', f'{default_sink}:playback_FR'], stderr=subprocess.DEVNULL)
    
    print("Playing 3 notes...")
    
    # Play note 1: A4
    server.add_synth(simple_sine, frequency=440, amplitude=0.1, duration=1.0)
    time.sleep(1.0)
    
    # Play note 2: C#5
    server.add_synth(simple_sine, frequency=550, amplitude=0.1, duration=1.0)
    time.sleep(1.0)
    
    # Play note 3: E5
    server.add_synth(simple_sine, frequency=660, amplitude=0.1, duration=1.0)
    time.sleep(1.0)
    
    print("Done!")
    server.quit()


if __name__ == "__main__":
    main()