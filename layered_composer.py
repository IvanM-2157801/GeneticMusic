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
    ChordProgression,
    random_chord_progression,
    mutate_chord_progression,
    crossover_chord_progression,
)
from fitness.base import FitnessFunction
from fitness.chords import ChordFitnessFunction


@dataclass
class LayerConfig:
    """Configuration for a layer with separate rhythm and note evolution."""

    name: str
    instrument: str
    bars: int = 1
    beats_per_bar: int = 8
    max_subdivision: int = 2
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
    chord_mode: bool = False  # Use comma-separated notes for chords
    # Drum parameters
    is_drum: bool = False  # If True, only evolves rhythm (no melody)
    drum_sound: str = ""  # Drum sound name (e.g., "bd", "hh", "sd")
    # Chord parameters
    is_chord_layer: bool = False  # If True, evolves chord progressions instead of melody
    num_chords: int = 4  # Number of chords in the progression
    notes_per_chord: int = 3  # Number of notes per chord (2=dyad, 3=triad, 4=7th)
    allowed_chord_types: list[str] = None  # e.g., ["major", "minor", "dom7"]
    chord_fitness_fn: ChordFitnessFunction = None  # Takes ChordProgression

    def __post_init__(self):
        if self.scale is None:
            # Default to C major
            self.scale = [
                NoteName.C,
                NoteName.D,
                NoteName.E,
                NoteName.F,
                NoteName.G,
                NoteName.A,
                NoteName.B,
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
        chord_generations: int = 25,  # New: generations for chord evolution
        use_context: bool = True,  # Enable inter-layer dependencies
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.rhythm_generations = rhythm_generations
        self.melody_generations = melody_generations
        self.chord_generations = chord_generations
        self.use_context = use_context

        self.layer_configs: list[LayerConfig] = []
        self.evolved_rhythms: dict[str, str] = {}  # layer_name -> rhythm string
        self.evolved_phrases: dict[str, Phrase] = {}  # layer_name -> Phrase
        self.evolved_chords: dict[str, ChordProgression] = {}  # layer_name -> ChordProgression
        self.evolved_layers: dict[str, tuple[Layer, str]] = {}  # layer_name -> (Layer, rhythm)

    def add_layer(self, config: LayerConfig) -> None:
        """Add a layer configuration."""
        self.layer_configs.append(config)

    def evolve_layer_rhythm(self, config: LayerConfig, verbose: bool = True) -> str:
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
                mutate_fn=lambda r: mutate_rhythm(
                    r, self.mutation_rate, config.max_subdivision
                ),
                crossover_fn=crossover_rhythm,
            )

            best = population[0]
            best_fitness = best.fitness

            if verbose and (gen % 5 == 0 or gen == self.rhythm_generations - 1):
                print(
                    f"  Gen {gen:3d}: Best fitness = {best_fitness:.4f}, rhythm = {best.genome}"
                )

        best_rhythm = population[0].genome
        if verbose:
            print(f"✓ Final rhythm: {best_rhythm} (fitness: {best_fitness:.4f})")

        return best_rhythm

    def evolve_layer_melody(
        self, config: LayerConfig, rhythm: str, verbose: bool = True
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
            Individual(
                rhythm_to_phrase(
                    rhythm, scale=config.scale, octave_range=config.octave_range
                )
            )
            for _ in range(self.population_size)
        ]

        # Evolve with contextual fitness
        from fitness.contextual import create_contextual_fitness

        # Create contextual fitness that considers already-evolved layers
        contextual_fitness = create_contextual_fitness(
            intrinsic_fitness=config.melody_fitness_fn,
            evolved_layers=self.evolved_layers,
            use_context=self.use_context,
        )

        def melody_fitness(phrase: Phrase) -> float:
            layer = Layer(
                name=config.name,
                phrases=[phrase],
                instrument=config.instrument,
                rhythm=rhythm,
                is_drum=config.is_drum,
            )
            return contextual_fitness.evaluate(layer)

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

    def evolve_layer_chords(
        self, config: LayerConfig, verbose: bool = True
    ) -> ChordProgression:
        """Evolve chord progression for a chord layer."""
        if verbose:
            print(f"\n{'='*60}")
            print(f"Evolving chords for layer: {config.name}")
            print(f"Num chords: {config.num_chords}, Notes per chord: {config.notes_per_chord}")
            print(f"{'='*60}")

        ga = GeneticAlgorithm[ChordProgression](
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            elitism_count=self.elitism_count,
        )

        # Initialize population
        population = [
            Individual(
                random_chord_progression(
                    num_chords=config.num_chords,
                    notes_per_chord=config.notes_per_chord,
                    allowed_types=config.allowed_chord_types,
                )
            )
            for _ in range(self.population_size)
        ]

        # Fitness function
        def chord_fitness(prog: ChordProgression) -> float:
            if config.chord_fitness_fn:
                return config.chord_fitness_fn.evaluate(prog)
            return 0.5  # Default neutral fitness

        def chord_mutate(prog: ChordProgression) -> ChordProgression:
            return mutate_chord_progression(
                prog,
                mutation_rate=self.mutation_rate,
                notes_per_chord=config.notes_per_chord,
            )

        # Evolve
        best_fitness = 0.0
        for gen in range(self.chord_generations):
            population = ga.evolve(
                population=population,
                fitness_fn=chord_fitness,
                mutate_fn=chord_mutate,
                crossover_fn=crossover_chord_progression,
            )

            best = population[0]
            best_fitness = best.fitness

            if verbose and (gen % 5 == 0 or gen == self.chord_generations - 1):
                chord_summary = " → ".join(
                    f"{c.root_degree}({len(c.intervals)})" for c in best.genome.chords
                )
                print(f"  Gen {gen:3d}: Best fitness = {best_fitness:.4f}, chords = {chord_summary}")

        best_progression = population[0].genome
        if verbose:
            print(f"✓ Final chord fitness: {best_fitness:.4f}")

        return best_progression

    def evolve_all_layers(self, verbose: bool = True) -> None:
        """Evolve all layers (rhythm then melody/chords for each) with inter-layer dependencies."""
        for config in self.layer_configs:
            # Phase 1: Evolve rhythm (for all layer types except pure chord layers)
            if not config.is_chord_layer:
                rhythm = self.evolve_layer_rhythm(config, verbose=verbose)
                self.evolved_rhythms[config.name] = rhythm
            else:
                # Chord layers don't need rhythm evolution
                rhythm = ""
                self.evolved_rhythms[config.name] = rhythm

            # Phase 2: Evolve melody, chords, or skip (for drums)
            if config.is_drum:
                # Drums only need rhythm, no melody
                if verbose:
                    print(f"✓ Drum layer '{config.name}' complete (rhythm only)\n")
                self.evolved_phrases[config.name] = None
                self.evolved_chords[config.name] = None

                # Add drum layer to context for future layers
                drum_layer = Layer(
                    name=config.name,
                    instrument=config.instrument,
                    rhythm=rhythm,
                    is_drum=True,
                    drum_sound=config.drum_sound,
                )
                self.evolved_layers[config.name] = (drum_layer, rhythm)

            elif config.is_chord_layer:
                # Chord layer: evolve chord progression
                chord_progression = self.evolve_layer_chords(config, verbose=verbose)
                self.evolved_chords[config.name] = chord_progression
                self.evolved_phrases[config.name] = None

                # Add chord layer to context for future layers
                chord_layer = Layer(
                    name=config.name,
                    instrument=config.instrument,
                    is_chord_layer=True,
                    chord_progression=chord_progression.chords,
                    gain=config.gain,
                    lpf=config.lpf,
                    octave_shift=config.octave_shift,
                )
                self.evolved_layers[config.name] = (chord_layer, rhythm)
                if verbose:
                    print(f"✓ Chord layer '{config.name}' complete\n")

            else:
                # Regular melodic layer
                phrase = self.evolve_layer_melody(config, rhythm, verbose=verbose)
                self.evolved_phrases[config.name] = phrase
                self.evolved_chords[config.name] = None

                # Add melodic layer to context for future layers
                melodic_layer = Layer(
                    name=config.name,
                    phrases=[phrase],
                    instrument=config.instrument,
                    rhythm=rhythm,
                )
                self.evolved_layers[config.name] = (melodic_layer, rhythm)

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
            rhythm = self.evolved_rhythms.get(config.name)

            if config.is_drum:
                # Drum layer: only rhythm, no phrases
                if rhythm:
                    layer = Layer(
                        name=config.name,
                        phrases=[],
                        instrument=config.instrument,
                        rhythm=rhythm,
                        gain=config.gain,
                        is_drum=True,
                        drum_sound=config.drum_sound,
                    )
                    layers.append(layer)
            
            elif config.is_chord_layer:
                # Chord layer: uses chord progression
                chord_progression = self.evolved_chords.get(config.name)
                if chord_progression:
                    # Use config scale if specified, otherwise use composition scale
                    layer_scale = (
                        config.strudel_scale if config.strudel_scale else composition_scale
                    )
                    
                    layer = Layer(
                        name=config.name,
                        phrases=[],
                        instrument=config.instrument,
                        rhythm="",
                        scale=layer_scale,
                        octave_shift=config.octave_shift,
                        gain=config.gain,
                        lpf=config.lpf,
                        is_chord_layer=True,
                        chord_progression=chord_progression.chords,
                    )
                    layers.append(layer)
            
            else:
                # Melodic layer: needs phrases
                phrase = self.evolved_phrases.get(config.name)
                if phrase:
                    # Use config scale if specified, otherwise use composition scale
                    layer_scale = (
                        config.strudel_scale if config.strudel_scale else composition_scale
                    )

                    layer = Layer(
                        name=config.name,
                        phrases=[phrase],
                        instrument=config.instrument,
                        rhythm=rhythm if rhythm else "",
                        scale=layer_scale,
                        octave_shift=config.octave_shift,
                        gain=config.gain,
                        lpf=config.lpf,
                        use_scale_degrees=config.use_scale_degrees,
                        chord_mode=config.chord_mode,
                    )
                    layers.append(layer)

        return Composition(layers=layers, bpm=bpm)

    def print_summary(self) -> None:
        """Print a summary of all evolved layers."""
        from fitness.rhythm import (
            rhythm_complexity,
            rhythm_density,
            rhythm_syncopation,
            rhythm_groove,
            rhythm_rest_ratio,
        )
        from core.genome_ops import CHORD_TYPES

        print("\n" + "=" * 60)
        print("COMPOSITION SUMMARY")
        print("=" * 60)
        for config in self.layer_configs:
            rhythm = self.evolved_rhythms.get(config.name, "Not evolved")
            phrase = self.evolved_phrases.get(config.name)
            chord_prog = self.evolved_chords.get(config.name)
            
            print(f"\n{config.name.upper()} ({config.instrument}):")
            
            if config.is_chord_layer:
                print(f"  Type: Chord Layer")
                if chord_prog:
                    chord_strs = []
                    for c in chord_prog.chords:
                        # Find matching chord type name
                        chord_type = "custom"
                        for name, intervals in CHORD_TYPES.items():
                            if c.intervals == intervals:
                                chord_type = name
                                break
                        chord_strs.append(f"deg{c.root_degree}({chord_type})")
                    print(f"  Chords: {' → '.join(chord_strs)}")
            else:
                print(f"  Rhythm: {rhythm}")

                # Show rhythm analysis if available
                if rhythm and rhythm != "Not evolved":
                    print(f"  Rhythm Analysis:")
                    print(f"    - Complexity: {rhythm_complexity(rhythm):.2f}")
                    print(f"    - Density: {rhythm_density(rhythm):.2f}")
                    print(f"    - Syncopation: {rhythm_syncopation(rhythm):.2f}")
                    print(f"    - Groove: {rhythm_groove(rhythm):.2f}")
                    print(f"    - Rest Ratio: {rhythm_rest_ratio(rhythm):.2f}")

                if phrase:
                    print(f"  Notes:  {phrase.to_strudel()}")
