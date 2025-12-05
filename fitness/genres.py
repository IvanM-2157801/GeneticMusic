from .base import (
    FitnessFunction,
    RhythmFitnessFunction,
    note_variety,
    rest_ratio,
    interval_smoothness,
    scale_adherence,
    rhythmic_variety,
    rhythm_density,
    rhythm_rest_ratio,
    rhythm_variety,
    rhythm_syncopation,
    rhythm_regularity,
    rhythm_downbeat_emphasis,
    MAJOR_SCALE,
    MINOR_SCALE,
    PENTATONIC,
    BLUES_SCALE,
)
from core.music import Layer, Phrase, NoteName


# === Melody Fitness Functions ===

class PopMelodyFitness(FitnessFunction):
    """Melody fitness for pop music: catchy, smooth, major key."""
    
    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0
        
        scores = []
        for phrase in layer.phrases:
            score = (
                # 0.60 * scale_adherence(phrase, MAJOR_SCALE) +
                0.40 * interval_smoothness(phrase) +
                0.20 * note_variety(phrase) +
                0.15 * self._repetition_bonus(phrase) +
                0.25 * rest_ratio(phrase)
            )
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    def _repetition_bonus(self, phrase: Phrase) -> float:
        """Reward repeated motifs."""
        if len(phrase.notes) < 4:
            return 0.0
        patterns = []
        for i in range(len(phrase.notes) - 1):
            p = (phrase.notes[i].pitch, phrase.notes[i + 1].pitch)
            patterns.append(p)
        
        unique = len(set(patterns))
        return 1 - (unique / len(patterns)) if patterns else 0.0


class JazzMelodyFitness(FitnessFunction):
    """Melody fitness for jazz: chromatic, varied."""
    
    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0
        
        scores = []
        for phrase in layer.phrases:
            score = (
                0.35 * note_variety(phrase) +
                0.35 * self._chromatic_interest(phrase) +
                0.30 * interval_smoothness(phrase)
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


class BluesMelodyFitness(FitnessFunction):
    """Melody fitness for blues: blue notes, smooth."""
    
    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0
        
        scores = []
        for phrase in layer.phrases:
            score = (
                0.40 * scale_adherence(phrase, BLUES_SCALE) +
                0.35 * self._blue_note_bonus(phrase) +
                0.25 * interval_smoothness(phrase)
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
        return 1.0 if 0.2 <= ratio <= 0.4 else max(0, 1 - abs(ratio - 0.3) * 2)


class AmbientMelodyFitness(FitnessFunction):
    """Melody fitness for ambient: smooth, pentatonic."""
    
    def evaluate(self, layer: Layer) -> float:
        if not layer.phrases:
            return 0.0
        
        scores = []
        for phrase in layer.phrases:
            score = (
                0.50 * interval_smoothness(phrase) +
                0.50 * scale_adherence(phrase, PENTATONIC)
            )
            scores.append(score)
        
        return sum(scores) / len(scores)


# === Rhythm Fitness Functions ===

class PopRhythmFitness(RhythmFitnessFunction):
    """Rhythm fitness for pop: regular, moderate density, downbeat emphasis."""
    
    def evaluate(self, rhythm: str) -> float:
        if not rhythm:
            return 0.0
        
        density = rhythm_density(rhythm)
        regularity = rhythm_regularity(rhythm)
        downbeat = rhythm_downbeat_emphasis(rhythm)
        rests = rhythm_rest_ratio(rhythm)
        
        # Pop wants: moderate density (0.3-0.6), regular patterns, strong downbeats, few rests
        density_score = 1.0 - abs(density - 0.4) * 2  # Optimal around 0.4
        rest_score = 1.0 - rests  # Fewer rests better
        
        return (
            0.10 * max(0, density_score) +
            0.15 * regularity +
            0.55 * downbeat +
            0.20 * rest_score
        )


class JazzRhythmFitness(RhythmFitnessFunction):
    """Rhythm fitness for jazz: syncopated, varied, some rests."""
    
    def evaluate(self, rhythm: str) -> float:
        if not rhythm:
            return 0.0
        
        syncopation = rhythm_syncopation(rhythm)
        variety = rhythm_variety(rhythm)
        rests = rhythm_rest_ratio(rhythm)
        density = rhythm_density(rhythm)
        
        # Jazz wants: syncopation, variety, moderate rests, moderate-high density
        rest_score = 1.0 - abs(rests - 0.2) * 3  # Some rests good (around 20%)
        density_score = 1.0 - abs(density - 0.5) * 2  # Moderate-high density
        
        return (
            0.35 * syncopation +
            0.25 * variety +
            0.20 * max(0, rest_score) +
            0.20 * max(0, density_score)
        )


class BluesRhythmFitness(RhythmFitnessFunction):
    """Rhythm fitness for blues: shuffle feel, moderate, some swing."""
    
    def evaluate(self, rhythm: str) -> float:
        if not rhythm:
            return 0.0
        
        density = rhythm_density(rhythm)
        variety = rhythm_variety(rhythm)
        downbeat = rhythm_downbeat_emphasis(rhythm)
        syncopation = rhythm_syncopation(rhythm)
        
        # Blues wants: moderate density, some variety, downbeat emphasis with swing
        density_score = 1.0 - abs(density - 0.35) * 2
        
        return (
            0.30 * max(0, density_score) +
            0.25 * downbeat +
            0.25 * syncopation +
            0.20 * variety
        )


class AmbientRhythmFitness(RhythmFitnessFunction):
    """Rhythm fitness for ambient: sparse, lots of rests, slow."""
    
    def evaluate(self, rhythm: str) -> float:
        if not rhythm:
            return 0.0
        
        density = rhythm_density(rhythm)
        rests = rhythm_rest_ratio(rhythm)
        regularity = rhythm_regularity(rhythm)
        
        # Ambient wants: low density, many rests, regular/predictable
        density_score = 1.0 - density  # Lower density better
        
        return (
            0.40 * density_score +
            0.35 * rests +
            0.25 * regularity
        )




# Registry for easy access
MELODY_FITNESS = {
    "pop": PopMelodyFitness,
    "jazz": JazzMelodyFitness,
    "blues": BluesMelodyFitness,
    "ambient": AmbientMelodyFitness,
}

RHYTHM_FITNESS = {
    "pop": PopRhythmFitness,
    "jazz": JazzRhythmFitness,
    "blues": BluesRhythmFitness,
    "ambient": AmbientRhythmFitness,
}
