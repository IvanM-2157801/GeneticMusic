"""Dynamic envelope fitness functions.

This module provides fitness functions for evaluating dynamic (gain) and
filter (LPF) envelopes, ensuring musically appropriate automation curves.
"""

from typing import TYPE_CHECKING
from enum import Enum
from core.music import DynamicEnvelope, FilterEnvelope

if TYPE_CHECKING:
    from song_composer import SectionType

# Local copy of section dynamics to avoid circular import
# These match the values in song_composer.SECTION_DYNAMICS
SECTION_DYNAMICS_LOCAL = {
    "intro": {"gain": (0.3, 0.5), "lpf": (2000, 4000)},
    "verse": {"gain": (0.5, 0.7), "lpf": (3000, 6000)},
    "prechorus": {"gain": (0.6, 0.8), "lpf": (5000, 8000)},
    "chorus": {"gain": (0.8, 1.0), "lpf": (6000, 10000)},
    "bridge": {"gain": (0.4, 0.6), "lpf": (2000, 5000)},
    "breakdown": {"gain": (0.3, 0.5), "lpf": (2000, 4000)},
    "buildup": {"gain": (0.4, 0.8), "lpf": (2000, 8000)},
    "drop": {"gain": (0.9, 1.0), "lpf": (8000, 12000)},
    "outro": {"gain": (0.5, 0.2), "lpf": (4000, 1000)},
}


class DynamicEnvelopeFitness:
    """Evaluate dynamic envelope quality for a section type.

    Good dynamic envelopes:
    - Match section energy expectations (loud chorus, quiet verse)
    - Have smooth transitions (no jarring jumps)
    - Show appropriate movement (not too static, not too erratic)
    """

    def __init__(
        self,
        section_type: "SectionType",
        smoothness_weight: float = 0.3,
        appropriateness_weight: float = 0.5,
        interest_weight: float = 0.2,
    ):
        """Initialize dynamic envelope fitness.

        Args:
            section_type: The type of section (affects expected gain range)
            smoothness_weight: Weight for smooth transitions
            appropriateness_weight: Weight for matching section expectations
            interest_weight: Weight for dynamic interest/movement
        """
        self.section_type = section_type
        self.smoothness_weight = smoothness_weight
        self.appropriateness_weight = appropriateness_weight
        self.interest_weight = interest_weight

        # Get expected gain range for this section type
        # Use .value to get string key for the local dict
        section_key = section_type.value if hasattr(section_type, 'value') else str(section_type)
        defaults = SECTION_DYNAMICS_LOCAL.get(section_key, {"gain": (0.5, 0.7)})
        self.expected_min, self.expected_max = defaults["gain"]

    def evaluate(self, envelope: DynamicEnvelope) -> float:
        """Evaluate the fitness of a dynamic envelope.

        Args:
            envelope: The dynamic envelope to evaluate

        Returns:
            Fitness score from 0.0 to 1.0
        """
        if not envelope.points:
            return 0.3

        smoothness = self._evaluate_smoothness(envelope)
        appropriateness = self._evaluate_appropriateness(envelope)
        interest = self._evaluate_interest(envelope)

        return (
            self.smoothness_weight * smoothness +
            self.appropriateness_weight * appropriateness +
            self.interest_weight * interest
        )

    def _evaluate_smoothness(self, envelope: DynamicEnvelope) -> float:
        """Evaluate how smooth the envelope transitions are."""
        if len(envelope.points) < 2:
            return 0.8  # Single point is fine

        sorted_points = sorted(envelope.points, key=lambda p: p[0])
        max_jump = 0.0

        for i in range(len(sorted_points) - 1):
            t1, g1 = sorted_points[i]
            t2, g2 = sorted_points[i + 1]

            # Calculate gain change per time unit
            time_diff = t2 - t1
            gain_diff = abs(g2 - g1)

            if time_diff > 0:
                rate = gain_diff / time_diff
                max_jump = max(max_jump, rate)

        # Penalize very fast changes (rate > 2.0 is jarring)
        if max_jump <= 0.5:
            return 1.0
        elif max_jump <= 1.0:
            return 0.8
        elif max_jump <= 2.0:
            return 0.5
        else:
            return 0.2

    def _evaluate_appropriateness(self, envelope: DynamicEnvelope) -> float:
        """Evaluate if envelope values match section expectations."""
        if not envelope.points:
            return 0.5

        gains = [p[1] for p in envelope.points]
        actual_min = min(gains)
        actual_max = max(gains)
        actual_avg = sum(gains) / len(gains)

        # Check if gains are in expected range
        in_range_score = 0.0

        # Average should be near expected midpoint
        expected_mid = (self.expected_min + self.expected_max) / 2
        avg_diff = abs(actual_avg - expected_mid)
        in_range_score += 1.0 - min(avg_diff * 2, 1.0)

        # Min should be at or above expected min
        if actual_min >= self.expected_min - 0.1:
            in_range_score += 0.5
        else:
            in_range_score += max(0, 0.5 - (self.expected_min - actual_min))

        # Max should be at or below expected max
        if actual_max <= self.expected_max + 0.1:
            in_range_score += 0.5
        else:
            in_range_score += max(0, 0.5 - (actual_max - self.expected_max))

        return in_range_score / 2.0

    def _evaluate_interest(self, envelope: DynamicEnvelope) -> float:
        """Evaluate if envelope has interesting movement (not too static)."""
        if len(envelope.points) < 2:
            return 0.4  # Static is OK but not great

        gains = [p[1] for p in envelope.points]
        gain_range = max(gains) - min(gains)

        # Some movement is good (0.1-0.3 range is ideal)
        if 0.1 <= gain_range <= 0.4:
            return 1.0
        elif gain_range < 0.1:
            return 0.5 + gain_range * 5  # Too static
        else:
            return 0.7  # Too much variation is OK but not ideal


class FilterEnvelopeFitness:
    """Evaluate filter envelope quality for a section type.

    Good filter envelopes:
    - Match section character (open filter on drops, closed on breakdowns)
    - Have musically appropriate sweeps
    - Create tension and release
    """

    def __init__(
        self,
        section_type: "SectionType",
        smoothness_weight: float = 0.3,
        appropriateness_weight: float = 0.5,
        sweep_quality_weight: float = 0.2,
    ):
        """Initialize filter envelope fitness.

        Args:
            section_type: The type of section
            smoothness_weight: Weight for smooth transitions
            appropriateness_weight: Weight for matching section expectations
            sweep_quality_weight: Weight for sweep direction appropriateness
        """
        self.section_type = section_type
        self.smoothness_weight = smoothness_weight
        self.appropriateness_weight = appropriateness_weight
        self.sweep_quality_weight = sweep_quality_weight

        # Get expected filter range for this section type
        section_key = section_type.value if hasattr(section_type, 'value') else str(section_type)
        defaults = SECTION_DYNAMICS_LOCAL.get(section_key, {"lpf": (3000, 6000)})
        self.expected_min, self.expected_max = defaults["lpf"]

    def evaluate(self, envelope: FilterEnvelope) -> float:
        """Evaluate the fitness of a filter envelope.

        Args:
            envelope: The filter envelope to evaluate

        Returns:
            Fitness score from 0.0 to 1.0
        """
        if not envelope.points:
            return 0.3

        smoothness = self._evaluate_smoothness(envelope)
        appropriateness = self._evaluate_appropriateness(envelope)
        sweep_quality = self._evaluate_sweep_quality(envelope)

        return (
            self.smoothness_weight * smoothness +
            self.appropriateness_weight * appropriateness +
            self.sweep_quality_weight * sweep_quality
        )

    def _evaluate_smoothness(self, envelope: FilterEnvelope) -> float:
        """Evaluate how smooth the filter transitions are."""
        if len(envelope.points) < 2:
            return 0.8

        sorted_points = sorted(envelope.points, key=lambda p: p[0])
        max_rate = 0.0

        for i in range(len(sorted_points) - 1):
            t1, f1 = sorted_points[i]
            t2, f2 = sorted_points[i + 1]

            time_diff = t2 - t1
            freq_diff = abs(f2 - f1)

            if time_diff > 0:
                # Normalize by typical frequency range (1000-10000 Hz)
                rate = (freq_diff / 9000) / time_diff
                max_rate = max(max_rate, rate)

        # Penalize very fast changes
        if max_rate <= 0.5:
            return 1.0
        elif max_rate <= 1.0:
            return 0.7
        else:
            return 0.4

    def _evaluate_appropriateness(self, envelope: FilterEnvelope) -> float:
        """Evaluate if filter values match section expectations."""
        if not envelope.points:
            return 0.5

        freqs = [p[1] for p in envelope.points]
        actual_min = min(freqs)
        actual_max = max(freqs)
        actual_avg = sum(freqs) / len(freqs)

        score = 0.0

        # Average should be in expected range
        expected_mid = (self.expected_min + self.expected_max) / 2
        if self.expected_min <= actual_avg <= self.expected_max:
            score += 1.0
        else:
            diff = min(
                abs(actual_avg - self.expected_min),
                abs(actual_avg - self.expected_max)
            )
            score += max(0, 1.0 - diff / 5000)

        # Range should be reasonable
        freq_range = actual_max - actual_min
        if freq_range <= 5000:
            score += 0.5
        else:
            score += max(0, 0.5 - (freq_range - 5000) / 10000)

        return score / 1.5

    def _evaluate_sweep_quality(self, envelope: FilterEnvelope) -> float:
        """Evaluate the quality and direction of filter sweeps.

        Different sections prefer different sweep directions:
        - BUILDUP: ascending sweep (opening filter)
        - BREAKDOWN: descending sweep (closing filter)
        - CHORUS: high and open
        - VERSE: moderate and stable
        """
        if len(envelope.points) < 2:
            return 0.5

        sorted_points = sorted(envelope.points, key=lambda p: p[0])
        start_freq = sorted_points[0][1]
        end_freq = sorted_points[-1][1]

        sweep_direction = end_freq - start_freq  # Positive = opening, negative = closing

        # Get section name for comparison
        section_name = self.section_type.value if hasattr(self.section_type, 'value') else str(self.section_type)

        # Section-specific preferences
        if section_name in {"buildup", "prechorus"}:
            # Should be ascending (opening)
            if sweep_direction > 1000:
                return 1.0
            elif sweep_direction > 0:
                return 0.7
            else:
                return 0.3

        elif section_name in {"breakdown", "outro"}:
            # Should be descending (closing)
            if sweep_direction < -1000:
                return 1.0
            elif sweep_direction < 0:
                return 0.7
            else:
                return 0.4

        elif section_name in {"chorus", "drop"}:
            # Should be high and open (stable or slightly ascending)
            if end_freq > 6000:
                return 1.0
            elif end_freq > 4000:
                return 0.7
            else:
                return 0.4

        elif section_name == "intro":
            # Can be either direction, prefer ascending
            if sweep_direction > 500:
                return 0.9
            elif abs(sweep_direction) < 500:
                return 0.7
            else:
                return 0.5

        else:
            # VERSE, BRIDGE: moderate and stable
            if abs(sweep_direction) < 2000:
                return 0.8
            else:
                return 0.5


def evaluate_section_dynamics(
    dynamic_envelope: DynamicEnvelope,
    filter_envelope: FilterEnvelope,
    section_type: "SectionType",
) -> float:
    """Evaluate both dynamic and filter envelopes for a section.

    Args:
        dynamic_envelope: Gain envelope for the section
        filter_envelope: LPF envelope for the section
        section_type: Type of section being evaluated

    Returns:
        Combined fitness score from 0.0 to 1.0
    """
    dynamic_fitness = DynamicEnvelopeFitness(section_type)
    filter_fitness = FilterEnvelopeFitness(section_type)

    dynamic_score = dynamic_fitness.evaluate(dynamic_envelope)
    filter_score = filter_fitness.evaluate(filter_envelope)

    # Weight dynamics slightly higher than filter
    return 0.55 * dynamic_score + 0.45 * filter_score
