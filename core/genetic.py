from dataclasses import dataclass
from typing import TypeVar, Generic, Callable
import random

T = TypeVar("T")


@dataclass
class Individual(Generic[T]):
    genome: T
    fitness: float = 0.0


class GeneticAlgorithm(Generic[T]):
    def __init__(
        self,
        population_size: int,
        mutation_rate: float,
        elitism_count: int = 2,
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count

    def evolve(
        self,
        population: list[Individual[T]],
        fitness_fn: Callable[[T], float],
        mutate_fn: Callable[[T], T],
        crossover_fn: Callable[[T, T], T],
    ) -> list[Individual[T]]:
        # Evaluate fitness
        for ind in population:
            ind.fitness = fitness_fn(ind.genome)

        # Sort by fitness (descending)
        population.sort(key=lambda x: x.fitness, reverse=True)

        # Elitism: keep top performers
        new_population = [Individual(p.genome, p.fitness) for p in population[: self.elitism_count]]

        # Fill rest with offspring
        while len(new_population) < self.population_size:
            parent1 = self._select(population)
            parent2 = self._select(population)

            child_genome = crossover_fn(parent1.genome, parent2.genome)

            if random.random() < self.mutation_rate:
                child_genome = mutate_fn(child_genome)

            new_population.append(Individual(child_genome))

        return new_population

    def _select(self, population: list[Individual[T]]) -> Individual[T]:
        tournament_size = 3
        contestants = random.sample(population, min(tournament_size, len(population)))
        return max(contestants, key=lambda x: x.fitness)
