"""Primitive fitness functions for rhythm patterns (string genomes).

RHYTHM STRING FORMAT:
Each character represents subdivisions per beat:
- '0' = rest (no notes)
- '1' = quarter note (1 note per beat)
- '2' = eighth notes (2 notes per beat)
- '3' = triplets (3 notes per beat)
- '4' = sixteenth notes (4 notes per beat)

Example: "21312240" = 8 beats with mixed subdivisions

PRIMITIVE METRICS (all return 0.0-1.0):
- rhythm_complexity(rhythm)     : Variety of subdivisions (higher = more types)
- rhythm_rest_ratio(rhythm)     : Ratio of rests (higher = more rests)
- rhythm_density(rhythm)        : Notes per beat (higher = denser)
- rhythm_syncopation(rhythm)    : Subdivision changes (higher = more syncopated)
- rhythm_groove(rhythm)         : Strong/weak alternation (higher = more groove)
- rhythm_consistency(rhythm)    : Pattern repetition (higher = more repetitive)
- rhythm_offbeat_emphasis(rhythm): Offbeat activity (higher = more offbeat)

USAGE:
Combine these primitives with weights to create custom rhythm fitness:

    def my_rhythm_fitness(rhythm: str) -> float:
        return (
            0.4 * rhythm_groove(rhythm) +
            0.3 * rhythm_consistency(rhythm) +
            0.2 * (1 - rhythm_rest_ratio(rhythm)) +
            0.1 * rhythm_density(rhythm)
        )
"""

import itertools


def rhythm_complexity(rhythm: str) -> float:
    """Measure rhythmic complexity (0-1). Higher = more subdivision types.

    Counts unique subdivision values (0-4) and normalizes to 5.

    High complexity = jazz, progressive
    Low complexity = steady beats, ambient
    """
    if not rhythm:
        return 0.0
    unique_subdivisions = len(set(rhythm)) - 1
    return min(unique_subdivisions / 3.0, 1.0)


def rhythm_rest_ratio(rhythm: str) -> float:
    """Ratio of rests in rhythm (0-1). Higher = more rests.

    Use (1 - rhythm_rest_ratio) to penalize rests.

    High rest ratio = sparse, ambient
    Low rest ratio = dense, driving
    """
    if not rhythm:
        return 0.0
    rests = rhythm.count("0")
    return rests / len(rhythm)


def rhythm_density(rhythm: str) -> float:
    """Average notes per beat (0-1). Higher = denser.

    Normalized to max 4 notes per beat.

    High density = fast, busy, arpeggiated
    Low density = sparse, open, spacious
    """
    if not rhythm:
        return 0.0
    total_notes = sum(int(char) for char in rhythm)
    return min(total_notes / (len(rhythm) * 4.0), 1.0)


def rhythm_syncopation(rhythm: str) -> float:
    """Measure syncopation (0-1). Higher = more syncopated.

    Counts transitions between different subdivision levels.

    High syncopation = jazz, funk, complex
    Low syncopation = steady, predictable
    """
    if len(rhythm) < 2:
        return 0.0

    transitions = 0
    for i in range(len(rhythm) - 1):
        if rhythm[i] != rhythm[i + 1]:
            transitions += 1

    return min(transitions / (len(rhythm) - 1), 1.0)


def rhythm_groove(rhythm: str) -> float:
    """Measure groove (0-1). Higher = more strong/weak alternation.

    Looks for patterns with alternating dense and sparse beats.

    High groove = danceable, funk, rock
    Low groove = ambient, static
    """
    if len(rhythm) < 4:
        return 0.0

    groove_score = 0
    for i in range(len(rhythm) - 1):
        curr = int(rhythm[i])
        next_val = int(rhythm[i + 1])
        if (curr >= 2 and next_val <= 1) or (curr <= 1 and next_val >= 2):
            groove_score += 1

    return groove_score / (len(rhythm) - 1) if len(rhythm) > 1 else 0.0


from collections import Counter


def rhythm_consistency(rhythm: str) -> float:
    """Score based on actual pattern repetition (0-1)."""
    if len(rhythm) < 4:
        return 0.5

    repeat_score = 0
    max_possible = 0

    for length in range(2, min(len(rhythm) // 2 + 1, 9)):
        patterns = [rhythm[i : i + length] for i in range(len(rhythm) - length + 1)]
        counts = Counter(patterns)
        repeats = sum(c - 1 for c in counts.values())
        repeat_score += repeats * length
        max_possible += (len(patterns) - 1) * length

    return repeat_score / max_possible if max_possible else 0.5


def rhythm_offbeat_emphasis(rhythm: str) -> float:
    """Measure offbeat emphasis (0-1). Higher = more offbeat activity.

    In 4/4, offbeats are beats 2 and 4 (indices 1 and 3 in each group of 4).

    High offbeat = syncopated, funky
    Low offbeat = downbeat-heavy, march-like
    """
    if len(rhythm) < 4:
        return 0.0

    offbeat_score = 0
    total_offbeats = 0

    for i in range(len(rhythm)):
        if i % 4 in [1, 3]:  # Offbeats in 4/4
            total_offbeats += 1
            if int(rhythm[i]) >= 2:  # Strong beat
                offbeat_score += 1

    return offbeat_score / total_offbeats if total_offbeats > 0 else 0.0
