"""Base fitness functions and primitive metrics for music evaluation.

This module contains:
1. FitnessFunction - Abstract base class for evaluating Layer objects
2. Primitive metrics - Building blocks for creating custom fitness functions

PRIMITIVE METRICS (all return 0.0-1.0):
- note_variety(phrase)       : Pitch variety (higher = more unique pitches)
- rest_ratio(phrase)         : Ratio of rests (higher = more rests)
- interval_smoothness(phrase): Melodic smoothness (higher = smaller intervals)
- scale_adherence(phrase, scale): How well notes fit a scale
- rhythmic_variety(phrase)   : Duration variety (higher = more varied durations)

SCALES:
- MAJOR_SCALE  : C major scale notes
- MINOR_SCALE  : C natural minor scale notes
- PENTATONIC   : C pentatonic scale notes
- BLUES_SCALE  : C blues scale notes
"""

from abc import ABC, abstractmethod
from core.music import Layer, Phrase, Note, NoteName


class FitnessFunction(ABC):
    """Abstract base for fitness functions that evaluate Layer objects.

    To create a custom fitness function:
    1. Subclass FitnessFunction
    2. Implement evaluate() returning 0.0-1.0
    3. Use the primitive metrics below as building blocks

    Example:
        class MyFitness(FitnessFunction):
            def evaluate(self, layer: Layer) -> float:
                scores = []
                for phrase in layer.phrases:
                    score = (
                        0.5 * note_variety(phrase) +
                        0.3 * interval_smoothness(phrase) +
                        0.2 * (1 - rest_ratio(phrase))
                    )
                    scores.append(score)
                return sum(scores) / len(scores) if scores else 0.0
    """

    @abstractmethod
    def evaluate(self, layer: Layer) -> float:
        """Evaluate fitness of a layer. Returns 0.0 - 1.0."""
        pass

    def evaluate_phrase(self, phrase: Phrase) -> float:
        """Evaluate a single phrase. Override for phrase-level fitness."""
        return 0.5


# === Primitive Fitness Metrics ===
# Use these as building blocks for custom fitness functions


def note_variety(phrase: Phrase) -> float:
    """Measure pitch variety (0-1). Higher = more unique pitches.

    Counts unique pitches and normalizes to ~7 (one octave).
    Useful for: melodies that should use varied pitches vs. drones
    """
    if not phrase.notes:
        return 0.0
    pitches = {n.pitch for n in phrase.notes if n.pitch != NoteName.REST}
    return min(len(pitches) / 7.0, 1.0)


def rest_ratio(phrase: Phrase) -> float:
    """Ratio of rests to total notes (0-1). Higher = more rests.

    Useful for: sparse/ambient vs. dense/active patterns
    Use (1 - rest_ratio) if you want to penalize rests.
    """
    if not phrase.notes:
        return 0.0
    rests = sum(1 for n in phrase.notes if n.pitch == NoteName.REST)
    return rests / len(phrase.notes)


def interval_smoothness(phrase: Phrase) -> float:
    """Measure melodic smoothness (0-1). Higher = smaller intervals.

    Calculates average interval size and rewards stepwise motion.
    Large jumps (>12 semitones) result in low scores.

    Useful for: smooth/pad vs. jumpy/melodic lines
    Use (1 - interval_smoothness) if you want large intervals.
    """
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if len(notes) < 2:
        return 0.5

    total_interval = 0
    for i in range(len(notes) - 1):
        interval = abs(notes[i].midi_pitch - notes[i + 1].midi_pitch)
        total_interval += interval

    avg_interval = total_interval / (len(notes) - 1)
    return max(0, 1 - (avg_interval / 12))


def scale_adherence(phrase: Phrase, scale: list[NoteName]) -> float:
    """Measure how well notes fit a scale (0-1). Higher = more in-scale.

    Args:
        phrase: The phrase to evaluate
        scale: List of NoteName values that define the scale

    Useful for: enforcing tonality vs. chromatic freedom
    """
    notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
    if not notes:
        return 1.0

    in_scale = sum(1 for n in notes if n.pitch in scale)
    return in_scale / len(notes)


def rhythmic_variety(phrase: Phrase) -> float:
    """Measure duration variety (0-1). Higher = more varied durations.

    Counts unique durations and normalizes to 4 types.

    Useful for: rhythmically interesting vs. steady patterns
    """
    if not phrase.notes:
        return 0.0
    durations = {n.duration for n in phrase.notes}
    return min(len(durations) / 4.0, 1.0)


# === Common Scales ===
# Use with scale_adherence() to enforce tonality

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
