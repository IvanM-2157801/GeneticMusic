from dataclasses import dataclass, field
from enum import Enum


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

    def to_strudel_with_rhythm(self, rhythm: str, scale_degrees: bool = False) -> str:
        """Convert phrase to Strudel notation preserving rhythm structure.

        Example: rhythm "2103" with 6 notes becomes "[n1 n2] [n3] ~ [n4 n5 n6]"

        Args:
            rhythm: Rhythm pattern string (e.g., "2103")
            scale_degrees: If True, use scale degrees 0-7 instead of note names
        """
        note_idx = 0
        beat_groups = []

        for beat_char in rhythm:
            subdivisions = int(beat_char)
            if subdivisions == 0:
                # Rest beat
                beat_groups.append("~")
            else:
                # Collect notes for this beat
                beat_notes = []
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
                    beat_groups.append("[" + " ".join(beat_notes) + "]")

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

    def to_strudel(self) -> str:
        """Convert layer to Strudel notation.

        If rhythm is set, uses rhythm-aware formatting.
        Otherwise, falls back to simple grouping.
        """
        if self.rhythm and self.phrases:
            # Use rhythm-aware formatting for each phrase
            patterns = [p.to_strudel_with_rhythm(self.rhythm, self.use_scale_degrees) for p in self.phrases]
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


@dataclass
class Composition:
    layers: list[Layer] = field(default_factory=list)
    bpm: int = 120
    global_scale: str = ""  # If set, overrides individual layer scales

    def to_strudel(self) -> str:
        lines = [f"setcpm({self.bpm / 4})", ""]  # cpm = cycles per minute
        lines.extend(f"$: {layer.to_strudel()}" for layer in self.layers)
        return "\n".join(lines)

    @staticmethod
    def random_scale() -> str:
        """Generate a random scale (e.g., 'c:minor', 'g:major')."""
        import random
        roots = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
        modes = ['major', 'minor']
        return f"{random.choice(roots)}:{random.choice(modes)}"
