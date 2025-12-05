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


# Common scales
MAJOR_SCALE = [NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B]
MINOR_SCALE = [NoteName.C, NoteName.D, NoteName.DS, NoteName.F, NoteName.G, NoteName.GS, NoteName.AS]
PENTATONIC = [NoteName.C, NoteName.D, NoteName.E, NoteName.G, NoteName.A]
BLUES_SCALE = [NoteName.C, NoteName.DS, NoteName.F, NoteName.FS, NoteName.G, NoteName.AS]
