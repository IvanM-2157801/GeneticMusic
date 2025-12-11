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
                0.50 * scale_adherence(phrase, MAJOR_SCALE) +
                0.25 * interval_smoothness(phrase) +
                0.12 * (1 - rest_ratio(phrase)) +  # Prefer fewer rests
                # 0.10 * self._repetition_bonus(phrase) +
                0.13 * rhythmic_variety(phrase)
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
    """Fitness for ambient: smooth movement, consonant intervals, meditative.

    Key characteristics:
    - Very smooth interval movement (stepwise or small jumps)
    - Pentatonic scale adherence for consonance
    - Narrow pitch range (stays in comfortable zone)
    - Some notes required (not all rests)
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            # Must have actual notes, not just rests
            non_rest_notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
            if len(non_rest_notes) < 2:
                scores.append(0.2)  # Penalize phrases with too few notes
                continue

            # Ambient should be smooth and consonant
            smoothness = interval_smoothness(phrase)

            # Pentatonic adherence for that ethereal sound
            pentatonic_score = scale_adherence(phrase, PENTATONIC)

            # Narrow range - ambient stays in comfortable zone
            narrow_range = self._narrow_range_score(phrase)

            # Reward repeated notes (drones, sustained tones)
            drone_score = self._drone_tendency(phrase)

            score = (
                0.35 * smoothness +  # Very smooth movement
                0.25 * pentatonic_score +  # Consonant scale
                0.25 * narrow_range +  # Stay in narrow range
                0.15 * drone_score  # Drone/sustained notes
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _narrow_range_score(self, phrase: Phrase) -> float:
        """Reward narrow pitch range (ambient stays in one zone)."""
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.5

        pitches = [n.midi_pitch for n in notes]
        pitch_range = max(pitches) - min(pitches)

        # Ideal range: 5-8 semitones (perfect fourth to minor sixth)
        if pitch_range <= 5:
            return 1.0
        elif pitch_range <= 8:
            return 0.9
        elif pitch_range <= 12:
            return 0.6
        else:
            return max(0, 1.0 - (pitch_range - 12) / 12)

    def _drone_tendency(self, phrase: Phrase) -> float:
        """Reward repeated notes (drone-like quality)."""
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.5

        # Count consecutive repeated notes
        repeated = 0
        for i in range(len(notes) - 1):
            if notes[i].pitch == notes[i + 1].pitch:
                repeated += 1

        return repeated / (len(notes) - 1) if len(notes) > 1 else 0


class ElectronicFitness(FitnessFunction):
    """Fitness for electronic/EDM melodies: repetitive, arpeggiated, hypnotic.

    Key characteristics:
    - Repetitive patterns (hypnotic)
    - Arpeggiated movement (stepwise with occasional jumps)
    - Minor scale preference for darker sound
    - Consistent note patterns
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            non_rest_notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
            if len(non_rest_notes) < 2:
                scores.append(0.3)
                continue

            # Repetitive patterns are good for electronic
            repetition = self._repetition_score(phrase)

            # Minor scale adherence for darker EDM sound
            minor_score = scale_adherence(phrase, MINOR_SCALE)

            # Arpeggiated movement (mix of steps and thirds)
            arp_score = self._arpeggio_score(phrase)

            # Note variety should be moderate (not too chaotic)
            variety = note_variety(phrase)
            # Target 40-60% variety
            variety_score = 1.0 - abs(0.5 - variety)

            score = (
                0.30 * repetition +  # Hypnotic repetition
                0.25 * minor_score +  # Minor scale
                0.25 * arp_score +  # Arpeggiated movement
                0.20 * variety_score  # Moderate variety
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _repetition_score(self, phrase: Phrase) -> float:
        """Reward repetitive patterns (electronic is hypnotic)."""
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 4:
            return 0.5

        # Check for 2-note and 4-note repeating patterns
        patterns_2 = []
        patterns_4 = []

        for i in range(len(notes) - 1):
            patterns_2.append((notes[i].pitch, notes[i + 1].pitch))

        for i in range(len(notes) - 3):
            patterns_4.append(tuple(n.pitch for n in notes[i:i + 4]))

        # Calculate repetition ratio
        unique_2 = len(set(patterns_2)) / len(patterns_2) if patterns_2 else 1
        unique_4 = len(set(patterns_4)) / len(patterns_4) if patterns_4 else 1

        # Lower unique ratio = more repetition = better
        return (1 - unique_2) * 0.5 + (1 - unique_4) * 0.5

    def _arpeggio_score(self, phrase: Phrase) -> float:
        """Reward arpeggiated movement (steps and thirds)."""
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.5

        good_intervals = 0
        for i in range(len(notes) - 1):
            interval = abs(notes[i].midi_pitch - notes[i + 1].midi_pitch)
            # Arpeggios use steps (1-2), thirds (3-4), and fifths (7)
            if interval in [1, 2, 3, 4, 7]:
                good_intervals += 1

        return good_intervals / (len(notes) - 1) if len(notes) > 1 else 0


# Registry for easy access
FITNESS_FUNCTIONS = {
    "pop": PopFitness,
    "jazz": JazzFitness,
    "blues": BluesFitness,
    "ambient": AmbientFitness,
    "electronic": ElectronicFitness,
}
