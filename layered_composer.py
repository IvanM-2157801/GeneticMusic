"""Improved multi-layer composer with separate rhythm and note evolution.

Features:
- Two-phase evolution (rhythm then melody) for each layer
- Chord-aware melody evolution using HarmonicContext
- Inter-layer fitness for coherent arrangements
- Theme tracking for musical development
"""

import random
from dataclasses import dataclass, field
from typing import Callable, Optional, Union
from core.genetic import GeneticAlgorithm, Individual
from core.music import (
    Phrase,
    NoteName,
    Layer,
    Composition,
    HarmonicContext,
    LayerGroup,
    Arrangement,
    SongStructure,
)
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
from fitness.harmony import create_harmony_fitness, GENRE_CHORD_STRICTNESS


@dataclass
class LayerConfig:
    """Configuration for a layer with separate rhythm and note evolution."""

    name: str
    instrument: Union[str, list[str]]  # Single instrument or list to choose from
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
    # Basic effects
    gain: float = 0.5  # Volume (0.0-1.0)
    lpf: int = 4000  # Low-pass filter (Hz, 0 = disabled)
    hpf: int = 0  # High-pass filter (Hz, 0 = disabled)
    # Post effects
    postgain: float = 0.0  # Volume after effects (0.0 = disabled)
    # Reverb
    room: float = 0.0  # Reverb amount (0.0-1.0, 0 = disabled)
    roomsize: float = 2.0  # Reverb size (0.0-10.0)
    # Delay
    delay: float = 0.0  # Delay send (0.0-1.0, 0 = disabled)
    delaytime: float = 0.25  # Delay time (in cycles)
    delayfeedback: float = 0.5  # Delay feedback (0.0-0.9)
    # Distortion
    distort: float = 0.0  # Distortion amount (0.0-10.0, 0 = disabled)
    # Panning
    pan: float = 0.5  # Stereo pan (0=left, 0.5=center, 1=right)
    # Envelope (ADSR)
    attack: float = 0.0  # Attack time (0 = disabled)
    decay: float = 0.0  # Decay time (0 = disabled)
    sustain: float = 0.0  # Sustain level (0 = disabled)
    release: float = 0.0  # Release time (0 = disabled)
    # Other
    use_scale_degrees: bool = True  # Use 0-7 scale degrees
    chord_mode: bool = False  # Use comma-separated notes for chords
    base_octave: int = 4  # Base octave for scale degree calculation (notes at this octave output 0-6)
    # Context group - layers with the same group name share context during evolution
    context_group: str = ""
    # Drum parameters
    is_drum: bool = False  # If True, only evolves rhythm (no melody)
    drum_sound: str = ""  # Drum sound name (e.g., "bd", "hh", "sd")
    # Sound bank for Strudel (e.g., "RolandTR808", "alesissr16")
    bank: str = ""
    # Chord parameters
    is_chord_layer: bool = (
        False  # If True, evolves chord progressions instead of melody
    )
    num_chords: int = 4  # Number of chords in the progression
    notes_per_chord: int = 3  # Number of notes per chord (2=dyad, 3=triad, 4=7th)
    allowed_chord_types: list[str] = None  # e.g., ["major", "minor", "dom7"]
    chord_fitness_fn: ChordFitnessFunction = None  # Takes ChordProgression
    # Harmony-aware parameters
    use_harmonic_context: bool = True  # If True, melody fitness considers chords
    genre: str = "pop"  # Genre for chord-melody strictness (pop, jazz, blues, etc.)
    harmony_weight: float = 0.4  # Weight for harmonic fitness (0.0-1.0)
    # Layer role for evolution ordering
    layer_role: str = "melody"  # "chords", "drums", "bass", "melody", "pad"
    # Contextual fitness weights for inter-layer scoring
    # Available metrics: "rhythmic", "density", "harmonic", "voice_leading", "call_response"
    contextual_weights: dict = None  # e.g., {"rhythmic": 0.4, "harmonic": 0.3}
    # Metal-style output options
    use_note_notation: bool = False  # If True, uses note("e2") instead of n("0").scale()
    struct_pattern: str = ""  # Optional struct pattern (e.g., "x*8", "x(7,16)")
    slow_factor: float = 1.0  # Slow down factor (e.g., 2.0 for .slow(2))
    adsr: str = ""  # ADSR envelope string (e.g., ".001:.1:.8:.05")
    lpq: float = 0.0  # Low-pass filter Q/resonance (0 = disabled)

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

    def get_instrument(self) -> str:
        """Get the instrument, randomly selecting from list if multiple provided."""
        if isinstance(self.instrument, list):
            return random.choice(self.instrument)
        return self.instrument


# Layer role priority for evolution order
# Lower numbers = evolved first (provides context for later layers)
LAYER_ROLE_PRIORITY = {
    "chords": 0,    # Harmonic foundation - evolve first
    "drums": 1,     # Rhythmic foundation
    "bass": 2,      # Harmonic + rhythmic bridge
    "melody": 3,    # Main melodic line
    "pad": 4,       # Harmonic fill
    "lead": 5,      # Solo/lead line (last, most freedom)
}


class LayeredComposer:
    """Composer that evolves rhythm and melody separately for each layer.

    Features:
    - Two-phase evolution (rhythm then melody)
    - Harmonic context for chord-aware melody evolution
    - Inter-layer fitness for coherent arrangements
    - Automatic layer ordering based on musical role
    - Theme storage for musical development
    """

    def __init__(
        self,
        population_size: int = 20,
        mutation_rate: float = 0.25,
        elitism_count: int = 6,
        rhythm_generations: int = 20,
        melody_generations: int = 30,
        chord_generations: int = 25,
        use_context: bool = True,  # Enable inter-layer dependencies
        use_harmonic_context: bool = True,  # Enable chord-aware melody evolution
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.rhythm_generations = rhythm_generations
        self.melody_generations = melody_generations
        self.chord_generations = chord_generations
        self.use_context = use_context
        self.use_harmonic_context = use_harmonic_context

        self.layer_configs: list[LayerConfig] = []
        self.evolved_rhythms: dict[str, str] = {}  # layer_name -> rhythm string
        self.evolved_phrases: dict[str, Phrase] = {}  # layer_name -> Phrase
        self.evolved_chords: dict[str, ChordProgression] = {}  # layer_name -> ChordProgression
        self.evolved_layers: dict[str, tuple[Layer, str]] = {}  # layer_name -> (Layer, rhythm)
        self.resolved_instruments: dict[str, str] = {}  # layer_name -> chosen instrument

        # Harmonic context (set after chord evolution)
        self.harmonic_context: Optional[HarmonicContext] = None

        # Theme storage for musical development
        self.themes: dict[str, Phrase] = {}  # layer_name -> original theme phrase

        # Scale info (set before evolution)
        self.scale_root: str = "c"
        self.scale_type: str = "major"

    def add_layer(self, config: LayerConfig) -> None:
        """Add a layer configuration."""
        self.layer_configs.append(config)

    def get_instrument(self, config: LayerConfig) -> str:
        """Get the resolved instrument for a layer.

        If instrument is a list, randomly selects one on first call
        and caches it for subsequent calls.
        """
        if config.name not in self.resolved_instruments:
            self.resolved_instruments[config.name] = config.get_instrument()
        return self.resolved_instruments[config.name]

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
        """Evolve melody for a single layer with fixed rhythm.

        If harmonic context is available and use_harmonic_context is enabled,
        the melody fitness will consider how well notes fit the chord progression.
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Evolving melody for layer: {config.name}")
            print(f"Using rhythm: {rhythm}")
            if self.harmonic_context and self.use_harmonic_context and config.use_harmonic_context:
                strictness = GENRE_CHORD_STRICTNESS.get(config.genre, 0.6)
                print(f"Harmonic context: enabled (genre={config.genre}, strictness={strictness:.1f})")
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

        # Build fitness function with optional harmonic awareness
        base_fitness = config.melody_fitness_fn

        # Add harmonic context if available and enabled
        if (self.harmonic_context and
            self.use_harmonic_context and
            config.use_harmonic_context and
            base_fitness):
            # Wrap with harmony-aware fitness
            harmony_fitness = create_harmony_fitness(
                intrinsic_fitness=base_fitness,
                harmonic_context=self.harmonic_context,
                genre=config.genre,
                harmony_weight=config.harmony_weight,
            )
        else:
            harmony_fitness = base_fitness

        # Wrap with contextual fitness for inter-layer awareness
        from fitness.contextual import create_contextual_fitness

        contextual_fitness = create_contextual_fitness(
            intrinsic_fitness=harmony_fitness,
            evolved_layers=self.evolved_layers,
            use_context=self.use_context,
            context_group=config.context_group,
            metric_weights=config.contextual_weights,
        )

        def melody_fitness(phrase: Phrase) -> float:
            layer = Layer(
                name=config.name,
                phrases=[phrase],
                instrument=self.get_instrument(config),
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

            # Log detailed fitness breakdown if using contextual fitness
            from fitness.contextual import ContextualFitness
            if isinstance(contextual_fitness, ContextualFitness):
                best_layer = Layer(
                    name=config.name,
                    phrases=[best_phrase],
                    instrument=self.get_instrument(config),
                    rhythm=rhythm,
                    is_drum=config.is_drum,
                )
                details = contextual_fitness.evaluate_detailed(best_layer)
                self._log_fitness_breakdown(config.name, details)

        # Store as theme for potential variation development
        if config.name not in self.themes:
            self.themes[config.name] = best_phrase

        return best_phrase

    def evolve_layer_chords(
        self, config: LayerConfig, verbose: bool = True
    ) -> ChordProgression:
        """Evolve chord progression for a chord layer."""
        if verbose:
            print(f"\n{'='*60}")
            print(f"Evolving chords for layer: {config.name}")
            print(
                f"Num chords: {config.num_chords}, Notes per chord: {config.notes_per_chord}"
            )
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
                allowed_types=config.allowed_chord_types,
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
                print(
                    f"  Gen {gen:3d}: Best fitness = {best_fitness:.4f}, chords = {chord_summary}"
                )

        best_progression = population[0].genome
        if verbose:
            print(f"✓ Final chord fitness: {best_fitness:.4f}")

        return best_progression

    def _get_sorted_configs(self) -> list[LayerConfig]:
        """Sort layer configs by evolution priority.

        Layers are sorted so that harmonic foundation (chords) comes first,
        then rhythmic foundation (drums), then harmonic bridge (bass),
        then melodic layers (melody, pad, lead).
        """
        return sorted(
            self.layer_configs,
            key=lambda c: LAYER_ROLE_PRIORITY.get(c.layer_role, 3)
        )

    def evolve_all_layers(self, verbose: bool = True) -> None:
        """Evolve all layers with proper ordering and inter-layer dependencies.

        Evolution order:
        1. Chord layers (harmonic foundation)
        2. Drum layers (rhythmic foundation)
        3. Bass layers (harmonic + rhythmic bridge)
        4. Melody/Pad/Lead layers (melodic content)

        After chord layers are evolved, harmonic context is established
        and used for subsequent melodic layer evolution.
        """
        # Sort configs by evolution priority
        sorted_configs = self._get_sorted_configs()

        if verbose:
            print(f"\n{'#'*60}")
            print("# EVOLVING LAYERS")
            print(f"# Order: {' → '.join(c.name for c in sorted_configs)}")
            print(f"{'#'*60}")

        for config in sorted_configs:
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
                    instrument=self.get_instrument(config),
                    rhythm=rhythm,
                    is_drum=True,
                    drum_sound=config.drum_sound,
                    layer_role=config.layer_role,
                    context_group=config.context_group,
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
                    instrument=self.get_instrument(config),
                    is_chord_layer=True,
                    chord_progression=chord_progression.chords,
                    gain=config.gain,
                    lpf=config.lpf,
                    octave_shift=config.octave_shift,
                    layer_role=config.layer_role,
                    context_group=config.context_group,
                )
                self.evolved_layers[config.name] = (chord_layer, rhythm)

                # Establish harmonic context for subsequent layers
                if self.use_harmonic_context and not self.harmonic_context:
                    self.harmonic_context = HarmonicContext(
                        chord_progression=chord_progression,
                        beats_per_chord=config.beats_per_bar,  # One chord per bar by default
                        scale_root=self.scale_root,
                        scale_type=self.scale_type,
                    )
                    if verbose:
                        print(f"   ↳ Harmonic context established from '{config.name}'")

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
                    instrument=self.get_instrument(config),
                    rhythm=rhythm,
                    layer_role=config.layer_role,
                    context_group=config.context_group,
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
                        instrument=self.get_instrument(config),
                        rhythm=rhythm,
                        gain=config.gain,
                        lpf=config.lpf,
                        hpf=config.hpf,
                        postgain=config.postgain,
                        room=config.room,
                        roomsize=config.roomsize,
                        delay=config.delay,
                        delaytime=config.delaytime,
                        delayfeedback=config.delayfeedback,
                        distort=config.distort,
                        pan=config.pan,
                        is_drum=True,
                        drum_sound=config.drum_sound,
                        layer_role=config.layer_role,
                        context_group=config.context_group,
                        bank=config.bank,
                        struct_pattern=config.struct_pattern,
                    )
                    layers.append(layer)

            elif config.is_chord_layer:
                # Chord layer: uses chord progression
                chord_progression = self.evolved_chords.get(config.name)
                if chord_progression:
                    # Use config scale if specified, otherwise use composition scale
                    layer_scale = (
                        config.strudel_scale
                        if config.strudel_scale
                        else composition_scale
                    )

                    layer = Layer(
                        name=config.name,
                        phrases=[],
                        instrument=self.get_instrument(config),
                        rhythm="",
                        scale=layer_scale,
                        octave_shift=config.octave_shift,
                        gain=config.gain,
                        lpf=config.lpf,
                        hpf=config.hpf,
                        postgain=config.postgain,
                        room=config.room,
                        roomsize=config.roomsize,
                        delay=config.delay,
                        delaytime=config.delaytime,
                        delayfeedback=config.delayfeedback,
                        distort=config.distort,
                        pan=config.pan,
                        attack=config.attack,
                        decay=config.decay,
                        sustain=config.sustain,
                        release=config.release,
                        is_chord_layer=True,
                        chord_progression=chord_progression.chords,
                        layer_role=config.layer_role,
                        context_group=config.context_group,
                        bank=config.bank,
                        use_note_notation=config.use_note_notation,
                        struct_pattern=config.struct_pattern,
                        slow_factor=config.slow_factor,
                        adsr=config.adsr,
                        lpq=config.lpq,
                    )
                    layers.append(layer)

            else:
                # Melodic layer: needs phrases
                phrase = self.evolved_phrases.get(config.name)
                if phrase:
                    # Use config scale if specified, otherwise use composition scale
                    layer_scale = (
                        config.strudel_scale
                        if config.strudel_scale
                        else composition_scale
                    )

                    layer = Layer(
                        name=config.name,
                        phrases=[phrase],
                        instrument=self.get_instrument(config),
                        rhythm=rhythm if rhythm else "",
                        scale=layer_scale,
                        octave_shift=config.octave_shift,
                        gain=config.gain,
                        lpf=config.lpf,
                        hpf=config.hpf,
                        postgain=config.postgain,
                        room=config.room,
                        roomsize=config.roomsize,
                        delay=config.delay,
                        delaytime=config.delaytime,
                        delayfeedback=config.delayfeedback,
                        distort=config.distort,
                        pan=config.pan,
                        attack=config.attack,
                        decay=config.decay,
                        sustain=config.sustain,
                        release=config.release,
                        use_scale_degrees=config.use_scale_degrees,
                        chord_mode=config.chord_mode,
                        base_octave=config.base_octave,
                        layer_role=config.layer_role,
                        context_group=config.context_group,
                        bank=config.bank,
                        use_note_notation=config.use_note_notation,
                        struct_pattern=config.struct_pattern,
                        slow_factor=config.slow_factor,
                        adsr=config.adsr,
                        lpq=config.lpq,
                    )
                    layers.append(layer)

        return Composition(layers=layers, bpm=bpm)

    def get_song_structure(
        self,
        bpm: int = 120,
        random_scale: bool = True,
        groups: dict[str, list[str]] = None,
        arrangement: list[tuple[int, str]] = None,
    ) -> SongStructure:
        """Get the final composition as a SongStructure with named constants.

        Args:
            bpm: Beats per minute
            random_scale: If True, uses a random scale for all layers
            groups: Dict mapping group_name -> [layer_names] to create LayerGroups
                    Example: {"drums": ["kick", "hihat", "snare"]}
            arrangement: List of (bars, group_or_layer_name) for the song structure
                    Example: [(4, "drums"), (4, "melody_group"), (4, "drums")]

        Returns:
            SongStructure with named layer constants, groups, and arrangement
        """
        # Generate random scale if needed
        if random_scale:
            composition_scale = Composition.random_scale()
        else:
            composition_scale = "c:major"

        song = SongStructure(bpm=bpm)

        # Build layers dict (name -> Layer)
        layers_by_name: dict[str, Layer] = {}
        for config in self.layer_configs:
            rhythm = self.evolved_rhythms.get(config.name)
            layer_scale = config.strudel_scale if config.strudel_scale else composition_scale

            if config.is_drum:
                if rhythm:
                    layer = Layer(
                        name=config.name,
                        phrases=[],
                        instrument=self.get_instrument(config),
                        rhythm=rhythm,
                        gain=config.gain,
                        lpf=config.lpf,
                        hpf=config.hpf,
                        postgain=config.postgain,
                        room=config.room,
                        roomsize=config.roomsize,
                        delay=config.delay,
                        delaytime=config.delaytime,
                        delayfeedback=config.delayfeedback,
                        distort=config.distort,
                        pan=config.pan,
                        is_drum=True,
                        drum_sound=config.drum_sound,
                        layer_role=config.layer_role,
                        context_group=config.context_group,
                        bank=config.bank,
                        struct_pattern=config.struct_pattern,
                    )
                    layers_by_name[config.name] = layer

            elif config.is_chord_layer:
                chord_progression = self.evolved_chords.get(config.name)
                if chord_progression:
                    layer = Layer(
                        name=config.name,
                        phrases=[],
                        instrument=self.get_instrument(config),
                        rhythm="",
                        scale=layer_scale,
                        octave_shift=config.octave_shift,
                        gain=config.gain,
                        lpf=config.lpf,
                        hpf=config.hpf,
                        postgain=config.postgain,
                        room=config.room,
                        roomsize=config.roomsize,
                        delay=config.delay,
                        delaytime=config.delaytime,
                        delayfeedback=config.delayfeedback,
                        distort=config.distort,
                        pan=config.pan,
                        attack=config.attack,
                        decay=config.decay,
                        sustain=config.sustain,
                        release=config.release,
                        is_chord_layer=True,
                        chord_progression=chord_progression.chords,
                        layer_role=config.layer_role,
                        context_group=config.context_group,
                        bank=config.bank,
                        use_note_notation=config.use_note_notation,
                        struct_pattern=config.struct_pattern,
                        slow_factor=config.slow_factor,
                        adsr=config.adsr,
                        lpq=config.lpq,
                    )
                    layers_by_name[config.name] = layer

            else:
                phrase = self.evolved_phrases.get(config.name)
                if phrase:
                    layer = Layer(
                        name=config.name,
                        phrases=[phrase],
                        instrument=self.get_instrument(config),
                        rhythm=rhythm if rhythm else "",
                        scale=layer_scale,
                        octave_shift=config.octave_shift,
                        gain=config.gain,
                        lpf=config.lpf,
                        hpf=config.hpf,
                        postgain=config.postgain,
                        room=config.room,
                        roomsize=config.roomsize,
                        delay=config.delay,
                        delaytime=config.delaytime,
                        delayfeedback=config.delayfeedback,
                        distort=config.distort,
                        pan=config.pan,
                        attack=config.attack,
                        decay=config.decay,
                        sustain=config.sustain,
                        release=config.release,
                        use_scale_degrees=config.use_scale_degrees,
                        chord_mode=config.chord_mode,
                        base_octave=config.base_octave,
                        layer_role=config.layer_role,
                        context_group=config.context_group,
                        bank=config.bank,
                        use_note_notation=config.use_note_notation,
                        struct_pattern=config.struct_pattern,
                        slow_factor=config.slow_factor,
                        adsr=config.adsr,
                        lpq=config.lpq,
                    )
                    layers_by_name[config.name] = layer

        # Add all layers to song structure
        for layer in layers_by_name.values():
            song.add_layer(layer)

        # Create layer groups if specified
        if groups:
            for group_name, layer_names in groups.items():
                group_layers = [layers_by_name[name] for name in layer_names if name in layers_by_name]
                if group_layers:
                    group = LayerGroup(name=group_name, layers=group_layers)
                    song.add_group(group)

        # Create arrangement if specified
        if arrangement:
            arr = Arrangement(name="main")
            for bars, content_name in arrangement:
                arr.add_section(bars, content_name)
            song.add_arrangement(arr)

        return song

    def _log_fitness_breakdown(self, layer_name: str, details: dict) -> None:
        """Log detailed fitness breakdown for a layer."""
        print(f"\n  ─── Fitness Breakdown for '{layer_name}' ───")
        print(f"  Intrinsic score:  {details['intrinsic_score']:.4f} (weight: 0.7)")
        print(f"  Context score:    {details['context_score']:.4f} (weight: 0.3)")
        print(f"  Final score:      {details['final_score']:.4f}")

        if details["metric_scores"]:
            print(f"\n  Context Metrics (averaged across context layers):")
            for metric, (score, weight) in details["metric_scores"].items():
                bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                print(f"    {metric:<15} {bar} {score:.3f} (w={weight:.2f})")

        if details["per_layer_scores"]:
            print(f"\n  Per-Layer Context Scores:")
            for context_layer_name, scores in details["per_layer_scores"].items():
                if scores:
                    score_strs = [f"{m}={s:.2f}" for m, s in scores.items()]
                    print(f"    vs {context_layer_name}: {', '.join(score_strs)}")

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

            print(f"\n{config.name.upper()} ({self.get_instrument(config)}):")

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
