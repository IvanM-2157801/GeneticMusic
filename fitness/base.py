from abc import ABC, abstractmethod
from core.music import Layer, Phrase, Note, NoteName


class FitnessFunction(ABC):
    """Abstract base for genre-specific fitness functions."""

    @abstractmethod
    def evaluate(self, layer: Layer) -> float:
        """Evaluate fitness of a layer. Returns 0.0 - 1.0."""
        pass

    def evaluate_phrase(self, phrase: Phrase) -> float:
        """Evaluate a single phrase. Override for phrase-level fitness."""
        return 0.5


# === Common Fitness Utilities ===


def note_variety(phrase: Phrase) -> float:
    """Measure pitch variety (0-1). Higher = more variety."""
    if not phrase.notes:
        return 0.0
    pitches = {n.pitch for n in phrase.notes if n.pitch != NoteName.REST}
    return min(len(pitches) / 7.0, 1.0)  # Normalize to ~octave


def rest_ratio(phrase: Phrase) -> float:
    """Ratio of rests to total notes."""
    if not phrase.notes:
        return 0.0
    rests = sum(1 for n in phrase.notes if n.pitch == NoteName.REST)
    return rests / len(phrase.notes)


def interval_smoothness(phrase: Phrase) -> float:
    """Measure melodic smoothness (smaller intervals = higher score)."""
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if len(notes) < 2:
        return 0.5

    total_interval = 0
    for i in range(len(notes) - 1):
        interval = abs(notes[i].midi_pitch - notes[i + 1].midi_pitch)
        total_interval += interval

    avg_interval = total_interval / (len(notes) - 1)
    # Penalize large jumps, reward stepwise motion
    return max(0, 1 - (avg_interval / 12))


def scale_adherence(phrase: Phrase, scale: list[NoteName]) -> float:
    """Measure how well notes fit a scale."""
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if not notes:
        return 1.0

    in_scale = sum(1 for n in notes if n.pitch in scale)
    return in_scale / len(notes)


def rhythmic_variety(phrase: Phrase) -> float:
    """Measure duration variety."""
    if not phrase.notes:
        return 0.0
    durations = {n.duration for n in phrase.notes}
    return min(len(durations) / 4.0, 1.0)


# === New Advanced Utilities ===


def tonic_resolution(phrase: Phrase, root_pitch: NoteName) -> float:
    """Checks if the last note resolves to the Tonic (root) of the key."""
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if not notes:
        return 0.0

    last_note = notes[-1]
    # Check if the note pitch matches the root
    if last_note.pitch == root_pitch:
        return 1.0

    # Partial credit for ending on the 5th (Dominant)
    # This logic assumes we can calculate the 5th based on NoteName structure
    # For now, we return 0.0 if not root
    return 0.0


def contour_direction(phrase: Phrase) -> float:
    """
    Measures 'Arc' consistency.
    Low score = zig-zag (jittery). High score = consistent rising/falling lines.
    """
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if len(notes) < 3:
        return 1.0

    changes = 0
    # Calculate directions: 1 for up, -1 for down, 0 for same
    directions = []
    for i in range(len(notes) - 1):
        diff = notes[i + 1].midi_pitch - notes[i].midi_pitch
        if diff > 0:
            directions.append(1)
        elif diff < 0:
            directions.append(-1)
        else:
            directions.append(0)

    # Count how many times the sign changes (zigzagging)
    for i in range(len(directions) - 1):
        if directions[i] != directions[i + 1] and directions[i] != 0:
            changes += 1

    # Normalize: Fewer changes is better for an "Arc"
    return max(0, 1.0 - (changes / len(notes)))


def syncopation_score(phrase: Phrase) -> float:
    """
    Measures groove: Ratio of notes starting on off-beats vs on-beats.
    Assumes standard 4/4 time where x.0 is a beat.
    """
    on_beat_count = 0
    off_beat_count = 0
    current_time = 0.0

    for note in phrase.notes:
        if note.pitch != NoteName.REST:
            # If current_time is close to a whole number, it's on a beat
            if abs(current_time - round(current_time)) < 0.05:
                on_beat_count += 1
            else:
                off_beat_count += 1
        current_time += note.duration

    total = on_beat_count + off_beat_count
    if total == 0:
        return 0.0

    # We want a balance. Pure syncopation (1.0) is chaotic.
    # A ratio of ~0.4 (40% off-beat) is usually "groovy".
    ratio = off_beat_count / total
    return 1.0 - abs(0.4 - ratio)


# Common scales
MAJOR_SCALE = [
    NoteName.C,
    NoteName.D,
    NoteName.E,
    NoteName.F,
    NoteName.G,
    NoteName.A,
    NoteName.B,
]
MINOR_SCALE = [
    NoteName.C,
    NoteName.D,
    NoteName.DS,
    NoteName.F,
    NoteName.G,
    NoteName.GS,
    NoteName.AS,
]
PENTATONIC = [NoteName.C, NoteName.D, NoteName.E, NoteName.G, NoteName.A]
BLUES_SCALE = [
    NoteName.C,
    NoteName.DS,
    NoteName.F,
    NoteName.FS,
    NoteName.G,
    NoteName.AS,
]
