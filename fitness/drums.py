"""Primitive fitness functions for drum patterns.

These functions evaluate rhythm strings for different drum roles.
Each returns 0.0-1.0 and can be combined with weights.

DRUM ROLE PRIMITIVES:
- strong_beat_emphasis(rhythm)  : Activity on beats 1/5 (higher = more downbeat)
- backbeat_emphasis(rhythm)     : Activity on beats 3/7 (higher = more backbeat)
- sparsity(rhythm)              : Inverse of density (higher = more sparse)
- simplicity(rhythm)            : Ratio of simple hits (higher = more single hits)

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
