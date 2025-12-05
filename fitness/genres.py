from .base import (
    FitnessFunction,
    note_variety,
    rest_ratio,
    interval_smoothness,
    scale_adherence,
    rhythmic_variety,
    syncopation_score,
    contour_direction,
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
                0.40 * scale_adherence(phrase, MAJOR_SCALE)
                + 0.20 * interval_smoothness(phrase)
                + 0.15 * (1 - rest_ratio(phrase))
                + 0.10 * contour_direction(phrase)  # Pop likes smooth arcs
                + 0.15 * rhythmic_variety(phrase)
            )
            scores.append(score)

        return sum(scores) / len(scores)


class JazzFitness(FitnessFunction):
    """Fitness for jazz: chromatic movement, syncopation, variety."""

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            score = (
                0.20 * note_variety(phrase)
                + 0.15 * rhythmic_variety(phrase)
                + 0.20 * self._chromatic_interest(phrase)
                + 0.15 * (0.5 + 0.5 * rest_ratio(phrase))
                + 0.30 * syncopation_score(phrase)  # Jazz relies heavily on syncopation
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


class BluesFitness(FitnessFunction):
    """Fitness for blues: blue notes, bends, call-response."""

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            score = (
                0.35 * scale_adherence(phrase, BLUES_SCALE)
                + 0.25 * self._blue_note_bonus(phrase)
                + 0.20 * interval_smoothness(phrase)
                + 0.20 * syncopation_score(phrase)  # Blues has a swing/syncopation feel
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
        ratio = blue_count / len(notes)
        # We want "some" blue notes (20-40%), not ALL blue notes
        return 1.0 if 0.2 <= ratio <= 0.4 else max(0, 1 - abs(ratio - 0.3) * 2)


class AmbientFitness(FitnessFunction):
    """Fitness for ambient: long notes, slow movement, sparse."""

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            score = (
                0.35 * self._long_note_ratio(phrase)
                + 0.25 * interval_smoothness(phrase)
                + 0.20 * rest_ratio(phrase)
                + 0.20 * scale_adherence(phrase, PENTATONIC)
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _long_note_ratio(self, phrase: Phrase) -> float:
        """Reward longer note durations."""
        if not phrase.notes:
            return 0.0
        # Assuming duration 1.0 is a quarter note, ambient likes whole notes (4.0) or longer
        long_notes = sum(1 for n in phrase.notes if n.duration >= 2.0)
        return long_notes / len(phrase.notes)


# Registry for easy access
FITNESS_FUNCTIONS = {
    "pop": PopFitness,
    "jazz": JazzFitness,
    "blues": BluesFitness,
    "ambient": AmbientFitness,
}
