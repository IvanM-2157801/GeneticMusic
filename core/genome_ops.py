import random
from copy import deepcopy
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
        duration=random.choice([0.25, 0.5, 1.0, 2.0]),
        velocity=random.uniform(0.5, 1.0),
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
    mutation_type = random.choice(["pitch", "octave", "duration", "velocity"])
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
    else:
        new_note.velocity = max(0.1, min(1.0, new_note.velocity + random.uniform(-0.2, 0.2)))
    
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
