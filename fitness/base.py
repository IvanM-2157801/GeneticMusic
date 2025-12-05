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


# === Rhythm Fitness Utilities ===
# Rhythm is a string like "12041302" where each char is subdivisions per beat

class RhythmFitnessFunction(ABC):
    """Abstract base for rhythm-specific fitness functions."""
    
    @abstractmethod
    def evaluate(self, rhythm: str) -> float:
        """Evaluate fitness of a rhythm pattern. Returns 0.0 - 1.0."""
        pass


def rhythm_density(rhythm: str) -> float:
    """Average note density (notes per beat). Returns 0-1 normalized."""
    if not rhythm:
        return 0.0
    total = sum(int(c) for c in rhythm)
    # Normalize: 0 notes = 0, 4 notes per beat average = 1
    return min(total / (len(rhythm) * 4), 1.0)


def rhythm_rest_ratio(rhythm: str) -> float:
    """Ratio of rest beats to total beats."""
    if not rhythm:
        return 0.0
    rests = sum(1 for c in rhythm if c == '0')
    return rests / len(rhythm)


def rhythm_variety(rhythm: str) -> float:
    """Measure variety of subdivisions used."""
    if not rhythm:
        return 0.0
    unique_subdivisions = len(set(rhythm))
    return min(unique_subdivisions / 5.0, 1.0)  # 0-4 subdivisions possible


def rhythm_syncopation(rhythm: str) -> float:
    """Measure syncopation (off-beat emphasis)."""
    if len(rhythm) < 2:
        return 0.0
    # Syncopation: more notes on weak beats than strong beats
    # Assuming 4/4: beats 1,3 are strong, 2,4 are weak
    strong_notes = 0
    weak_notes = 0
    for i, c in enumerate(rhythm):
        subdivs = int(c)
        if i % 2 == 0:  # Strong beat
            strong_notes += subdivs
        else:  # Weak beat
            weak_notes += subdivs
    
    total = strong_notes + weak_notes
    if total == 0:
        return 0.0
    # More weak beat notes = more syncopation
    return weak_notes / total


def rhythm_regularity(rhythm: str) -> float:
    """Measure rhythmic regularity/consistency."""
    if not rhythm:
        return 0.0
    # Count how many beats have the same subdivision
    from collections import Counter
    counts = Counter(rhythm)
    most_common_count = counts.most_common(1)[0][1]
    return most_common_count / len(rhythm)


def rhythm_downbeat_emphasis(rhythm: str) -> float:
    """Measure emphasis on downbeats (beat 1 of each bar)."""
    if len(rhythm) < 4:
        return 0.0
    # Assuming 4 beats per bar
    downbeat_notes = 0
    other_notes = 0
    for i, c in enumerate(rhythm):
        subdivs = int(c)
        if i % 4 == 0:  # Downbeat
            downbeat_notes += subdivs
        else:
            other_notes += subdivs
    
    total = downbeat_notes + other_notes
    if total == 0:
        return 0.0
    # Want downbeats to have notes
    return min(downbeat_notes / (total * 0.25 + 0.001), 1.0)
