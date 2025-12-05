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
            NoteName.C: "c", NoteName.CS: "cs",
            NoteName.D: "d", NoteName.DS: "ds",
            NoteName.E: "e", NoteName.F: "f",
            NoteName.FS: "fs", NoteName.G: "g",
            NoteName.GS: "gs", NoteName.A: "a",
            NoteName.AS: "as", NoteName.B: "b",
        }
        return f"{name_map[self.pitch]}{self.octave}"


@dataclass
class Phrase:
    notes: list[Note] = field(default_factory=list)
    
    def to_strudel(self) -> str:
        return " ".join(n.to_strudel() for n in self.notes)


@dataclass 
class Layer:
    name: str
    phrases: list[Phrase] = field(default_factory=list)
    instrument: str = "piano"
    
    def to_strudel(self) -> str:
        pattern = " ".join(f"[{p.to_strudel()}]" for p in self.phrases)
        return f'n("{pattern}").s("{self.instrument}")'


@dataclass
class Composition:
    layers: list[Layer] = field(default_factory=list)
    bpm: int = 120
    
    def to_strudel(self) -> str:
        lines = [f"setcpm({self.bpm / 4})", ""]  # cpm = cycles per minute
        lines.extend(
            f"${layer.to_strudel()}" 
            for layer in self.layers
        )
        return "\n".join(lines)
