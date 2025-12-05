"""Fitness functions for drum patterns."""


def kick_pattern_fitness(rhythm: str) -> float:
    """Fitness for kick drum (bass drum) patterns.

    Characteristics:
    - Strong beats (1 and 5 in 8-beat pattern)
    - Simple, powerful
    - Not too busy
    - Provides foundation

    Example good patterns: "10001000", "12001200", "10101000"
    """
    if not rhythm:
        return 0.0

    # Check strong beat emphasis (beats 1, 5 should have notes)
    strong_beat_score = 0.0
    beat_count = len(rhythm)

    # For 8-beat patterns, emphasize beats 1 and 5 (indices 0 and 4)
    if beat_count >= 8:
        if rhythm[0] != '0':  # Beat 1
            strong_beat_score += 0.5
        if rhythm[4] != '0':  # Beat 5
            strong_beat_score += 0.5
    elif beat_count >= 4:
        if rhythm[0] != '0':  # Beat 1
            strong_beat_score += 0.5
        if beat_count > 2 and rhythm[2] != '0':  # Beat 3
            strong_beat_score += 0.5

    # Prefer sparse patterns (not too busy)
    density = sum(int(c) for c in rhythm) / (len(rhythm) * 4.0)
    sparsity_score = 1.0 - min(density * 2, 1.0)  # Penalize high density

    # Prefer simple patterns (mostly 1s, few subdivisions)
    simplicity_score = rhythm.count('1') / len(rhythm)

    # Rest ratio (should have some rests for power)
    rest_ratio = rhythm.count('0') / len(rhythm)
    rest_score = min(rest_ratio * 1.5, 1.0)

    return (
        0.40 * strong_beat_score +
        0.25 * sparsity_score +
        0.20 * simplicity_score +
        0.15 * rest_score
    )


def hihat_pattern_fitness(rhythm: str) -> float:
    """Fitness for hi-hat patterns.

    Characteristics:
    - Consistent, steady
    - High density (constant rhythm)
    - Mostly simple subdivisions (1s and 2s)
    - Few rests (keeps time)

    Example good patterns: "22222222", "12121212", "21212121"
    """
    if not rhythm:
        return 0.0

    # High density is good for hi-hats
    density = sum(int(c) for c in rhythm) / (len(rhythm) * 4.0)
    density_score = min(density * 1.5, 1.0)

    # Consistency (repetitive patterns)
    unique_ratio = len(set(rhythm)) / len(rhythm)
    consistency_score = 1.0 - unique_ratio

    # Prefer simple subdivisions (1s and 2s, not 3s and 4s)
    simple_count = rhythm.count('1') + rhythm.count('2')
    simplicity_score = simple_count / len(rhythm)

    # Few rests (hi-hat keeps time)
    rest_ratio = rhythm.count('0') / len(rhythm)
    no_rest_score = 1.0 - rest_ratio

    return (
        0.35 * density_score +
        0.30 * consistency_score +
        0.20 * simplicity_score +
        0.15 * no_rest_score
    )


def snare_pattern_fitness(rhythm: str) -> float:
    """Fitness for snare drum patterns.

    Characteristics:
    - Emphasis on backbeat (beats 2 and 4, or 3 and 7 in 8-beat)
    - Sparse (creates accents)
    - Simple hits (mostly 1s)
    - Strategic placement

    Example good patterns: "00100010", "00120012", "01001000"
    """
    if not rhythm:
        return 0.0

    # Backbeat emphasis (beats 3 and 7 in 8-beat, or 2 and 4 in 4-beat)
    backbeat_score = 0.0
    beat_count = len(rhythm)

    if beat_count >= 8:
        # For 8-beat: emphasize beats 3 and 7 (indices 2 and 6)
        if rhythm[2] != '0':
            backbeat_score += 0.5
        if rhythm[6] != '0':
            backbeat_score += 0.5
    elif beat_count >= 4:
        # For 4-beat: emphasize beats 2 and 4 (indices 1 and 3)
        if rhythm[1] != '0':
            backbeat_score += 0.5
        if beat_count > 3 and rhythm[3] != '0':
            backbeat_score += 0.5

    # Sparsity (snare is accent, not filler)
    rest_ratio = rhythm.count('0') / len(rhythm)
    sparsity_score = min(rest_ratio * 1.3, 1.0)

    # Simplicity (prefer single hits)
    simplicity_score = rhythm.count('1') / max(len(rhythm) - rhythm.count('0'), 1)

    # Not too dense
    density = sum(int(c) for c in rhythm) / (len(rhythm) * 4.0)
    low_density_score = 1.0 - density

    return (
        0.45 * backbeat_score +
        0.25 * sparsity_score +
        0.20 * simplicity_score +
        0.10 * low_density_score
    )


def percussion_pattern_fitness(rhythm: str) -> float:
    """Fitness for additional percussion (shakers, tambourine, etc.).

    Characteristics:
    - Moderate density
    - Adds texture
    - Complements other drums
    - Can be syncopated

    Example good patterns: "20202020", "12012012", "02020202"
    """
    if not rhythm:
        return 0.0

    # Moderate density (not too sparse, not too dense)
    density = sum(int(c) for c in rhythm) / (len(rhythm) * 4.0)
    density_score = 1.0 - abs(0.5 - density)

    # Some variety (not completely repetitive)
    unique_ratio = len(set(rhythm)) / len(rhythm)
    variety_score = unique_ratio

    # Balance of rests and notes
    rest_ratio = rhythm.count('0') / len(rhythm)
    balance_score = 1.0 - abs(0.4 - rest_ratio)

    # Prefer subdivisions (2s and 3s for texture)
    subdivision_count = rhythm.count('2') + rhythm.count('3')
    subdivision_score = min(subdivision_count / len(rhythm) * 2, 1.0)

    return (
        0.30 * density_score +
        0.25 * variety_score +
        0.25 * balance_score +
        0.20 * subdivision_score
    )


def rock_kick_fitness(rhythm: str) -> float:
    """Rock kick drum: Strong on 1 and 3, powerful and consistent."""
    from fitness.rhythm import rhythm_consistency, rhythm_density

    # Emphasize beats 1, 3, 5, 7 (downbeats)
    downbeat_score = 0
    for i in [0, 2, 4, 6]:
        if i < len(rhythm) and int(rhythm[i]) >= 1:
            downbeat_score += 1
    downbeat_score = downbeat_score / 4.0 if len(rhythm) >= 8 else downbeat_score / 2.0

    # Moderate density (not too sparse, not too busy)
    density = rhythm_density(rhythm)
    target_density = 0.2  # About 20% density
    density_score = 1.0 - abs(density - target_density) / max(target_density, 0.1)

    return (
        0.50 * downbeat_score +  # Strong downbeats
        0.30 * density_score +  # Moderate density
        0.20 * rhythm_consistency(rhythm)  # Consistent pattern
    )


def metal_kick_fitness(rhythm: str) -> float:
    """Metal kick drum: Fast double bass, high density, aggressive."""
    from fitness.rhythm import rhythm_density, rhythm_complexity

    # Count fast hits (3s and 4s = triplets and sixteenths)
    fast_hits = sum(1 for c in rhythm if int(c) >= 3)
    fast_score = min(fast_hits / len(rhythm), 1.0) if rhythm else 0.0

    # High density
    density = rhythm_density(rhythm)
    density_score = min(density / 0.4, 1.0)  # Target 40%+ density

    return (
        0.50 * fast_score +  # Fast double bass patterns
        0.35 * density_score +  # High density
        0.15 * rhythm_complexity(rhythm)  # Complex patterns
    )


def jazz_kick_fitness(rhythm: str) -> float:
    """Jazz kick drum: Syncopated, dynamic, conversational."""
    from fitness.rhythm import rhythm_syncopation, rhythm_complexity, rhythm_density

    # Jazz kick is all about syncopation and variety
    density = rhythm_density(rhythm)
    target_density = 0.15  # Sparse but present
    density_score = 1.0 - abs(density - target_density) / 0.3

    return (
        0.40 * rhythm_syncopation(rhythm) +  # Highly syncopated
        0.35 * rhythm_complexity(rhythm) +  # Varied patterns
        0.25 * density_score  # Moderate-low density
    )


def electronic_kick_fitness(rhythm: str) -> float:
    """Electronic kick drum: Four-on-the-floor or quantized patterns."""
    from fitness.rhythm import rhythm_consistency, rhythm_density

    # Check for four-on-the-floor pattern (every beat)
    all_beats = sum(1 for c in rhythm if int(c) >= 1)
    four_on_floor_score = all_beats / len(rhythm) if rhythm else 0.0

    # Very consistent
    consistency = rhythm_consistency(rhythm)

    return (
        0.50 * four_on_floor_score +  # Every beat or regular pattern
        0.35 * consistency +  # Very consistent
        0.15 * rhythm_density(rhythm)  # Moderate density
    )


# Genre-specific complete drum kits
DRUM_GENRE_FUNCTIONS = {
    "rock": {
        "kick": rock_kick_fitness,
        "hihat": hihat_pattern_fitness,
        "snare": snare_pattern_fitness,
    },
    "metal": {
        "kick": metal_kick_fitness,
        "hihat": hihat_pattern_fitness,  # Fast, steady
        "snare": snare_pattern_fitness,
    },
    "jazz": {
        "kick": jazz_kick_fitness,
        "hihat": percussion_pattern_fitness,  # Varied, textural
        "snare": percussion_pattern_fitness,  # Light, varied
    },
    "electronic": {
        "kick": electronic_kick_fitness,
        "hihat": hihat_pattern_fitness,
        "snare": snare_pattern_fitness,
    },
}

# Registry for drum-specific fitness functions
DRUM_FITNESS_FUNCTIONS = {
    "kick": kick_pattern_fitness,
    "hihat": hihat_pattern_fitness,
    "snare": snare_pattern_fitness,
    "percussion": percussion_pattern_fitness,
    # Genre-specific variants
    "rock_kick": rock_kick_fitness,
    "metal_kick": metal_kick_fitness,
    "jazz_kick": jazz_kick_fitness,
    "electronic_kick": electronic_kick_fitness,
}
