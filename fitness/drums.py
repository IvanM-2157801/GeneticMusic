"""Primitive fitness functions for drum patterns.

These functions evaluate rhythm strings for different drum roles.
Each returns 0.0-1.0 and can be combined with weights.

DRUM ROLE PRIMITIVES (Basic):
- strong_beat_emphasis(rhythm)  : Activity on beats 1/5 (higher = more downbeat)
- backbeat_emphasis(rhythm)     : Activity on beats 3/7 (higher = more backbeat)
- sparsity(rhythm)              : Inverse of density (higher = more sparse)
- simplicity(rhythm)            : Ratio of simple hits (higher = more single hits)
- offbeat_pattern(rhythm)       : Activity on offbeats (higher = more offbeat)

DRUM ROLE PRIMITIVES (Advanced):
- total_hits(rhythm)            : Count of total note subdivisions
- hit_count_score(rhythm, min, max) : Score for hit count in target range
- hits_at_positions(rhythm, positions) : Score for hits at specific beat positions
- avoid_positions(rhythm, positions)   : Score for NOT having hits at positions
- single_hits_at_positions(rhythm, positions) : Score for "1" at positions
- perfect_consistency(rhythm)   : Score for all beats being same subdivision
- uniform_subdivision(rhythm, target) : Score for matching target pattern

USAGE:
Combine these primitives for different drum sounds:

    # Kick drum: strong beats, sparse, simple
    def kick_fitness(rhythm: str) -> float:
        return (
            0.4 * strong_beat_emphasis(rhythm) +
            0.3 * sparsity(rhythm) +
            0.3 * simplicity(rhythm)
        )

    # Hi-hat: high density, consistent
    def hihat_fitness(rhythm: str) -> float:
        from fitness.rhythm import rhythm_density, rhythm_consistency
        return (
            0.4 * rhythm_density(rhythm) +
            0.4 * rhythm_consistency(rhythm) +
            0.2 * (1 - rhythm_rest_ratio(rhythm))
        )

    # Snare: backbeat, sparse
    def snare_fitness(rhythm: str) -> float:
        return (
            0.5 * backbeat_emphasis(rhythm) +
            0.3 * sparsity(rhythm) +
            0.2 * simplicity(rhythm)
        )

    # DnB kick: sparse, avoid backbeats, anchor on beat 1
    def dnb_kick_fitness(rhythm: str) -> float:
        return (
            0.3 * hit_count_score(rhythm, 3, 5) +  # 3-5 hits
            0.3 * hits_at_positions(rhythm, [0]) +  # Anchor beat 1
            0.2 * avoid_positions(rhythm, [2, 6]) +  # Avoid snare positions
            0.2 * hits_at_positions(rhythm, [1, 5])  # Offbeat syncopation
        )
"""

from fitness.rhythm import rhythm_rest_ratio


def strong_beat_emphasis(rhythm: str) -> float:
    """Measure emphasis on strong beats (0-1). Higher = more downbeat.

    For 8-beat patterns: checks beats 1 and 5 (indices 0 and 4)
    For 4-beat patterns: checks beats 1 and 3 (indices 0 and 2)

    High = kick drums, downbeat emphasis
    Low = offbeat, syncopated
    """
    if not rhythm:
        return 0.0

    score = 0.0
    beat_count = len(rhythm)

    if beat_count >= 8:
        if rhythm[0] != "0":  # Beat 1
            score += 0.5
        if rhythm[4] != "0":  # Beat 5
            score += 0.5
    elif beat_count >= 4:
        if rhythm[0] != "0":  # Beat 1
            score += 0.5
        if beat_count > 2 and rhythm[2] != "0":  # Beat 3
            score += 0.5

    return score


def backbeat_emphasis(rhythm: str) -> float:
    """Measure emphasis on backbeats (0-1). Higher = more backbeat.

    For 8-beat patterns: checks beats 3 and 7 (indices 2 and 6)
    For 4-beat patterns: checks beats 2 and 4 (indices 1 and 3)

    High = snare/clap on 2 and 4
    Low = downbeat emphasis
    """
    if not rhythm:
        return 0.0

    score = 0.0
    beat_count = len(rhythm)

    if beat_count >= 8:
        if rhythm[2] != "0":  # Beat 3
            score += 0.5
        if rhythm[6] != "0":  # Beat 7
            score += 0.5
    elif beat_count >= 4:
        if rhythm[1] != "0":  # Beat 2
            score += 0.5
        if beat_count > 3 and rhythm[3] != "0":  # Beat 4
            score += 0.5

    return score


def sparsity(rhythm: str) -> float:
    """Measure sparsity (0-1). Higher = more sparse/open.

    Inverse of density - rewards patterns with more space.

    High = kick, snare (accent instruments)
    Low = hi-hat, shaker (time-keeping instruments)
    """
    if not rhythm:
        return 0.0

    density = sum(int(c) for c in rhythm) / (len(rhythm) * 4.0)
    return 1.0 - min(density * 2, 1.0)


def simplicity(rhythm: str) -> float:
    """Measure simplicity (0-1). Higher = more single hits.

    Ratio of '1' subdivisions to all active beats.
    Simple hits (1s) vs subdivisions (2s, 3s, 4s).

    High = kick, snare (powerful single hits)
    Low = hi-hat rolls, fills (subdivided)
    """
    if not rhythm:
        return 0.0

    ones_count = rhythm.count("1")
    active_beats = len(rhythm) - rhythm.count("0")

    return ones_count / active_beats if active_beats > 0 else 0.0


def offbeat_pattern(rhythm: str) -> float:
    """Measure offbeat pattern (0-1). Higher = more offbeat hits.

    Checks for notes on even indices (offbeats) and rests on odd (downbeats).

    High = offbeat hi-hats, syncopation
    Low = downbeat patterns
    """
    if not rhythm:
        return 0.0

    total_beats = len(rhythm)
    offbeat_score = 0

    for i, c in enumerate(rhythm):
        if i % 2 == 1 and c != '0':  # Offbeat positions have notes
            offbeat_score += 1
        elif i % 2 == 0 and c == '0':  # On-beat positions are rest
            offbeat_score += 0.5

    return offbeat_score / total_beats


# =============================================================================
# ADVANCED PRIMITIVES - For fine-grained drum pattern control
# =============================================================================


def total_hits(rhythm: str) -> int:
    """Count total note subdivisions in rhythm.

    Sum of all subdivision values (0-4 per beat).
    '0' = 0 hits, '1' = 1 hit, '2' = 2 hits, etc.

    Returns:
        Integer count of total hits/notes
    """
    if not rhythm:
        return 0
    return sum(int(c) for c in rhythm)


def hit_count_score(rhythm: str, target_min: int, target_max: int) -> float:
    """Score rhythm based on hit count falling within target range (0-1).

    Returns 1.0 if hit count is within [target_min, target_max].
    Returns partial score for close misses.

    Args:
        rhythm: Rhythm string
        target_min: Minimum acceptable hit count
        target_max: Maximum acceptable hit count

    High = sparse patterns (kick, snare)
    Low = dense patterns (hi-hat)
    """
    if not rhythm:
        return 0.0

    hits = total_hits(rhythm)

    if target_min <= hits <= target_max:
        return 1.0
    elif hits < target_min:
        # Partial score for being close
        distance = target_min - hits
        return max(0.0, 1.0 - distance * 0.2)
    else:
        # Partial score for being close
        distance = hits - target_max
        return max(0.0, 1.0 - distance * 0.2)


def hits_at_positions(rhythm: str, positions: list[int]) -> float:
    """Score for having hits at specific beat positions (0-1).

    Returns ratio of specified positions that have hits (non-zero).

    Args:
        rhythm: Rhythm string
        positions: List of beat indices to check (0-indexed)

    High = hits where expected (anchor kicks, backbeats)
    Low = misses at expected positions
    """
    if not rhythm or not positions:
        return 0.0

    valid_positions = [p for p in positions if p < len(rhythm)]
    if not valid_positions:
        return 0.0

    hits = sum(1 for p in valid_positions if rhythm[p] != "0")
    return hits / len(valid_positions)


def avoid_positions(rhythm: str, positions: list[int]) -> float:
    """Score for NOT having hits at specific positions (0-1).

    Returns ratio of specified positions that are rests.
    Use to keep kick away from snare positions, etc.

    Args:
        rhythm: Rhythm string
        positions: List of beat indices to avoid (0-indexed)

    High = successfully avoiding positions (e.g., kick avoiding snare beats)
    Low = unwanted hits at forbidden positions
    """
    if not rhythm or not positions:
        return 1.0

    valid_positions = [p for p in positions if p < len(rhythm)]
    if not valid_positions:
        return 1.0

    rests = sum(1 for p in valid_positions if rhythm[p] == "0")
    return rests / len(valid_positions)


def single_hits_at_positions(rhythm: str, positions: list[int]) -> float:
    """Score for having exactly '1' (single hit) at positions (0-1).

    Unlike hits_at_positions, this specifically wants single quarter-note hits,
    not subdivided beats. Good for punchy snares/kicks.

    Args:
        rhythm: Rhythm string
        positions: List of beat indices to check (0-indexed)

    High = clean single hits at positions (punchy drums)
    Low = subdivided or missing hits
    """
    if not rhythm or not positions:
        return 0.0

    valid_positions = [p for p in positions if p < len(rhythm)]
    if not valid_positions:
        return 0.0

    singles = sum(1 for p in valid_positions if rhythm[p] == "1")
    return singles / len(valid_positions)


def perfect_consistency(rhythm: str) -> float:
    """Score for all beats having the same subdivision value (0-1).

    Returns 1.0 if all characters are identical (e.g., "22222222").
    Good for driving hi-hat patterns.

    High = perfectly consistent pattern (driving hi-hats)
    Low = varied subdivisions
    """
    if not rhythm:
        return 0.0

    unique_vals = len(set(rhythm))
    if unique_vals == 1:
        return 1.0
    elif unique_vals == 2:
        return 0.5
    else:
        return max(0.0, 1.0 - (unique_vals - 1) * 0.25)


def uniform_subdivision(rhythm: str, target: str) -> float:
    """Score for matching a specific uniform subdivision pattern (0-1).

    Returns 1.0 if rhythm equals target repeated for its length.
    E.g., uniform_subdivision("22222222", "2") returns 1.0

    Args:
        rhythm: Rhythm string
        target: Single character target subdivision ("1", "2", "3", or "4")

    High = matches target subdivision pattern
    Low = doesn't match
    """
    if not rhythm or not target:
        return 0.0

    expected = target * len(rhythm)
    if rhythm == expected:
        return 1.0

    # Partial score based on how many beats match
    matches = sum(1 for i in range(len(rhythm)) if rhythm[i] == target)
    return matches / len(rhythm)
