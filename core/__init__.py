"""Core genetic algorithm and music representation."""
from .genetic import GeneticAlgorithm, Individual
from .music import Note, Phrase, Layer, Composition, NoteName
from .genome_ops import (
    random_note,
    random_phrase,
    random_layer,
    mutate_note,
    mutate_phrase,
    mutate_layer,
    crossover_phrase,
    crossover_layer,
)
