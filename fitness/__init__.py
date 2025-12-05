"""Fitness functions for music evaluation."""
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
from .genres import (
    PopFitness,
    JazzFitness,
    BluesFitness,
    AmbientFitness,
    FITNESS_FUNCTIONS,
)
from .rhythm import (
    rhythm_complexity,
    rhythm_rest_ratio,
    rhythm_density,
    rhythm_syncopation,
    rhythm_groove,
    rhythm_consistency,
    rhythm_offbeat_emphasis,
    pop_rhythm_fitness,
    jazz_rhythm_fitness,
    funk_rhythm_fitness,
    ambient_rhythm_fitness,
    rock_rhythm_fitness,
    RHYTHM_FITNESS_FUNCTIONS,
)
