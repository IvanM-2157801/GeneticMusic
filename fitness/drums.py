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
        if rhythm[0] != "0":  # Beat 1
            strong_beat_score += 0.5
        if rhythm[4] != "0":  # Beat 5
            strong_beat_score += 0.5
    elif beat_count >= 4:
        if rhythm[0] != "0":  # Beat 1
            strong_beat_score += 0.5
        if beat_count > 2 and rhythm[2] != "0":  # Beat 3
            strong_beat_score += 0.5

    # Prefer sparse patterns (not too busy)
    density = sum(int(c) for c in rhythm) / (len(rhythm) * 4.0)
    sparsity_score = 1.0 - min(density * 2, 1.0)  # Penalize high density

    # Prefer simple patterns (mostly 1s, few subdivisions)
    simplicity_score = rhythm.count("1") / len(rhythm)

    # Rest ratio (should have some rests for power)
    rest_ratio = rhythm.count("0") / len(rhythm)
    rest_score = min(rest_ratio * 1.5, 1.0)

    return (
        0.40 * strong_beat_score
        + 0.25 * sparsity_score
        + 0.20 * simplicity_score
        + 0.15 * rest_score
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
    simple_count = rhythm.count("1") + rhythm.count("2")
    simplicity_score = simple_count / len(rhythm)

    # Few rests (hi-hat keeps time)
    rest_ratio = rhythm.count("0") / len(rhythm)
    no_rest_score = 1.0 - rest_ratio

    return (
        0.35 * density_score
        + 0.30 * consistency_score
        + 0.20 * simplicity_score
        + 0.15 * no_rest_score
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
        if rhythm[2] != "0":
            backbeat_score += 0.5
        if rhythm[6] != "0":
            backbeat_score += 0.5
    elif beat_count >= 4:
        # For 4-beat: emphasize beats 2 and 4 (indices 1 and 3)
        if rhythm[1] != "0":
            backbeat_score += 0.5
        if beat_count > 3 and rhythm[3] != "0":
            backbeat_score += 0.5

    # Sparsity (snare is accent, not filler)
    rest_ratio = rhythm.count("0") / len(rhythm)
    sparsity_score = min(rest_ratio * 1.3, 1.0)

    # Simplicity (prefer single hits)
    simplicity_score = rhythm.count("1") / max(len(rhythm) - rhythm.count("0"), 1)

    # Not too dense
    density = sum(int(c) for c in rhythm) / (len(rhythm) * 4.0)
    low_density_score = 1.0 - density

    return (
        0.45 * backbeat_score
        + 0.25 * sparsity_score
        + 0.20 * simplicity_score
        + 0.10 * low_density_score
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
    rest_ratio = rhythm.count("0") / len(rhythm)
    balance_score = 1.0 - abs(0.4 - rest_ratio)

    # Prefer subdivisions (2s and 3s for texture)
    subdivision_count = rhythm.count("2") + rhythm.count("3")
    subdivision_score = min(subdivision_count / len(rhythm) * 2, 1.0)

    return (
        0.30 * density_score
        + 0.25 * variety_score
        + 0.25 * balance_score
        + 0.20 * subdivision_score
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
        0.50 * downbeat_score  # Strong downbeats
        + 0.30 * density_score  # Moderate density
        + 0.20 * rhythm_consistency(rhythm)  # Consistent pattern
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
        0.50 * fast_score  # Fast double bass patterns
        + 0.35 * density_score  # High density
        + 0.15 * rhythm_complexity(rhythm)  # Complex patterns
    )


def jazz_kick_fitness(rhythm: str) -> float:
    """Jazz kick drum: Syncopated, dynamic, conversational."""
    from fitness.rhythm import rhythm_syncopation, rhythm_complexity, rhythm_density

    # Jazz kick is all about syncopation and variety
    density = rhythm_density(rhythm)
    target_density = 0.15  # Sparse but present
    density_score = 1.0 - abs(density - target_density) / 0.3

    return (
        0.40 * rhythm_syncopation(rhythm)  # Highly syncopated
        + 0.35 * rhythm_complexity(rhythm)  # Varied patterns
        + 0.25 * density_score  # Moderate-low density
    )


def electronic_kick_fitness(rhythm: str) -> float:
    """Electronic kick drum: Four-on-the-floor - kick on EVERY beat.

    The classic EDM kick pattern is "1111" or "11111111" - a kick on every
    single beat. This creates the driving, relentless feel of electronic music.

    Example ideal patterns: "1111", "11111111", "10101010" (half-time)
    """
    if not rhythm:
        return 0.0

    # Four-on-the-floor: EVERY beat should have a kick (value >= 1)
    kicks_on_beat = sum(1 for c in rhythm if c != '0')
    total_beats = len(rhythm)

    # Perfect score if every beat has a kick
    four_on_floor_score = kicks_on_beat / total_beats

    # Strong preference for simple single hits (1s) - not subdivisions
    # We want "1111" not "2222" or "4444"
    ones_count = rhythm.count('1')
    simplicity_score = ones_count / max(kicks_on_beat, 1) if kicks_on_beat > 0 else 0

    # Penalize rests - electronic kick should be relentless
    no_rest_score = 1.0 - (rhythm.count('0') / total_beats)

    # Very consistent pattern
    from fitness.rhythm import rhythm_consistency
    consistency = rhythm_consistency(rhythm)

    return (
        0.45 * four_on_floor_score +  # Kick on every beat
        0.25 * simplicity_score +  # Simple 1s, not subdivisions
        0.20 * no_rest_score +  # No rests
        0.10 * consistency  # Consistent pattern
    )


def electronic_hihat_fitness(rhythm: str) -> float:
    """Electronic hi-hat: Offbeat pattern or steady 8ths/16ths.

    Classic electronic hi-hat patterns:
    - Offbeat: "02020202" (hat on the "and" of each beat)
    - Steady 8ths: "22222222"
    - Steady 16ths: "44444444"

    Example ideal patterns: "02020202", "22222222", "21212121"
    """
    if not rhythm:
        return 0.0

    total_beats = len(rhythm)

    # Check for offbeat pattern (notes on even indices, rests on odd)
    offbeat_score = 0
    for i, c in enumerate(rhythm):
        if i % 2 == 1 and c != '0':  # Offbeat positions should have notes
            offbeat_score += 1
        elif i % 2 == 0 and c == '0':  # On-beat positions can be rest (pure offbeat)
            offbeat_score += 0.5

    offbeat_ratio = offbeat_score / total_beats

    # High density is good for hi-hats
    from fitness.rhythm import rhythm_density, rhythm_consistency
    density = rhythm_density(rhythm)
    density_score = min(density * 1.5, 1.0)

    # Consistency (repetitive patterns)
    consistency = rhythm_consistency(rhythm)

    # Prefer even subdivisions (2s and 4s)
    even_count = rhythm.count('2') + rhythm.count('4')
    even_score = even_count / total_beats

    return (
        0.30 * offbeat_ratio +  # Offbeat emphasis
        0.25 * density_score +  # High density
        0.25 * consistency +  # Consistent pattern
        0.20 * even_score  # Even subdivisions
    )


def electronic_clap_fitness(rhythm: str) -> float:
    """Electronic clap/snare: On beats 2 and 4 (backbeat).

    Classic EDM clap pattern is "0101" or "01010101" - clap on beats 2 and 4.

    Example ideal patterns: "0101", "01010101", "00100010"
    """
    if not rhythm:
        return 0.0

    total_beats = len(rhythm)

    # Backbeat: notes should be on beats 2, 4, 6, 8... (indices 1, 3, 5, 7...)
    backbeat_score = 0
    backbeat_positions = 0

    for i in range(total_beats):
        if i % 2 == 1:  # Backbeat position (2, 4, 6, 8...)
            backbeat_positions += 1
            if rhythm[i] != '0':
                backbeat_score += 1
        else:  # On-beat position (1, 3, 5, 7...)
            # Reward rests on downbeats for clean backbeat
            if rhythm[i] == '0':
                backbeat_score += 0.3

    backbeat_ratio = backbeat_score / max(backbeat_positions + total_beats / 2, 1)

    # Sparse - clap is accent, not filler
    rest_ratio = rhythm.count('0') / total_beats
    sparsity_score = min(rest_ratio * 1.5, 1.0)

    # Simple single hits (1s)
    ones_count = rhythm.count('1')
    non_rest = total_beats - rhythm.count('0')
    simplicity_score = ones_count / max(non_rest, 1) if non_rest > 0 else 0

    return (
        0.50 * backbeat_ratio +  # Strong backbeat
        0.30 * sparsity_score +  # Sparse
        0.20 * simplicity_score  # Simple hits
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
        "hihat": electronic_hihat_fitness,
        "snare": electronic_clap_fitness,
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
    "electronic_hihat": electronic_hihat_fitness,
    "electronic_clap": electronic_clap_fitness,
}
