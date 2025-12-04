"""Music Genetic Algorithm - Generate music using evolutionary algorithms."""
from .composer import Composer, LayerConfig
from .core.music import Note, Phrase, Layer, Composition, NoteName
from .fitness.genres import FITNESS_FUNCTIONS

__all__ = [
    "Composer",
    "LayerConfig", 
    "Note",
    "Phrase",
    "Layer",
    "Composition",
    "NoteName",
    "FITNESS_FUNCTIONS",
]
