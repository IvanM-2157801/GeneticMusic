"""Fitness functions for music evaluation.

This module provides primitive building blocks for creating custom fitness functions.
Combine these primitives with weights to define your own musical style.

MELODY PRIMITIVES (fitness/base.py):
- note_variety(phrase)        : Pitch variety (0-1)
- rest_ratio(phrase)          : Rest ratio (0-1)
- interval_smoothness(phrase) : Melodic smoothness (0-1)
- scale_adherence(phrase, scale): Scale conformity (0-1)
- rhythmic_variety(phrase)    : Duration variety (0-1)

RHYTHM PRIMITIVES (fitness/rhythm.py):
- rhythm_complexity(rhythm)     : Subdivision variety (0-1)
- rhythm_rest_ratio(rhythm)     : Rest ratio (0-1)
- rhythm_density(rhythm)        : Notes per beat (0-1)
- rhythm_syncopation(rhythm)    : Subdivision changes (0-1)
- rhythm_groove(rhythm)         : Strong/weak alternation (0-1)
- rhythm_consistency(rhythm)    : Pattern repetition (0-1)
- rhythm_offbeat_emphasis(rhythm): Offbeat activity (0-1)

DRUM PRIMITIVES (fitness/drums.py):
- strong_beat_emphasis(rhythm)  : Downbeat activity (0-1)
- backbeat_emphasis(rhythm)     : Backbeat activity (0-1)
- sparsity(rhythm)              : Inverse of density (0-1)
- simplicity(rhythm)            : Single hit ratio (0-1)
- offbeat_pattern(rhythm)       : Offbeat pattern (0-1)

CHORD PRIMITIVES (fitness/chords.py):
- chord_variety(progression)          : Root variety (0-1)
- chord_type_variety(progression)     : Quality variety (0-1)
- root_motion_smoothness(progression) : Smooth motion (0-1)
- functional_harmony_score(progression): I/IV/V usage (0-1)
- resolution_bonus(progression)       : V-I patterns (0-1)
- triadic_bonus(progression)          : Simple triads (0-1)
- seventh_chord_bonus(progression)    : 7th chords (0-1)

SCALES:
- MAJOR_SCALE, MINOR_SCALE, PENTATONIC, BLUES_SCALE

EXAMPLE - Creating a custom melody fitness:

    from fitness.base import FitnessFunction, note_variety, interval_smoothness, rest_ratio

    class MyMelodyFitness(FitnessFunction):
        def evaluate(self, layer):
            scores = []
            for phrase in layer.phrases:
                score = (
                    0.4 * note_variety(phrase) +
                    0.4 * interval_smoothness(phrase) +
                    0.2 * (1 - rest_ratio(phrase))
                )
                scores.append(score)
            return sum(scores) / len(scores) if scores else 0.0

EXAMPLE - Creating a custom rhythm fitness:

    from fitness.rhythm import rhythm_groove, rhythm_consistency, rhythm_density

    def my_rhythm_fitness(rhythm: str) -> float:
        return (
            0.4 * rhythm_groove(rhythm) +
            0.3 * rhythm_consistency(rhythm) +
            0.3 * rhythm_density(rhythm)
        )
"""

# Base classes and melody primitives
from .base import (
    FitnessFunction,
    note_variety,
    rest_ratio,
    interval_smoothness,
    scale_adherence,
    rhythmic_variety,
    MAJOR_SCALE,
    MINOR_SCALE,
    PENTATONIC,
    BLUES_SCALE,
)

# Rhythm primitives
from .rhythm import (
    rhythm_complexity,
    rhythm_rest_ratio,
    rhythm_density,
    rhythm_syncopation,
    rhythm_groove,
    rhythm_consistency,
    rhythm_offbeat_emphasis,
)

# Drum primitives
from .drums import (
    strong_beat_emphasis,
    backbeat_emphasis,
    sparsity,
    simplicity,
    offbeat_pattern,
)

# Chord primitives
from .chords import (
    ChordFitnessFunction,
    chord_variety,
    chord_type_variety,
    root_motion_smoothness,
    functional_harmony_score,
    resolution_bonus,
    triadic_bonus,
    seventh_chord_bonus,
)
