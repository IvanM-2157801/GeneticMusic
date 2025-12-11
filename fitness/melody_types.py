"""Fitness functions for different melody types: melodic (varied) vs stable (smooth)."""

from .base import (
    FitnessFunction,
    interval_smoothness,
    note_variety,
    rest_ratio,
    scale_adherence,
)
from core.music import Layer, NoteName


class MelodicFitness(FitnessFunction):
    """Fitness for melodic lines: varied intervals, interesting jumps, expressive.

    Characteristics:
    - Large intervals (jumps, leaps)
    - High note variety
    - Less concern for smoothness
    - Expressive, attention-grabbing
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            # Heavily penalize phrases with too many rests
            rest_penalty = rest_ratio(phrase)
            if rest_penalty > 0.7:  # More than 70% rests
                return 0.1  # Very low score
            if rest_penalty > 0.5:  # More than 50% rests
                rest_penalty = 0.5  # Cap the penalty

            # Calculate interval variety
            interval_variety = self._interval_variety(phrase)

            score = (
                0.30 * interval_variety  # Favor varied/large intervals
                + 0.25 * note_variety(phrase)  # High note variety
                + 0.20 * (1 - interval_smoothness(phrase))  # Allow large jumps
                + 0.15 * self._octave_usage(phrase)  # Use wide range
                + 0.10 * (1 - rest_penalty)  # Penalize rests more
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _interval_variety(self, phrase) -> float:
        """Reward varied interval sizes."""
        from core.music import NoteName

        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.0

        intervals = []
        for i in range(len(notes) - 1):
            interval = abs(notes[i].midi_pitch - notes[i + 1].midi_pitch)
            intervals.append(interval)

        if not intervals:
            return 0.0

        # Reward larger intervals and variety
        avg_interval = sum(intervals) / len(intervals)
        unique_intervals = len(set(intervals))

        # Normalize: larger intervals (up to 12 semitones) are better
        interval_size_score = min(avg_interval / 7.0, 1.0)  # Target ~7 semitones avg
        variety_score = min(unique_intervals / len(intervals), 1.0)

        return 0.6 * interval_size_score + 0.4 * variety_score

    def _octave_usage(self, phrase) -> float:
        """Reward usage of wide pitch range."""
        from core.music import NoteName

        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if not notes:
            return 0.0

        pitches = [n.midi_pitch for n in notes]
        pitch_range = max(pitches) - min(pitches)

        # Normalize to octave (12 semitones)
        return min(pitch_range / 12.0, 1.0)


class StableFitness(FitnessFunction):
    """Fitness for stable synth lines: smooth intervals, consistent, supportive.

    Characteristics:
    - Small intervals (stepwise motion)
    - High smoothness
    - Consistent note patterns
    - Background/supportive role
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            # Heavily penalize phrases with too many rests
            rest_penalty = rest_ratio(phrase)
            if rest_penalty > 0.7:  # More than 70% rests
                return 0.1  # Very low score
            if rest_penalty > 0.5:  # More than 50% rests
                rest_penalty = 0.5  # Cap the penalty

            score = (
                0.35 * interval_smoothness(phrase)  # Very smooth
                + 0.25 * self._stepwise_motion(phrase)  # Prefer steps over jumps
                + 0.15
                * scale_adherence(phrase, self._get_major_scale())  # Stay in scale
                + 0.10 * self._narrow_range(phrase)  # Stay in narrow range
                + 0.15 * (1 - rest_penalty)  # Penalize rests more
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _stepwise_motion(self, phrase) -> float:
        """Reward stepwise motion (intervals of 1-2 semitones)."""
        from core.music import NoteName

        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.0

        stepwise_count = 0
        for i in range(len(notes) - 1):
            interval = abs(notes[i].midi_pitch - notes[i + 1].midi_pitch)
            if interval <= 2:  # Step (1-2 semitones)
                stepwise_count += 1

        return stepwise_count / (len(notes) - 1) if len(notes) > 1 else 0.0

    def _narrow_range(self, phrase) -> float:
        """Reward narrow pitch range (stays in small area)."""
        from core.music import NoteName

        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if not notes:
            return 0.0

        pitches = [n.midi_pitch for n in notes]
        pitch_range = max(pitches) - min(pitches)

        # Reward range of 5-7 semitones (about a fifth)
        if pitch_range <= 7:
            return 1.0 - (pitch_range / 12.0)
        else:
            return max(0, 1.0 - (pitch_range / 24.0))

    def _get_major_scale(self):
        """Get major scale notes."""
        return [
            NoteName.C,
            NoteName.D,
            NoteName.E,
            NoteName.F,
            NoteName.G,
            NoteName.A,
            NoteName.B,
        ]


class ChordFitness(FitnessFunction):
    """Fitness for chord-based melodies: sustained harmonies, simple progressions.

    Characteristics:
    - Fewer, longer notes (sustained)
    - Triadic intervals (thirds, fifths)
    - Simple, meditative
    - Minimal rests
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            # Heavily penalize phrases with too many rests
            rest_penalty = rest_ratio(phrase)
            if rest_penalty > 0.7:  # More than 70% rests
                return 0.1  # Very low score
            if rest_penalty > 0.5:  # More than 50% rests
                rest_penalty = 0.5  # Cap the penalty

            # Reward triadic intervals (3, 4, 7 semitones - thirds and fifths)
            triadic_score = self._triadic_intervals(phrase)

            # Reward sustained notes (fewer unique notes, more repetition)
            sustained_score = 1.0 - note_variety(phrase)

            score = (
                0.35 * triadic_score  # Favor thirds and fifths
                + 0.25 * sustained_score  # Sustained/repeated notes
                + 0.20 * self._narrow_range(phrase)  # Stay in narrow range
                + 0.15 * (1 - rest_penalty)  # Penalize rests
                + 0.05 * interval_smoothness(phrase)  # Some smoothness
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _triadic_intervals(self, phrase) -> float:
        """Reward triadic intervals (thirds and fifths)."""
        from core.music import NoteName

        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.0

        triadic_intervals = {
            3,
            4,
            7,
            8,
        }  # Minor third, major third, perfect fifth, minor sixth
        triadic_count = 0
        total_intervals = 0

        for i in range(len(notes) - 1):
            interval = abs(notes[i].midi_pitch - notes[i + 1].midi_pitch) % 12
            total_intervals += 1
            if interval in triadic_intervals:
                triadic_count += 1

        return triadic_count / total_intervals if total_intervals > 0 else 0.0

    def _narrow_range(self, phrase) -> float:
        """Reward narrow pitch range (stays in small area)."""
        from core.music import NoteName

        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if not notes:
            return 0.0

        pitches = [n.midi_pitch for n in notes]
        pitch_range = max(pitches) - min(pitches)

        # Reward range of 7-12 semitones (about an octave)
        if pitch_range <= 12:
            return 1.0 - (pitch_range / 24.0)
        else:
            return max(0, 1.0 - (pitch_range / 36.0))
