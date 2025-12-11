"""Musical development fitness functions.

This module provides fitness functions for evaluating variations of themes,
enabling musically coherent development throughout a composition.

Key concepts:
- Theme recognition: variations should be recognizably related to the original
- Interest: variations should add something new, not be boring copies
- Musical coherence: variations should work as standalone musical phrases
"""

from core.music import Layer, Phrase, NoteName
from core.genome_ops import phrase_similarity
from fitness.base import FitnessFunction


class VariationFitness(FitnessFunction):
    """Evaluate variations based on similarity to theme and musical interest.

    A good variation:
    - Is recognizably related to the original theme (0.5-0.8 similarity)
    - Adds something new and interesting
    - Works as a standalone musical phrase
    """

    def __init__(
        self,
        original_theme: Phrase,
        similarity_target: float = 0.6,
        similarity_tolerance: float = 0.15,
        intrinsic_fitness: FitnessFunction = None,
        similarity_weight: float = 0.5,
        interest_weight: float = 0.3,
        intrinsic_weight: float = 0.2,
    ):
        """Initialize variation fitness.

        Args:
            original_theme: The original theme phrase to vary
            similarity_target: Target similarity (0.0-1.0), default 0.6
            similarity_tolerance: Acceptable deviation from target
            intrinsic_fitness: Optional fitness for standalone phrase quality
            similarity_weight: Weight for similarity score
            interest_weight: Weight for interest/novelty score
            intrinsic_weight: Weight for intrinsic phrase quality
        """
        self.theme = original_theme
        self.similarity_target = similarity_target
        self.similarity_tolerance = similarity_tolerance
        self.intrinsic_fitness = intrinsic_fitness
        self.similarity_weight = similarity_weight
        self.interest_weight = interest_weight
        self.intrinsic_weight = intrinsic_weight

    def evaluate(self, layer: Layer) -> float:
        """Evaluate a variation of the theme.

        Args:
            layer: Layer containing the variation phrase

        Returns:
            Fitness score from 0.0 to 1.0
        """
        if not layer.phrases:
            return 0.3

        variation = layer.phrases[0]

        # Calculate similarity to theme
        similarity = phrase_similarity(self.theme, variation)
        similarity_score = self._similarity_score(similarity)

        # Calculate interest/novelty
        interest_score = self._interest_score(variation, similarity)

        # Calculate intrinsic quality if available
        if self.intrinsic_fitness:
            intrinsic_score = self.intrinsic_fitness.evaluate(layer)
        else:
            intrinsic_score = 0.5  # Neutral

        # Combine scores
        return (
            self.similarity_weight * similarity_score +
            self.interest_weight * interest_score +
            self.intrinsic_weight * intrinsic_score
        )

    def _similarity_score(self, similarity: float) -> float:
        """Score based on how close to target similarity.

        Penalizes both too similar (boring) and too different (unrecognizable).
        """
        deviation = abs(similarity - self.similarity_target)

        if deviation <= self.similarity_tolerance:
            # Within tolerance - full score
            return 1.0
        elif deviation <= self.similarity_tolerance * 2:
            # Slightly outside tolerance - reduced score
            return 0.7
        elif deviation <= self.similarity_tolerance * 3:
            return 0.4
        else:
            # Very far from target
            return 0.1

    def _interest_score(self, variation: Phrase, similarity: float) -> float:
        """Score based on musical interest/novelty.

        Interest comes from:
        - New pitch material (pitch classes not in theme)
        - Different rhythmic groupings
        - New contour patterns
        """
        theme_notes = [n for n in self.theme.notes if n.pitch != NoteName.REST]
        var_notes = [n for n in variation.notes if n.pitch != NoteName.REST]

        if not theme_notes or not var_notes:
            return 0.5

        scores = []

        # 1. New pitch classes
        theme_pcs = {n.pitch.value % 12 for n in theme_notes}
        var_pcs = {n.pitch.value % 12 for n in var_notes}
        new_pcs = var_pcs - theme_pcs
        novelty_ratio = len(new_pcs) / max(len(var_pcs), 1)
        # Some novelty is good, too much is disconnected
        if 0.1 <= novelty_ratio <= 0.4:
            scores.append(1.0)
        elif novelty_ratio < 0.1:
            scores.append(0.5 + novelty_ratio * 5)
        else:
            scores.append(0.6)

        # 2. Duration variety
        theme_durations = {n.duration for n in theme_notes}
        var_durations = {n.duration for n in var_notes}
        new_durations = var_durations - theme_durations
        if new_durations:
            scores.append(0.8)  # New rhythmic material is interesting
        else:
            scores.append(0.5)  # Same rhythms can be OK

        # 3. Register usage
        theme_range = max(n.octave for n in theme_notes) - min(n.octave for n in theme_notes)
        var_range = max(n.octave for n in var_notes) - min(n.octave for n in var_notes)
        # Different range is interesting
        if abs(theme_range - var_range) >= 1:
            scores.append(0.9)
        else:
            scores.append(0.6)

        return sum(scores) / len(scores) if scores else 0.5


class DevelopmentArcFitness(FitnessFunction):
    """Evaluate a sequence of variations for overall developmental arc.

    Good development:
    - Starts recognizable, becomes more distant, returns to original
    - Builds tension and releases
    - Each variation connects to neighbors
    """

    def __init__(
        self,
        original_theme: Phrase,
        num_variations: int = 4,
        arc_type: str = "departure_return",
    ):
        """Initialize development arc fitness.

        Args:
            original_theme: The original theme
            num_variations: Expected number of variations
            arc_type: Type of developmental arc:
                - "departure_return": Start close, go far, come back
                - "progressive": Gradually move away
                - "arch": Build to climax in middle, return at end
        """
        self.theme = original_theme
        self.num_variations = num_variations
        self.arc_type = arc_type

    def evaluate_sequence(self, variations: list[Phrase]) -> float:
        """Evaluate a sequence of variations.

        Args:
            variations: List of variation phrases

        Returns:
            Fitness score for the overall development
        """
        if not variations:
            return 0.0

        # Calculate similarity of each variation to theme
        similarities = [phrase_similarity(self.theme, v) for v in variations]

        # Calculate neighbor connectivity
        connectivity_scores = []
        for i in range(len(variations) - 1):
            neighbor_sim = phrase_similarity(variations[i], variations[i + 1])
            # Neighbors should be somewhat similar (0.4-0.7)
            if 0.4 <= neighbor_sim <= 0.8:
                connectivity_scores.append(1.0)
            else:
                connectivity_scores.append(0.5)

        # Evaluate arc shape
        arc_score = self._evaluate_arc(similarities)

        # Combine scores
        connectivity_avg = sum(connectivity_scores) / len(connectivity_scores) if connectivity_scores else 0.5

        return 0.6 * arc_score + 0.4 * connectivity_avg

    def _evaluate_arc(self, similarities: list[float]) -> float:
        """Evaluate if similarity arc matches expected pattern."""
        if len(similarities) < 2:
            return 0.5

        if self.arc_type == "departure_return":
            # First and last should be most similar, middle least
            first_sim = similarities[0]
            last_sim = similarities[-1]
            mid_idx = len(similarities) // 2
            mid_sim = similarities[mid_idx]

            # Check pattern: high -> low -> high
            if first_sim > mid_sim < last_sim:
                return 1.0
            elif first_sim > mid_sim or mid_sim < last_sim:
                return 0.7
            else:
                return 0.4

        elif self.arc_type == "progressive":
            # Should generally decrease
            decreasing = sum(1 for i in range(len(similarities) - 1)
                            if similarities[i] > similarities[i + 1])
            return decreasing / (len(similarities) - 1)

        elif self.arc_type == "arch":
            # Build to middle, then return
            mid_idx = len(similarities) // 2
            first_half = similarities[:mid_idx + 1]
            second_half = similarities[mid_idx:]

            # First half should decrease, second half should increase
            first_decreasing = sum(1 for i in range(len(first_half) - 1)
                                  if first_half[i] > first_half[i + 1])
            second_increasing = sum(1 for i in range(len(second_half) - 1)
                                   if second_half[i] < second_half[i + 1])

            first_score = first_decreasing / max(len(first_half) - 1, 1)
            second_score = second_increasing / max(len(second_half) - 1, 1)

            return (first_score + second_score) / 2

        return 0.5


class CallResponseFitness(FitnessFunction):
    """Evaluate call-and-response patterns.

    Good call-response:
    - Response acknowledges the call (some similarity)
    - Response adds something new (some contrast)
    - Response provides resolution or continuation
    """

    def __init__(
        self,
        call_phrase: Phrase,
        response_type: str = "answer",
    ):
        """Initialize call-response fitness.

        Args:
            call_phrase: The "call" phrase
            response_type: Expected response type:
                - "answer": Resolve the call
                - "echo": Repeat/reflect the call
                - "contrast": Complement with different material
        """
        self.call = call_phrase
        self.response_type = response_type

    def evaluate(self, layer: Layer) -> float:
        """Evaluate a response phrase.

        Args:
            layer: Layer containing the response phrase

        Returns:
            Fitness score for the response
        """
        if not layer.phrases:
            return 0.3

        response = layer.phrases[0]
        similarity = phrase_similarity(self.call, response)

        if self.response_type == "answer":
            # Should be moderately similar but resolve tension
            similarity_score = 1.0 if 0.4 <= similarity <= 0.7 else 0.5
            resolution_score = self._resolution_score(response)
            return 0.5 * similarity_score + 0.5 * resolution_score

        elif self.response_type == "echo":
            # Should be very similar
            return 1.0 if similarity >= 0.7 else similarity

        elif self.response_type == "contrast":
            # Should be different but complementary
            contrast_score = 1.0 - similarity if similarity < 0.5 else 0.3
            complement_score = self._complement_score(response)
            return 0.5 * contrast_score + 0.5 * complement_score

        return 0.5

    def _resolution_score(self, response: Phrase) -> float:
        """Score based on how well response resolves tension."""
        response_notes = [n for n in response.notes if n.pitch != NoteName.REST]

        if not response_notes:
            return 0.3

        # Check if response ends on stable tones (C, E, G in C major)
        stable_pitches = {0, 4, 7}  # C, E, G
        last_note = response_notes[-1]
        if last_note.pitch.value % 12 in stable_pitches:
            return 1.0

        # Check for descending motion at end (implies resolution)
        if len(response_notes) >= 2:
            if response_notes[-1].midi_pitch < response_notes[-2].midi_pitch:
                return 0.8

        return 0.5

    def _complement_score(self, response: Phrase) -> float:
        """Score based on how well response complements call."""
        call_notes = [n for n in self.call.notes if n.pitch != NoteName.REST]
        response_notes = [n for n in response.notes if n.pitch != NoteName.REST]

        if not call_notes or not response_notes:
            return 0.5

        # Good complement: response fills gaps in call's register
        call_avg_pitch = sum(n.midi_pitch for n in call_notes) / len(call_notes)
        response_avg_pitch = sum(n.midi_pitch for n in response_notes) / len(response_notes)

        # Different register is good
        pitch_diff = abs(call_avg_pitch - response_avg_pitch)
        if 5 <= pitch_diff <= 12:  # At least a fourth apart
            return 1.0
        elif pitch_diff >= 3:
            return 0.7
        else:
            return 0.4


def create_variation_fitness(
    theme: Phrase,
    intrinsic_fitness: FitnessFunction = None,
    similarity_target: float = 0.6,
) -> VariationFitness:
    """Factory function to create variation fitness.

    Args:
        theme: Original theme phrase
        intrinsic_fitness: Optional fitness for phrase quality
        similarity_target: Target similarity (0.0-1.0)

    Returns:
        VariationFitness instance
    """
    return VariationFitness(
        original_theme=theme,
        similarity_target=similarity_target,
        intrinsic_fitness=intrinsic_fitness,
    )
