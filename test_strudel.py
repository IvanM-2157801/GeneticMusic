"""Test Strudel URL generation."""
import strudel
from core.music import Note, NoteName, Phrase, Layer

# Test simple notes
notes = ["c4", "d4", "e4", "f4", "g4"]
print("Simple test:")
strudel.create_strudel(notes, 4)

# Test with rests
notes_with_rest = ["c4", "~", "e4", "~"]
print("\nWith rests:")
strudel.create_strudel(notes_with_rest, 4)

# Test with subdivisions
notes_subdivided = ["c4", "[d4 e4]", "f4", "[g4 a4 b4]"]
print("\nWith subdivisions:")
strudel.create_strudel(notes_subdivided, 4)

# Test with Phrase object
phrase = Phrase([
    Note(NoteName.C, octave=4, duration=1.0),
    Note(NoteName.D, octave=4, duration=0.5),
    Note(NoteName.E, octave=4, duration=0.5),
    Note(NoteName.REST, octave=4, duration=1.0),
])
print("\nFrom Phrase:")
print(phrase.to_strudel())
