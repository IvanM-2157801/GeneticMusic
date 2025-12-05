"""Contextual fitness functions that consider inter-layer dependencies."""
from core.music import Layer, Phrase, NoteName
from fitness.base import FitnessFunction


class ContextualFitness(FitnessFunction):
    """Wrapper fitness that combines intrinsic quality with inter-layer compatibility.

    This allows new layers to "fit in" with already-evolved layers by:
    - Balancing rhythmic density (not all layers busy at once)
    - Ensuring complementary rhythms (not too similar, not clashing)
    - Maintaining harmonic compatibility (for melodic layers)
    """

    def __init__(
        self,
        intrinsic_fitness: FitnessFunction,
        context_layers: list[tuple[Layer, str]],  # (layer, rhythm) pairs
        intrinsic_weight: float = 0.7,
        context_weight: float = 0.3,
    ):
        """Initialize contextual fitness.

        Args:
            intrinsic_fitness: The layer's own fitness function
            context_layers: List of (layer, rhythm) tuples for context
            intrinsic_weight: Weight for intrinsic fitness (0.0-1.0)
            context_weight: Weight for contextual fitness (0.0-1.0)
        """
        self.intrinsic_fitness = intrinsic_fitness
        self.context_layers = context_layers
        self.intrinsic_weight = intrinsic_weight
        self.context_weight = context_weight

    def evaluate(self, layer: Layer) -> float:
        """Evaluate layer considering both intrinsic quality and context fit."""
        # Get intrinsic fitness (how good is the layer on its own?)
        intrinsic_score = self.intrinsic_fitness.evaluate(layer)

        # If no context, just return intrinsic score
        if not self.context_layers:
            return intrinsic_score

        # Calculate contextual fitness (how well does it fit with other layers?)
        context_score = self._evaluate_context_fit(layer)

        # Combine scores
        return (
            self.intrinsic_weight * intrinsic_score +
            self.context_weight * context_score
        )

    def _evaluate_context_fit(self, layer: Layer) -> float:
        """Evaluate how well this layer fits with context layers."""
        if not layer.rhythm:
            return 0.5  # Neutral score if no rhythm

        scores = []

        # Compare with each context layer
        for context_layer, context_rhythm in self.context_layers:
            # Rhythmic compatibility
            if context_rhythm:
                rhythm_score = self._rhythmic_compatibility(layer.rhythm, context_rhythm)
                scores.append(rhythm_score)

            # Density balance (don't want all layers busy at once)
            density_score = self._density_balance(layer.rhythm, context_rhythm)
            scores.append(density_score)

            # Harmonic compatibility (for melodic layers)
            if not layer.is_drum and not context_layer.is_drum:
                if layer.phrases and context_layer.phrases:
                    harmonic_score = self._harmonic_compatibility(
                        layer.phrases[0], context_layer.phrases[0]
                    )
                    scores.append(harmonic_score)

        return sum(scores) / len(scores) if scores else 0.5

    def _rhythmic_compatibility(self, rhythm1: str, rhythm2: str) -> float:
        """Check if rhythms complement each other (not too similar, not clashing)."""
        if not rhythm1 or not rhythm2:
            return 0.5

        # Make same length for comparison
        min_len = min(len(rhythm1), len(rhythm2))
        r1 = rhythm1[:min_len]
        r2 = rhythm2[:min_len]

        # Count where both have notes vs where both have rests
        both_notes = sum(1 for i in range(min_len) if r1[i] != '0' and r2[i] != '0')
        both_rests = sum(1 for i in range(min_len) if r1[i] == '0' and r2[i] == '0')

        # Target: some overlap (50-70%) but not too much
        overlap_ratio = both_notes / min_len
        rest_overlap = both_rests / min_len

        # Reward moderate overlap (good groove)
        if 0.3 <= overlap_ratio <= 0.7:
            overlap_score = 1.0 - abs(overlap_ratio - 0.5) / 0.5
        else:
            overlap_score = 0.5

        # Don't want both resting too much at the same time
        rest_score = 1.0 - min(rest_overlap, 0.5) * 2

        return 0.6 * overlap_score + 0.4 * rest_score

    def _density_balance(self, rhythm1: str, rhythm2: str) -> float:
        """Ensure layers don't all have the same density (create dynamic range)."""
        if not rhythm1 or not rhythm2:
            return 0.5

        # Calculate densities
        density1 = sum(int(c) for c in rhythm1) / (len(rhythm1) * 4.0)
        density2 = sum(int(c) for c in rhythm2) / (len(rhythm2) * 4.0)

        # Reward different densities (creates space and interest)
        density_diff = abs(density1 - density2)

        # Target difference of 0.2-0.5 (enough contrast but not extreme)
        if 0.2 <= density_diff <= 0.5:
            return 1.0
        elif density_diff < 0.2:
            return 0.5 + density_diff * 2.5  # Linearly increase
        else:
            return 1.0 - (density_diff - 0.5) * 2  # Penalize extreme differences

    def _harmonic_compatibility(self, phrase1: Phrase, phrase2: Phrase) -> float:
        """Check if melodic phrases are harmonically compatible."""
        # Get non-rest notes
        notes1 = [n for n in phrase1.notes if n.pitch != NoteName.REST]
        notes2 = [n for n in phrase2.notes if n.pitch != NoteName.REST]

        if not notes1 or not notes2:
            return 0.5

        # Check for consonant intervals (unison, thirds, fifths, octaves)
        consonant_intervals = {0, 3, 4, 7, 8, 12}  # Semitones

        # Sample some note pairs
        sample_size = min(5, len(notes1), len(notes2))
        consonance_scores = []

        for i in range(sample_size):
            idx1 = i * len(notes1) // sample_size
            idx2 = i * len(notes2) // sample_size

            interval = abs(notes1[idx1].midi_pitch - notes2[idx2].midi_pitch) % 12
            if interval in consonant_intervals:
                consonance_scores.append(1.0)
            else:
                consonance_scores.append(0.3)  # Dissonance is OK sometimes

        return sum(consonance_scores) / len(consonance_scores) if consonance_scores else 0.5


def create_contextual_fitness(
    intrinsic_fitness: FitnessFunction,
    evolved_layers: dict[str, tuple[Layer, str]],
    use_context: bool = True,
) -> FitnessFunction:
    """Helper to create contextual fitness from evolved layers.

    Args:
        intrinsic_fitness: The layer's own fitness function
        evolved_layers: Dict of {name: (layer, rhythm)} for context
        use_context: If False, just returns intrinsic fitness

    Returns:
        ContextualFitness wrapper or intrinsic fitness
    """
    if not use_context or not evolved_layers:
        return intrinsic_fitness

    context_list = list(evolved_layers.values())
    return ContextualFitness(
        intrinsic_fitness=intrinsic_fitness,
        context_layers=context_list,
        intrinsic_weight=0.7,  # 70% own quality
        context_weight=0.3,  # 30% fit with others
    )
