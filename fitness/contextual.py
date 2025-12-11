"""Contextual fitness functions that consider inter-layer dependencies.

This module provides fitness functions that evaluate how well a new layer
fits with already-evolved layers, enabling coherent multi-layer arrangements.

Key features:
- Rhythmic compatibility (complementary patterns, not clashing)
- Density balance (layers have different busy-ness levels)
- Harmonic compatibility (consonant intervals between melodic layers)
- Voice leading (avoid parallel fifths/octaves, reward contrary motion)
- Bass-melody relationship (bass supports melody harmonically)
- Drum-melody alignment (accents complement melodic phrasing)
"""

from core.music import Layer, Phrase, NoteName
from fitness.base import FitnessFunction


class ContextualFitness(FitnessFunction):
    """Wrapper fitness that combines intrinsic quality with inter-layer compatibility.

    This allows new layers to "fit in" with already-evolved layers by:
    - Balancing rhythmic density (not all layers busy at once)
    - Ensuring complementary rhythms (not too similar, not clashing)
    - Maintaining harmonic compatibility (for melodic layers)
    - Proper voice leading between parts
    - Bass-melody harmonic support
    """

    # Default metric weights for contextual fitness
    DEFAULT_METRIC_WEIGHTS = {
        "rhythmic": 0.25,
        "density": 0.15,
        "harmonic": 0.25,
        "voice_leading": 0.20,
        "call_response": 0.15,
    }

    def __init__(
        self,
        intrinsic_fitness: FitnessFunction,
        context_layers: list[tuple[Layer, str]],  # (layer, rhythm) pairs
        intrinsic_weight: float = 0.7,
        context_weight: float = 0.3,
        metric_weights: dict[str, float] = None,
    ):
        """Initialize contextual fitness.

        Args:
            intrinsic_fitness: The layer's own fitness function
            context_layers: List of (layer, rhythm) tuples for context
            intrinsic_weight: Weight for intrinsic fitness (0.0-1.0)
            context_weight: Weight for contextual fitness (0.0-1.0)
            metric_weights: Custom weights for context metrics. Available metrics:
                - "rhythmic": How rhythms complement each other (0.0-1.0)
                - "density": Different busy-ness levels between layers (0.0-1.0)
                - "harmonic": Consonant intervals between melodic layers (0.0-1.0)
                - "voice_leading": Contrary motion, avoid parallel 5ths/octaves (0.0-1.0)
                - "call_response": Alternating activity patterns (0.0-1.0)
                If None, uses DEFAULT_METRIC_WEIGHTS.
        """
        self.intrinsic_fitness = intrinsic_fitness
        self.context_layers = context_layers
        self.intrinsic_weight = intrinsic_weight
        self.context_weight = context_weight

        # Use provided weights or defaults
        if metric_weights is not None:
            self.metric_weights = {**self.DEFAULT_METRIC_WEIGHTS, **metric_weights}
        else:
            self.metric_weights = self.DEFAULT_METRIC_WEIGHTS.copy()

    def evaluate(self, layer: Layer) -> float:
        """Evaluate layer considering both intrinsic quality and context fit."""
        # Get intrinsic fitness (how good is the layer on its own?)
        if self.intrinsic_fitness:
            intrinsic_score = self.intrinsic_fitness.evaluate(layer)
        else:
            intrinsic_score = 0.5

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
        if not layer.rhythm and not layer.phrases:
            return 0.5  # Neutral score if no content

        scores = {
            "rhythmic": [],
            "density": [],
            "harmonic": [],
            "voice_leading": [],
            "call_response": [],
        }

        # Compare with each context layer
        for context_layer, context_rhythm in self.context_layers:
            # Rhythmic compatibility
            if layer.rhythm and context_rhythm:
                rhythm_score = self._rhythmic_compatibility(layer.rhythm, context_rhythm)
                scores["rhythmic"].append(rhythm_score)

                # Check for call-and-response patterns
                cr_score = self._call_response_pattern(layer.rhythm, context_rhythm)
                scores["call_response"].append(cr_score)

            # Density balance (don't want all layers busy at once)
            if layer.rhythm and context_rhythm:
                density_score = self._density_balance(layer.rhythm, context_rhythm)
                scores["density"].append(density_score)

            # Melodic layer interactions
            if not layer.is_drum and not context_layer.is_drum:
                if layer.phrases and context_layer.phrases:
                    # Basic harmonic compatibility
                    harmonic_score = self._harmonic_compatibility(
                        layer.phrases[0], context_layer.phrases[0]
                    )
                    scores["harmonic"].append(harmonic_score)

                    # Voice leading quality
                    vl_score = self._voice_leading_quality(
                        layer.phrases[0], context_layer.phrases[0]
                    )
                    scores["voice_leading"].append(vl_score)

            # Special case: bass supporting melody
            if self._is_bass_melody_pair(layer, context_layer):
                bass_support = self._bass_melody_support(layer, context_layer)
                scores["harmonic"].append(bass_support)

        # Calculate weighted average of all scores
        final_score = 0.0
        total_weight = 0.0

        for metric, metric_scores in scores.items():
            if metric_scores:
                avg_score = sum(metric_scores) / len(metric_scores)
                weight = self.metric_weights.get(metric, 0.1)
                final_score += avg_score * weight
                total_weight += weight

        return final_score / total_weight if total_weight > 0 else 0.5

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

        # Target: some overlap (30-70%) but not too much
        overlap_ratio = both_notes / min_len if min_len > 0 else 0
        rest_overlap = both_rests / min_len if min_len > 0 else 0

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

        # Consonant intervals (semitones)
        # Perfect consonances: unison (0), octave (12)
        # Imperfect consonances: thirds (3, 4), sixths (8, 9)
        # Perfect fifth (7)
        consonant_intervals = {0, 3, 4, 7, 8, 9, 12}
        mild_dissonance = {2, 5, 10}  # Seconds, fourths, sevenths

        # Sample note pairs at corresponding positions
        sample_size = min(8, len(notes1), len(notes2))
        consonance_scores = []

        for i in range(sample_size):
            idx1 = i * len(notes1) // sample_size
            idx2 = i * len(notes2) // sample_size

            interval = abs(notes1[idx1].midi_pitch - notes2[idx2].midi_pitch) % 12
            if interval in consonant_intervals:
                consonance_scores.append(1.0)
            elif interval in mild_dissonance:
                consonance_scores.append(0.6)  # Mild dissonance is OK
            else:
                consonance_scores.append(0.3)  # Strong dissonance

        return sum(consonance_scores) / len(consonance_scores) if consonance_scores else 0.5

    def _voice_leading_quality(self, phrase1: Phrase, phrase2: Phrase) -> float:
        """Evaluate voice leading between two melodic parts.

        Good voice leading:
        - Contrary motion rewarded
        - Parallel motion in thirds/sixths acceptable
        - Parallel fifths/octaves penalized
        - Voice crossing penalized
        """
        notes1 = [n for n in phrase1.notes if n.pitch != NoteName.REST]
        notes2 = [n for n in phrase2.notes if n.pitch != NoteName.REST]

        if len(notes1) < 2 or len(notes2) < 2:
            return 0.5

        scores = []
        sample_size = min(7, len(notes1) - 1, len(notes2) - 1)

        for i in range(sample_size):
            idx1 = i * (len(notes1) - 1) // sample_size
            idx2 = i * (len(notes2) - 1) // sample_size

            # Get motion direction for each voice
            motion1 = notes1[idx1 + 1].midi_pitch - notes1[idx1].midi_pitch
            motion2 = notes2[idx2 + 1].midi_pitch - notes2[idx2].midi_pitch

            # Calculate interval at both positions
            interval_before = abs(notes1[idx1].midi_pitch - notes2[idx2].midi_pitch) % 12
            interval_after = abs(notes1[idx1 + 1].midi_pitch - notes2[idx2 + 1].midi_pitch) % 12

            score = 0.5  # Default neutral

            # Contrary motion: voices move in opposite directions
            if (motion1 > 0 and motion2 < 0) or (motion1 < 0 and motion2 > 0):
                score = 1.0  # Excellent

            # Parallel fifths or octaves: penalize
            elif interval_before in {0, 7, 12} and interval_after in {0, 7, 12}:
                if (motion1 > 0) == (motion2 > 0):  # Same direction
                    score = 0.2  # Bad parallel motion

            # Parallel thirds/sixths: acceptable
            elif interval_before in {3, 4, 8, 9} and interval_after in {3, 4, 8, 9}:
                score = 0.8  # Good parallel motion

            # Oblique motion (one voice stays, other moves)
            elif motion1 == 0 or motion2 == 0:
                score = 0.7  # Acceptable

            # Similar motion (same direction, different intervals)
            else:
                score = 0.6

            # Check for voice crossing
            if notes1[idx1].midi_pitch > notes2[idx2].midi_pitch:
                if notes1[idx1 + 1].midi_pitch < notes2[idx2 + 1].midi_pitch:
                    score *= 0.7  # Penalize crossing

            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.5

    def _call_response_pattern(self, rhythm1: str, rhythm2: str) -> float:
        """Detect and reward call-and-response rhythmic patterns.

        Good call-and-response:
        - One layer busy while other rests, then swap
        - Alternating activity creates dialogue
        """
        if not rhythm1 or not rhythm2:
            return 0.5

        min_len = min(len(rhythm1), len(rhythm2))

        # Count alternation patterns
        alternations = 0
        for i in range(min_len - 1):
            r1_active = rhythm1[i] != '0'
            r2_active = rhythm2[i] != '0'
            r1_next = rhythm1[i + 1] != '0'
            r2_next = rhythm2[i + 1] != '0'

            # One active, other rest, then swap
            if (r1_active and not r2_active and not r1_next and r2_next) or \
               (not r1_active and r2_active and r1_next and not r2_next):
                alternations += 1

        # Some alternation is good, but not constant
        alternation_ratio = alternations / (min_len - 1) if min_len > 1 else 0

        # Target: 10-30% alternation for good dialogue
        if 0.1 <= alternation_ratio <= 0.3:
            return 1.0
        elif alternation_ratio < 0.1:
            return 0.5 + alternation_ratio * 5
        else:
            return 0.7  # Too much alternation can sound choppy

    def _is_bass_melody_pair(self, layer1: Layer, layer2: Layer) -> bool:
        """Check if two layers form a bass-melody pair."""
        role1 = layer1.layer_role
        role2 = layer2.layer_role

        is_bass1 = role1 == "bass"
        is_bass2 = role2 == "bass"
        is_melody1 = role1 in ("melody", "lead")
        is_melody2 = role2 in ("melody", "lead")

        return (is_bass1 and is_melody2) or (is_bass2 and is_melody1)

    def _get_role_relationship(self, layer1: Layer, layer2: Layer) -> str:
        """Get the relationship type between two layers based on their roles.

        Returns one of:
        - "bass_melody": Bass supporting melody/lead
        - "chords_melody": Chords supporting melody/lead
        - "chords_bass": Chords and bass (harmonic foundation)
        - "drums_melody": Drums and melody (rhythmic alignment)
        - "drums_bass": Drums and bass (rhythmic lock)
        - "parallel_melody": Two melodic layers (melody, lead, pad)
        - "same_role": Same role (e.g., two drum layers)
        - "other": No specific relationship
        """
        role1, role2 = layer1.layer_role, layer2.layer_role

        # Sort roles for consistent comparison
        roles = tuple(sorted([role1, role2]))

        relationships = {
            ("bass", "lead"): "bass_melody",
            ("bass", "melody"): "bass_melody",
            ("chords", "lead"): "chords_melody",
            ("chords", "melody"): "chords_melody",
            ("bass", "chords"): "chords_bass",
            ("drums", "lead"): "drums_melody",
            ("drums", "melody"): "drums_melody",
            ("bass", "drums"): "drums_bass",
            ("lead", "melody"): "parallel_melody",
            ("melody", "pad"): "parallel_melody",
            ("lead", "pad"): "parallel_melody",
        }

        if role1 == role2:
            return "same_role"

        return relationships.get(roles, "other")

    def _bass_melody_support(self, layer1: Layer, layer2: Layer) -> float:
        """Evaluate how well bass supports melody harmonically.

        Good bass-melody relationship:
        - Bass plays roots and fifths when melody has thirds/sevenths
        - Bass avoids doubling melody notes at unison/octave too often
        - Bass provides harmonic foundation
        """
        # Determine which is bass and which is melody
        if "bass" in layer1.name.lower():
            bass_layer, melody_layer = layer1, layer2
        else:
            bass_layer, melody_layer = layer2, layer1

        if not bass_layer.phrases or not melody_layer.phrases:
            return 0.5

        bass_notes = [n for n in bass_layer.phrases[0].notes if n.pitch != NoteName.REST]
        melody_notes = [n for n in melody_layer.phrases[0].notes if n.pitch != NoteName.REST]

        if not bass_notes or not melody_notes:
            return 0.5

        scores = []
        sample_size = min(6, len(bass_notes), len(melody_notes))

        for i in range(sample_size):
            bass_idx = i * len(bass_notes) // sample_size
            melody_idx = i * len(melody_notes) // sample_size

            interval = abs(melody_notes[melody_idx].midi_pitch - bass_notes[bass_idx].midi_pitch) % 12

            # Bass on root (0) or fifth (7) while melody elsewhere: excellent
            # This is approximated by checking if they're not at same pitch class
            if interval in {3, 4, 8, 9, 10, 11}:  # Third, sixth, seventh relationships
                scores.append(1.0)
            elif interval in {0, 12}:  # Unison/octave doubling
                scores.append(0.5)  # Sometimes OK but not ideal
            elif interval == 7:  # Fifth apart
                scores.append(0.9)  # Strong harmonic support
            else:
                scores.append(0.6)

        return sum(scores) / len(scores) if scores else 0.5


def create_contextual_fitness(
    intrinsic_fitness: FitnessFunction,
    evolved_layers: dict[str, tuple[Layer, str]],
    use_context: bool = True,
    intrinsic_weight: float = 0.7,
    context_weight: float = 0.3,
    context_group: str = "",
    metric_weights: dict[str, float] = None,
) -> FitnessFunction:
    """Helper to create contextual fitness from evolved layers.

    Args:
        intrinsic_fitness: The layer's own fitness function
        evolved_layers: Dict of {name: (layer, rhythm)} for context
        use_context: If False, just returns intrinsic fitness
        intrinsic_weight: Weight for intrinsic quality (default 0.7)
        context_weight: Weight for context fit (default 0.3)
        context_group: If set, only consider layers with the same context_group.
                       Empty string means consider all layers.
        metric_weights: Custom weights for context metrics. Available metrics:
            - "rhythmic": How rhythms complement each other
            - "density": Different busy-ness levels between layers
            - "harmonic": Consonant intervals between melodic layers
            - "voice_leading": Contrary motion, avoid parallel 5ths/octaves
            - "call_response": Alternating activity patterns

    Returns:
        ContextualFitness wrapper or intrinsic fitness
    """
    if not use_context or not evolved_layers:
        return intrinsic_fitness

    # Filter by context_group if specified
    if context_group:
        filtered_layers = {
            name: (layer, rhythm)
            for name, (layer, rhythm) in evolved_layers.items()
            if layer.context_group == context_group
        }
    else:
        filtered_layers = evolved_layers

    if not filtered_layers:
        return intrinsic_fitness

    context_list = list(filtered_layers.values())
    return ContextualFitness(
        intrinsic_fitness=intrinsic_fitness,
        context_layers=context_list,
        intrinsic_weight=intrinsic_weight,
        context_weight=context_weight,
        metric_weights=metric_weights,
    )


def get_context_groups(evolved_layers: dict[str, tuple[Layer, str]]) -> dict[str, list[str]]:
    """Get a mapping of context groups to layer names.

    Args:
        evolved_layers: Dict of {name: (layer, rhythm)} for all layers

    Returns:
        Dict mapping context_group -> list of layer names in that group.
        Layers with empty context_group are listed under "".
    """
    groups: dict[str, list[str]] = {}
    for name, (layer, _) in evolved_layers.items():
        group = layer.context_group
        if group not in groups:
            groups[group] = []
        groups[group].append(name)
    return groups
