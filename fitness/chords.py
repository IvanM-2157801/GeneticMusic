"""Primitive fitness functions for chord progressions.

These functions evaluate ChordProgression objects.
Each returns 0.0-1.0 and can be combined with weights.

CHORD PRIMITIVES:
- chord_variety(progression)          : Variety of root notes
- chord_type_variety(progression)     : Variety of chord qualities
- root_motion_smoothness(progression) : Smooth root movement
- functional_harmony_score(progression): Use of I, IV, V chords
- resolution_bonus(progression)       : V-I and ii-V-I patterns

USAGE:
Combine these primitives for custom chord fitness:

    class MyChordFitness(ChordFitnessFunction):
        def evaluate(self, progression: ChordProgression) -> float:
            return (
                0.3 * functional_harmony_score(progression) +
                0.3 * root_motion_smoothness(progression) +
                0.2 * resolution_bonus(progression) +
                0.2 * chord_variety(progression)
            )
"""
from abc import ABC, abstractmethod
from core.genome_ops import ChordProgression


class ChordFitnessFunction(ABC):
    """Abstract base for chord/harmony fitness functions.

    To create a custom chord fitness:
    1. Subclass ChordFitnessFunction
    2. Implement evaluate() returning 0.0-1.0
    3. Use the primitive metrics below as building blocks
    """

    @abstractmethod
    def evaluate(self, progression: ChordProgression) -> float:
        """Evaluate fitness of a chord progression. Returns 0.0 - 1.0."""
        pass


# === Primitive Chord Metrics ===

def chord_variety(progression: ChordProgression) -> float:
    """Measure chord root variety (0-1). Higher = more variety.

    Counts unique root degrees and penalizes consecutive repetitions.

    High = varied progressions
    Low = repetitive/droning
    """
    if not progression.chords:
        return 0.0

    roots = [c.root_degree for c in progression.chords]
    unique_roots = set(roots)

    # Penalize consecutive repetitions
    repetitions = sum(1 for i in range(len(roots) - 1) if roots[i] == roots[i + 1])
    repetition_penalty = repetitions / max(len(roots) - 1, 1)

    variety_score = min(len(unique_roots) / min(len(roots), 4), 1.0)
    return 0.6 * variety_score + 0.4 * (1.0 - repetition_penalty)


def chord_type_variety(progression: ChordProgression) -> float:
    """Measure chord quality variety (0-1). Higher = more chord types.

    Counts unique interval patterns (major, minor, 7th, etc.)

    High = varied textures (jazz, complex)
    Low = uniform texture (pop, rock)
    """
    if not progression.chords:
        return 0.0
    types = {tuple(c.intervals) for c in progression.chords}
    return min(len(types) / 3.0, 1.0)


def root_motion_smoothness(progression: ChordProgression) -> float:
    """Measure smoothness of root motion (0-1). Higher = smoother.

    Rewards stepwise motion and 4ths/5ths, penalizes large jumps.

    High = classical voice leading
    Low = dramatic jumps
    """
    if len(progression.chords) < 2:
        return 0.5

    smooth_moves = 0
    for i in range(len(progression.chords) - 1):
        interval = abs(progression.chords[i].root_degree - progression.chords[i + 1].root_degree)
        if interval > 3:
            interval = 7 - interval  # Wrap around
        if interval <= 3 or interval == 4:  # Steps or 4ths/5ths
            smooth_moves += 1

    return smooth_moves / (len(progression.chords) - 1)


def functional_harmony_score(progression: ChordProgression) -> float:
    """Measure use of functional harmony (0-1). Higher = more tonal.

    Rewards I (0), IV (3), V (4) chords.
    Secondary credit for ii (1), vi (5).

    High = traditional tonal harmony
    Low = modal, chromatic
    """
    if not progression.chords:
        return 0.0

    strong_roots = {0, 3, 4}  # I, IV, V
    secondary_roots = {1, 5}  # ii, vi

    score = 0.0
    for chord in progression.chords:
        if chord.root_degree in strong_roots:
            score += 1.0
        elif chord.root_degree in secondary_roots:
            score += 0.7
        else:
            score += 0.4

    return score / len(progression.chords)


def resolution_bonus(progression: ChordProgression) -> float:
    """Measure resolution patterns (0-1). Higher = more resolution.

    Rewards: ending on I, V-I patterns, ii-V-I patterns.

    High = satisfying resolutions
    Low = unresolved tension
    """
    if not progression.chords:
        return 0.0

    score = 0.0

    # Bonus for ending on tonic
    if progression.chords[-1].root_degree == 0:
        score += 0.5

    # Bonus for V-I resolution
    for i in range(len(progression.chords) - 1):
        if (progression.chords[i].root_degree == 4 and
            progression.chords[i + 1].root_degree == 0):
            score += 0.25

    # Bonus for ii-V-I
    for i in range(len(progression.chords) - 2):
        if (progression.chords[i].root_degree == 1 and
            progression.chords[i + 1].root_degree == 4 and
            progression.chords[i + 2].root_degree == 0):
            score += 0.25

    return min(score, 1.0)


def triadic_bonus(progression: ChordProgression) -> float:
    """Measure use of simple triads (0-1). Higher = more triads.

    Rewards major and minor triads over complex voicings.

    High = pop, rock (simple chords)
    Low = jazz (extensions, altered)
    """
    if not progression.chords:
        return 0.0

    simple_types = {(0, 4, 7), (0, 3, 7)}  # major, minor triads
    simple_count = sum(1 for c in progression.chords if tuple(c.intervals) in simple_types)
    return simple_count / len(progression.chords)


def seventh_chord_bonus(progression: ChordProgression) -> float:
    """Measure use of 7th chords (0-1). Higher = more 7ths.

    Rewards chords with 4+ intervals (7th chords and extensions).

    High = jazz, R&B
    Low = simple pop, rock
    """
    if not progression.chords:
        return 0.0

    seventh_count = sum(1 for c in progression.chords if len(c.intervals) >= 4)
    return seventh_count / len(progression.chords)
