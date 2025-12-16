"""Primitive fitness functions for chord progressions.

These functions evaluate ChordProgression objects.
Each returns 0.0-1.0 and can be combined with weights.

CHORD PRIMITIVES:
- chord_variety(progression)              : Variety of root notes
- chord_type_variety(progression)         : Variety of chord qualities
- root_motion_smoothness(progression)     : Smooth root movement
- functional_harmony_score(progression)   : Use of I, IV, V chords
- resolution_bonus(progression)           : V-I and ii-V-I patterns
- triadic_bonus(progression)              : Use of simple triads
- seventh_chord_bonus(progression)        : Use of 7th chords
- diminished_chord_score(progression)     : Presence of diminished chords
- close_voicing_score(progression)        : Adjacent scale degrees in chords
- repetitive_pattern_score(progression)   : Repetitive patterns (A-B-A-B, etc.)
- chord_progression_similarity(progression): Similarity between consecutive chords

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
        interval = abs(
            progression.chords[i].root_degree - progression.chords[i + 1].root_degree
        )
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
        if (
            progression.chords[i].root_degree == 4
            and progression.chords[i + 1].root_degree == 0
        ):
            score += 0.25

    # Bonus for ii-V-I
    for i in range(len(progression.chords) - 2):
        if (
            progression.chords[i].root_degree == 1
            and progression.chords[i + 1].root_degree == 4
            and progression.chords[i + 2].root_degree == 0
        ):
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
    simple_count = sum(
        1 for c in progression.chords if tuple(c.intervals) in simple_types
    )
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


def diminished_chord_score(progression: ChordProgression) -> float:
    """Measure presence of diminished chords (0-1). Higher = more diminished.

    A diminished chord has equal intervals between notes (minor thirds = 3 semitones).
    Detects both diminished triads [0, 3, 6] and diminished 7ths [0, 3, 6, 9].

    Also detects any chord where consecutive intervals are 3 semitones apart
    (the characteristic "stacked minor thirds" of diminished harmony).

    High = dark, tense harmony
    Low = standard major/minor harmony
    """
    if not progression.chords:
        return 0.0

    diminished_count = 0
    for chord in progression.chords:
        if len(chord.intervals) < 2:
            continue

        is_diminished = True
        for i in range(len(chord.intervals) - 1):
            diff = chord.intervals[i + 1] - chord.intervals[i]
            if diff != 3:
                is_diminished = False
                break

        if is_diminished:
            diminished_count += 1

    return diminished_count / len(progression.chords)


def close_voicing_score(progression: ChordProgression) -> float:
    """Measure chords with adjacent scale degrees (0-1). Higher = more adjacent.

    Detects chords where the output scale degrees are adjacent (0&1, 1&2, etc.).
    This creates clustered/dissonant voicings when rendered to Strudel.

    The scale degree calculation is: (root_degree + interval//2) % 7
    So intervals like 3 (minor 3rd) produce adjacent degrees since 3//2 = 1.

    High = clustered, potentially dissonant voicings
    Low = spread, open voicings

    Use with NEGATIVE weight to penalize close voicings.
    """
    if not progression.chords:
        return 0.0

    close_count = 0
    for chord in progression.chords:
        if len(chord.intervals) < 2:
            continue

        # Calculate the actual scale degrees that will be output
        degrees = [
            (chord.root_degree + (interval // 2)) % 7 for interval in chord.intervals
        ]
        degrees_sorted = sorted(degrees)

        # Check for adjacent degrees
        has_adjacent = False
        for i in range(len(degrees_sorted) - 1):
            diff = degrees_sorted[i + 1] - degrees_sorted[i]
            if diff == 1 or diff == 6:  # Adjacent or wrapping (6&0)
                has_adjacent = True
                break

        if has_adjacent:
            close_count += 1

    return close_count / len(progression.chords)


def repetitive_pattern_score(progression: ChordProgression) -> float:
    """Measure repetitive patterns like A-B-A-B (0-1). Higher = more repetitive.

    Detects common repetitive patterns:
    - A-B-A-B (alternating)
    - A-A-B-B (paired)
    - A-B-C-A (looping)

    Use with NEGATIVE weight to encourage more varied progressions.

    High = repetitive, predictable
    Low = varied, interesting
    """
    if len(progression.chords) < 3:
        return 0.0

    # Create chord signatures (root + interval pattern)
    signatures = []
    for c in progression.chords:
        sig = (c.root_degree, tuple(c.intervals))
        signatures.append(sig)

    n = len(signatures)
    repetition_score = 0.0

    # Check for A-B-A-B pattern (alternating)
    if n >= 4:
        alternating_matches = 0
        for i in range(n - 2):
            if signatures[i] == signatures[i + 2]:
                alternating_matches += 1
        repetition_score += alternating_matches / (n - 2)

    # Check for A-A-B-B pattern (paired repetition)
    if n >= 2:
        paired_matches = 0
        for i in range(n - 1):
            if signatures[i] == signatures[i + 1]:
                paired_matches += 1
        repetition_score += paired_matches / (n - 1) * 0.5

    # Check for limited unique chords
    unique_chords = len(set(signatures))
    if unique_chords <= 2 and n >= 4:
        repetition_score += 0.5  # Penalty for using only 2 unique chords

    return min(repetition_score, 1.0)


def chord_progression_similarity(progression: ChordProgression) -> float:
    """Measure similarity between consecutive chords (0-1). Higher = more similar.

    Calculates the "distance" between adjacent chords based on:
    - Root degree difference (closer roots = more similar)
    - Interval pattern difference (same chord type = more similar)

    A score of 1.0 means all consecutive chords are identical.
    Lower scores indicate more varied/contrasting progressions.

    High = smooth, static progressions
    Low = dynamic, contrasting progressions
    """
    if len(progression.chords) < 2:
        return 1.0  # Single chord is maximally "similar" to itself

    total_similarity = 0.0
    num_pairs = len(progression.chords) - 1

    for i in range(num_pairs):
        chord1 = progression.chords[i]
        chord2 = progression.chords[i + 1]

        # Root similarity: distance of 0 = 1.0, distance of 3 (tritone) = 0.0
        root_diff = abs(chord1.root_degree - chord2.root_degree)
        if root_diff > 3:
            root_diff = 7 - root_diff  # Wrap around (e.g., 6 -> 1)
        root_similarity = 1.0 - (root_diff / 3.5)  # Normalize to 0-1

        # Interval similarity: same intervals = 1.0, different = based on overlap
        intervals1 = set(chord1.intervals)
        intervals2 = set(chord2.intervals)
        if intervals1 == intervals2:
            interval_similarity = 1.0
        else:
            # Calculate Jaccard similarity for intervals
            intersection = len(intervals1 & intervals2)
            union = len(intervals1 | intervals2)
            interval_similarity = intersection / union if union > 0 else 0.0

        # Combine root and interval similarity (weighted)
        pair_similarity = 0.5 * root_similarity + 0.5 * interval_similarity
        total_similarity += pair_similarity

    return total_similarity / num_pairs
