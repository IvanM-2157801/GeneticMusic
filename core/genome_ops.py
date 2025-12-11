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


def mutate_rhythm(
    rhythm: str, mutation_rate: float = 0.1, max_subdivision: int = 4
) -> str:
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
        scale = [
            NoteName.C,
            NoteName.D,
            NoteName.E,
            NoteName.F,
            NoteName.G,
            NoteName.A,
            NoteName.B,
        ]

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
                    pitch, octave = (
                        pitches[pitch_idx % len(pitches)]
                        if pitches
                        else (NoteName.C, 4)
                    )
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
        phrases=[
            random_phrase(phrase_length, **note_kwargs) for _ in range(phrase_count)
        ],
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
        crossover_phrase(l1.phrases[i], l2.phrases[i]) for i in range(min_phrases)
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
        degrees = [
            str((self.root_degree + (interval // 2)) % 7) for interval in self.intervals
        ]
        return ", ".join(degrees)


@dataclass
class ChordProgression:
    """A sequence of chords for a layer."""

    chords: list[Chord]

    def __len__(self) -> int:
        return len(self.chords)

    def copy(self) -> "ChordProgression":
        return ChordProgression(
            [Chord(c.root_degree, c.intervals.copy()) for c in self.chords]
        )


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
            intervals = random.choice(
                [
                    [0, 4, 7],  # major
                    [0, 3, 7],  # minor
                    [0, 3, 6],  # dim
                    [0, 4, 8],  # aug
                    [0, 2, 7],  # sus2
                    [0, 5, 7],  # sus4
                ]
            )
        else:
            # 4+ notes: 7th chords and extensions
            base = random.choice(
                [
                    [0, 4, 7, 11],  # maj7
                    [0, 3, 7, 10],  # min7
                    [0, 4, 7, 10],  # dom7
                    [0, 3, 6, 9],  # dim7
                ]
            )
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
            new_chord.intervals = random.choice(
                [[0, 4, 7], [0, 3, 7], [0, 3, 6], [0, 4, 8], [0, 2, 7], [0, 5, 7]]
            )
        else:
            new_chord.intervals = random.choice(
                [[0, 4, 7, 11], [0, 3, 7, 10], [0, 4, 7, 10], [0, 3, 6, 9]]
            )[:notes_per_chord]

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


# === Dynamic Envelope Operations ===
# Envelope genome is a list of (time, value) points


@dataclass
class EnvelopeGenome:
    """Genome for dynamic/filter envelope evolution."""

    points: list[tuple[float, float]]  # (time_fraction 0-1, value)
    min_value: float = 0.0
    max_value: float = 1.0

    def copy(self) -> "EnvelopeGenome":
        return EnvelopeGenome(
            points=[(t, v) for t, v in self.points],
            min_value=self.min_value,
            max_value=self.max_value,
        )


def random_envelope(
    num_points: int = 3,
    min_value: float = 0.0,
    max_value: float = 1.0,
) -> EnvelopeGenome:
    """Generate a random envelope genome.

    Args:
        num_points: Number of control points (including start and end)
        min_value: Minimum possible value
        max_value: Maximum possible value

    Returns:
        EnvelopeGenome with random control points
    """
    points = []

    # Always have start point at time 0
    points.append((0.0, random.uniform(min_value, max_value)))

    # Add intermediate points
    for i in range(1, num_points - 1):
        time = random.uniform(0.1, 0.9)
        value = random.uniform(min_value, max_value)
        points.append((time, value))

    # Always have end point at time 1
    points.append((1.0, random.uniform(min_value, max_value)))

    # Sort by time
    points.sort(key=lambda p: p[0])

    return EnvelopeGenome(
        points=points,
        min_value=min_value,
        max_value=max_value,
    )


def mutate_envelope(
    envelope: EnvelopeGenome,
    mutation_rate: float = 0.2,
) -> EnvelopeGenome:
    """Mutate an envelope genome.

    Mutations:
    - Shift point values up/down
    - Add new point
    - Remove point (if > 2 points)
    - Shift point time position
    """
    new_points = [(t, v) for t, v in envelope.points]

    for i in range(len(new_points)):
        if random.random() < mutation_rate:
            t, v = new_points[i]

            mutation_type = random.choice(["value", "time", "both"])

            if mutation_type in ("value", "both"):
                # Mutate value
                delta = random.gauss(0, (envelope.max_value - envelope.min_value) * 0.2)
                new_v = max(envelope.min_value, min(envelope.max_value, v + delta))
                v = new_v

            if mutation_type in ("time", "both") and 0 < i < len(new_points) - 1:
                # Mutate time (not for first/last points)
                delta = random.gauss(0, 0.1)
                new_t = max(0.05, min(0.95, t + delta))
                t = new_t

            new_points[i] = (t, v)

    # Occasionally add or remove a point
    if random.random() < mutation_rate * 0.5:
        if len(new_points) < 6:
            # Add a new point
            time = random.uniform(0.1, 0.9)
            value = random.uniform(envelope.min_value, envelope.max_value)
            new_points.append((time, value))
        elif len(new_points) > 2:
            # Remove a random intermediate point
            idx = random.randint(1, len(new_points) - 2)
            new_points.pop(idx)

    # Sort by time
    new_points.sort(key=lambda p: p[0])

    return EnvelopeGenome(
        points=new_points,
        min_value=envelope.min_value,
        max_value=envelope.max_value,
    )


def crossover_envelope(
    env1: EnvelopeGenome,
    env2: EnvelopeGenome,
) -> EnvelopeGenome:
    """Crossover between two envelope genomes.

    Uses interpolation-based crossover at random time points.
    """
    # Sample both envelopes at the same time points
    sample_times = [0.0, 0.25, 0.5, 0.75, 1.0]
    new_points = []

    for t in sample_times:
        # Get interpolated value from each parent
        v1 = _interpolate_envelope(env1.points, t)
        v2 = _interpolate_envelope(env2.points, t)

        # Randomly choose or blend
        if random.random() < 0.3:
            # Blend
            value = (v1 + v2) / 2
        else:
            # Choose one
            value = v1 if random.random() < 0.5 else v2

        new_points.append((t, value))

    return EnvelopeGenome(
        points=new_points,
        min_value=min(env1.min_value, env2.min_value),
        max_value=max(env1.max_value, env2.max_value),
    )


def _interpolate_envelope(points: list[tuple[float, float]], time: float) -> float:
    """Interpolate envelope value at a given time."""
    if not points:
        return 0.5

    sorted_points = sorted(points, key=lambda p: p[0])

    # Find surrounding points
    for i in range(len(sorted_points) - 1):
        t1, v1 = sorted_points[i]
        t2, v2 = sorted_points[i + 1]

        if t1 <= time <= t2:
            if t2 == t1:
                return v1
            ratio = (time - t1) / (t2 - t1)
            return v1 + ratio * (v2 - v1)

    # Outside range
    if time <= sorted_points[0][0]:
        return sorted_points[0][1]
    return sorted_points[-1][1]


# === Phrase Variation Operations ===
# For musical development (theme and variations)


def phrase_similarity(phrase1: Phrase, phrase2: Phrase) -> float:
    """Calculate similarity between two phrases.

    Measures:
    - Melodic contour similarity (rising/falling pattern)
    - Rhythmic pattern similarity
    - Pitch class overlap
    - Key note positions (start, end, peak)

    Returns:
        Similarity score from 0.0 (completely different) to 1.0 (identical)
    """
    notes1 = [n for n in phrase1.notes if n.pitch != NoteName.REST]
    notes2 = [n for n in phrase2.notes if n.pitch != NoteName.REST]

    if not notes1 or not notes2:
        return 0.0 if (notes1 or notes2) else 1.0

    scores = []

    # 1. Melodic contour similarity
    contour1 = _get_melodic_contour(notes1)
    contour2 = _get_melodic_contour(notes2)
    contour_score = _contour_similarity(contour1, contour2)
    scores.append(contour_score)

    # 2. Pitch class overlap
    pc1 = {n.pitch.value % 12 for n in notes1}
    pc2 = {n.pitch.value % 12 for n in notes2}
    overlap = len(pc1 & pc2) / max(len(pc1 | pc2), 1)
    scores.append(overlap)

    # 3. Length similarity
    len_ratio = min(len(notes1), len(notes2)) / max(len(notes1), len(notes2))
    scores.append(len_ratio)

    # 4. Start/end note similarity
    start_same = 1.0 if notes1[0].pitch == notes2[0].pitch else 0.3
    end_same = 1.0 if notes1[-1].pitch == notes2[-1].pitch else 0.3
    scores.append((start_same + end_same) / 2)

    return sum(scores) / len(scores)


def _get_melodic_contour(notes: list[Note]) -> list[int]:
    """Get melodic contour as sequence of directions (-1, 0, 1)."""
    if len(notes) < 2:
        return []

    contour = []
    for i in range(len(notes) - 1):
        diff = notes[i + 1].midi_pitch - notes[i].midi_pitch
        if diff > 0:
            contour.append(1)  # Ascending
        elif diff < 0:
            contour.append(-1)  # Descending
        else:
            contour.append(0)  # Same

    return contour


def _contour_similarity(contour1: list[int], contour2: list[int]) -> float:
    """Compare two melodic contours."""
    if not contour1 or not contour2:
        return 0.5

    # Resample to same length
    len1, len2 = len(contour1), len(contour2)
    target_len = min(len1, len2, 10)

    def resample(contour, target):
        if len(contour) == target:
            return contour
        return [contour[i * len(contour) // target] for i in range(target)]

    c1 = resample(contour1, target_len)
    c2 = resample(contour2, target_len)

    # Count matches
    matches = sum(1 for i in range(target_len) if c1[i] == c2[i])
    return matches / target_len


def create_variation(
    original: Phrase,
    variation_type: str = "melodic",
    similarity_target: float = 0.6,
) -> Phrase:
    """Create a variation of a phrase.

    Args:
        original: The original theme phrase
        variation_type: Type of variation:
            - "rhythmic": Keep pitches, modify rhythm
            - "melodic": Keep rhythm, modify pitches
            - "ornamental": Add passing tones and embellishments
            - "simplify": Remove notes, longer durations
            - "inversion": Flip intervals
            - "retrograde": Reverse note order
        similarity_target: Target similarity (0.0-1.0)

    Returns:
        A variation phrase
    """
    notes = deepcopy(original.notes)

    if variation_type == "rhythmic":
        # Keep pitches, shift rhythms
        for note in notes:
            if random.random() < 0.3:
                note.duration *= random.choice([0.5, 1.0, 2.0])

    elif variation_type == "melodic":
        # Keep rhythm, shift some pitches
        for note in notes:
            if note.pitch != NoteName.REST and random.random() < 0.4:
                # Shift by step or third
                shift = random.choice([-3, -2, -1, 1, 2, 3])
                new_pitch_val = (note.pitch.value + shift) % 12
                # Find matching NoteName
                for name in NoteName:
                    if name.value == new_pitch_val:
                        note.pitch = name
                        break

    elif variation_type == "ornamental":
        # Add passing tones between notes
        new_notes = []
        for i, note in enumerate(notes):
            new_notes.append(note)
            if i < len(notes) - 1 and random.random() < 0.3:
                # Add passing tone
                if note.pitch != NoteName.REST and notes[i + 1].pitch != NoteName.REST:
                    passing = deepcopy(note)
                    passing.duration = note.duration * 0.5
                    note.duration = note.duration * 0.5
                    # Pitch between current and next
                    mid_val = (note.pitch.value + notes[i + 1].pitch.value) // 2
                    for name in NoteName:
                        if name.value == mid_val % 12:
                            passing.pitch = name
                            break
                    new_notes.append(passing)
        notes = new_notes

    elif variation_type == "simplify":
        # Remove some notes, lengthen others
        new_notes = []
        i = 0
        while i < len(notes):
            note = deepcopy(notes[i])
            if random.random() < 0.3 and i < len(notes) - 1:
                # Skip next note, double this duration
                note.duration *= 2
                i += 1
            new_notes.append(note)
            i += 1
        notes = new_notes

    elif variation_type == "inversion":
        # Invert intervals around first note
        if notes and notes[0].pitch != NoteName.REST:
            pivot = notes[0].midi_pitch
            for note in notes[1:]:
                if note.pitch != NoteName.REST:
                    interval = note.midi_pitch - pivot
                    new_pitch = pivot - interval
                    # Keep in reasonable range
                    new_pitch = max(36, min(84, new_pitch))
                    note.octave = new_pitch // 12 - 1
                    pitch_val = new_pitch % 12
                    for name in NoteName:
                        if name.value == pitch_val:
                            note.pitch = name
                            break

    elif variation_type == "retrograde":
        # Reverse note order (keep durations in place)
        pitches = [(n.pitch, n.octave) for n in notes]
        pitches.reverse()
        for i, note in enumerate(notes):
            if i < len(pitches):
                note.pitch, note.octave = pitches[i]

    return Phrase(notes)


def generate_response(
    call: Phrase,
    response_type: str = "answer",
) -> Phrase:
    """Generate a response phrase to a call.

    Args:
        call: The "call" phrase
        response_type:
            - "answer": Similar rhythm, complementary melody (resolve tension)
            - "echo": Similar but shorter/softer
            - "contrast": Different rhythm/melody that complements

    Returns:
        A response phrase
    """
    notes = deepcopy(call.notes)

    if response_type == "answer":
        # Similar rhythm, resolve to tonic area
        for note in notes:
            if note.pitch != NoteName.REST:
                # Move toward tonic (C) or dominant (G)
                if random.random() < 0.5:
                    # Resolve to nearby stable tone
                    stable_tones = [NoteName.C, NoteName.E, NoteName.G]
                    note.pitch = random.choice(stable_tones)

    elif response_type == "echo":
        # Shorter version (take first half)
        mid = len(notes) // 2
        notes = notes[: max(mid, 2)]
        # Lower octave
        for note in notes:
            if note.pitch != NoteName.REST:
                note.octave = max(2, note.octave - 1)

    elif response_type == "contrast":
        # Different rhythm and complementary pitches
        for note in notes:
            if random.random() < 0.4:
                note.duration *= random.choice([0.5, 2.0])
            if note.pitch != NoteName.REST and random.random() < 0.5:
                # Move to third or sixth above/below
                shift = random.choice([-4, -3, 3, 4])
                new_pitch_val = (note.pitch.value + shift) % 12
                for name in NoteName:
                    if name.value == new_pitch_val:
                        note.pitch = name
                        break

    return Phrase(notes)
