"""Song structure composer - Creates complete songs with intro, verse, chorus, outro.

This module extends the layered composer to support full song structures with
multiple sections that are each evolved separately using genetic algorithms.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from enum import Enum
import base64

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


class SectionType(Enum):
    """Types of song sections."""

    INTRO = "intro"
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    OUTRO = "outro"


@dataclass
class SectionConfig:
    """Configuration for a song section."""

    section_type: SectionType
    bars: int = 4  # Length of this section in bars
    energy_level: float = 0.5  # 0.0 = low energy, 1.0 = high energy

    # Optional overrides for fitness functions
    rhythm_fitness_modifier: float = 1.0  # Multiplier for rhythm density
    melody_fitness_modifier: float = 1.0  # Multiplier for melody complexity
    chord_fitness_modifier: float = 1.0  # Multiplier for chord complexity


@dataclass
class InstrumentConfig:
    """Configuration for an instrument across the song."""

    name: str
    instrument: str
    beats_per_bar: int = 4
    max_subdivision: int = 2
    octave_range: tuple[int, int] = (4, 5)
    scale: list[NoteName] = None
    rhythm_fitness_fn: Callable[[str], float] = None
    melody_fitness_fn: FitnessFunction = None
    strudel_scale: str = ""
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

    def __post_init__(self):
        if self.scale is None:
            self.scale = [
                NoteName.C,
                NoteName.D,
                NoteName.E,
                NoteName.F,
                NoteName.G,
                NoteName.A,
                NoteName.B,
            ]
        if self.play_in_sections is None:
            # Default: play in all sections
            self.play_in_sections = list(SectionType)


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
                    rhythm, scale=instrument.scale, octave_range=instrument.octave_range
                )
            )
            for _ in range(self.population_size)
        ]

        def melody_fitness(phrase: Phrase) -> float:
            if instrument.melody_fitness_fn:
                layer = Layer(
                    name=instrument.name,
                    phrases=[phrase],
                    instrument=instrument.instrument,
                    rhythm=rhythm,
                )
                base_score = instrument.melody_fitness_fn.evaluate(layer)
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
        num_chords = section.bars  # One chord per bar typically

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

        for instrument in self.instruments:
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

            elif instrument.is_chord_layer:
                # Chord layer
                chords, fitness = self._evolve_chords(
                    instrument, section_config, verbose
                )
                evolved.chords[instrument.name] = chords
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

                if verbose:
                    print(f"     Rhythm: {rhythm} (fitness: {r_fitness:.3f})")
                    print(f"     Melody fitness: {m_fitness:.3f}")

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

        # Set random scale for the whole song
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
