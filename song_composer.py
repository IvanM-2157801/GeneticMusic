"""Song structure composer - Creates complete songs with intro, verse, chorus, outro.

This module extends the layered composer to support full song structures with
multiple sections that are each evolved separately using genetic algorithms.

Features:
- Pre-defined song forms (pop standard, electronic drop, ballad, etc.)
- Section templates with energy levels and layer assignments
- Transition types (fill, buildup, breakdown, cut)
- Dynamic envelopes per section
- Harmonic context integration
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from enum import Enum
import base64

from core.genetic import GeneticAlgorithm, Individual
from core.music import (
    Phrase,
    NoteName,
    Layer,
    Composition,
    HarmonicContext,
    DynamicEnvelope,
    FilterEnvelope,
    parse_scale_string,
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
    EnvelopeGenome,
    random_envelope,
    mutate_envelope,
    crossover_envelope,
)
from fitness.base import FitnessFunction
from fitness.chords import ChordFitnessFunction
from fitness.harmony import create_harmony_fitness, GENRE_CHORD_STRICTNESS
from fitness.development import VariationFitness, create_variation_fitness
from fitness.dynamics import DynamicEnvelopeFitness, FilterEnvelopeFitness


class SectionType(Enum):
    """Types of song sections."""

    INTRO = "intro"
    VERSE = "verse"
    PRECHORUS = "prechorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    BREAKDOWN = "breakdown"
    BUILDUP = "buildup"
    DROP = "drop"
    OUTRO = "outro"


class TransitionType(Enum):
    """Types of transitions between sections."""

    CUT = "cut"  # Hard transition, all layers change at once
    FILL = "fill"  # Drum fill at boundary
    BUILDUP = "buildup"  # Gradual density/filter increase
    BREAKDOWN = "breakdown"  # Remove layers gradually
    RISER = "riser"  # Ascending filter sweep
    IMPACT = "impact"  # Big hit on downbeat


class SongForm(Enum):
    """Pre-defined song structures."""

    POP_STANDARD = "pop_standard"
    VERSE_CHORUS = "verse_chorus"
    AABA = "aaba"
    ELECTRONIC_DROP = "electronic_drop"
    BALLAD = "ballad"
    ROCK = "rock"
    JAZZ_STANDARD = "jazz_standard"


@dataclass
class SectionTemplate:
    """Template for a song section with all properties."""

    section_type: SectionType
    bars: int = 4
    energy: float = 0.5  # 0.0 = low energy, 1.0 = high energy
    density_modifier: float = 1.0  # Affects rhythm density
    layers_active: list[str] = None  # Which instruments play (None = all)
    transition_in: TransitionType = TransitionType.CUT
    transition_out: TransitionType = TransitionType.CUT

    # Dynamics for this section
    gain_range: tuple[float, float] = (0.5, 0.7)  # (min, max) gain
    lpf_range: tuple[float, float] = (3000, 8000)  # (min, max) filter cutoff

    def __post_init__(self):
        if self.layers_active is None:
            self.layers_active = []  # Empty means all layers


# Pre-defined song forms
SONG_FORM_TEMPLATES = {
    SongForm.POP_STANDARD: [
        SectionTemplate(
            SectionType.INTRO,
            bars=4,
            energy=0.3,
            gain_range=(0.3, 0.5),
            lpf_range=(2000, 4000),
        ),
        SectionTemplate(
            SectionType.VERSE,
            bars=8,
            energy=0.5,
            gain_range=(0.5, 0.6),
            lpf_range=(3000, 6000),
        ),
        SectionTemplate(
            SectionType.PRECHORUS,
            bars=4,
            energy=0.7,
            gain_range=(0.6, 0.7),
            lpf_range=(5000, 8000),
            transition_out=TransitionType.BUILDUP,
        ),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=0.9,
            gain_range=(0.8, 1.0),
            lpf_range=(6000, 10000),
        ),
        SectionTemplate(
            SectionType.VERSE,
            bars=8,
            energy=0.6,
            gain_range=(0.5, 0.7),
            lpf_range=(3000, 6000),
        ),
        SectionTemplate(
            SectionType.PRECHORUS,
            bars=4,
            energy=0.7,
            gain_range=(0.6, 0.8),
            lpf_range=(5000, 8000),
            transition_out=TransitionType.BUILDUP,
        ),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=1.0,
            gain_range=(0.9, 1.0),
            lpf_range=(8000, 12000),
        ),
        SectionTemplate(
            SectionType.BRIDGE,
            bars=8,
            energy=0.4,
            gain_range=(0.4, 0.6),
            lpf_range=(2000, 5000),
            transition_in=TransitionType.BREAKDOWN,
        ),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=1.0,
            gain_range=(0.9, 1.0),
            lpf_range=(8000, 12000),
            transition_in=TransitionType.IMPACT,
        ),
        SectionTemplate(
            SectionType.OUTRO,
            bars=4,
            energy=0.3,
            gain_range=(0.5, 0.2),
            lpf_range=(4000, 1000),
        ),
    ],
    SongForm.VERSE_CHORUS: [
        SectionTemplate(SectionType.INTRO, bars=4, energy=0.3, gain_range=(0.3, 0.5)),
        SectionTemplate(SectionType.VERSE, bars=8, energy=0.5, gain_range=(0.5, 0.6)),
        SectionTemplate(SectionType.CHORUS, bars=8, energy=0.9, gain_range=(0.8, 1.0)),
        SectionTemplate(SectionType.VERSE, bars=8, energy=0.6, gain_range=(0.5, 0.7)),
        SectionTemplate(SectionType.CHORUS, bars=8, energy=1.0, gain_range=(0.9, 1.0)),
        SectionTemplate(SectionType.OUTRO, bars=4, energy=0.3, gain_range=(0.5, 0.2)),
    ],
    SongForm.AABA: [
        SectionTemplate(
            SectionType.VERSE, bars=8, energy=0.6, gain_range=(0.6, 0.7)
        ),  # A
        SectionTemplate(
            SectionType.VERSE, bars=8, energy=0.7, gain_range=(0.6, 0.8)
        ),  # A
        SectionTemplate(
            SectionType.BRIDGE, bars=8, energy=0.5, gain_range=(0.5, 0.6)
        ),  # B
        SectionTemplate(
            SectionType.VERSE, bars=8, energy=0.8, gain_range=(0.7, 0.9)
        ),  # A
    ],
    SongForm.ELECTRONIC_DROP: [
        SectionTemplate(
            SectionType.INTRO,
            bars=8,
            energy=0.2,
            gain_range=(0.2, 0.4),
            lpf_range=(1000, 3000),
        ),
        SectionTemplate(
            SectionType.BUILDUP,
            bars=8,
            energy=0.6,
            gain_range=(0.4, 0.8),
            lpf_range=(2000, 8000),
            transition_out=TransitionType.RISER,
        ),
        SectionTemplate(
            SectionType.DROP,
            bars=16,
            energy=1.0,
            gain_range=(0.9, 1.0),
            lpf_range=(8000, 12000),
            transition_in=TransitionType.IMPACT,
        ),
        SectionTemplate(
            SectionType.BREAKDOWN,
            bars=8,
            energy=0.3,
            gain_range=(0.3, 0.5),
            lpf_range=(2000, 4000),
        ),
        SectionTemplate(
            SectionType.BUILDUP,
            bars=8,
            energy=0.7,
            gain_range=(0.5, 0.9),
            lpf_range=(3000, 10000),
            transition_out=TransitionType.RISER,
        ),
        SectionTemplate(
            SectionType.DROP,
            bars=16,
            energy=1.0,
            gain_range=(0.9, 1.0),
            lpf_range=(8000, 12000),
            transition_in=TransitionType.IMPACT,
        ),
        SectionTemplate(
            SectionType.OUTRO,
            bars=8,
            energy=0.2,
            gain_range=(0.5, 0.1),
            lpf_range=(6000, 1000),
        ),
    ],
    SongForm.BALLAD: [
        SectionTemplate(
            SectionType.INTRO,
            bars=4,
            energy=0.2,
            gain_range=(0.2, 0.3),
            lpf_range=(2000, 4000),
        ),
        SectionTemplate(
            SectionType.VERSE,
            bars=8,
            energy=0.4,
            gain_range=(0.3, 0.5),
            lpf_range=(3000, 5000),
        ),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=0.6,
            gain_range=(0.5, 0.7),
            lpf_range=(4000, 7000),
        ),
        SectionTemplate(
            SectionType.VERSE,
            bars=8,
            energy=0.5,
            gain_range=(0.4, 0.6),
            lpf_range=(3000, 6000),
        ),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=0.7,
            gain_range=(0.6, 0.8),
            lpf_range=(5000, 8000),
        ),
        SectionTemplate(
            SectionType.BRIDGE,
            bars=8,
            energy=0.8,
            gain_range=(0.7, 0.9),
            lpf_range=(6000, 10000),
        ),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=0.7,
            gain_range=(0.6, 0.8),
            lpf_range=(5000, 8000),
        ),
        SectionTemplate(
            SectionType.OUTRO,
            bars=8,
            energy=0.2,
            gain_range=(0.4, 0.1),
            lpf_range=(4000, 2000),
        ),
    ],
    SongForm.ROCK: [
        SectionTemplate(
            SectionType.INTRO,
            bars=4,
            energy=0.7,
            gain_range=(0.6, 0.8),
            transition_in=TransitionType.IMPACT,
        ),
        SectionTemplate(SectionType.VERSE, bars=8, energy=0.6, gain_range=(0.6, 0.7)),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=0.9,
            gain_range=(0.8, 1.0),
            transition_in=TransitionType.FILL,
        ),
        SectionTemplate(SectionType.VERSE, bars=8, energy=0.7, gain_range=(0.6, 0.8)),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=1.0,
            gain_range=(0.9, 1.0),
            transition_in=TransitionType.FILL,
        ),
        SectionTemplate(
            SectionType.BRIDGE,
            bars=8,
            energy=0.5,
            gain_range=(0.5, 0.7),
            transition_in=TransitionType.BREAKDOWN,
        ),
        SectionTemplate(
            SectionType.CHORUS,
            bars=8,
            energy=1.0,
            gain_range=(0.9, 1.0),
            transition_in=TransitionType.FILL,
        ),
        SectionTemplate(SectionType.OUTRO, bars=8, energy=0.8, gain_range=(0.8, 0.5)),
    ],
    SongForm.JAZZ_STANDARD: [
        SectionTemplate(SectionType.INTRO, bars=4, energy=0.4, gain_range=(0.4, 0.5)),
        SectionTemplate(
            SectionType.VERSE, bars=8, energy=0.5, gain_range=(0.5, 0.6)
        ),  # Head A
        SectionTemplate(
            SectionType.VERSE, bars=8, energy=0.6, gain_range=(0.5, 0.7)
        ),  # Head A
        SectionTemplate(
            SectionType.BRIDGE, bars=8, energy=0.6, gain_range=(0.6, 0.7)
        ),  # Head B
        SectionTemplate(
            SectionType.VERSE, bars=8, energy=0.7, gain_range=(0.6, 0.8)
        ),  # Head A
        # Solo sections would go here
        SectionTemplate(
            SectionType.VERSE, bars=8, energy=0.6, gain_range=(0.5, 0.7)
        ),  # Out Head
        SectionTemplate(SectionType.OUTRO, bars=4, energy=0.4, gain_range=(0.5, 0.3)),
    ],
}


# Default dynamics for each section type
SECTION_DYNAMICS = {
    SectionType.INTRO: {"gain": (0.3, 0.5), "lpf": (2000, 4000)},
    SectionType.VERSE: {"gain": (0.5, 0.7), "lpf": (3000, 6000)},
    SectionType.PRECHORUS: {"gain": (0.6, 0.8), "lpf": (5000, 8000)},
    SectionType.CHORUS: {"gain": (0.8, 1.0), "lpf": (6000, 10000)},
    SectionType.BRIDGE: {"gain": (0.4, 0.6), "lpf": (2000, 5000)},
    SectionType.BREAKDOWN: {"gain": (0.3, 0.5), "lpf": (2000, 4000)},
    SectionType.BUILDUP: {"gain": (0.4, 0.8), "lpf": (2000, 8000)},
    SectionType.DROP: {"gain": (0.9, 1.0), "lpf": (8000, 12000)},
    SectionType.OUTRO: {"gain": (0.5, 0.2), "lpf": (4000, 1000)},
}


@dataclass
class SectionConfig:
    """Configuration for a song section (legacy compatibility)."""

    section_type: SectionType
    bars: int = 4  # Length of this section in bars
    energy_level: float = 0.5  # 0.0 = low energy, 1.0 = high energy

    # Optional overrides for fitness functions
    rhythm_fitness_modifier: float = 1.0  # Multiplier for rhythm density
    melody_fitness_modifier: float = 1.0  # Multiplier for melody complexity
    chord_fitness_modifier: float = 1.0  # Multiplier for chord complexity

    # Dynamics
    gain_range: tuple[float, float] = None
    lpf_range: tuple[float, float] = None
    transition_in: TransitionType = TransitionType.CUT
    transition_out: TransitionType = TransitionType.CUT

    def __post_init__(self):
        # Set defaults from section type if not specified
        if self.gain_range is None:
            defaults = SECTION_DYNAMICS.get(self.section_type, {"gain": (0.5, 0.7)})
            self.gain_range = defaults["gain"]
        if self.lpf_range is None:
            defaults = SECTION_DYNAMICS.get(self.section_type, {"lpf": (3000, 6000)})
            self.lpf_range = defaults["lpf"]

    @classmethod
    def from_template(cls, template: SectionTemplate) -> "SectionConfig":
        """Create SectionConfig from a SectionTemplate."""
        return cls(
            section_type=template.section_type,
            bars=template.bars,
            energy_level=template.energy,
            rhythm_fitness_modifier=template.density_modifier,
            gain_range=template.gain_range,
            lpf_range=template.lpf_range,
            transition_in=template.transition_in,
            transition_out=template.transition_out,
        )


@dataclass
class InstrumentConfig:
    """Configuration for an instrument across the song."""

    name: str
    instrument: str
    beats_per_bar: int = 4
    max_subdivision: int = 2
    octave_range: tuple[int, int] = (4, 5)
    scale: str | list[NoteName] = (
        None  # Scale string (e.g., "d:minor") or list of NoteName
    )
    rhythm_fitness_fn: Callable[[str], float] = None
    melody_fitness_fn: FitnessFunction = None
    octave_shift: int = 0
    gain: float = 0.5
    lpf: int = 4000
    use_scale_degrees: bool = True

    # Drum parameters
    is_drum: bool = False
    drum_sound: str = ""

    # Chord parameters
    is_chord_layer: bool = False
    notes_per_chord: int = 3
    allowed_chord_types: list[str] = None
    chord_fitness_fn: ChordFitnessFunction = None

    # Section behavior
    play_in_sections: list[SectionType] = (
        None  # Which sections this instrument plays in
    )

    # Inter-layer fitness (new features)
    use_inter_layer_fitness: bool = True  # Enable contextual fitness
    inter_layer_weight: float = 0.3  # Weight for inter-layer fitness (0.0-1.0)
    layer_role: str = "melody"  # Role: chords, drums, bass, melody, pad, lead

    # Harmonic context (new features)
    use_harmonic_context: bool = False  # Enable chord-aware melody evolution
    genre: str = "pop"  # Genre for chord-melody strictness
    harmony_weight: float = 0.4  # Weight for harmonic fitness

    # Theme variation settings
    use_variations: bool = (
        False  # If True, later sections evolve as variations of first
    )
    variation_similarity: float = 0.6  # Target similarity to theme (0.0-1.0)
    variation_weight: float = 0.5  # Weight for variation fitness vs intrinsic

    # Dynamic envelope settings
    evolve_dynamics: bool = False  # Evolve gain/filter envelopes per section
    dynamics_generations: int = 15  # Generations for envelope evolution

    # Parsed scale data (set in __post_init__)
    _scale_notes: list[NoteName] = field(default=None, repr=False)
    _scale_string: str = field(default="", repr=False)

    def __post_init__(self):
        if self.scale is None:
            # Default to C major
            self._scale_string = "c:major"
            self._scale_notes = [
                NoteName.C,
                NoteName.D,
                NoteName.E,
                NoteName.F,
                NoteName.G,
                NoteName.A,
                NoteName.B,
            ]
        elif isinstance(self.scale, str):
            # Parse scale string like "d:minor"
            root, mode, notes = parse_scale_string(self.scale)
            self._scale_string = self.scale
            self._scale_notes = notes
        else:
            # Legacy: list of NoteName provided directly
            self._scale_notes = self.scale
            self._scale_string = ""  # Will use composition's random scale

        if self.play_in_sections is None:
            # Default: play in all sections
            self.play_in_sections = list(SectionType)

    def get_scale_notes(self) -> list[NoteName]:
        """Get the list of NoteName values for this instrument's scale."""
        return self._scale_notes

    def get_scale_string(self) -> str:
        """Get the scale string for Strudel output (e.g., 'd:minor')."""
        return self._scale_string


@dataclass
class EvolvedSection:
    """Stores evolved genomes for a section."""

    section_type: SectionType
    bars: int
    rhythms: dict[str, str] = field(default_factory=dict)  # instrument_name -> rhythm
    phrases: dict[str, Phrase] = field(
        default_factory=dict
    )  # instrument_name -> phrase
    chords: dict[str, ChordProgression] = field(
        default_factory=dict
    )  # instrument_name -> chords
    dynamic_envelopes: dict[str, DynamicEnvelope] = field(
        default_factory=dict
    )  # instrument_name -> gain envelope
    filter_envelopes: dict[str, FilterEnvelope] = field(
        default_factory=dict
    )  # instrument_name -> lpf envelope


class SongComposer:
    """Composer that creates complete songs with multiple sections.

    Each section (intro, verse, chorus, etc.) is evolved separately,
    allowing for variation while maintaining coherence within sections.
    """

    def __init__(
        self,
        population_size: int = 30,
        mutation_rate: float = 0.2,
        elitism_count: int = 5,
        rhythm_generations: int = 20,
        melody_generations: int = 25,
        chord_generations: int = 20,
        # Fitness threshold settings
        fitness_threshold: float = None,  # If set, stop when best fitness >= threshold
        max_generations: int = 100,  # Maximum generations if using threshold
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.rhythm_generations = rhythm_generations
        self.melody_generations = melody_generations
        self.chord_generations = chord_generations
        self.fitness_threshold = fitness_threshold
        self.max_generations = max_generations

        self.instruments: list[InstrumentConfig] = []
        self.sections: list[SectionConfig] = []
        self.song_structure: list[SectionType] = []  # Order of sections in the song

        self.evolved_sections: dict[SectionType, EvolvedSection] = {}
        self.composition_scale: str = ""

        # Inter-layer fitness tracking (per section)
        self._current_section_layers: dict[str, tuple[Layer, str]] = {}
        self._current_section_chords: ChordProgression = None
        self._harmonic_context: HarmonicContext = None

        # Theme tracking for variations (instrument_name -> first evolved phrase)
        self._theme_phrases: dict[str, Phrase] = {}
        self._theme_rhythms: dict[str, str] = {}

    def add_instrument(self, config: InstrumentConfig) -> None:
        """Add an instrument to the song."""
        self.instruments.append(config)

    def add_section(self, config: SectionConfig) -> None:
        """Add a section type to the song."""
        self.sections.append(config)

    def set_song_structure(self, structure: list[SectionType]) -> None:
        """Set the order of sections in the song.

        Example: [INTRO, VERSE, CHORUS, VERSE, CHORUS, BRIDGE, CHORUS, OUTRO]
        """
        self.song_structure = structure

    def use_song_form(self, form: SongForm) -> None:
        """Configure the song using a pre-defined song form.

        This sets up the sections and song structure based on the chosen form.

        Args:
            form: One of the pre-defined SongForm values
        """
        templates = SONG_FORM_TEMPLATES.get(form)
        if not templates:
            raise ValueError(f"Unknown song form: {form}")

        # Clear existing sections
        self.sections = []
        self.song_structure = []

        # Add sections from templates
        for template in templates:
            config = SectionConfig.from_template(template)
            self.sections.append(config)
            self.song_structure.append(template.section_type)

    def get_section_dynamics(
        self, section_type: SectionType
    ) -> tuple[DynamicEnvelope, FilterEnvelope]:
        """Get dynamic and filter envelopes for a section type.

        Args:
            section_type: The type of section

        Returns:
            Tuple of (DynamicEnvelope, FilterEnvelope) for the section
        """
        # Find the section config
        config = self._get_section_config(section_type)

        # Create envelopes based on section dynamics
        gain_start, gain_end = config.gain_range
        lpf_start, lpf_end = config.lpf_range

        # Simple linear envelopes
        dynamic_env = DynamicEnvelope(
            points=[(0.0, gain_start), (1.0, gain_end)], envelope_type="linear"
        )
        filter_env = FilterEnvelope(
            points=[(0.0, lpf_start), (1.0, lpf_end)], envelope_type="linear"
        )

        return dynamic_env, filter_env

    def _get_section_config(self, section_type: SectionType) -> SectionConfig:
        """Get config for a section type."""
        for section in self.sections:
            if section.section_type == section_type:
                return section
        # Default config if not found
        return SectionConfig(section_type=section_type)

    def _evolve_rhythm(
        self, instrument: InstrumentConfig, section: SectionConfig, verbose: bool = True
    ) -> tuple[str, float]:
        """Evolve rhythm for an instrument in a section. Returns (rhythm, fitness)."""
        total_beats = section.bars * instrument.beats_per_bar

        # Adjust max subdivision based on section energy
        effective_max_sub = min(
            instrument.max_subdivision,
            max(1, int(instrument.max_subdivision * (0.5 + section.energy_level))),
        )

        ga = GeneticAlgorithm[str](
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            elitism_count=self.elitism_count,
        )

        population = [
            Individual(random_rhythm(total_beats, effective_max_sub))
            for _ in range(self.population_size)
        ]

        # Fitness with section modifier
        def rhythm_fitness(rhythm: str) -> float:
            if instrument.rhythm_fitness_fn:
                base_score = instrument.rhythm_fitness_fn(rhythm)
                # Adjust based on section energy
                return base_score * section.rhythm_fitness_modifier
            return 0.5

        # Use threshold-based or fixed generations
        max_gens = (
            self.max_generations if self.fitness_threshold else self.rhythm_generations
        )

        for gen in range(max_gens):
            population = ga.evolve(
                population=population,
                fitness_fn=rhythm_fitness,
                mutate_fn=lambda r: mutate_rhythm(
                    r, self.mutation_rate, effective_max_sub
                ),
                crossover_fn=crossover_rhythm,
            )

            # Check threshold
            if (
                self.fitness_threshold
                and population[0].fitness >= self.fitness_threshold
            ):
                if verbose:
                    print(
                        f"       ✓ Reached threshold {self.fitness_threshold:.2f} at gen {gen+1} (fitness: {population[0].fitness:.3f})"
                    )
                break

        return population[0].genome, population[0].fitness

    def _evolve_melody(
        self,
        instrument: InstrumentConfig,
        section: SectionConfig,
        rhythm: str,
        verbose: bool = True,
    ) -> tuple[Phrase, float]:
        """Evolve melody for an instrument in a section. Returns (phrase, fitness)."""
        ga = GeneticAlgorithm[Phrase](
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            elitism_count=self.elitism_count,
        )

        population = [
            Individual(
                rhythm_to_phrase(
                    rhythm,
                    scale=instrument.get_scale_notes(),
                    octave_range=instrument.octave_range,
                )
            )
            for _ in range(self.population_size)
        ]

        # Build the effective fitness function
        base_fitness_fn = instrument.melody_fitness_fn

        # Wrap with harmonic context if enabled and we have chords
        if instrument.use_harmonic_context and self._harmonic_context:
            from fitness.harmony import create_harmony_fitness

            base_fitness_fn = create_harmony_fitness(
                intrinsic_fitness=base_fitness_fn,
                harmonic_context=self._harmonic_context,
                genre=instrument.genre,
                harmony_weight=instrument.harmony_weight,
            )

        # Wrap with contextual (inter-layer) fitness if enabled
        if instrument.use_inter_layer_fitness and self._current_section_layers:
            from fitness.contextual import create_contextual_fitness

            base_fitness_fn = create_contextual_fitness(
                intrinsic_fitness=base_fitness_fn,
                evolved_layers=self._current_section_layers,
                use_context=True,
                intrinsic_weight=1.0 - instrument.inter_layer_weight,
                context_weight=instrument.inter_layer_weight,
            )

        # Wrap with variation fitness if enabled and we have a theme
        theme_phrase = self._theme_phrases.get(instrument.name)
        if instrument.use_variations and theme_phrase:
            base_fitness_fn = create_variation_fitness(
                theme=theme_phrase,
                intrinsic_fitness=base_fitness_fn,
                similarity_target=instrument.variation_similarity,
            )
            if verbose:
                print(f"       (evolving as variation of theme)")

        def melody_fitness(phrase: Phrase) -> float:
            if base_fitness_fn:
                layer = Layer(
                    name=instrument.name,
                    phrases=[phrase],
                    instrument=instrument.instrument,
                    rhythm=rhythm,
                )
                base_score = base_fitness_fn.evaluate(layer)
                return base_score * section.melody_fitness_modifier
            return 0.5

        def melody_mutate(phrase: Phrase) -> Phrase:
            mutated = mutate_phrase(phrase, mutation_rate=self.mutation_rate)
            return phrase_with_rhythm(mutated, rhythm)

        def melody_crossover(p1: Phrase, p2: Phrase) -> Phrase:
            child = crossover_phrase(p1, p2)
            return phrase_with_rhythm(child, rhythm)

        # Use threshold-based or fixed generations
        max_gens = (
            self.max_generations if self.fitness_threshold else self.melody_generations
        )

        for gen in range(max_gens):
            population = ga.evolve(
                population=population,
                fitness_fn=melody_fitness,
                mutate_fn=melody_mutate,
                crossover_fn=melody_crossover,
            )

            # Check threshold
            if (
                self.fitness_threshold
                and population[0].fitness >= self.fitness_threshold
            ):
                if verbose:
                    print(
                        f"       ✓ Reached threshold {self.fitness_threshold:.2f} at gen {gen+1} (fitness: {population[0].fitness:.3f})"
                    )
                break

        return population[0].genome, population[0].fitness

    def _evolve_chords(
        self, instrument: InstrumentConfig, section: SectionConfig, verbose: bool = True
    ) -> tuple[ChordProgression, float]:
        """Evolve chord progression for a section. Returns (progression, fitness)."""
        # beats_per_bar determines chords per bar (e.g., 1 = whole note chords, 4 = quarter note chords)
        num_chords = section.bars * instrument.beats_per_bar

        ga = GeneticAlgorithm[ChordProgression](
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            elitism_count=self.elitism_count,
        )

        population = [
            Individual(
                random_chord_progression(
                    num_chords=num_chords,
                    notes_per_chord=instrument.notes_per_chord,
                    allowed_types=instrument.allowed_chord_types,
                )
            )
            for _ in range(self.population_size)
        ]

        def chord_fitness(prog: ChordProgression) -> float:
            if instrument.chord_fitness_fn:
                base_score = instrument.chord_fitness_fn.evaluate(prog)
                return base_score * section.chord_fitness_modifier
            return 0.5

        def chord_mutate(prog: ChordProgression) -> ChordProgression:
            return mutate_chord_progression(
                prog,
                mutation_rate=self.mutation_rate,
                notes_per_chord=instrument.notes_per_chord,
            )

        # Use threshold-based or fixed generations
        max_gens = (
            self.max_generations if self.fitness_threshold else self.chord_generations
        )

        for gen in range(max_gens):
            population = ga.evolve(
                population=population,
                fitness_fn=chord_fitness,
                mutate_fn=chord_mutate,
                crossover_fn=crossover_chord_progression,
            )

            # Check threshold
            if (
                self.fitness_threshold
                and population[0].fitness >= self.fitness_threshold
            ):
                if verbose:
                    print(
                        f"       ✓ Reached threshold {self.fitness_threshold:.2f} at gen {gen+1} (fitness: {population[0].fitness:.3f})"
                    )
                break

        return population[0].genome, population[0].fitness

    def _evolve_dynamics(
        self, instrument: InstrumentConfig, section: SectionConfig, verbose: bool = True
    ) -> tuple[DynamicEnvelope, FilterEnvelope, float]:
        """Evolve gain and filter envelopes for an instrument in a section."""
        # Get expected ranges from section type
        section_defaults = SECTION_DYNAMICS.get(
            section.section_type, {"gain": (0.3, 0.7), "lpf": (2000, 8000)}
        )
        gain_range = section.gain_range or section_defaults["gain"]
        lpf_range = section.lpf_range or section_defaults["lpf"]

        ga = GeneticAlgorithm[EnvelopeGenome](
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            elitism_count=self.elitism_count,
        )

        # Create initial population of envelope pairs
        population = [
            Individual(
                random_envelope(
                    num_points=3,
                    value_range=gain_range,
                )
            )
            for _ in range(self.population_size)
        ]

        # Create fitness evaluator for this section
        dynamic_fitness_fn = DynamicEnvelopeFitness(section.section_type)

        def envelope_fitness(env: EnvelopeGenome) -> float:
            # Convert genome to DynamicEnvelope
            dyn_env = DynamicEnvelope(points=env.points)
            return dynamic_fitness_fn.evaluate(dyn_env)

        for gen in range(instrument.dynamics_generations):
            population = ga.evolve(
                population=population,
                fitness_fn=envelope_fitness,
                mutate_fn=lambda e: mutate_envelope(e, self.mutation_rate),
                crossover_fn=crossover_envelope,
            )

        # Best gain envelope
        best_gain = population[0].genome
        gain_fitness = population[0].fitness

        # Now evolve filter envelope
        filter_population = [
            Individual(
                random_envelope(
                    num_points=3,
                    value_range=lpf_range,
                )
            )
            for _ in range(self.population_size)
        ]

        filter_fitness_fn = FilterEnvelopeFitness(section.section_type)

        def filter_envelope_fitness(env: EnvelopeGenome) -> float:
            filt_env = FilterEnvelope(points=env.points)
            return filter_fitness_fn.evaluate(filt_env)

        for gen in range(instrument.dynamics_generations):
            filter_population = ga.evolve(
                population=filter_population,
                fitness_fn=filter_envelope_fitness,
                mutate_fn=lambda e: mutate_envelope(e, self.mutation_rate),
                crossover_fn=crossover_envelope,
            )

        best_filter = filter_population[0].genome
        filter_fitness = filter_population[0].fitness

        # Convert to actual envelope objects
        dyn_envelope = DynamicEnvelope(points=best_gain.points)
        filt_envelope = FilterEnvelope(points=best_filter.points)

        combined_fitness = (gain_fitness + filter_fitness) / 2

        if verbose:
            print(f"     Dynamics evolved (fitness: {combined_fitness:.3f})")

        return dyn_envelope, filt_envelope, combined_fitness

    def _get_sorted_instruments(self) -> list[InstrumentConfig]:
        """Sort instruments by layer role priority for proper evolution order.

        Chords evolve first (provide harmonic context), then drums, bass, melody, pad, lead.
        """
        LAYER_ROLE_PRIORITY = {
            "chords": 0,
            "drums": 1,
            "bass": 2,
            "melody": 3,
            "pad": 4,
            "lead": 5,
        }
        return sorted(
            self.instruments, key=lambda i: LAYER_ROLE_PRIORITY.get(i.layer_role, 10)
        )

    def evolve_section(
        self, section_type: SectionType, verbose: bool = True
    ) -> EvolvedSection:
        """Evolve all instruments for a single section."""
        section_config = self._get_section_config(section_type)

        if verbose:
            print(f"\n{'='*60}")
            print(
                f"🎵 Evolving {section_type.value.upper()} section ({section_config.bars} bars)"
            )
            print(f"   Energy level: {section_config.energy_level:.1f}")
            print(f"{'='*60}")

        evolved = EvolvedSection(
            section_type=section_type,
            bars=section_config.bars,
        )

        # Reset inter-layer tracking for this section
        self._current_section_layers = {}
        self._current_section_chords = None
        self._harmonic_context = None

        # Sort instruments by role priority (chords first, then drums, bass, melody, etc.)
        sorted_instruments = self._get_sorted_instruments()

        for instrument in sorted_instruments:
            # Skip if instrument doesn't play in this section
            if section_type not in instrument.play_in_sections:
                if verbose:
                    print(f"  ⏸️  {instrument.name}: skipped (not in this section)")
                continue

            if verbose:
                print(f"\n  🎸 Evolving {instrument.name}...")

            if instrument.is_drum:
                # Drums only need rhythm
                rhythm, fitness = self._evolve_rhythm(
                    instrument, section_config, verbose
                )
                evolved.rhythms[instrument.name] = rhythm
                if verbose:
                    print(f"     Rhythm: {rhythm} (fitness: {fitness:.3f})")

                # Track for inter-layer fitness (drums can inform other layers)
                drum_layer = Layer(
                    name=instrument.name,
                    phrases=[],
                    instrument=instrument.instrument,
                    rhythm=rhythm,
                    is_drum=True,
                )
                self._current_section_layers[instrument.name] = (drum_layer, rhythm)

            elif instrument.is_chord_layer:
                # Chord layer - evolve first to provide harmonic context
                chords, fitness = self._evolve_chords(
                    instrument, section_config, verbose
                )
                evolved.chords[instrument.name] = chords
                self._current_section_chords = chords

                # Set up harmonic context for melodic layers
                scale_parts = self.composition_scale.split(":")
                self._harmonic_context = HarmonicContext(
                    chord_progression=chords,
                    beats_per_chord=4,  # One chord per bar typically
                    scale_root=scale_parts[0] if scale_parts else "c",
                    scale_type=scale_parts[1] if len(scale_parts) > 1 else "major",
                )

                if verbose:
                    chord_summary = " → ".join(
                        f"deg{c.root_degree}" for c in chords.chords
                    )
                    print(f"     Chords: {chord_summary} (fitness: {fitness:.3f})")

            else:
                # Melodic instrument
                rhythm, r_fitness = self._evolve_rhythm(
                    instrument, section_config, verbose
                )
                evolved.rhythms[instrument.name] = rhythm

                phrase, m_fitness = self._evolve_melody(
                    instrument, section_config, rhythm, verbose
                )
                evolved.phrases[instrument.name] = phrase

                # Store as theme if this is the first occurrence (for variations)
                if (
                    instrument.use_variations
                    and instrument.name not in self._theme_phrases
                ):
                    self._theme_phrases[instrument.name] = phrase
                    self._theme_rhythms[instrument.name] = rhythm
                    if verbose:
                        print(f"     (stored as theme for future variations)")

                if verbose:
                    print(f"     Rhythm: {rhythm} (fitness: {r_fitness:.3f})")
                    print(f"     Melody fitness: {m_fitness:.3f}")

                # Track evolved layer for inter-layer fitness
                layer = Layer(
                    name=instrument.name,
                    phrases=[phrase],
                    instrument=instrument.instrument,
                    rhythm=rhythm,
                )
                self._current_section_layers[instrument.name] = (layer, rhythm)

                # Evolve dynamics if enabled
                if instrument.evolve_dynamics:
                    dyn_env, filt_env, d_fitness = self._evolve_dynamics(
                        instrument, section_config, verbose
                    )
                    evolved.dynamic_envelopes[instrument.name] = dyn_env
                    evolved.filter_envelopes[instrument.name] = filt_env

        return evolved

    def evolve_song(self, verbose: bool = True) -> None:
        """Evolve all unique sections in the song."""
        # Get unique section types
        unique_sections = set(self.song_structure)

        if verbose:
            print(f"\n{'#'*60}")
            print(f"# EVOLVING COMPLETE SONG")
            print(f"# Structure: {' → '.join(s.value for s in self.song_structure)}")
            print(f"# Unique sections to evolve: {len(unique_sections)}")
            print(f"{'#'*60}")

        # Determine the song scale - use first instrument's scale if defined, otherwise random
        self.composition_scale = ""
        for instrument in self.instruments:
            if instrument.get_scale_string():
                self.composition_scale = instrument.get_scale_string()
                break
        if not self.composition_scale:
            self.composition_scale = Composition.random_scale()
        if verbose:
            print(f"\n🎼 Song scale: {self.composition_scale}")

        # Evolve each unique section
        for section_type in unique_sections:
            evolved = self.evolve_section(section_type, verbose)
            self.evolved_sections[section_type] = evolved

    def _section_to_strudel(
        self, section: EvolvedSection, section_idx: int
    ) -> list[str]:
        """Convert an evolved section to Strudel layer strings."""
        layers_strudel = []

        for instrument in self.instruments:
            if section.section_type not in instrument.play_in_sections:
                continue

            if instrument.is_drum:
                rhythm = section.rhythms.get(instrument.name, "")
                if rhythm:
                    # Build drum pattern
                    beat_groups = []
                    for beat_char in rhythm:
                        subdivisions = int(beat_char)
                        if subdivisions == 0:
                            beat_groups.append("~")
                        elif subdivisions == 1:
                            beat_groups.append(instrument.drum_sound)
                        else:
                            beat_groups.append(
                                "["
                                + " ".join([instrument.drum_sound] * subdivisions)
                                + "]"
                            )
                    pattern = " ".join(beat_groups)
                    layers_strudel.append(f'sound("{pattern}").gain({instrument.gain})')

            elif instrument.is_chord_layer:
                chords = section.chords.get(instrument.name)
                if chords:
                    # Build chord pattern
                    chord_strs = []
                    for chord in chords.chords:
                        degrees = []
                        for interval in chord.intervals:
                            if interval == 0:
                                degree = chord.root_degree
                            elif interval in (3, 4):
                                degree = (chord.root_degree + 2) % 7
                            elif interval in (7, 8):
                                degree = (chord.root_degree + 4) % 7
                            elif interval in (10, 11):
                                degree = (chord.root_degree + 6) % 7
                            else:
                                degree = (chord.root_degree + interval // 2) % 7
                            degrees.append(str(degree))
                        chord_strs.append("[" + ", ".join(degrees) + "]")
                    pattern = " ".join(chord_strs)

                    layer_str = f'n("{pattern}")'
                    if instrument.octave_shift:
                        layer_str += f".sub({abs(instrument.octave_shift)})"
                    layer_str += f'.scale("{self.composition_scale}")'
                    layer_str += f'.s("{instrument.instrument}")'
                    layer_str += f".gain({instrument.gain})"
                    if instrument.lpf:
                        layer_str += f".lpf({instrument.lpf})"
                    layers_strudel.append(layer_str)

            else:
                # Melodic instrument
                rhythm = section.rhythms.get(instrument.name, "")
                phrase = section.phrases.get(instrument.name)

                if rhythm and phrase:
                    pattern = phrase.to_strudel_with_rhythm(
                        rhythm, instrument.use_scale_degrees
                    )

                    layer_str = f'n("{pattern}")'
                    if instrument.octave_shift:
                        layer_str += f".sub({abs(instrument.octave_shift)}))"
                    layer_str += f'.scale("{self.composition_scale}")'
                    layer_str += f'.s("{instrument.instrument}")'
                    layer_str += f".gain({instrument.gain})"
                    if instrument.lpf:
                        layer_str += f".lpf({instrument.lpf})"
                    layers_strudel.append(layer_str)

        return layers_strudel

    def get_strudel_code(self, bpm: int = 120) -> str:
        """Generate Strudel code for the complete song.

        Uses Strudel's arrangement features to sequence sections.
        """
        lines = [f"// Complete Song - BPM: {bpm}"]
        lines.append(
            f"// Structure: {' → '.join(s.value for s in self.song_structure)}"
        )
        lines.append(f"// Scale: {self.composition_scale}")
        lines.append("")
        lines.append(f"setcpm({bpm / 4})")
        lines.append("")

        # Calculate total bars for timing
        section_bars = {}
        for section in self.sections:
            section_bars[section.section_type] = section.bars

        # Generate each section's code with timing
        current_bar = 0
        section_instances = []  # Track (start_bar, end_bar, section_type)

        for section_type in self.song_structure:
            bars = section_bars.get(section_type, 4)
            section_instances.append((current_bar, current_bar + bars, section_type))
            current_bar += bars

        total_bars = current_bar

        # For each instrument, create a pattern that sequences through sections
        for instrument in self.instruments:
            patterns_by_section = {}

            # Collect patterns for each section type this instrument plays in
            for section_type, evolved in self.evolved_sections.items():
                if section_type not in instrument.play_in_sections:
                    patterns_by_section[section_type] = "~"  # Rest
                    continue

                if instrument.is_drum:
                    rhythm = evolved.rhythms.get(instrument.name, "")
                    if rhythm:
                        beat_groups = []
                        for beat_char in rhythm:
                            subdivisions = int(beat_char)
                            if subdivisions == 0:
                                beat_groups.append("~")
                            elif subdivisions == 1:
                                beat_groups.append(instrument.drum_sound)
                            else:
                                beat_groups.append(
                                    "["
                                    + " ".join([instrument.drum_sound] * subdivisions)
                                    + "]"
                                )
                        patterns_by_section[section_type] = " ".join(beat_groups)
                    else:
                        patterns_by_section[section_type] = "~"

                elif instrument.is_chord_layer:
                    chords = evolved.chords.get(instrument.name)
                    if chords:
                        chord_strs = []
                        for chord in chords.chords:
                            degrees = []
                            for interval in chord.intervals:
                                if interval == 0:
                                    degree = chord.root_degree
                                elif interval in (3, 4):
                                    degree = (chord.root_degree + 2) % 7
                                elif interval in (7, 8):
                                    degree = (chord.root_degree + 4) % 7
                                elif interval in (10, 11):
                                    degree = (chord.root_degree + 6) % 7
                                else:
                                    degree = (chord.root_degree + interval // 2) % 7
                                degrees.append(str(degree))
                            chord_strs.append("[" + ", ".join(degrees) + "]")
                        patterns_by_section[section_type] = " ".join(chord_strs)
                    else:
                        patterns_by_section[section_type] = "~"

                else:
                    rhythm = evolved.rhythms.get(instrument.name, "")
                    phrase = evolved.phrases.get(instrument.name)
                    if rhythm and phrase:
                        patterns_by_section[section_type] = (
                            phrase.to_strudel_with_rhythm(
                                rhythm, instrument.use_scale_degrees
                            )
                        )
                    else:
                        patterns_by_section[section_type] = "~"

            # Build the full song pattern by explicitly repeating each section
            # All layers use the same structure, ensuring perfect alignment
            all_patterns = []
            for start, end, section_type in section_instances:
                pattern = patterns_by_section.get(section_type, "~")
                all_patterns.append(f"[{pattern}]")

            # Join all section patterns with spaces and wrap in <...> for sequential playback
            # The <...> syntax makes each bracketed section play for one cycle
            full_pattern = "<" + " ".join(all_patterns) + ">"

            # Build the layer - $: patterns run in parallel automatically
            if instrument.is_drum:
                layer_str = f'$: sound("{full_pattern}")'
            else:
                layer_str = f'$: n("{full_pattern}")'
                if instrument.octave_shift:
                    layer_str += f".sub({abs(instrument.octave_shift)})"
                layer_str += f'.scale("{self.composition_scale}")'
                layer_str += f'.s("{instrument.instrument}")'

            layer_str += f".gain({instrument.gain})"

            if not instrument.is_drum and instrument.lpf:
                layer_str += f".lpf({instrument.lpf})"

            lines.append(layer_str)

        return "\n".join(lines)

    def get_strudel_link(self, bpm: int = 120) -> str:
        """Generate a Strudel REPL link for the complete song."""
        code = self.get_strudel_code(bpm)
        encoded = base64.b64encode(code.encode("utf-8")).decode("utf-8")
        return f"https://strudel.cc/#{encoded}"

    def print_summary(self) -> None:
        """Print a summary of the evolved song."""
        print(f"\n{'='*60}")
        print("SONG SUMMARY")
        print(f"{'='*60}")
        print(f"\nScale: {self.composition_scale}")
        print(f"Structure: {' → '.join(s.value for s in self.song_structure)}")

        for section_type, evolved in self.evolved_sections.items():
            print(f"\n{section_type.value.upper()} ({evolved.bars} bars):")

            for instrument in self.instruments:
                if section_type not in instrument.play_in_sections:
                    continue

                if instrument.is_drum:
                    rhythm = evolved.rhythms.get(instrument.name, "N/A")
                    print(f"  {instrument.name}: {rhythm}")
                elif instrument.is_chord_layer:
                    chords = evolved.chords.get(instrument.name)
                    if chords:
                        chord_str = " → ".join(
                            f"deg{c.root_degree}" for c in chords.chords
                        )
                        print(f"  {instrument.name}: {chord_str}")
                else:
                    rhythm = evolved.rhythms.get(instrument.name, "")
                    print(f"  {instrument.name}: rhythm={rhythm}")


# =============================================================================
# INSTRUMENT PRESETS - Easy-to-use instrument configurations
# =============================================================================


def create_melody(
    name: str = "melody",
    instrument: str = "sawtooth",
    scale: str = None,
    octave_range: tuple[int, int] = (4, 6),
    gain: float = 0.4,
    lpf: int = 6000,
    use_variations: bool = False,
    play_in_sections: list[SectionType] = None,
) -> InstrumentConfig:
    """Create a lead melody instrument."""
    from fitness.melody_types import MelodicFitness
    from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS

    return InstrumentConfig(
        name=name,
        instrument=instrument,
        beats_per_bar=4,
        max_subdivision=3,
        octave_range=octave_range,
        scale=scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS.get("pop"),
        melody_fitness_fn=MelodicFitness(),
        octave_shift=0,
        gain=gain,
        lpf=lpf,
        layer_role="melody",
        use_variations=use_variations,
        play_in_sections=play_in_sections,
    )


def create_bass(
    name: str = "bass",
    instrument: str = "sawtooth",
    scale: str = None,
    gain: float = 0.5,
    lpf: int = 2000,
    play_in_sections: list[SectionType] = None,
) -> InstrumentConfig:
    """Create a bass instrument."""
    from fitness.melody_types import StableFitness
    from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS

    return InstrumentConfig(
        name=name,
        instrument=instrument,
        beats_per_bar=4,
        max_subdivision=2,
        octave_range=(2, 3),
        scale=scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS.get("bass"),
        melody_fitness_fn=StableFitness(),
        octave_shift=0,
        gain=gain,
        lpf=lpf,
        layer_role="bass",
        play_in_sections=play_in_sections,
    )


def create_pad(
    name: str = "pad",
    instrument: str = "triangle",
    scale: str = None,
    gain: float = 0.25,
    lpf: int = 3000,
    use_variations: bool = False,
    play_in_sections: list[SectionType] = None,
) -> InstrumentConfig:
    """Create a synth pad instrument."""
    from fitness.melody_types import StableFitness
    from fitness.rhythm import RHYTHM_FITNESS_FUNCTIONS

    return InstrumentConfig(
        name=name,
        instrument=instrument,
        beats_per_bar=2,
        max_subdivision=1,
        octave_range=(3, 5),
        scale=scale,
        rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS.get("pop"),
        melody_fitness_fn=StableFitness(),
        octave_shift=0,
        gain=gain,
        lpf=lpf,
        layer_role="pad",
        use_variations=use_variations,
        play_in_sections=play_in_sections,
    )


def create_chords(
    name: str = "chords",
    instrument: str = "piano",
    scale: str = None,
    beats_per_bar: int = 1,
    notes_per_chord: int = 3,
    chord_types: list[str] = None,
    genre: str = "pop",
    gain: float = 0.35,
    lpf: int = 4000,
    play_in_sections: list[SectionType] = None,
) -> InstrumentConfig:
    """Create a chord instrument."""
    from fitness.chords import CHORD_FITNESS_FUNCTIONS

    if chord_types is None:
        chord_types = ["major", "minor", "major7", "minor7"]

    # Get the fitness class and instantiate it
    fitness_class = CHORD_FITNESS_FUNCTIONS.get(genre)
    chord_fitness = fitness_class() if fitness_class else None

    return InstrumentConfig(
        name=name,
        instrument=instrument,
        beats_per_bar=beats_per_bar,
        octave_range=(3, 5),
        scale=scale,
        is_chord_layer=True,
        notes_per_chord=notes_per_chord,
        allowed_chord_types=chord_types,
        chord_fitness_fn=chord_fitness,
        octave_shift=3,
        gain=gain,
        lpf=lpf,
        layer_role="chords",
        play_in_sections=play_in_sections,
    )


def create_drum(
    name: str,
    sound: str,
    pattern_type: str = "kick",
    gain: float = 0.6,
    max_subdivision: int = 2,
    beats_per_bar: int = 4,
    play_in_sections: list[SectionType] = None,
) -> InstrumentConfig:
    """Create a drum instrument.

    Args:
        name: Instrument name
        sound: Strudel drum sound (bd, hh, sd, oh, cp, rim)
        pattern_type: Fitness type (kick, hihat, snare, percussion)
        gain: Volume level
        max_subdivision: Max notes per beat
        beats_per_bar: Beats per bar (4 = quarter notes, 8 = eighth notes)
        play_in_sections: Which sections to play in
    """
    from fitness.drums import DRUM_FITNESS_FUNCTIONS

    return InstrumentConfig(
        name=name,
        instrument=sound,
        beats_per_bar=beats_per_bar,
        max_subdivision=max_subdivision,
        is_drum=True,
        drum_sound=sound,
        rhythm_fitness_fn=DRUM_FITNESS_FUNCTIONS.get(pattern_type),
        gain=gain,
        layer_role="drums",
        play_in_sections=play_in_sections,
    )


def create_kick(
    gain: float = 0.7, play_in_sections: list[SectionType] = None
) -> InstrumentConfig:
    """Create a kick drum - 4 beats per bar, simple subdivisions."""
    return create_drum("kick", "bd", "kick", gain, max_subdivision=1, beats_per_bar=4, play_in_sections=play_in_sections)


def create_snare(
    gain: float = 0.6, play_in_sections: list[SectionType] = None
) -> InstrumentConfig:
    """Create a snare drum - 4 beats per bar, simple subdivisions."""
    return create_drum("snare", "sd", "snare", gain, max_subdivision=1, beats_per_bar=4, play_in_sections=play_in_sections)


def create_hihat(
    gain: float = 0.4, play_in_sections: list[SectionType] = None
) -> InstrumentConfig:
    """Create a closed hi-hat - 4 beats per bar, can have some subdivisions."""
    return create_drum("hihat", "hh", "hihat", gain, max_subdivision=2, beats_per_bar=4, play_in_sections=play_in_sections)


def create_open_hihat(
    gain: float = 0.35, play_in_sections: list[SectionType] = None
) -> InstrumentConfig:
    """Create an open hi-hat - sparse accents."""
    return create_drum("open_hihat", "oh", "percussion", gain, max_subdivision=1, beats_per_bar=4, play_in_sections=play_in_sections)


# =============================================================================
# QUICK COMPOSER FACTORY
# =============================================================================


def quick_composer(
    scale: str = "c:minor",
    bpm: int = 120,
    structure: list[SectionType] = None,
    include_melody: bool = True,
    include_bass: bool = True,
    include_chords: bool = False,
    include_drums: bool = True,
    genre: str = "pop",
    fitness_threshold: float = 0.85,
) -> SongComposer:
    """Create a pre-configured SongComposer with common settings.

    Args:
        scale: Scale string (e.g., "c:minor", "g:major")
        bpm: Tempo in BPM
        structure: Song structure (default: intro, verse, chorus, verse, chorus, outro)
        include_melody: Add a lead melody
        include_bass: Add a bass line
        include_chords: Add chord progression
        include_drums: Add drum kit (kick, snare, hihat)
        genre: Genre for fitness functions (pop, jazz, blues, rock, ambient)
        fitness_threshold: Target fitness before stopping evolution

    Returns:
        Configured SongComposer ready to evolve
    """
    if structure is None:
        structure = [
            SectionType.INTRO,
            SectionType.VERSE,
            SectionType.CHORUS,
            SectionType.VERSE,
            SectionType.CHORUS,
            SectionType.OUTRO,
        ]

    composer = SongComposer(
        population_size=30,
        mutation_rate=0.25,
        fitness_threshold=fitness_threshold,
        max_generations=50,
    )

    # Add sections
    unique_sections = set(structure)
    for section_type in unique_sections:
        composer.add_section(SectionConfig(section_type=section_type, bars=4))

    composer.set_song_structure(structure)

    # Add instruments
    if include_chords:
        composer.add_instrument(create_chords(scale=scale, genre=genre))

    if include_drums:
        composer.add_instrument(create_kick())
        composer.add_instrument(create_snare())
        composer.add_instrument(create_hihat())

    if include_bass:
        composer.add_instrument(create_bass(scale=scale))

    if include_melody:
        composer.add_instrument(create_melody(scale=scale, use_variations=True))

    return composer
