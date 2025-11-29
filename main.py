from pyo import *

BPM = 128
BARS = 8
NOTES_PER_BAR = 2
NOTES = ["C", "C#", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "B"]

s = Server()
s.boot()
s.start()

def main():
    s.amp = 0.1
    a = Sine(freq=500).out()
    s.gui(locals)
    Events()


if __name__ == "__main__":
    main()