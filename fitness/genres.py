from .base import (
    FitnessFunction,
    note_variety,
    rest_ratio,
    interval_smoothness,
    scale_adherence,
    rhythmic_variety,
    MAJOR_SCALE,
    MINOR_SCALE,
    PENTATONIC,
    BLUES_SCALE,
)
from core.music import Layer, Phrase, NoteName


class PopFitness(FitnessFunction):
    """Fitness for pop music: catchy, repetitive, major key."""
    
    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0
        
        scores = []
        for phrase in layer.phrases:
            score = (
                0.3 * scale_adherence(phrase, MAJOR_SCALE) +
                0.2 * interval_smoothness(phrase) +
                0.2 * (1 - rest_ratio(phrase)) +  # Prefer fewer rests
                0.15 * self._repetition_bonus(phrase) +
                0.15 * rhythmic_variety(phrase)
            )
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    def _repetition_bonus(self, phrase: Phrase) -> float:
        """Reward repeated motifs."""
        if len(phrase.notes) < 4:
            return 0.0
        # Check for 2-note patterns
        patterns = []
        for i in range(len(phrase.notes) - 1):
            p = (phrase.notes[i].pitch, phrase.notes[i + 1].pitch)
            patterns.append(p)
        
        unique = len(set(patterns))
        return 1 - (unique / len(patterns)) if patterns else 0.0


class JazzFitness(FitnessFunction):
    """Fitness for jazz: chromatic movement, syncopation, variety."""
    
    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0
        
        scores = []
        for phrase in layer.phrases:
            score = (
                0.25 * note_variety(phrase) +
                0.25 * rhythmic_variety(phrase) +
                0.2 * self._chromatic_interest(phrase) +
                0.15 * (0.5 + 0.5 * rest_ratio(phrase)) +  # Some rests good
                0.15 * self._syncopation_score(phrase)
            )
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    def _chromatic_interest(self, phrase: Phrase) -> float:
        """Reward chromatic passing tones."""
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.0
        
        semitone_moves = 0
        for i in range(len(notes) - 1):
            if abs(notes[i].midi_pitch - notes[i + 1].midi_pitch) == 1:
                semitone_moves += 1
        
        return min(semitone_moves / (len(notes) - 1) * 2, 1.0)
    
    def _syncopation_score(self, phrase: Phrase) -> float:
        """Reward off-beat rhythms."""
        odd_durations = sum(1 for n in phrase.notes if n.duration in [0.25, 0.75])
        return min(odd_durations / max(len(phrase.notes), 1), 1.0)


class BluesFitness(FitnessFunction):
    """Fitness for blues: blue notes, bends, call-response."""
    
    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0
        
        scores = []
        for phrase in layer.phrases:
            score = (
                0.35 * scale_adherence(phrase, BLUES_SCALE) +
                0.25 * self._blue_note_bonus(phrase) +
                0.2 * interval_smoothness(phrase) +
                0.2 * rhythmic_variety(phrase)
            )
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    def _blue_note_bonus(self, phrase: Phrase) -> float:
        """Reward blue notes (b3, b5, b7)."""
        blue_notes = {NoteName.DS, NoteName.FS, NoteName.AS}
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if not notes:
            return 0.0
        
        blue_count = sum(1 for n in notes if n.pitch in blue_notes)
        # Want some but not all
        ratio = blue_count / len(notes)
        return 1.0 if 0.2 <= ratio <= 0.4 else max(0, 1 - abs(ratio - 0.3) * 2)


class AmbientFitness(FitnessFunction):
    """Fitness for ambient: long notes, slow movement, sparse."""
    
    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0
        
        scores = []
        for phrase in layer.phrases:
            score = (
                0.3 * self._long_note_ratio(phrase) +
                0.3 * interval_smoothness(phrase) +
                0.2 * rest_ratio(phrase) +  # Rests are good
                0.2 * scale_adherence(phrase, PENTATONIC)
            )
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    def _long_note_ratio(self, phrase: Phrase) -> float:
        """Reward longer note durations."""
        if not phrase.notes:
            return 0.0
        long_notes = sum(1 for n in phrase.notes if n.duration >= 1.0)
        return long_notes / len(phrase.notes)


# Registry for easy access
FITNESS_FUNCTIONS = {
    "pop": PopFitness,
    "jazz": JazzFitness,
    "blues": BluesFitness,
    "ambient": AmbientFitness,
}
