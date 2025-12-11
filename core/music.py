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

    def to_strudel_with_rhythm(self, rhythm: str, scale_degrees: bool = False, drum_sound: str = None, chord_mode: bool = False) -> str:
        """Convert phrase to Strudel notation preserving rhythm structure.

        Example: rhythm "2103" with 6 notes becomes "[n1 n2] [n3] ~ [n4 n5 n6]"
        With chord_mode=True: "[n1, n2] [n3] ~ [n4, n5, n6]" (parallel notes)

        Args:
            rhythm: Rhythm pattern string (e.g., "2103")
            scale_degrees: If True, use scale degrees 0-7 instead of note names
            drum_sound: If set, uses this drum sound name (e.g., "bd", "hh", "sd")
            chord_mode: If True, uses comma separation for parallel notes (chords)
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
                                    beat_notes.append(str(degree))
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
    gain: float = 0.5  # Volume/gain
    lpf: int = 4000  # Low-pass filter frequency
    use_scale_degrees: bool = True  # Use scale degrees 0-7 instead of note names
    is_drum: bool = False  # If True, uses sound() instead of n()
    drum_sound: str = ""  # Drum sound name (e.g., "bd", "hh", "sd")
    chord_mode: bool = False  # If True, uses comma-separated notes for chords
    chord_progression: list = field(default_factory=list)  # List of Chord objects
    is_chord_layer: bool = False  # If True, this layer plays chords from chord_progression

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
                        beat_groups.append("[" + " ".join([self.drum_sound] * subdivisions) + "]")
                pattern = " ".join(beat_groups)
            else:
                # Fallback for drums without rhythm
                pattern = self.drum_sound

            # Build drum expression
            result = f'sound("{pattern}")'
            result += f'.gain({self.gain})'
            return result

        elif self.is_chord_layer and self.chord_progression:
            # Chord layer: output chords as comma-separated scale degrees
            pattern = self._chord_progression_to_strudel()
            
            # Build Strudel expression
            result = f'n("{pattern}")'
            
            # Add octave shift if specified
            if self.octave_shift != 0:
                result += f'.sub({abs(self.octave_shift)})'
            
            # Add scale
            result += f'.scale("{self.scale}")'
            
            # Add instrument
            result += f'.s("{self.instrument}")'
            
            # Add gain
            result += f'.gain({self.gain})'
            
            # Add low-pass filter
            if self.lpf:
                result += f'.lpf({self.lpf})'
            
            return result

        else:
            # Melodic layer: use n() with scale/effects
            if self.rhythm and self.phrases:
                # Use rhythm-aware formatting for each phrase
                patterns = [p.to_strudel_with_rhythm(self.rhythm, self.use_scale_degrees, chord_mode=self.chord_mode) for p in self.phrases]
                pattern = " ".join(patterns)
            else:
                # Fallback: simple grouping
                pattern = " ".join(f"[{p.to_strudel()}]" for p in self.phrases)

            # Build Strudel expression
            result = f'n("{pattern}")'

            # Add octave shift if specified
            if self.octave_shift != 0:
                result += f'.sub({abs(self.octave_shift)})'

            # Add scale
            result += f'.scale("{self.scale}")'

            # Add instrument
            result += f'.s("{self.instrument}")'

            # Add gain
            result += f'.gain({self.gain})'

            # Add low-pass filter
            if self.lpf:
                result += f'.lpf({self.lpf})'

            return result

    def _chord_progression_to_strudel(self) -> str:
        """Convert chord progression to Strudel notation.
        
        Each chord becomes a group of comma-separated scale degrees.
        Example: [Chord(0, [0,4,7]), Chord(4, [0,4,7])] -> "[0, 2, 4] [4, 6, 1]"
        """
        if not self.chord_progression:
            return "0"
        
        chord_strs = []
        for chord in self.chord_progression:
            # Convert chord to scale degrees
            # Each interval maps to a scale degree offset from the root
            degrees = []
            for interval in chord.intervals:
                # Approximate: semitone intervals to scale degrees
                # 0=root, 3-4=3rd, 7=5th, 10-11=7th, 14=9th
                if interval == 0:
                    degree = chord.root_degree
                elif interval in (3, 4):
                    degree = (chord.root_degree + 2) % 7  # 3rd
                elif interval in (5,):
                    degree = (chord.root_degree + 3) % 7  # 4th
                elif interval in (7, 8):
                    degree = (chord.root_degree + 4) % 7  # 5th
                elif interval in (10, 11):
                    degree = (chord.root_degree + 6) % 7  # 7th
                elif interval >= 12:
                    degree = (chord.root_degree + (interval - 12) // 2) % 7
                else:
                    # For sus2, etc.
                    degree = (chord.root_degree + interval // 2) % 7
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
        return self.chord_progression.chords[chord_idx % len(self.chord_progression.chords)]

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
    points: list[tuple[float, float]] = field(default_factory=list)  # (time_fraction, gain_value)
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
    points: list[tuple[float, float]] = field(default_factory=list)  # (time_fraction, cutoff_hz)
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
class Composition:
    layers: list[Layer] = field(default_factory=list)
    bpm: int = 120
    global_scale: str = ""  # If set, overrides individual layer scales
    harmonic_context: HarmonicContext = None  # Optional harmonic context for the composition

    def to_strudel(self) -> str:
        lines = [f"setcpm({self.bpm / 4})", ""]  # cpm = cycles per minute
        lines.extend(f"$: {layer.to_strudel()}" for layer in self.layers)
        return "\n".join(lines)

    def to_strudel_link(self) -> str:
        """Generate a Strudel REPL link for this composition."""
        import base64
        strudel_code = self.to_strudel()
        encoded = base64.b64encode(strudel_code.encode('utf-8')).decode('utf-8')
        return f"https://strudel.cc/#{encoded}"

    @staticmethod
    def random_scale() -> str:
        """Generate a random scale (e.g., 'c:minor', 'g:major')."""
        import random
        roots = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
        modes = ['major', 'minor']
        return f"{random.choice(roots)}:{random.choice(modes)}"
