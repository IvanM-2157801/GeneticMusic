"""Fitness functions for different melody structural archetypes."""

from .base import (
    FitnessFunction,
    interval_smoothness,
    note_variety,
    rest_ratio,
    scale_adherence,
    tonic_resolution,
    contour_direction,
    syncopation_score,
)
from core.music import Layer, NoteName


class MelodicFitness(FitnessFunction):
    """
    Fitness for expressive melodic lines.
    Characteristics: Varied intervals, interesting jumps, expressive range.
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            rest_penalty = rest_ratio(phrase)
            if rest_penalty > 0.7:
                return 0.1
            if rest_penalty > 0.5:
                rest_penalty = 0.5

            interval_variety = self._interval_variety(phrase)

            score = (
                0.30 * interval_variety
                + 0.25 * note_variety(phrase)
                + 0.20 * (1 - interval_smoothness(phrase))
                + 0.15 * self._octave_usage(phrase)
                + 0.10 * (1 - rest_penalty)
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _interval_variety(self, phrase) -> float:
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.0

        intervals = [
            abs(notes[i].midi_pitch - notes[i + 1].midi_pitch)
            for i in range(len(notes) - 1)
        ]
        if not intervals:
            return 0.0

        avg_interval = sum(intervals) / len(intervals)
        unique_intervals = len(set(intervals))

        interval_size_score = min(avg_interval / 7.0, 1.0)
        variety_score = min(unique_intervals / len(intervals), 1.0)

        return 0.6 * interval_size_score + 0.4 * variety_score

    def _octave_usage(self, phrase) -> float:
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if not notes:
            return 0.0
        pitches = [n.midi_pitch for n in notes]
        return min((max(pitches) - min(pitches)) / 12.0, 1.0)


class StableFitness(FitnessFunction):
    """
    Fitness for stable synth/bass lines.
    Characteristics: Smooth, stepwise, root-note oriented.
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            rest_penalty = rest_ratio(phrase)
            if rest_penalty > 0.7:
                return 0.1
            if rest_penalty > 0.5:
                rest_penalty = 0.5

            score = (
                0.35 * interval_smoothness(phrase)
                + 0.25 * self._stepwise_motion(phrase)
                + 0.15 * scale_adherence(phrase, self._get_major_scale())
                + 0.10 * self._narrow_range(phrase)
                + 0.15 * (1 - rest_penalty)
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _stepwise_motion(self, phrase) -> float:
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.0
        stepwise = sum(
            1
            for i in range(len(notes) - 1)
            if abs(notes[i].midi_pitch - notes[i + 1].midi_pitch) <= 2
        )
        return stepwise / (len(notes) - 1)

    def _narrow_range(self, phrase) -> float:
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if not notes:
            return 0.0
        r = max(n.midi_pitch for n in notes) - min(n.midi_pitch for n in notes)
        return 1.0 - (r / 12.0) if r <= 7 else max(0, 1.0 - (r / 24.0))

    def _get_major_scale(self):
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
    """
    Fitness for arpeggios or pads.
    Characteristics: Triadic intervals (3rds, 5ths), sustained notes.
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            rest_penalty = rest_ratio(phrase)
            if rest_penalty > 0.7:
                return 0.1
            if rest_penalty > 0.5:
                rest_penalty = 0.5

            triadic_score = self._triadic_intervals(phrase)
            sustained_score = 1.0 - note_variety(phrase)

            score = (
                0.35 * triadic_score
                + 0.25 * sustained_score
                + 0.20 * self._narrow_range(phrase)
                + 0.15 * (1 - rest_penalty)
                + 0.05 * interval_smoothness(phrase)
            )
            scores.append(score)

        return sum(scores) / len(scores)

    def _triadic_intervals(self, phrase) -> float:
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if len(notes) < 2:
            return 0.0
        triads = {3, 4, 7, 8}
        count = sum(
            1
            for i in range(len(notes) - 1)
            if (abs(notes[i].midi_pitch - notes[i + 1].midi_pitch) % 12) in triads
        )
        return count / (len(notes) - 1)

    def _narrow_range(self, phrase) -> float:
        notes = [n for n in phrase.notes if n.pitch != NoteName.REST]
        if not notes:
            return 0.0
        r = max(n.midi_pitch for n in notes) - min(n.midi_pitch for n in notes)
        return 1.0 - (r / 24.0) if r <= 12 else max(0, 1.0 - (r / 36.0))


class LeadArcFitness(FitnessFunction):
    """
    Generates melodies with a clear 'Story Arc'.
    Starts, moves away, and resolves. Best for solos.
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            # 1. Shape: Prefer consistent motion over zig-zags
            shape_score = contour_direction(phrase)

            # 2. Resolution: Does it end on the root? (Assuming C is root here)
            # ideally root_pitch should be passed in context
            resolution_score = tonic_resolution(phrase, NoteName.C)

            # 3. Interest: Good interval variety but controlled
            interest_score = min(note_variety(phrase) * 1.5, 1.0)

            score = 0.3 * shape_score + 0.4 * resolution_score + 0.3 * interest_score
            scores.append(score)

        return sum(scores) / len(scores)


class RhythmicMotifFitness(FitnessFunction):
    """
    Focuses on rhythmic repetition and groove.
    Pitch matters less; the rhythmic pattern is king. Best for Bass/Hooks.
    """

    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0

        scores = []
        for phrase in layer.phrases:
            # 1. Groove: Is it syncopated?
            groove = syncopation_score(phrase)

            # 2. Repetition check (first half vs second half duration pattern)
            durations = [n.duration for n in phrase.notes]
            repetition_bonus = 0.0
            if len(durations) > 4:
                mid = len(durations) // 2
                first_half = durations[:mid]
                # Try to match length of first half
                second_half = durations[mid : mid + len(first_half)]
                if first_half == second_half:
                    repetition_bonus = 1.0

            # 3. Rest Ratio: Rhythmic hooks need space
            r_ratio = rest_ratio(phrase)
            spacing_score = 1.0 - abs(0.25 - r_ratio)

            score = 0.4 * groove + 0.3 * repetition_bonus + 0.3 * spacing_score
            scores.append(score)

        return sum(scores) / len(scores)
