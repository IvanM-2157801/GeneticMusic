"""Chord-melody relationship fitness functions.

This module provides fitness functions that evaluate how well melody notes
fit with underlying chord progressions, enabling chord-aware melody evolution.
"""

from core.music import Layer, Phrase, Note, NoteName, HarmonicContext
from fitness.base import FitnessFunction


# Genre-specific chord-melody strictness levels
# 0.0 = free (any scale tone), 1.0 = strict (chord tones only on strong beats)
GENRE_CHORD_STRICTNESS = {
    "pop": 0.8,       # Strict: chord tones on strong beats, scale tones on weak
    "jazz": 0.4,      # Flexible: extensions and chromatic approach allowed
    "blues": 0.6,     # Moderate: chord tones + blue notes
    "ambient": 0.3,   # Very flexible: any scale tone
    "rock": 0.7,      # Moderate-strict: root/5th preferred
    "electronic": 0.5, # Balanced: melodic freedom with harmonic grounding
    "classical": 0.75, # Strict: traditional voice leading
    "funk": 0.6,      # Moderate: groove-oriented with chord awareness
}


class ChordMelodyFitness(FitnessFunction):
    """Evaluates how well melody notes fit with underlying chord progression.

    This fitness function considers:
    - Chord tones on strong beats (high score)
    - Chord extensions on weak beats (medium score)
    - Scale tones (acceptable)
    - Non-chord/non-scale tones (penalized based on strictness)
    - Passing tones between chord tones (allowed if stepwise)
    """

    def __init__(
        self,
        harmonic_context: HarmonicContext,
        strictness: float = 0.7,
        strong_beat_weight: float = 0.6,
        weak_beat_weight: float = 0.4,
    ):
        """Initialize chord-melody fitness.

        Args:
            harmonic_context: The harmonic context with chord progression
            strictness: How strictly to enforce chord tones (0.0-1.0)
            strong_beat_weight: Weight for strong beat evaluation
            weak_beat_weight: Weight for weak beat evaluation
        """
        self.context = harmonic_context
        self.strictness = strictness
        self.strong_beat_weight = strong_beat_weight
        self.weak_beat_weight = weak_beat_weight

    def evaluate(self, layer: Layer) -> float:
        """Evaluate how well the layer's melody fits the chord progression.

        Args:
            layer: The layer to evaluate

        Returns:
            Fitness score from 0.0 to 1.0
        """
        if not layer.phrases or not self.context:
            return 0.5  # Neutral score if no data

        all_notes = []
        for phrase in layer.phrases:
            all_notes.extend(phrase.notes)

        if not all_notes:
            return 0.5

        strong_beat_scores = []
        weak_beat_scores = []

        beat_position = 0.0
        for note in all_notes:
            if note.pitch == NoteName.REST:
                beat_position += note.duration
                continue

            # Determine if this is a strong or weak beat
            is_strong_beat = self._is_strong_beat(beat_position)
            score = self._score_note(note, int(beat_position), is_strong_beat)

            if is_strong_beat:
                strong_beat_scores.append(score)
            else:
                weak_beat_scores.append(score)

            beat_position += note.duration

        # Combine scores
        strong_score = sum(strong_beat_scores) / len(strong_beat_scores) if strong_beat_scores else 0.5
        weak_score = sum(weak_beat_scores) / len(weak_beat_scores) if weak_beat_scores else 0.5

        return (
            self.strong_beat_weight * strong_score +
            self.weak_beat_weight * weak_score
        )

    def _is_strong_beat(self, beat_position: float) -> bool:
        """Determine if a beat position is a strong beat.

        Strong beats are typically beats 1 and 3 in 4/4 time.
        """
        beat_in_bar = beat_position % 4
        return beat_in_bar < 0.5 or (2.0 <= beat_in_bar < 2.5)

    def _score_note(self, note: Note, beat: int, is_strong_beat: bool) -> float:
        """Score a single note against the chord at this beat.

        Args:
            note: The note to score
            beat: Current beat position
            is_strong_beat: Whether this is a strong beat

        Returns:
            Score from 0.0 to 1.0
        """
        if note.pitch == NoteName.REST:
            return 0.8  # Rests are generally fine

        # Check if chord tone
        if self.context.is_chord_tone(note, beat):
            return 1.0  # Perfect: chord tone

        # Check if extension (more valuable on weak beats)
        if self.context.is_extension(note, beat):
            if is_strong_beat:
                # Extensions on strong beats: penalize slightly based on strictness
                return 1.0 - (self.strictness * 0.3)
            else:
                return 0.9  # Extensions on weak beats are good

        # Check if scale tone
        if self._is_scale_tone(note):
            if is_strong_beat:
                # Non-chord scale tones on strong beats: penalize based on strictness
                return 1.0 - (self.strictness * 0.5)
            else:
                return 0.7  # Scale tones on weak beats are acceptable

        # Non-scale tone (chromatic)
        if is_strong_beat:
            # Chromatic on strong beats: heavily penalized
            return 1.0 - (self.strictness * 0.8)
        else:
            # Chromatic on weak beats: might be passing tone
            return 0.5 - (self.strictness * 0.3)

    def _is_scale_tone(self, note: Note) -> bool:
        """Check if a note is in the current scale."""
        scale_intervals = {
            "major": {0, 2, 4, 5, 7, 9, 11},
            "minor": {0, 2, 3, 5, 7, 8, 10},
            "dorian": {0, 2, 3, 5, 7, 9, 10},
            "mixolydian": {0, 2, 4, 5, 7, 9, 10},
            "blues": {0, 3, 5, 6, 7, 10},
        }

        scale = scale_intervals.get(self.context.scale_type, scale_intervals["major"])
        note_semitone = note.pitch.value % 12
        return note_semitone in scale


class CompositeHarmonyFitness(FitnessFunction):
    """Combines chord-melody fitness with intrinsic melody fitness.

    This wrapper allows combining harmonic awareness with genre-specific
    melodic qualities (like interval smoothness, variety, etc.)
    """

    def __init__(
        self,
        intrinsic_fitness: FitnessFunction,
        harmonic_context: HarmonicContext,
        strictness: float = 0.7,
        harmony_weight: float = 0.4,
    ):
        """Initialize composite harmony fitness.

        Args:
            intrinsic_fitness: The base melody fitness function
            harmonic_context: The harmonic context with chords
            strictness: Chord-melody strictness (0.0-1.0)
            harmony_weight: Weight for harmonic fitness (0.0-1.0)
        """
        self.intrinsic_fitness = intrinsic_fitness
        self.chord_melody_fitness = ChordMelodyFitness(
            harmonic_context=harmonic_context,
            strictness=strictness,
        )
        self.harmony_weight = harmony_weight

    def evaluate(self, layer: Layer) -> float:
        """Evaluate with both intrinsic and harmonic fitness.

        Args:
            layer: The layer to evaluate

        Returns:
            Combined fitness score
        """
        intrinsic_score = self.intrinsic_fitness.evaluate(layer)
        harmony_score = self.chord_melody_fitness.evaluate(layer)

        return (
            (1.0 - self.harmony_weight) * intrinsic_score +
            self.harmony_weight * harmony_score
        )


class PassingToneFitness(FitnessFunction):
    """Evaluates melodic lines for proper use of passing tones.

    Passing tones should:
    - Connect chord tones by step
    - Occur on weak beats
    - Be approached and left by step in the same direction
    """

    def __init__(self, harmonic_context: HarmonicContext):
        self.context = harmonic_context

    def evaluate(self, layer: Layer) -> float:
        """Evaluate passing tone usage.

        Args:
            layer: The layer to evaluate

        Returns:
            Fitness score for passing tone usage
        """
        if not layer.phrases or not self.context:
            return 0.5

        all_notes = [n for phrase in layer.phrases for n in phrase.notes
                     if n.pitch != NoteName.REST]

        if len(all_notes) < 3:
            return 0.5

        passing_tone_scores = []

        for i in range(1, len(all_notes) - 1):
            prev_note = all_notes[i - 1]
            curr_note = all_notes[i]
            next_note = all_notes[i + 1]

            # Calculate intervals
            prev_interval = curr_note.midi_pitch - prev_note.midi_pitch
            next_interval = next_note.midi_pitch - curr_note.midi_pitch

            # Check if this could be a passing tone
            beat = i  # Simplified beat calculation
            is_chord_tone = self.context.is_chord_tone(curr_note, beat)

            if not is_chord_tone:
                # Non-chord tone: evaluate as potential passing tone
                # Good passing tone: stepwise approach and departure in same direction
                is_stepwise = abs(prev_interval) <= 2 and abs(next_interval) <= 2
                same_direction = (prev_interval > 0 and next_interval > 0) or \
                                 (prev_interval < 0 and next_interval < 0)

                if is_stepwise and same_direction:
                    passing_tone_scores.append(1.0)  # Good passing tone
                elif is_stepwise:
                    passing_tone_scores.append(0.7)  # Neighbor tone (acceptable)
                else:
                    passing_tone_scores.append(0.3)  # Bad non-chord tone usage

        if not passing_tone_scores:
            return 0.8  # No passing tones needed = fine

        return sum(passing_tone_scores) / len(passing_tone_scores)


class VoiceLeadingFitness(FitnessFunction):
    """Evaluates voice leading in melodic lines.

    Good voice leading includes:
    - Smooth stepwise motion
    - Proper resolution of tendency tones
    - Avoiding awkward leaps
    """

    def __init__(
        self,
        harmonic_context: HarmonicContext,
        prefer_stepwise: float = 0.7,
    ):
        self.context = harmonic_context
        self.prefer_stepwise = prefer_stepwise

    def evaluate(self, layer: Layer) -> float:
        """Evaluate voice leading quality.

        Args:
            layer: The layer to evaluate

        Returns:
            Voice leading fitness score
        """
        if not layer.phrases:
            return 0.5

        all_notes = [n for phrase in layer.phrases for n in phrase.notes
                     if n.pitch != NoteName.REST]

        if len(all_notes) < 2:
            return 0.5

        scores = []

        for i in range(len(all_notes) - 1):
            curr_note = all_notes[i]
            next_note = all_notes[i + 1]

            interval = abs(next_note.midi_pitch - curr_note.midi_pitch)

            # Score based on interval size
            if interval == 0:
                scores.append(0.7)  # Repeated note: okay but not great
            elif interval <= 2:
                scores.append(1.0)  # Stepwise: excellent
            elif interval <= 4:
                scores.append(0.9)  # Small skip: good
            elif interval <= 7:
                scores.append(0.7)  # 4th/5th: acceptable
            elif interval <= 12:
                scores.append(0.5)  # 6th-octave: use sparingly
            else:
                scores.append(0.3)  # Large leap: generally avoid

            # Bonus for resolution of tendency tones (leading tone -> tonic)
            if self.context:
                curr_beat = i
                next_beat = i + 1

                # Check for leading tone resolution
                if self._is_leading_tone(curr_note, curr_beat):
                    if self._is_tonic(next_note, next_beat):
                        scores[-1] = min(1.0, scores[-1] + 0.2)  # Bonus for resolution

        return sum(scores) / len(scores) if scores else 0.5

    def _is_leading_tone(self, note: Note, beat: int) -> bool:
        """Check if note is the leading tone (7th degree)."""
        if note.pitch == NoteName.REST:
            return False

        # Leading tone is 11 semitones above root in major
        scale_intervals = {
            "major": 11,
            "minor": 10,  # Natural minor uses subtonic
        }
        leading_interval = scale_intervals.get(self.context.scale_type, 11)
        return note.pitch.value % 12 == leading_interval

    def _is_tonic(self, note: Note, beat: int) -> bool:
        """Check if note is the tonic (root)."""
        if note.pitch == NoteName.REST:
            return False
        return note.pitch.value % 12 == 0  # Assuming C-based scale degrees


def create_harmony_fitness(
    intrinsic_fitness: FitnessFunction,
    harmonic_context: HarmonicContext,
    genre: str = "pop",
    harmony_weight: float = 0.4,
) -> FitnessFunction:
    """Factory function to create genre-appropriate harmony fitness.

    Args:
        intrinsic_fitness: Base melody fitness function
        harmonic_context: Chord progression context
        genre: Genre name for strictness lookup
        harmony_weight: How much to weight harmonic fit (0.0-1.0)

    Returns:
        Composite fitness function combining intrinsic and harmonic fitness
    """
    strictness = GENRE_CHORD_STRICTNESS.get(genre.lower(), 0.6)

    return CompositeHarmonyFitness(
        intrinsic_fitness=intrinsic_fitness,
        harmonic_context=harmonic_context,
        strictness=strictness,
        harmony_weight=harmony_weight,
    )
