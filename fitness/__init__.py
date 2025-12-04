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
