import random
from copy import deepcopy
from dataclasses import dataclass
from .music import Note, NoteName, Phrase, Layer

REST_PROBABILITY = 0.4

# === Rhythm Genome Operations ===
# Rhythm genome is a string where each char represents subdivisions per beat
# '0' = rest, '1' = 1 note, '2' = 2 notes (eighth notes), '3' = triplet, '4' = 4 notes (sixteenths)

def random_rhythm(num_beats: int, max_subdivision: int = 4) -> str:
    """Generate a random rhythm pattern."""
    return "".join(str(random.randint(0, max_subdivision)) for _ in range(num_beats))


def mutate_rhythm(rhythm: str, mutation_rate: float = 0.1, max_subdivision: int = 4) -> str:
    """Mutate a rhythm pattern."""
    chars = list(rhythm)
    for i in range(len(chars)):
        if random.random() < mutation_rate:
            chars[i] = str(random.randint(0, max_subdivision))
    return "".join(chars)


def crossover_rhythm(r1: str, r2: str) -> str:
    """Single-point crossover between two rhythm patterns."""
    min_len = min(len(r1), len(r2))
    if min_len < 2:
        return r1
    point = random.randint(1, min_len - 1)
    return r1[:point] + r2[point:min_len]


def rhythm_to_phrase(
    rhythm: str,
    scale: list[NoteName] | None = None,
    octave_range: tuple[int, int] = (4, 5),
) -> Phrase:
    """Convert a rhythm pattern to a Phrase with random pitches."""
    if scale is None:
        scale = [NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B]
    
    notes = []
    for beat_char in rhythm:
        subdivisions = int(beat_char)
        if subdivisions == 0:
            # Rest for the whole beat
            notes.append(Note(NoteName.REST, duration=1.0))
        else:
            # Create subdivided notes
            duration = 1.0 / subdivisions
            for _ in range(subdivisions):
                pitch = random.choice(scale)
                octave = random.randint(*octave_range)
                notes.append(Note(pitch, octave=octave, duration=duration))
    
    return Phrase(notes)


def phrase_with_rhythm(
    phrase: Phrase,
    rhythm: str,
) -> Phrase:
    """Apply a rhythm pattern to an existing phrase, keeping its pitches where possible."""
    # Extract pitches from the phrase (ignoring rests)
    pitches = [(n.pitch, n.octave) for n in phrase.notes if n.pitch != NoteName.REST]
    pitch_idx = 0
    
    notes = []
    for beat_char in rhythm:
        subdivisions = int(beat_char)
        if subdivisions == 0:
            notes.append(Note(NoteName.REST, duration=1.0))
        else:
            duration = 1.0 / subdivisions
            for _ in range(subdivisions):
                if pitch_idx < len(pitches):
                    pitch, octave = pitches[pitch_idx]
                    pitch_idx += 1
                else:
                    # Wrap around if we run out of pitches
                    pitch, octave = pitches[pitch_idx % len(pitches)] if pitches else (NoteName.C, 4)
                    pitch_idx += 1
                notes.append(Note(pitch, octave=octave, duration=duration))
    
    return Phrase(notes)


# === Note Operations ===

def random_note(
    scale: list[NoteName] | None = None,
    octave_range: tuple[int, int] = (3, 5),
) -> Note:
    if random.random() < REST_PROBABILITY:
        return Note(NoteName.REST)
    
    if scale is None:
        scale = list(NoteName)
        scale.remove(NoteName.REST)
    
    return Note(
        pitch=random.choice(scale),
        octave=random.randint(*octave_range),
        duration=random.choice([0.25, 0.5, 1.0, 2.0])
    )


def random_phrase(length: int, **note_kwargs) -> Phrase:
    return Phrase([random_note(**note_kwargs) for _ in range(length)])


def random_layer(
    name: str,
    phrase_count: int,
    phrase_length: int,
    instrument: str = "piano",
    **note_kwargs,
) -> Layer:
    return Layer(
        name=name,
        phrases=[random_phrase(phrase_length, **note_kwargs) for _ in range(phrase_count)],
        instrument=instrument,
    )


# === Mutation Operations ===

def mutate_note(note: Note, scale: list[NoteName] | None = None) -> Note:
    mutation_type = random.choice(["pitch", "octave", "duration"])
    new_note = deepcopy(note)
    
    if mutation_type == "pitch":
        if scale:
            new_note.pitch = random.choice(scale)
        else:
            pitches = [p for p in NoteName if p != NoteName.REST]
            new_note.pitch = random.choice(pitches)
    elif mutation_type == "octave":
        new_note.octave = max(1, min(7, new_note.octave + random.choice([-1, 1])))
    elif mutation_type == "duration":
        new_note.duration = random.choice([0.25, 0.5, 1.0, 2.0])
    
    return new_note


def mutate_phrase(phrase: Phrase, mutation_rate: float = 0.1) -> Phrase:
    new_notes = []
    for note in phrase.notes:
        if random.random() < mutation_rate:
            new_notes.append(mutate_note(note))
        else:
            new_notes.append(deepcopy(note))
    return Phrase(new_notes)


def mutate_layer(layer: Layer, mutation_rate: float = 0.1) -> Layer:
    return Layer(
        name=layer.name,
        phrases=[mutate_phrase(p, mutation_rate) for p in layer.phrases],
        instrument=layer.instrument,
    )


# === Crossover Operations ===

# TODO: crossover with multiple parents?
def crossover_phrase(p1: Phrase, p2: Phrase) -> Phrase:
    min_len = min(len(p1.notes), len(p2.notes))
    if min_len < 2:
        return deepcopy(p1)
    
    point = random.randint(1, min_len - 1)
    return Phrase(deepcopy(p1.notes[:point]) + deepcopy(p2.notes[point:min_len]))


def crossover_layer(l1: Layer, l2: Layer) -> Layer:
    min_phrases = min(len(l1.phrases), len(l2.phrases))
    new_phrases = [
        crossover_phrase(l1.phrases[i], l2.phrases[i])
        for i in range(min_phrases)
    ]
    return Layer(name=l1.name, phrases=new_phrases, instrument=l1.instrument)


# === Chord Genome Operations ===
# A chord genome is a list of chords, where each chord is a list of intervals (semitones from root)
# Example: [[0, 4, 7], [0, 3, 7], [0, 4, 7, 11]] = Major triad, Minor triad, Major 7th

# Common chord types as interval patterns
CHORD_TYPES = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented": [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "major7": [0, 4, 7, 11],
    "minor7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "dim7": [0, 3, 6, 9],
    "add9": [0, 4, 7, 14],
    "power": [0, 7],  # Power chord (root + fifth)
}

# Chord progressions common in different genres (as scale degrees 0-6)
COMMON_PROGRESSIONS = {
    "pop": [[0, 4, 5, 3], [0, 5, 3, 4], [0, 3, 4, 4]],  # I-V-vi-IV, I-vi-IV-V
    "jazz": [[1, 4, 0], [1, 4, 0, 3], [0, 1, 2, 4]],  # ii-V-I, ii-V-I-IV
    "blues": [[0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4]],  # 12-bar blues
    "rock": [[0, 3, 4, 3], [0, 4, 5, 4], [0, 6, 3, 4]],  # I-IV-V-IV
    "metal": [[0, 5, 6, 4], [0, 6, 5, 0]],  # Power chord progressions
}


@dataclass
class Chord:
    """Represents a single chord with root and intervals."""
    root_degree: int  # Scale degree (0-6) for the root
    intervals: list[int]  # Semitones from root (e.g., [0, 4, 7] for major)
    
    def to_strudel_notes(self, octave: int = 4) -> str:
        """Convert chord to Strudel notation (comma-separated scale degrees)."""
        # For scale-degree mode, we just output the degrees offset by root
        degrees = [str((self.root_degree + (interval // 2)) % 7) for interval in self.intervals]
        return ", ".join(degrees)


@dataclass
class ChordProgression:
    """A sequence of chords for a layer."""
    chords: list[Chord]
    
    def __len__(self) -> int:
        return len(self.chords)
    
    def copy(self) -> "ChordProgression":
        return ChordProgression([
            Chord(c.root_degree, c.intervals.copy()) 
            for c in self.chords
        ])


def random_chord(
    notes_per_chord: int = 3,
    allowed_types: list[str] | None = None,
) -> Chord:
    """Generate a random chord.
    
    Args:
        notes_per_chord: Number of notes in the chord (2-4 typically)
        allowed_types: List of chord type names to choose from, or None for any
    """
    root_degree = random.randint(0, 6)
    
    if allowed_types:
        chord_type = random.choice(allowed_types)
        intervals = CHORD_TYPES.get(chord_type, [0, 4, 7])[:notes_per_chord]
    else:
        # Generate random intervals based on notes_per_chord
        if notes_per_chord == 2:
            # Dyads: root + some interval
            intervals = [0, random.choice([3, 4, 5, 7])]
        elif notes_per_chord == 3:
            # Triads
            intervals = random.choice([
                [0, 4, 7],   # major
                [0, 3, 7],   # minor
                [0, 3, 6],   # dim
                [0, 4, 8],   # aug
                [0, 2, 7],   # sus2
                [0, 5, 7],   # sus4
            ])
        else:
            # 4+ notes: 7th chords and extensions
            base = random.choice([
                [0, 4, 7, 11],  # maj7
                [0, 3, 7, 10],  # min7
                [0, 4, 7, 10],  # dom7
                [0, 3, 6, 9],   # dim7
            ])
            intervals = base[:notes_per_chord]
    
    return Chord(root_degree, intervals)


def random_chord_progression(
    num_chords: int = 4,
    notes_per_chord: int = 3,
    allowed_types: list[str] | None = None,
) -> ChordProgression:
    """Generate a random chord progression.
    
    Args:
        num_chords: Number of chords in the progression
        notes_per_chord: Number of notes per chord
        allowed_types: List of chord type names to choose from
    """
    chords = [random_chord(notes_per_chord, allowed_types) for _ in range(num_chords)]
    return ChordProgression(chords)


def mutate_chord(chord: Chord, notes_per_chord: int = 3) -> Chord:
    """Mutate a single chord."""
    new_chord = Chord(chord.root_degree, chord.intervals.copy())
    
    mutation_type = random.choice(["root", "type", "voicing"])
    
    if mutation_type == "root":
        # Change root by step or skip
        step = random.choice([-2, -1, 1, 2])
        new_chord.root_degree = (new_chord.root_degree + step) % 7
    
    elif mutation_type == "type":
        # Change chord quality
        if notes_per_chord == 2:
            new_chord.intervals = [0, random.choice([3, 4, 5, 7])]
        elif notes_per_chord == 3:
            new_chord.intervals = random.choice([
                [0, 4, 7], [0, 3, 7], [0, 3, 6], [0, 4, 8], [0, 2, 7], [0, 5, 7]
            ])
        else:
            new_chord.intervals = random.choice([
                [0, 4, 7, 11], [0, 3, 7, 10], [0, 4, 7, 10], [0, 3, 6, 9]
            ])[:notes_per_chord]
    
    elif mutation_type == "voicing":
        # Shift one interval slightly
        if len(new_chord.intervals) > 1:
            idx = random.randint(1, len(new_chord.intervals) - 1)
            shift = random.choice([-1, 1])
            new_chord.intervals[idx] = max(1, new_chord.intervals[idx] + shift)
    
    return new_chord


def mutate_chord_progression(
    progression: ChordProgression,
    mutation_rate: float = 0.1,
    notes_per_chord: int = 3,
) -> ChordProgression:
    """Mutate a chord progression."""
    new_chords = []
    for chord in progression.chords:
        if random.random() < mutation_rate:
            new_chords.append(mutate_chord(chord, notes_per_chord))
        else:
            new_chords.append(Chord(chord.root_degree, chord.intervals.copy()))
    return ChordProgression(new_chords)


def crossover_chord_progression(
    prog1: ChordProgression,
    prog2: ChordProgression,
) -> ChordProgression:
    """Single-point crossover between two chord progressions."""
    min_len = min(len(prog1), len(prog2))
    if min_len < 2:
        return prog1.copy()
    
    point = random.randint(1, min_len - 1)
    
    new_chords = []
    for i in range(min_len):
        if i < point:
            c = prog1.chords[i]
        else:
            c = prog2.chords[i]
        new_chords.append(Chord(c.root_degree, c.intervals.copy()))
    
    return ChordProgression(new_chords)
