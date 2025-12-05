"""Improved multi-layer composer with separate rhythm and note evolution."""
from dataclasses import dataclass
from typing import Callable, Optional
from core.genetic import GeneticAlgorithm, Individual
from core.music import Phrase, NoteName, Layer, Composition
from core.genome_ops import (
    random_rhythm,
    mutate_rhythm,
    crossover_rhythm,
    rhythm_to_phrase,
    phrase_with_rhythm,
    mutate_phrase,
    crossover_phrase,
)
from fitness.base import FitnessFunction


@dataclass
class LayerConfig:
    """Configuration for a layer with separate rhythm and note evolution."""
    name: str
    instrument: str
    bars: int = 2
    beats_per_bar: int = 4
    max_subdivision: int = 4
    octave_range: tuple[int, int] = (4, 5)
    scale: list[NoteName] = None
    rhythm_fitness_fn: Callable[[str], float] = None  # Takes rhythm string
    melody_fitness_fn: FitnessFunction = None  # Takes Layer object
    # Strudel parameters
    strudel_scale: str = ""  # e.g., "c:minor" - if empty, will be set randomly
    octave_shift: int = 0  # e.g., -7 for .sub(7)
    gain: float = 0.5
    lpf: int = 4000
    use_scale_degrees: bool = True  # Use 0-7 scale degrees

    def __post_init__(self):
        if self.scale is None:
            # Default to C major
            self.scale = [
                NoteName.C, NoteName.D, NoteName.E, NoteName.F,
                NoteName.G, NoteName.A, NoteName.B
            ]

    @property
    def total_beats(self) -> int:
        return self.bars * self.beats_per_bar


class LayeredComposer:
    """Composer that evolves rhythm and melody separately for each layer."""

    def __init__(
        self,
        population_size: int = 20,
        mutation_rate: float = 0.25,
        elitism_count: int = 6,
        rhythm_generations: int = 20,
        melody_generations: int = 30,
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.rhythm_generations = rhythm_generations
        self.melody_generations = melody_generations

        self.layer_configs: list[LayerConfig] = []
        self.evolved_rhythms: dict[str, str] = {}  # layer_name -> rhythm string
        self.evolved_phrases: dict[str, Phrase] = {}  # layer_name -> Phrase

    def add_layer(self, config: LayerConfig) -> None:
        """Add a layer configuration."""
        self.layer_configs.append(config)

    def evolve_layer_rhythm(
        self,
        config: LayerConfig,
        verbose: bool = True
    ) -> str:
        """Evolve rhythm for a single layer."""
        if verbose:
            print(f"\n{'='*60}")
            print(f"Evolving rhythm for layer: {config.name}")
            print(f"{'='*60}")

        ga = GeneticAlgorithm[str](
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            elitism_count=self.elitism_count,
        )

        # Initialize population
        population = [
            Individual(random_rhythm(config.total_beats, config.max_subdivision))
            for _ in range(self.population_size)
        ]

        # Evolve
        best_fitness = 0.0
        for gen in range(self.rhythm_generations):
            population = ga.evolve(
                population=population,
                fitness_fn=config.rhythm_fitness_fn,
                mutate_fn=lambda r: mutate_rhythm(r, self.mutation_rate, config.max_subdivision),
                crossover_fn=crossover_rhythm,
            )

            best = population[0]
            best_fitness = best.fitness

            if verbose and (gen % 5 == 0 or gen == self.rhythm_generations - 1):
                print(f"  Gen {gen:3d}: Best fitness = {best_fitness:.4f}, rhythm = {best.genome}")

        best_rhythm = population[0].genome
        if verbose:
            print(f"✓ Final rhythm: {best_rhythm} (fitness: {best_fitness:.4f})")

        return best_rhythm

    def evolve_layer_melody(
        self,
        config: LayerConfig,
        rhythm: str,
        verbose: bool = True
    ) -> Phrase:
        """Evolve melody for a single layer with fixed rhythm."""
        if verbose:
            print(f"\n{'='*60}")
            print(f"Evolving melody for layer: {config.name}")
            print(f"Using rhythm: {rhythm}")
            print(f"{'='*60}")

        ga = GeneticAlgorithm[Phrase](
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            elitism_count=self.elitism_count,
        )

        # Initialize population with the rhythm
        population = [
            Individual(rhythm_to_phrase(rhythm, scale=config.scale, octave_range=config.octave_range))
            for _ in range(self.population_size)
        ]

        # Evolve
        def melody_fitness(phrase: Phrase) -> float:
            layer = Layer(name=config.name, phrases=[phrase], instrument=config.instrument)
            return config.melody_fitness_fn.evaluate(layer)

        def melody_mutate(phrase: Phrase) -> Phrase:
            mutated = mutate_phrase(phrase, mutation_rate=self.mutation_rate)
            return phrase_with_rhythm(mutated, rhythm)

        def melody_crossover(p1: Phrase, p2: Phrase) -> Phrase:
            child = crossover_phrase(p1, p2)
            return phrase_with_rhythm(child, rhythm)

        best_fitness = 0.0
        for gen in range(self.melody_generations):
            population = ga.evolve(
                population=population,
                fitness_fn=melody_fitness,
                mutate_fn=melody_mutate,
                crossover_fn=melody_crossover,
            )

            best = population[0]
            best_fitness = best.fitness

            if verbose and (gen % 10 == 0 or gen == self.melody_generations - 1):
                print(f"  Gen {gen:3d}: Best fitness = {best_fitness:.4f}")

        best_phrase = population[0].genome
        if verbose:
            print(f"✓ Final melody fitness: {best_fitness:.4f}")

        return best_phrase

    def evolve_all_layers(self, verbose: bool = True) -> None:
        """Evolve all layers (rhythm then melody for each)."""
        for config in self.layer_configs:
            # Phase 1: Evolve rhythm
            rhythm = self.evolve_layer_rhythm(config, verbose=verbose)
            self.evolved_rhythms[config.name] = rhythm

            # Phase 2: Evolve melody with that rhythm
            phrase = self.evolve_layer_melody(config, rhythm, verbose=verbose)
            self.evolved_phrases[config.name] = phrase

    def get_composition(self, bpm: int = 120, random_scale: bool = True) -> Composition:
        """Get the final composition with all evolved layers.

        Args:
            bpm: Beats per minute
            random_scale: If True, uses a random scale for all layers
        """
        # Generate random scale if needed
        if random_scale:
            composition_scale = Composition.random_scale()
        else:
            composition_scale = "c:major"

        layers = []
        for config in self.layer_configs:
            phrase = self.evolved_phrases.get(config.name)
            rhythm = self.evolved_rhythms.get(config.name)
            if phrase:
                # Use config scale if specified, otherwise use composition scale
                layer_scale = config.strudel_scale if config.strudel_scale else composition_scale

                layer = Layer(
                    name=config.name,
                    phrases=[phrase],
                    instrument=config.instrument,
                    rhythm=rhythm if rhythm else "",
                    scale=layer_scale,
                    octave_shift=config.octave_shift,
                    gain=config.gain,
                    lpf=config.lpf,
                    use_scale_degrees=config.use_scale_degrees
                )
                layers.append(layer)

        return Composition(layers=layers, bpm=bpm)

    def print_summary(self) -> None:
        """Print a summary of all evolved layers."""
        from fitness.rhythm import (
            rhythm_complexity, rhythm_density, rhythm_syncopation,
            rhythm_groove, rhythm_rest_ratio
        )

        print("\n" + "="*60)
        print("COMPOSITION SUMMARY")
        print("="*60)
        for config in self.layer_configs:
            rhythm = self.evolved_rhythms.get(config.name, "Not evolved")
            phrase = self.evolved_phrases.get(config.name)
            print(f"\n{config.name.upper()} ({config.instrument}):")
            print(f"  Rhythm: {rhythm}")

            # Show rhythm analysis if available
            if rhythm != "Not evolved":
                print(f"  Rhythm Analysis:")
                print(f"    - Complexity: {rhythm_complexity(rhythm):.2f}")
                print(f"    - Density: {rhythm_density(rhythm):.2f}")
                print(f"    - Syncopation: {rhythm_syncopation(rhythm):.2f}")
                print(f"    - Groove: {rhythm_groove(rhythm):.2f}")
                print(f"    - Rest Ratio: {rhythm_rest_ratio(rhythm):.2f}")

            if phrase:
                print(f"  Notes:  {phrase.to_strudel()}")
