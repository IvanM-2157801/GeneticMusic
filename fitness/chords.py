"""Chord/harmony fitness functions for different genres."""
from abc import ABC, abstractmethod
from core.genome_ops import ChordProgression, Chord, CHORD_TYPES


class ChordFitnessFunction(ABC):
    """Abstract base for chord/harmony fitness functions."""
    
    @abstractmethod
    def evaluate(self, progression: ChordProgression) -> float:
        """Evaluate fitness of a chord progression. Returns 0.0 - 1.0."""
        pass


# === Common Chord Fitness Utilities ===

def chord_variety(progression: ChordProgression) -> float:
    """Measure chord variety (0-1). Higher = more variety in roots.

    Strongly penalizes repetitive chords (same root repeated).
    """
    if not progression.chords:
        return 0.0

    roots = [c.root_degree for c in progression.chords]
    unique_roots = set(roots)

    # Count consecutive repetitions (bad)
    repetitions = sum(1 for i in range(len(roots) - 1) if roots[i] == roots[i + 1])
    repetition_penalty = repetitions / max(len(roots) - 1, 1)

    # Variety score: unique roots out of total
    variety_score = min(len(unique_roots) / min(len(roots), 4), 1.0)

    # Combine: variety is good, repetition is bad
    return 0.6 * variety_score + 0.4 * (1.0 - repetition_penalty)


def chord_type_variety(progression: ChordProgression) -> float:
    """Measure variety in chord types/qualities."""
    if not progression.chords:
        return 0.0
    types = {tuple(c.intervals) for c in progression.chords}
    return min(len(types) / 3.0, 1.0)  # 3 different types is good variety


def root_motion_smoothness(progression: ChordProgression) -> float:
    """Measure smoothness of root motion (prefer steps and 4ths/5ths)."""
    if len(progression.chords) < 2:
        return 0.5
    
    smooth_moves = 0
    for i in range(len(progression.chords) - 1):
        interval = abs(progression.chords[i].root_degree - progression.chords[i + 1].root_degree)
        # Wrapping around: intervals > 3 might be closer the other way
        if interval > 3:
            interval = 7 - interval
        # 1, 2, 3 steps are smooth; 4ths (3) and 5ths (4) are also common
        if interval <= 3 or interval == 4:
            smooth_moves += 1
    
    return smooth_moves / (len(progression.chords) - 1)


def functional_harmony_score(progression: ChordProgression) -> float:
    """Score based on functional harmony (I, IV, V relationships)."""
    if not progression.chords:
        return 0.0
    
    # Common functional progressions (by root degree)
    # 0 = I (tonic), 3 = IV (subdominant), 4 = V (dominant)
    strong_roots = {0, 3, 4}  # I, IV, V
    secondary_roots = {1, 5}  # ii, vi
    
    score = 0.0
    for chord in progression.chords:
        if chord.root_degree in strong_roots:
            score += 1.0
        elif chord.root_degree in secondary_roots:
            score += 0.7
        else:
            score += 0.4
    
    return score / len(progression.chords)


def resolution_bonus(progression: ChordProgression) -> float:
    """Bonus for ending on tonic (I) or having V-I resolution."""
    if not progression.chords:
        return 0.0
    
    score = 0.0
    
    # Bonus for ending on tonic
    if progression.chords[-1].root_degree == 0:
        score += 0.5
    
    # Bonus for V-I resolution anywhere
    for i in range(len(progression.chords) - 1):
        if (progression.chords[i].root_degree == 4 and 
            progression.chords[i + 1].root_degree == 0):
            score += 0.25
    
    # Bonus for ii-V-I
    for i in range(len(progression.chords) - 2):
        if (progression.chords[i].root_degree == 1 and 
            progression.chords[i + 1].root_degree == 4 and
            progression.chords[i + 2].root_degree == 0):
            score += 0.25
    
    return min(score, 1.0)


# === Genre-Specific Chord Fitness ===

class PopChordFitness(ChordFitnessFunction):
    """Fitness for pop music: simple progressions, major/minor, functional harmony."""
    
    def evaluate(self, progression: ChordProgression) -> float:
        if not progression.chords:
            return 0.0
        
        score = (
            0.30 * functional_harmony_score(progression) +
            0.25 * self._simple_chord_bonus(progression) +
            0.20 * resolution_bonus(progression) +
            0.15 * root_motion_smoothness(progression) +
            0.10 * chord_variety(progression)
        )
        return score
    
    def _simple_chord_bonus(self, progression: ChordProgression) -> float:
        """Reward simple major/minor triads."""
        simple_types = {(0, 4, 7), (0, 3, 7)}  # major, minor
        simple_count = sum(1 for c in progression.chords if tuple(c.intervals) in simple_types)
        return simple_count / len(progression.chords)


class JazzChordFitness(ChordFitnessFunction):
    """Fitness for jazz: 7th chords, ii-V-I, chromatic movement, extensions."""
    
    def evaluate(self, progression: ChordProgression) -> float:
        if not progression.chords:
            return 0.0
        
        score = (
            0.30 * self._seventh_chord_bonus(progression) +
            0.25 * resolution_bonus(progression) +  # ii-V-I is important
            0.20 * chord_type_variety(progression) +
            0.15 * self._voice_leading_score(progression) +
            0.10 * chord_variety(progression)
        )
        return score
    
    def _seventh_chord_bonus(self, progression: ChordProgression) -> float:
        """Reward 7th chords and extensions."""
        seventh_count = sum(1 for c in progression.chords if len(c.intervals) >= 4)
        return seventh_count / len(progression.chords)
    
    def _voice_leading_score(self, progression: ChordProgression) -> float:
        """Reward smooth voice leading between chords."""
        if len(progression.chords) < 2:
            return 0.5
        
        smooth_transitions = 0
        for i in range(len(progression.chords) - 1):
            # Compare interval sets - smaller differences = smoother
            c1_intervals = set(progression.chords[i].intervals)
            c2_intervals = set(progression.chords[i + 1].intervals)
            common = len(c1_intervals & c2_intervals)
            if common >= 1:  # At least one common tone
                smooth_transitions += 1
        
        return smooth_transitions / (len(progression.chords) - 1)


class BluesChordFitness(ChordFitnessFunction):
    """Fitness for blues: dom7 chords, I-IV-V, 12-bar structure."""
    
    def evaluate(self, progression: ChordProgression) -> float:
        if not progression.chords:
            return 0.0
        
        score = (
            0.35 * self._dominant_seventh_bonus(progression) +
            0.30 * self._blues_progression_score(progression) +
            0.20 * functional_harmony_score(progression) +
            0.15 * resolution_bonus(progression)
        )
        return score
    
    def _dominant_seventh_bonus(self, progression: ChordProgression) -> float:
        """Reward dominant 7th chords (blues uses dom7 on I, IV, V)."""
        dom7_intervals = (0, 4, 7, 10)
        dom7_count = sum(1 for c in progression.chords 
                         if len(c.intervals) >= 4 and tuple(c.intervals[:4]) == dom7_intervals)
        return dom7_count / len(progression.chords)
    
    def _blues_progression_score(self, progression: ChordProgression) -> float:
        """Reward I, IV, V root movements typical in blues."""
        blues_roots = {0, 3, 4}  # I, IV, V
        blues_count = sum(1 for c in progression.chords if c.root_degree in blues_roots)
        return blues_count / len(progression.chords)


class RockChordFitness(ChordFitnessFunction):
    """Fitness for rock: power chords, simple progressions, energy."""
    
    def evaluate(self, progression: ChordProgression) -> float:
        if not progression.chords:
            return 0.0
        
        score = (
            0.30 * self._power_chord_bonus(progression) +
            0.25 * functional_harmony_score(progression) +
            0.20 * self._repetition_bonus(progression) +
            0.15 * root_motion_smoothness(progression) +
            0.10 * chord_variety(progression)
        )
        return score
    
    def _power_chord_bonus(self, progression: ChordProgression) -> float:
        """Reward power chords and simple voicings."""
        # Power chords or simple triads
        simple_intervals = {(0, 7), (0, 4, 7), (0, 3, 7)}
        simple_count = sum(1 for c in progression.chords 
                          if tuple(c.intervals) in simple_intervals)
        return simple_count / len(progression.chords)
    
    def _repetition_bonus(self, progression: ChordProgression) -> float:
        """Reward some repetition (rock often has repeating patterns)."""
        if len(progression.chords) < 2:
            return 0.5
        
        repeats = 0
        for i in range(len(progression.chords) - 1):
            if progression.chords[i].root_degree == progression.chords[i + 1].root_degree:
                repeats += 0.5  # Same root
        
        # Some repetition is good, but not too much
        ratio = repeats / (len(progression.chords) - 1)
        return 1.0 if 0.1 <= ratio <= 0.4 else max(0, 1 - abs(ratio - 0.25) * 2)


class MetalChordFitness(ChordFitnessFunction):
    """Fitness for metal: power chords, tritones, chromatic movement."""
    
    def evaluate(self, progression: ChordProgression) -> float:
        if not progression.chords:
            return 0.0
        
        score = (
            0.35 * self._power_chord_bonus(progression) +
            0.25 * self._dark_intervals_bonus(progression) +
            0.20 * self._chromatic_root_motion(progression) +
            0.20 * chord_variety(progression)
        )
        return score
    
    def _power_chord_bonus(self, progression: ChordProgression) -> float:
        """Power chords are essential in metal."""
        power_intervals = {(0, 7), (0, 7, 12)}  # 5th, octave
        power_count = sum(1 for c in progression.chords 
                         if len(c.intervals) <= 3 and 7 in c.intervals)
        return power_count / len(progression.chords)
    
    def _dark_intervals_bonus(self, progression: ChordProgression) -> float:
        """Reward tritones, minor 2nds, and other dark intervals."""
        dark_intervals = {1, 6, 8}  # m2, tritone, aug5
        dark_count = 0
        for c in progression.chords:
            if any(i in dark_intervals for i in c.intervals):
                dark_count += 1
        return min(dark_count / len(progression.chords), 1.0)
    
    def _chromatic_root_motion(self, progression: ChordProgression) -> float:
        """Reward chromatic or tritone root movement."""
        if len(progression.chords) < 2:
            return 0.5
        
        chromatic_moves = 0
        for i in range(len(progression.chords) - 1):
            interval = abs(progression.chords[i].root_degree - progression.chords[i + 1].root_degree)
            if interval == 1 or interval == 6 or interval == 3:  # step, tritone, m3
                chromatic_moves += 1
        
        return chromatic_moves / (len(progression.chords) - 1)


class AmbientChordFitness(ChordFitnessFunction):
    """Fitness for ambient: suspended chords, slow changes, open voicings."""

    def evaluate(self, progression: ChordProgression) -> float:
        if not progression.chords:
            return 0.0

        # Minimum variety requirement - at least 2 different chords
        if chord_variety(progression) < 0.3:
            return 0.3  # Cap fitness if too repetitive

        score = (
            0.30 * self._suspended_chord_bonus(progression) +
            0.25 * self._open_voicing_bonus(progression) +
            0.25 * root_motion_smoothness(progression) +
            0.10 * self._static_bonus(progression) +
            0.10 * chord_variety(progression)
        )
        return score
    
    def _suspended_chord_bonus(self, progression: ChordProgression) -> float:
        """Reward sus2, sus4, and add9 chords."""
        sus_intervals = {(0, 2, 7), (0, 5, 7), (0, 4, 7, 14)}  # sus2, sus4, add9
        sus_count = sum(1 for c in progression.chords if tuple(c.intervals) in sus_intervals)
        return sus_count / len(progression.chords)
    
    def _open_voicing_bonus(self, progression: ChordProgression) -> float:
        """Reward open voicings (larger intervals between notes)."""
        open_count = 0
        for c in progression.chords:
            if len(c.intervals) >= 2:
                max_gap = max(c.intervals[i+1] - c.intervals[i] 
                             for i in range(len(c.intervals) - 1))
                if max_gap >= 5:  # At least a 4th between some notes
                    open_count += 1
        return open_count / len(progression.chords) if progression.chords else 0.0
    
    def _static_bonus(self, progression: ChordProgression) -> float:
        """Reward less movement (ambient tends to be static)."""
        if len(progression.chords) < 2:
            return 1.0
        
        static_count = 0
        for i in range(len(progression.chords) - 1):
            if progression.chords[i].root_degree == progression.chords[i + 1].root_degree:
                static_count += 1
        
        return static_count / (len(progression.chords) - 1)


class ElectronicChordFitness(ChordFitnessFunction):
    """Fitness for electronic: simple chords, minor keys, build tension."""
    
    def evaluate(self, progression: ChordProgression) -> float:
        if not progression.chords:
            return 0.0
        
        score = (
            0.30 * self._minor_chord_preference(progression) +
            0.25 * self._simple_voicing_bonus(progression) +
            0.20 * self._tension_build(progression) +
            0.15 * chord_variety(progression) +
            0.10 * root_motion_smoothness(progression)
        )
        return score
    
    def _minor_chord_preference(self, progression: ChordProgression) -> float:
        """Electronic music often uses minor chords."""
        minor_intervals = {(0, 3, 7), (0, 3, 7, 10)}  # minor, minor7
        minor_count = sum(1 for c in progression.chords 
                         if tuple(c.intervals) in minor_intervals)
        return minor_count / len(progression.chords)
    
    def _simple_voicing_bonus(self, progression: ChordProgression) -> float:
        """Reward simple 3-note voicings."""
        simple_count = sum(1 for c in progression.chords if len(c.intervals) == 3)
        return simple_count / len(progression.chords)
    
    def _tension_build(self, progression: ChordProgression) -> float:
        """Reward progressions that build tension then resolve."""
        if len(progression.chords) < 3:
            return 0.5
        
        # Check for movement away from then back to tonic
        away_from_tonic = False
        returned = False
        
        for i, c in enumerate(progression.chords):
            if i == 0 and c.root_degree == 0:
                continue
            if c.root_degree != 0:
                away_from_tonic = True
            if away_from_tonic and c.root_degree == 0:
                returned = True
        
        return 1.0 if (away_from_tonic and returned) else 0.5


# Registry for easy access
CHORD_FITNESS_FUNCTIONS = {
    "pop": PopChordFitness,
    "jazz": JazzChordFitness,
    "blues": BluesChordFitness,
    "rock": RockChordFitness,
    "metal": MetalChordFitness,
    "ambient": AmbientChordFitness,
    "electronic": ElectronicChordFitness,
}
