"""Fitness functions for rhythm patterns (string genomes).

Rhythm strings encode subdivisions per beat:
- '0' = rest (no notes)
- '1' = quarter note (1 note per beat)
- '2' = eighth notes (2 notes per beat)
- '3' = triplets (3 notes per beat)
- '4' = sixteenth notes (4 notes per beat)

Example: "21312240" = 8 beats with mixed subdivisions
"""


def rhythm_complexity(rhythm: str) -> float:
    """Measure rhythmic complexity (variety of subdivisions).

    Returns 0.0-1.0 where higher = more variety.
    """
    if not rhythm:
        return 0.0
    unique_subdivisions = len(set(rhythm))
    return min(unique_subdivisions / 5.0, 1.0)  # Max 5 different subdivision types


def rhythm_rest_ratio(rhythm: str) -> float:
    """Ratio of rests in the rhythm.

    Returns 0.0-1.0 where 1.0 = all rests.
    """
    if not rhythm:
        return 0.0
    rests = rhythm.count('0')
    return rests / len(rhythm)


def rhythm_density(rhythm: str) -> float:
    """Average notes per beat (higher = denser).

    Returns 0.0-1.0 normalized to max 4 notes per beat.
    """
    if not rhythm:
        return 0.0
    total_notes = sum(int(char) for char in rhythm)
    return min(total_notes / (len(rhythm) * 4.0), 1.0)  # Normalize to max 4 notes per beat


def rhythm_syncopation(rhythm: str) -> float:
    """Reward patterns with varied subdivision (syncopated feel).

    Measures how often the subdivision changes between beats.
    Returns 0.0-1.0 where higher = more syncopated.
    """
    if len(rhythm) < 2:
        return 0.0

    # Count transitions between different subdivision levels
    transitions = 0
    for i in range(len(rhythm) - 1):
        if rhythm[i] != rhythm[i + 1]:
            transitions += 1

    return min(transitions / (len(rhythm) - 1), 1.0)


def rhythm_groove(rhythm: str) -> float:
    """Reward groovy patterns (alternating dense and sparse beats).

    Looks for patterns with strong/weak beat alternation.
    Returns 0.0-1.0 where higher = more groove.
    """
    if len(rhythm) < 4:
        return 0.0

    # Look for patterns like high-low-high-low
    groove_score = 0
    for i in range(len(rhythm) - 1):
        curr = int(rhythm[i])
        next_val = int(rhythm[i + 1])
        # Reward alternation between active and less active beats
        if (curr >= 2 and next_val <= 1) or (curr <= 1 and next_val >= 2):
            groove_score += 1

    return groove_score / (len(rhythm) - 1) if len(rhythm) > 1 else 0.0


def rhythm_consistency(rhythm: str) -> float:
    """Reward consistent/repetitive patterns.

    Returns 0.0-1.0 where higher = more consistent.
    """
    if len(rhythm) < 2:
        return 0.5

    # Check for repeating patterns
    unique_ratio = len(set(rhythm)) / len(rhythm)
    return 1.0 - unique_ratio


def rhythm_offbeat_emphasis(rhythm: str) -> float:
    """Reward emphasis on offbeats (even indices in 4/4).

    Returns 0.0-1.0 where higher = more offbeat emphasis.
    """
    if len(rhythm) < 4:
        return 0.0

    # In 4/4, offbeats are typically beats 2 and 4 (indices 1 and 3)
    offbeat_score = 0
    total_offbeats = 0

    for i in range(len(rhythm)):
        if i % 4 in [1, 3]:  # Offbeats in 4/4
            total_offbeats += 1
            if int(rhythm[i]) >= 2:  # Strong beat
                offbeat_score += 1

    return offbeat_score / total_offbeats if total_offbeats > 0 else 0.0


# Genre-specific rhythm fitness functions

def pop_rhythm_fitness(rhythm: str) -> float:
    """Fitness for pop rhythms: consistent, catchy, moderate density.

    Characteristics:
    - Consistent patterns (high repetition)
    - Moderate density (not too busy)
    - Strong groove (danceable)
    - Few rests (keep energy up)

    Example good patterns: "22222222", "21212121", "22112211"
    """
    return (
        0.25 * rhythm_consistency(rhythm) +  # Repetitive/catchy
        0.25 * rhythm_groove(rhythm) +  # Strong groove
        0.25 * (1 - rhythm_rest_ratio(rhythm)) +  # Few rests
        0.15 * rhythm_density(rhythm) +  # Moderate density
        0.10 * (1 - rhythm_complexity(rhythm))  # Not too complex
    )


def jazz_rhythm_fitness(rhythm: str) -> float:
    """Fitness for jazz rhythms: complex, syncopated, varied.

    Characteristics:
    - High complexity (varied subdivisions)
    - Syncopated (offbeat emphasis)
    - Some space (strategic rests)
    - Not too dense (room to breathe)

    Example good patterns: "31402310", "24130421", "32142013"
    """
    return (
        0.35 * rhythm_syncopation(rhythm) +  # Very syncopated
        0.25 * rhythm_complexity(rhythm) +  # Complex patterns
        0.20 * rhythm_offbeat_emphasis(rhythm) +  # Offbeat accents
        0.10 * (0.5 - abs(0.3 - rhythm_rest_ratio(rhythm))) +  # ~30% rests
        0.10 * (1 - rhythm_consistency(rhythm))  # Avoid repetition
    )


def funk_rhythm_fitness(rhythm: str) -> float:
    """Fitness for funk rhythms: highly syncopated, groovy, tight.

    Characteristics:
    - Maximum groove (strong/weak alternation)
    - Very syncopated (unexpected accents)
    - Dense but articulated
    - Offbeat emphasis

    Example good patterns: "42142114", "32143214", "24243214"
    """
    return (
        0.40 * rhythm_groove(rhythm) +  # Maximum groove
        0.30 * rhythm_syncopation(rhythm) +  # Highly syncopated
        0.15 * rhythm_offbeat_emphasis(rhythm) +  # Offbeat accents
        0.10 * rhythm_density(rhythm) +  # Fairly dense
        0.05 * (1 - rhythm_rest_ratio(rhythm))  # Few rests
    )


def ambient_rhythm_fitness(rhythm: str) -> float:
    """Fitness for ambient rhythms: simple, sparse, meditative.

    Characteristics:
    - Very sparse (many rests)
    - Simple patterns (low complexity)
    - Consistent (meditative repetition)
    - Low density (spacious)

    Example good patterns: "10001000", "00100010", "01000100"
    """
    return (
        0.35 * rhythm_rest_ratio(rhythm) +  # Many rests
        0.25 * (1 - rhythm_density(rhythm)) +  # Very sparse
        0.20 * (1 - rhythm_complexity(rhythm)) +  # Simple
        0.15 * rhythm_consistency(rhythm) +  # Repetitive
        0.05 * (1 - rhythm_syncopation(rhythm))  # Steady/consistent
    )


def rock_rhythm_fitness(rhythm: str) -> float:
    """Fitness for rock rhythms: driving, consistent, powerful.

    Characteristics:
    - High density (energetic)
    - Consistent groove (driving feel)
    - Few rests (sustained energy)
    - Moderate complexity (not too busy)

    Example good patterns: "22222222", "24242424", "22242224"
    """
    return (
        0.30 * rhythm_density(rhythm) +  # Dense/energetic
        0.25 * rhythm_groove(rhythm) +  # Strong groove
        0.20 * (1 - rhythm_rest_ratio(rhythm)) +  # Few rests
        0.15 * rhythm_consistency(rhythm) +  # Consistent patterns
        0.10 * (0.5 - abs(0.3 - rhythm_complexity(rhythm)))  # Moderate complexity
    )


# Registry for easy access
RHYTHM_FITNESS_FUNCTIONS = {
    "pop": pop_rhythm_fitness,
    "jazz": jazz_rhythm_fitness,
    "funk": funk_rhythm_fitness,
    "ambient": ambient_rhythm_fitness,
    "rock": rock_rhythm_fitness,
}
