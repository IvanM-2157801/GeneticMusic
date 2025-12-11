from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.genome_ops import ChordProgression, Chord


class NoteName(Enum):
    C = 0
    CS = 1
    D = 2
    DS = 3
    E = 4
    F = 5
    FS = 6
    G = 7
    GS = 8
    A = 9
    AS = 10
    B = 11
    REST = -1


# Scale intervals in semitones from root
SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "blues": [0, 3, 5, 6, 7, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "minor_pentatonic": [0, 3, 5, 7, 10],
}

# Map note names to semitone values
NOTE_NAME_TO_SEMITONE = {
    "c": 0,
    "cs": 1,
    "db": 1,
    "d": 2,
    "ds": 3,
    "eb": 3,
    "e": 4,
    "f": 5,
    "fs": 6,
    "gb": 6,
    "g": 7,
    "gs": 8,
    "ab": 8,
    "a": 9,
    "as": 10,
    "bb": 10,
    "b": 11,
}


def parse_scale_string(scale_str: str) -> tuple[str, str, list[NoteName]]:
    """Parse a scale string like 'd:minor' into root, mode, and NoteName list.

    Args:
        scale_str: Scale string in format "root:mode" (e.g., "d:minor", "c:major")

    Returns:
        Tuple of (root, mode, list of NoteName values in the scale)

    Example:
        >>> parse_scale_string("d:minor")
        ('d', 'minor', [NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.AS, NoteName.C])
    """
    parts = scale_str.lower().split(":")
    root = parts[0] if parts else "c"
    mode = parts[1] if len(parts) > 1 else "major"

    # Get root semitone
    root_semitone = NOTE_NAME_TO_SEMITONE.get(root, 0)

    # Get scale intervals
    intervals = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])

    # Build list of NoteName values
    note_names = []
    for interval in intervals:
        semitone = (root_semitone + interval) % 12
        # Find the NoteName with this value
        for note in NoteName:
            if note.value == semitone and note != NoteName.REST:
                note_names.append(note)
                break

    return root, mode, note_names


@dataclass
class Note:
    pitch: NoteName
    octave: int = 4
    duration: float = 1.0  # In beats

    @property
    def midi_pitch(self) -> int:
        if self.pitch == NoteName.REST:
            return -1
        return (self.octave + 1) * 12 + self.pitch.value

    def to_strudel(self) -> str:
        if self.pitch == NoteName.REST:
            return "~"

        name_map = {
            NoteName.C: "c",
            NoteName.CS: "cs",
            NoteName.D: "d",
            NoteName.DS: "ds",
            NoteName.E: "e",
            NoteName.F: "f",
            NoteName.FS: "fs",
            NoteName.G: "g",
            NoteName.GS: "gs",
            NoteName.A: "a",
            NoteName.AS: "as",
            NoteName.B: "b",
        }
        return f"{name_map[self.pitch]}{self.octave}"


@dataclass
class Phrase:
    notes: list[Note] = field(default_factory=list)

    def to_strudel(self) -> str:
        return " ".join(n.to_strudel() for n in self.notes)

    def to_strudel_with_rhythm(
        self,
        rhythm: str,
        scale_degrees: bool = False,
        drum_sound: str = None,
        chord_mode: bool = False,
        base_octave: int = 4,
    ) -> str:
        """Convert phrase to Strudel notation preserving rhythm structure.

        Example: rhythm "2103" with 6 notes becomes "[n1 n2] [n3] ~ [n4 n5 n6]"
        With chord_mode=True: "[n1, n2] [n3] ~ [n4, n5, n6]" (parallel notes)

        Args:
            rhythm: Rhythm pattern string (e.g., "2103")
            scale_degrees: If True, use scale degrees 0-7 instead of note names
            drum_sound: If set, uses this drum sound name (e.g., "bd", "hh", "sd")
            chord_mode: If True, uses comma separation for parallel notes (chords)
            base_octave: Base octave for scale degree calculation (default 4).
                         Notes above this octave add +7 per octave to the degree,
                         notes below subtract -7 per octave.
        """
        beat_groups = []
        note_idx = 0

        for beat_char in rhythm:
            subdivisions = int(beat_char)
            if subdivisions == 0:
                # Rest beat
                beat_groups.append("~")
            else:
                beat_notes = []
                if drum_sound:
                    # For drums, just repeat the sound name
                    beat_notes = [drum_sound] * subdivisions
                else:
                    # For melodic instruments, use actual notes
                    for _ in range(subdivisions):
                        if note_idx < len(self.notes):
                            note = self.notes[note_idx]
                            if scale_degrees:
                                # Use scale degree (0-7) based on pitch value
                                if note.pitch == NoteName.REST:
                                    beat_notes.append("~")
                                else:
                                    degree = note.pitch.value % 7
                                    # Add octave offset: +7 per octave above base, -7 per octave below
                                    octave_offset = (note.octave - base_octave) * 7
                                    final_degree = degree + octave_offset
                                    beat_notes.append(str(final_degree))
                            else:
                                beat_notes.append(note.to_strudel())
                            note_idx += 1

                if len(beat_notes) == 1:
                    beat_groups.append(beat_notes[0])
                else:
                    # Use comma separation for chords, space for sequential notes
                    separator = ", " if chord_mode else " "
                    beat_groups.append("[" + separator.join(beat_notes) + "]")

        return " ".join(beat_groups)


@dataclass
class Layer:
    name: str
    phrases: list[Phrase] = field(default_factory=list)
    instrument: str = "piano"
    rhythm: str = ""  # Store rhythm pattern for proper Strudel output
    scale: str = "c:major"  # Scale specification (e.g., "c:minor", "d:major")
    octave_shift: int = 0  # Octave transposition (e.g., -7 for .sub(7))
    # Basic effects
    gain: float = 0.5  # Volume/gain (0.0-1.0)
    lpf: int = 4000  # Low-pass filter frequency (Hz, 0 = disabled)
    hpf: int = 0  # High-pass filter frequency (Hz, 0 = disabled)
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
    pan: float = 0.5  # Stereo pan (0.0=left, 0.5=center, 1.0=right)
    # Envelope
    attack: float = 0.0  # Attack time (0 = disabled)
    decay: float = 0.0  # Decay time (0 = disabled)
    sustain: float = 0.0  # Sustain level (0 = disabled)
    release: float = 0.0  # Release time (0 = disabled)
    # Layer type flags
    use_scale_degrees: bool = True  # Use scale degrees 0-7 instead of note names
    is_drum: bool = False  # If True, uses sound() instead of n()
    drum_sound: str = ""  # Drum sound name (e.g., "bd", "hh", "sd")
    chord_mode: bool = False  # If True, uses comma-separated notes for chords
    chord_progression: list = field(default_factory=list)  # List of Chord objects
    is_chord_layer: bool = (
        False  # If True, this layer plays chords from chord_progression
    )
    base_octave: int = 4  # Base octave for scale degree calculation
    # Layer role for contextual fitness (chords, drums, bass, melody, pad, lead)
    layer_role: str = "melody"
    # Context group - layers with the same group name share context during evolution
    context_group: str = ""
    # Sound bank for Strudel (e.g., "RolandTR808", "alesissr16")
    bank: str = ""

    def _build_effects_chain(self) -> str:
        """Build the effects chain for Strudel output."""
        effects = []

        # Gain (always add)
        effects.append(f".gain({self.gain})")

        # Filters
        if self.lpf:
            effects.append(f".lpf({self.lpf})")
        if self.hpf:
            effects.append(f".hpf({self.hpf})")

        # Envelope (ADSR)
        if self.attack > 0:
            effects.append(f".attack({self.attack})")
        if self.decay > 0:
            effects.append(f".decay({self.decay})")
        if self.sustain > 0:
            effects.append(f".sustain({self.sustain})")
        if self.release > 0:
            effects.append(f".release({self.release})")

        # Distortion
        if self.distort > 0:
            effects.append(f".distort({self.distort})")

        # Panning (only add if not center)
        if self.pan != 0.5:
            effects.append(f".pan({self.pan})")

        # Reverb
        if self.room > 0:
            effects.append(f".room({self.room})")
            effects.append(f".roomsize({self.roomsize})")

        # Delay
        if self.delay > 0:
            effects.append(f".delay({self.delay})")
            effects.append(f".delaytime({self.delaytime})")
            effects.append(f".delayfeedback({self.delayfeedback})")

        # Post-gain (after effects)
        if self.postgain > 0:
            effects.append(f".postgain({self.postgain})")

        return "".join(effects)

    def to_strudel(self) -> str:
        """Convert layer to Strudel notation.

        If rhythm is set, uses rhythm-aware formatting.
        Otherwise, falls back to simple grouping.
        """
        if self.is_drum:
            # Drum layer: use sound() with rhythm structure
            if self.rhythm:
                # Convert rhythm to sound pattern
                beat_groups = []
                for beat_char in self.rhythm:
                    subdivisions = int(beat_char)
                    if subdivisions == 0:
                        beat_groups.append("~")
                    elif subdivisions == 1:
                        beat_groups.append(self.drum_sound)
                    else:
                        beat_groups.append(
                            "[" + " ".join([self.drum_sound] * subdivisions) + "]"
                        )
                pattern = " ".join(beat_groups)
            else:
                # Fallback for drums without rhythm
                pattern = self.drum_sound

            # Build drum expression
            result = f'sound("{pattern}")'
            result += self._build_effects_chain()
            # Add bank if specified
            if self.bank:
                result += f'.bank("{self.bank}")'
            return result

        elif self.is_chord_layer and self.chord_progression:
            # Chord layer: output chords as comma-separated scale degrees
            pattern = self._chord_progression_to_strudel()

            # Build Strudel expression with .sub() applied to the pattern string
            if self.octave_shift != 0:
                result = f'n("{pattern}".sub({abs(self.octave_shift)}))'
            else:
                result = f'n("{pattern}")'

            # Add scale and instrument
            result += f'.scale("{self.scale}")'
            result += f'.s("{self.instrument}")'
            result += self._build_effects_chain()
            return result

        else:
            # Melodic layer: use n() with scale/effects
            if self.rhythm and self.phrases:
                # Use rhythm-aware formatting for each phrase
                patterns = [
                    p.to_strudel_with_rhythm(
                        self.rhythm,
                        self.use_scale_degrees,
                        chord_mode=self.chord_mode,
                        base_octave=self.base_octave,
                    )
                    for p in self.phrases
                ]
                pattern = " ".join(patterns)
            else:
                # Fallback: simple grouping
                pattern = " ".join(f"[{p.to_strudel()}]" for p in self.phrases)

            # Build Strudel expression with .sub() applied to the pattern string
            if self.octave_shift != 0:
                result = f'n("{pattern}".sub({abs(self.octave_shift)}))'
            else:
                result = f'n("{pattern}")'

            # Add scale and instrument
            result += f'.scale("{self.scale}")'
            result += f'.s("{self.instrument}")'
            result += self._build_effects_chain()
            return result

    def _chord_progression_to_strudel(self) -> str:
        """Convert chord progression to Strudel notation.

        Each chord becomes a group of comma-separated scale degrees.
        Uses simple stacked thirds from the root for clean diatonic harmony.
        Example: Chord with root=0 and 3 notes -> "[0, 2, 4]" (I chord: 1-3-5)
        Example: Chord with root=4 and 3 notes -> "[4, 6, 1]" (V chord: 5-7-2)
        """
        if not self.chord_progression:
            return "0"

        chord_strs = []
        for chord in self.chord_progression:
            # Simple approach: stack thirds from the root
            # This ensures proper diatonic harmony (no dissonant 0-1 intervals)
            root = chord.root_degree
            num_notes = len(chord.intervals)

            # Build chord by stacking scale degrees (thirds)
            # root, root+2 (3rd), root+4 (5th), root+6 (7th)
            degrees = []
            for i in range(num_notes):
                degree = (root + i * 2) % 7
                degrees.append(str(degree))

            if len(degrees) == 1:
                chord_strs.append(degrees[0])
            else:
                chord_strs.append("[" + ", ".join(degrees) + "]")

        return " ".join(chord_strs)


@dataclass
class HarmonicContext:
    """Tracks the current chord progression for chord-aware melody evolution.

    This provides context for melody fitness functions to evaluate how well
    melody notes fit with the underlying harmony.
    """

    chord_progression: "ChordProgression"
    beats_per_chord: int = 4  # How many beats each chord lasts
    scale_root: str = "c"  # Root note of the scale (e.g., "c", "g", "f#")
    scale_type: str = "major"  # Scale type (e.g., "major", "minor")

    def get_chord_at_beat(self, beat: int) -> "Chord":
        """Get the active chord at a given beat position.

        Args:
            beat: Beat position (0-indexed)

        Returns:
            The Chord active at that beat
        """
        if not self.chord_progression.chords:
            return None
        chord_idx = beat // self.beats_per_chord
        return self.chord_progression.chords[
            chord_idx % len(self.chord_progression.chords)
        ]

    def get_chord_tones_at_beat(self, beat: int) -> list[int]:
        """Get the chord tones (as semitone intervals from scale root) at a beat.

        Args:
            beat: Beat position (0-indexed)

        Returns:
            List of semitone intervals that are chord tones
        """
        chord = self.get_chord_at_beat(beat)
        if not chord:
            return []

        # Convert chord root degree to semitones based on scale type
        scale_intervals = {
            "major": [0, 2, 4, 5, 7, 9, 11],
            "minor": [0, 2, 3, 5, 7, 8, 10],
            "dorian": [0, 2, 3, 5, 7, 9, 10],
            "mixolydian": [0, 2, 4, 5, 7, 9, 10],
            "blues": [0, 3, 5, 6, 7, 10],
        }

        scale = scale_intervals.get(self.scale_type, scale_intervals["major"])
        root_semitone = scale[chord.root_degree % len(scale)]

        # Return chord tones as absolute semitones from scale root
        return [(root_semitone + interval) % 12 for interval in chord.intervals]

    def is_chord_tone(self, note: "Note", beat: int) -> bool:
        """Check if a note is a chord tone at the given beat.

        Args:
            note: The note to check
            beat: Beat position

        Returns:
            True if the note is a chord tone
        """
        if note.pitch == NoteName.REST:
            return True  # Rests are always "valid"

        chord_tones = self.get_chord_tones_at_beat(beat)
        note_semitone = note.pitch.value % 12
        return note_semitone in chord_tones

    def is_extension(self, note: "Note", beat: int) -> bool:
        """Check if a note is a chord extension (9th, 11th, 13th).

        Args:
            note: The note to check
            beat: Beat position

        Returns:
            True if the note is a chord extension
        """
        if note.pitch == NoteName.REST:
            return False

        chord = self.get_chord_at_beat(beat)
        if not chord:
            return False

        # Extensions are 2 (9th), 4 (11th), 6 (13th) scale degrees above root
        scale_intervals = {
            "major": [0, 2, 4, 5, 7, 9, 11],
            "minor": [0, 2, 3, 5, 7, 8, 10],
        }
        scale = scale_intervals.get(self.scale_type, scale_intervals["major"])
        root_semitone = scale[chord.root_degree % len(scale)]

        # 9th = root + 14 semitones, 11th = root + 17, 13th = root + 21
        extensions = [
            (root_semitone + 14) % 12,  # 9th
            (root_semitone + 17) % 12,  # 11th
            (root_semitone + 21) % 12,  # 13th
        ]

        note_semitone = note.pitch.value % 12
        return note_semitone in extensions


@dataclass
class DynamicEnvelope:
    """Represents gain changes over time within a section.

    Used for evolving volume automation (crescendos, diminuendos, etc.)
    """

    points: list[tuple[float, float]] = field(
        default_factory=list
    )  # (time_fraction, gain_value)
    envelope_type: str = "linear"  # "linear", "smooth", "step"

    def __post_init__(self):
        if not self.points:
            # Default: constant gain
            self.points = [(0.0, 0.5), (1.0, 0.5)]

    def get_gain_at(self, time_fraction: float) -> float:
        """Get interpolated gain value at a time position.

        Args:
            time_fraction: Position in section (0.0 to 1.0)

        Returns:
            Gain value (0.0 to 1.0)
        """
        if not self.points:
            return 0.5

        # Find surrounding points
        sorted_points = sorted(self.points, key=lambda p: p[0])

        for i in range(len(sorted_points) - 1):
            t1, g1 = sorted_points[i]
            t2, g2 = sorted_points[i + 1]

            if t1 <= time_fraction <= t2:
                # Linear interpolation
                if t2 == t1:
                    return g1
                ratio = (time_fraction - t1) / (t2 - t1)
                return g1 + ratio * (g2 - g1)

        # Outside range - return nearest
        if time_fraction <= sorted_points[0][0]:
            return sorted_points[0][1]
        return sorted_points[-1][1]

    def to_strudel(self) -> str:
        """Generate Strudel gain automation code.

        Returns:
            Strudel code for gain modulation
        """
        if len(self.points) <= 2:
            # Simple case: use range
            min_gain = min(p[1] for p in self.points)
            max_gain = max(p[1] for p in self.points)

            if min_gain == max_gain:
                return f".gain({min_gain:.2f})"

            # Use slow sine wave for smooth dynamics
            return f".gain(sine().range({min_gain:.2f}, {max_gain:.2f}).slow(8))"

        # Complex envelope: use perlin noise for organic feel
        min_gain = min(p[1] for p in self.points)
        max_gain = max(p[1] for p in self.points)
        return f".gain(perlin().range({min_gain:.2f}, {max_gain:.2f}).slow(4))"


@dataclass
class FilterEnvelope:
    """Represents LPF filter changes over time within a section.

    Used for evolving filter automation (sweeps, opens, etc.)
    """

    points: list[tuple[float, float]] = field(
        default_factory=list
    )  # (time_fraction, cutoff_hz)
    envelope_type: str = "linear"  # "linear", "smooth", "step"

    def __post_init__(self):
        if not self.points:
            # Default: constant filter
            self.points = [(0.0, 4000), (1.0, 4000)]

    def get_cutoff_at(self, time_fraction: float) -> float:
        """Get interpolated cutoff frequency at a time position.

        Args:
            time_fraction: Position in section (0.0 to 1.0)

        Returns:
            Cutoff frequency in Hz
        """
        if not self.points:
            return 4000

        sorted_points = sorted(self.points, key=lambda p: p[0])

        for i in range(len(sorted_points) - 1):
            t1, f1 = sorted_points[i]
            t2, f2 = sorted_points[i + 1]

            if t1 <= time_fraction <= t2:
                if t2 == t1:
                    return f1
                ratio = (time_fraction - t1) / (t2 - t1)
                return f1 + ratio * (f2 - f1)

        if time_fraction <= sorted_points[0][0]:
            return sorted_points[0][1]
        return sorted_points[-1][1]

    def to_strudel(self) -> str:
        """Generate Strudel filter automation code.

        Returns:
            Strudel code for LPF modulation
        """
        if len(self.points) <= 2:
            min_cutoff = min(p[1] for p in self.points)
            max_cutoff = max(p[1] for p in self.points)

            if min_cutoff == max_cutoff:
                return f".lpf({int(min_cutoff)})"

            # Use sine wave for smooth filter sweep
            return f".lpf(sine().range({int(min_cutoff)}, {int(max_cutoff)}).slow(4))"

        min_cutoff = min(p[1] for p in self.points)
        max_cutoff = max(p[1] for p in self.points)
        return f".lpf(perlin().range({int(min_cutoff)}, {int(max_cutoff)}).slow(2))"


@dataclass
class LayerGroup:
    """A group of layers that play together using stack().

    LayerGroups can have their own effects chain applied to all layers.
    In Strudel, this outputs as: stack(layer1, layer2, ...).effect1().effect2()

    Example output (use_references=True):
        const verse_drums = stack(kick, hihat, snare).bank("RolandTR808").gain(0.4)

    Example output (use_references=False):
        const verse_drums = stack(
            sound("bd ~ ~ ~ bd ~ ~ ~").gain(0.8),
            sound("[hh hh] [hh hh] ...").gain(0.5),
            sound("~ ~ sd ~ ~ ~ sd ~").gain(0.7)
        ).bank("RolandTR808").gain(0.4)
    """

    name: str
    layers: list[Layer] = field(default_factory=list)
    # Group-level effects (applied to the whole stack)
    gain: float = 0.0  # 0 = don't add
    lpf: int = 0
    hpf: int = 0
    room: float = 0.0
    bank: str = ""

    def to_strudel(self, use_references: bool = True) -> str:
        """Convert layer group to Strudel stack() notation.

        Args:
            use_references: If True, outputs layer names as references (e.g., stack(kick, snare)).
                           If False, outputs full layer definitions inline.
        """
        if not self.layers:
            return 'sound("~")'

        if use_references:
            # Use layer names as references
            layer_strs = [layer.name for layer in self.layers]
        else:
            # Output full layer definitions
            layer_strs = [layer.to_strudel() for layer in self.layers]

        # Wrap in stack()
        if len(layer_strs) == 1:
            result = layer_strs[0] if use_references else layer_strs[0]
        else:
            if use_references:
                result = "stack(" + ", ".join(layer_strs) + ")"
            else:
                result = "stack(\n  " + ",\n  ".join(layer_strs) + "\n)"

        # Add group-level effects
        if self.gain > 0:
            result += f".gain({self.gain})"
        if self.lpf > 0:
            result += f".lpf({self.lpf})"
        if self.hpf > 0:
            result += f".hpf({self.hpf})"
        if self.room > 0:
            result += f".room({self.room})"
        if self.bank:
            result += f'.bank("{self.bank}")'

        return result

    def to_strudel_const(self, use_references: bool = True) -> str:
        """Output as a JavaScript const declaration."""
        return f"const {self.name} = {self.to_strudel(use_references)}"


@dataclass
class ArrangementSection:
    """A section in an arrangement with a duration and content.

    Content can be a Layer, LayerGroup, or another Arrangement.
    Duration is in bars.
    """

    bars: int
    content: "Layer | LayerGroup | str"  # str for referencing named constants

    def to_strudel(self) -> str:
        """Convert to [bars, content] format for arrange()."""
        if isinstance(self.content, str):
            # Reference to a named constant
            return f"[{self.bars}, {self.content}]"
        elif isinstance(self.content, (Layer, LayerGroup)):
            return f"[{self.bars}, {self.content.to_strudel()}]"
        else:
            return f'[{self.bars}, sound("~")]'


@dataclass
class Arrangement:
    """An arrangement of sections using Strudel's arrange() function.

    Example output:
        arrange(
            [1, intro],
            [4, verse_drums],
            [4, chorus_drums],
            [1, outro]
        )
    """

    name: str
    sections: list[ArrangementSection] = field(default_factory=list)
    # Arrangement-level effects
    gain: float = 0.0
    bank: str = ""

    def add_section(self, bars: int, content: "Layer | LayerGroup | str") -> None:
        """Add a section to the arrangement."""
        self.sections.append(ArrangementSection(bars=bars, content=content))

    def to_strudel(self) -> str:
        """Convert to Strudel arrange() notation."""
        if not self.sections:
            return 'sound("~")'

        section_strs = [s.to_strudel() for s in self.sections]
        result = "arrange(\n  " + ",\n  ".join(section_strs) + "\n)"

        # Add arrangement-level effects
        if self.gain > 0:
            result += f".gain({self.gain})"
        if self.bank:
            result += f'.bank("{self.bank}")'

        return result

    def to_strudel_const(self) -> str:
        """Output as a JavaScript const declaration."""
        return f"const {self.name} = {self.to_strudel()}"


@dataclass
class SongStructure:
    """Complete song structure with named layers, groups, and arrangements.

    This is the top-level container that outputs a full Strudel composition
    with named constants for reusable sections.

    Example output:
        setcpm(30)

        // Layers
        const kick = sound("bd ~ ~ ~ bd ~ ~ ~").gain(0.8).bank("RolandTR808")
        const hihat = sound("[hh hh] [hh hh] ...").gain(0.5).bank("RolandTR808")
        const snare = sound("~ ~ sd ~ ~ ~ sd ~").gain(0.7).bank("RolandTR808")

        // Layer Groups
        const verse_drums = stack(kick, hihat, snare).gain(0.4)
        const chorus_drums = stack(kick, hihat, snare).gain(0.6)

        // Arrangements
        $: arrange(
            [4, verse_drums],
            [4, chorus_drums],
            [4, verse_drums],
            [4, chorus_drums]
        )
    """

    bpm: int = 120
    layers: dict[str, Layer] = field(default_factory=dict)
    groups: dict[str, LayerGroup] = field(default_factory=dict)
    arrangements: list[Arrangement] = field(default_factory=list)

    def add_layer(self, layer: Layer) -> None:
        """Add a named layer."""
        self.layers[layer.name] = layer

    def add_group(self, group: LayerGroup) -> None:
        """Add a named layer group."""
        self.groups[group.name] = group

    def add_arrangement(self, arrangement: Arrangement) -> None:
        """Add an arrangement track."""
        self.arrangements.append(arrangement)

    def to_strudel(self) -> str:
        """Generate complete Strudel code with named constants."""
        lines = [f"setcpm({self.bpm / 4})", ""]

        # Output layer constants
        if self.layers:
            lines.append("// Layers")
            for name, layer in self.layers.items():
                lines.append(f"const {name} = {layer.to_strudel()}")
            lines.append("")

        # Output group constants (using references to layer names)
        if self.groups:
            lines.append("// Layer Groups")
            for group in self.groups.values():
                lines.append(group.to_strudel_const(use_references=True))
            lines.append("")

        # Output arrangements as $: tracks
        if self.arrangements:
            lines.append("// Arrangement")
            for arr in self.arrangements:
                lines.append(f"$: {arr.to_strudel()}")

        return "\n".join(lines)

    def to_strudel_link(self) -> str:
        """Generate a Strudel REPL link for this song."""
        import base64

        strudel_code = self.to_strudel()
        encoded = base64.b64encode(strudel_code.encode("utf-8")).decode("utf-8")
        return f"https://strudel.cc/#{encoded}"


@dataclass
class Composition:
    layers: list[Layer] = field(default_factory=list)
    bpm: int = 120
    global_scale: str = ""  # If set, overrides individual layer scales
    harmonic_context: HarmonicContext = (
        None  # Optional harmonic context for the composition
    )

    def to_strudel(self) -> str:
        lines = [f"setcpm({self.bpm / 4})", ""]  # cpm = cycles per minute
        lines.extend(f"$: {layer.to_strudel()}" for layer in self.layers)
        return "\n".join(lines)

    def to_strudel_link(self) -> str:
        """Generate a Strudel REPL link for this composition."""
        import base64

        strudel_code = self.to_strudel()
        encoded = base64.b64encode(strudel_code.encode("utf-8")).decode("utf-8")
        return f"https://strudel.cc/#{encoded}"

    @staticmethod
    def random_scale() -> str:
        """Generate a random scale (e.g., 'c:minor', 'g:major')."""
        import random

        roots = ["c", "d", "e", "f", "g", "a", "b"]
        modes = ["major", "minor"]
        return f"{random.choice(roots)}:{random.choice(modes)}"
