"""Multi-layer composition evolution."""
from dataclasses import dataclass
from core.genetic import GeneticAlgorithm, Individual
from core.music import Layer, Composition
from core.genome_ops import random_layer, mutate_layer, crossover_layer
from fitness.base import FitnessFunction


@dataclass
class LayerConfig:
    """Configuration for a single layer."""
    name: str
    instrument: str
    phrase_count: int
    phrase_length: int
    octave_range: tuple[int, int]
    fitness_fn: FitnessFunction


class Composer:
    """Orchestrates multi-layer music evolution."""

    def __init__(
        self,
        population_size: int = 50,
        mutation_rate: float = 0.1,
        elitism: int = 2,
    ):
        self.ga = GeneticAlgorithm(
            population_size=population_size,
            mutation_rate=mutation_rate,
            elitism_count=elitism,
        )
        self.population_size = population_size
        self.layer_configs: list[LayerConfig] = []
        self.populations: dict[str, list[Individual[Layer]]] = {}

    def add_layer(self, config: LayerConfig) -> None:
        """Add a layer configuration."""
        self.layer_configs.append(config)
        # Initialize population for this layer
        self.populations[config.name] = [
            Individual(random_layer(
                name=config.name,
                phrase_count=config.phrase_count,
                phrase_length=config.phrase_length,
                instrument=config.instrument,
                octave_range=config.octave_range,
            ))
            for _ in range(self.population_size)
        ]

    def evolve(self, generations: int = 100) -> dict[str, list[float]]:
        """Evolve all layers for specified generations."""
        history = {cfg.name: [] for cfg in self.layer_configs}

        for gen in range(generations):
            for config in self.layer_configs:
                pop = self.populations[config.name]

                # Evolve this layer
                new_pop = self.ga.evolve(
                    population=pop,
                    fitness_fn=config.fitness_fn.evaluate,
                    mutate_fn=lambda l: mutate_layer(l, 0.1),
                    crossover_fn=crossover_layer,
                )

                self.populations[config.name] = new_pop
                best_fitness = max(ind.fitness for ind in new_pop)
                history[config.name].append(best_fitness)

            if gen % 10 == 0:
                print(f"Generation {gen}: ", end="")
                for cfg in self.layer_configs:
                    best = max(self.populations[cfg.name], key=lambda x: x.fitness)
                    print(f"{cfg.name}={best.fitness:.3f} ", end="")
                print()

        return history

    def get_best_composition(self, bpm: int = 120) -> Composition:
        """Get the best individual from each layer as a composition."""
        layers = []
        for config in self.layer_configs:
            best = max(self.populations[config.name], key=lambda x: x.fitness)
            layers.append(best.genome)

        return Composition(layers=layers, bpm=bpm)
