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
    rests = rhythm.count("0")
    return rests / len(rhythm)


def rhythm_density(rhythm: str) -> float:
    """Average notes per beat (higher = denser).

    Returns 0.0-1.0 normalized to max 4 notes per beat.
    """
    if not rhythm:
        return 0.0
    total_notes = sum(int(char) for char in rhythm)
    return min(
        total_notes / (len(rhythm) * 4.0), 1.0
    )  # Normalize to max 4 notes per beat


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
    # Target density around 0.5 (moderate)
    density_score = 1.0 - abs(0.5 - rhythm_density(rhythm))

    return (
        0.35 * rhythm_consistency(rhythm)  # Very repetitive/catchy
        + 0.25 * rhythm_groove(rhythm)  # Strong groove
        + 0.20 * (1 - rhythm_rest_ratio(rhythm))  # Few rests
        + 0.15 * density_score  # Moderate density (not too dense)
        + 0.05 * (1 - rhythm_complexity(rhythm))  # Simple patterns
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
    # Target moderate rest ratio (10-30%)
    rest_score = 1.0 - abs(0.2 - rhythm_rest_ratio(rhythm)) / 0.2

    return (
        0.30 * rhythm_syncopation(rhythm)  # Syncopated
        + 0.25 * rhythm_complexity(rhythm)  # Complex patterns
        + 0.20 * rhythm_offbeat_emphasis(rhythm)  # Offbeat accents
        + 0.15 * rest_score  # Some rests but not too many
        + 0.10 * (1 - rhythm_consistency(rhythm))  # Varied, not repetitive
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
    # Target moderate to high density (0.6-0.8)
    density_score = 1.0 - abs(0.7 - rhythm_density(rhythm))

    return (
        0.40 * rhythm_groove(rhythm)  # Maximum groove
        + 0.25 * rhythm_syncopation(rhythm)  # Highly syncopated
        + 0.20 * rhythm_offbeat_emphasis(rhythm)  # Offbeat accents
        + 0.10 * density_score  # Moderate to high density
        + 0.05 * (1 - rhythm_rest_ratio(rhythm))  # Few rests
    )


def ambient_rhythm_fitness(rhythm: str) -> float:
    """Fitness for ambient rhythms: flowing, meditative, but not silent.

    Characteristics:
    - Moderate density (enough notes to create atmosphere)
    - Simple, mostly single hits with occasional gentle subdivisions
    - Consistent, flowing patterns
    - Some space but not excessive silence

    Example good patterns: "10101010", "11001100", "10110101", "11101110"
    """
    if not rhythm:
        return 0.0

    # Count note beats (non-rest) and rest beats
    note_beats = sum(1 for c in rhythm if c != '0')
    rest_beats = rhythm.count('0')
    total_beats = len(rhythm)

    # Must have notes - ambient should be atmospheric, not silent
    if note_beats == 0:
        return 0.0

    # Target: 40-70% of beats have notes (flowing, not sparse)
    # This creates a continuous atmospheric texture
    note_ratio = note_beats / total_beats
    if note_ratio < 0.3:
        density_score = 0.4  # Too sparse - no atmosphere
    elif 0.4 <= note_ratio <= 0.7:
        density_score = 1.0  # Perfect flowing density
    elif note_ratio <= 0.85:
        density_score = 0.8  # Still good
    else:
        density_score = 0.6  # A bit too dense but ok

    # Prefer simple single hits (1s) but allow some gentle subdivisions (2s)
    ones_count = rhythm.count('1')
    twos_count = rhythm.count('2')
    heavy_subdivision = sum(1 for c in rhythm if c in '34')

    # Ones and twos are good for ambient, 3s and 4s are too busy
    simple_notes = ones_count + twos_count * 0.8
    simplicity_score = simple_notes / max(note_beats, 1) if note_beats > 0 else 0

    # Penalize heavy subdivisions (triplets, 16ths)
    if heavy_subdivision > 0:
        simplicity_score *= max(0.3, 1.0 - heavy_subdivision * 0.2)

    # Reward consistent patterns (ambient is meditative)
    consistency = rhythm_consistency(rhythm)

    # Some rests are good but not too many
    rest_ratio = rest_beats / total_beats if total_beats > 0 else 0
    # Ideal: 30-60% rests
    if 0.3 <= rest_ratio <= 0.6:
        rest_score = 1.0
    elif rest_ratio < 0.3:
        rest_score = 0.7  # Too dense
    else:
        rest_score = max(0.3, 1.0 - (rest_ratio - 0.6) * 2)  # Too sparse

    return (
        0.35 * density_score  # Flowing density
        + 0.30 * simplicity_score  # Simple patterns
        + 0.20 * rest_score  # Balanced rests
        + 0.15 * consistency  # Meditative repetition
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
    # Target high density (0.6-0.8)
    density_score = 1.0 - abs(0.7 - rhythm_density(rhythm))

    return (
        0.30 * density_score  # High but not extreme density
        + 0.25 * rhythm_groove(rhythm)  # Strong groove
        + 0.20 * (1 - rhythm_rest_ratio(rhythm))  # Few rests
        + 0.15 * rhythm_consistency(rhythm)  # Consistent patterns
        + 0.10 * (1 - rhythm_complexity(rhythm))  # Not too complex
    )


def drum_rhythm_fitness(rhythm: str) -> float:
    """Fitness for drum rhythms: steady, driving, simple.

    Characteristics:
    - Very consistent (steady beat)
    - High density (constant rhythm)
    - Simple patterns (not complex)
    - Strong groove (danceable)
    - Minimal rests (keep the beat)

    Example good patterns: "22222222", "44444444", "24242424"
    """
    # Target high density (0.7-0.9) for drums
    density_score = 1.0 - abs(0.8 - rhythm_density(rhythm))

    return (
        0.35 * rhythm_consistency(rhythm)  # Very consistent beat
        + 0.30 * density_score  # High density
        + 0.20 * (1 - rhythm_rest_ratio(rhythm))  # Minimal rests
        + 0.10 * rhythm_groove(rhythm)  # Groove
        + 0.05 * (1 - rhythm_complexity(rhythm))  # Simple patterns
    )


def bass_rhythm_fitness(rhythm: str) -> float:
    """Fitness for bass rhythms: solid, groovy, supportive.

    Characteristics:
    - Simple, repetitive patterns
    - Moderate density (not too busy)
    - Strong groove (locks with drums)
    - Few rests (solid foundation)

    Example good patterns: "21212121", "11112222", "22112211"
    """
    # Target moderate density (0.4-0.6)
    density_score = 1.0 - abs(0.5 - rhythm_density(rhythm))

    return (
        0.35 * rhythm_consistency(rhythm)  # Very repetitive
        + 0.25 * rhythm_groove(rhythm)  # Strong groove
        + 0.20 * density_score  # Moderate density
        + 0.15 * (1 - rhythm_rest_ratio(rhythm))  # Few rests
        + 0.05 * (1 - rhythm_complexity(rhythm))  # Simple patterns
    )


def electronic_rhythm_fitness(rhythm: str) -> float:
    """Fitness for electronic/EDM rhythms: repetitive, quantized, hypnotic.

    Characteristics:
    - Highly repetitive (hypnotic)
    - Quantized feel (even subdivisions)
    - Moderate to high density
    - Very consistent patterns
    - Minimal variation (trance-like)

    Example good patterns: "22222222", "24242424", "44444444", "21212121"
    """
    if not rhythm:
        return 0.0

    # Electronic music loves consistency - same pattern throughout
    consistency = rhythm_consistency(rhythm)

    # Prefer even subdivisions (2s and 4s) over odd (3s)
    even_count = rhythm.count('2') + rhythm.count('4')
    odd_count = rhythm.count('3')
    total_notes = len(rhythm) - rhythm.count('0')
    even_score = even_count / max(total_notes, 1) if total_notes > 0 else 0

    # Moderate to high density (not sparse like ambient)
    density = rhythm_density(rhythm)
    # Target 50-80% density
    if 0.5 <= density <= 0.8:
        density_score = 1.0
    elif density < 0.5:
        density_score = density / 0.5
    else:
        density_score = 1.0 - (density - 0.8) * 2

    # Few rests (keep the energy up)
    rest_ratio = rhythm_rest_ratio(rhythm)
    no_rest_score = 1.0 - rest_ratio

    return (
        0.40 * consistency  # Highly repetitive
        + 0.25 * even_score  # Even subdivisions
        + 0.20 * density_score  # Good density
        + 0.15 * no_rest_score  # Few rests
    )


def electronic_arp_fitness(rhythm: str) -> float:
    """Fitness for electronic arpeggios: fast, consistent, 16th-note patterns.

    Characteristics:
    - High density (continuous notes)
    - Very consistent (same subdivision throughout)
    - Prefer 4s (16th notes) or 2s (8th notes)
    - Minimal rests

    Example good patterns: "44444444", "42424242", "44224422"
    """
    if not rhythm:
        return 0.0

    # Arpeggios need high density
    density = rhythm_density(rhythm)
    # Target 70-100% density
    density_score = min(density / 0.7, 1.0)

    # Strong preference for 4s (16th notes) for arpeggios
    fours_count = rhythm.count('4')
    twos_count = rhythm.count('2')
    fast_score = (fours_count * 1.0 + twos_count * 0.5) / len(rhythm)

    # Ultra-consistent (same pattern)
    consistency = rhythm_consistency(rhythm)

    # No rests in arpeggios
    no_rest_score = 1.0 - rhythm_rest_ratio(rhythm)

    return (
        0.35 * fast_score  # Fast subdivisions
        + 0.30 * density_score  # High density
        + 0.20 * consistency  # Very consistent
        + 0.15 * no_rest_score  # No rests
    )


# Registry for easy access
RHYTHM_FITNESS_FUNCTIONS = {
    "pop": pop_rhythm_fitness,
    "jazz": jazz_rhythm_fitness,
    "funk": funk_rhythm_fitness,
    "drum": drum_rhythm_fitness,
    "bass": bass_rhythm_fitness,
    "ambient": ambient_rhythm_fitness,
    "rock": rock_rhythm_fitness,
    "electronic": electronic_rhythm_fitness,
    "electronic_arp": electronic_arp_fitness,
}
