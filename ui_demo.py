import gradio as gr
from core.music import Phrase, Layer, NoteName
from core.genome_ops import ChordProgression
from fitness.base import (
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
from fitness.rhythm import (
    rhythm_complexity,
    rhythm_rest_ratio,
    rhythm_density,
    rhythm_syncopation,
    rhythm_groove,
    rhythm_consistency,
    rhythm_offbeat_emphasis,
)
from fitness.drums import (
    strong_beat_emphasis,
    backbeat_emphasis,
    sparsity,
    simplicity,
    offbeat_pattern,
    perfect_consistency,
)
from fitness.chords import (
    ChordFitnessFunction,
    chord_variety,
    chord_type_variety,
    root_motion_smoothness,
    functional_harmony_score,
    resolution_bonus,
    triadic_bonus,
    seventh_chord_bonus,
    diminished_chord_score,
    close_voicing_score,
    repetitive_pattern_score,
    chord_progression_similarity,
)
from layered_composer import LayeredComposer, LayerConfig


# =============================================================================
# SCALE OPTIONS
# =============================================================================

SCALES = {
    "Minor": MINOR_SCALE,
    "Major": MAJOR_SCALE,
    "Pentatonic": PENTATONIC,
    "Blues": BLUES_SCALE,
}

SCALE_IMPORTS = {
    "Minor": "MINOR_SCALE",
    "Major": "MAJOR_SCALE",
    "Pentatonic": "PENTATONIC",
    "Blues": "BLUES_SCALE",
}


# =============================================================================
# FITNESS FUNCTION BUILDERS
# =============================================================================


def make_rhythm_fitness(weights: dict[str, float]):
    """Create rhythm fitness from all available rhythm metrics."""
    metric_fns = {
        "groove": rhythm_groove,
        "complexity": rhythm_complexity,
        "density": rhythm_density,
        "syncopation": rhythm_syncopation,
        "consistency": rhythm_consistency,
        "offbeat": rhythm_offbeat_emphasis,
        "rests": rhythm_rest_ratio,
        "strong_beat": strong_beat_emphasis,
        "backbeat": backbeat_emphasis,
        "sparsity": sparsity,
        "simplicity": simplicity,
        "drum_offbeat": offbeat_pattern,
        "perfect_consistency": perfect_consistency,
    }

    def fitness(rhythm: str) -> float:
        score = 0.0
        total_weight = 0.0
        for metric, weight in weights.items():
            if metric in metric_fns and weight != 0:
                fn = metric_fns[metric]
                value = fn(rhythm)
                if weight < 0:
                    score += abs(weight) * (1 - value)
                else:
                    score += weight * value
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5

    return fitness


def make_melody_fitness(weights: dict[str, float], scale_notes: list):
    """Create melody fitness from all available melody metrics."""

    class CustomMelodyFitness(FitnessFunction):
        def evaluate(self, layer: Layer) -> float:
            if not layer.phrases:
                return 0.0

            metric_fns = {
                "note_variety": note_variety,
                "interval_smoothness": interval_smoothness,
                "scale_adherence": lambda p: scale_adherence(p, scale_notes),
                "rest_ratio": rest_ratio,
                "rhythmic_variety": rhythmic_variety,
            }

            def score_phrase(phrase: Phrase) -> float:
                score = 0.0
                total_weight = 0.0
                for metric, weight in weights.items():
                    if metric in metric_fns and weight != 0:
                        fn = metric_fns[metric]
                        value = fn(phrase)
                        if weight < 0:
                            score += abs(weight) * (1 - value)
                        else:
                            score += weight * value
                        total_weight += abs(weight)
                return score / total_weight if total_weight > 0 else 0.5

            scores = [score_phrase(p) for p in layer.phrases]
            return sum(scores) / len(scores)

    return CustomMelodyFitness()


def make_chord_fitness(weights: dict[str, float]):
    """Create chord fitness from all available chord metrics."""

    class CustomChordFitness(ChordFitnessFunction):
        def evaluate(self, progression: ChordProgression) -> float:
            metric_fns = {
                "chord_variety": chord_variety,
                "chord_type_variety": chord_type_variety,
                "root_motion_smoothness": root_motion_smoothness,
                "functional_harmony": functional_harmony_score,
                "resolution": resolution_bonus,
                "triadic": triadic_bonus,
                "seventh_chord": seventh_chord_bonus,
                "diminished": diminished_chord_score,
                "close_voicing": close_voicing_score,
                "repetitive_pattern": repetitive_pattern_score,
                "progression_similarity": chord_progression_similarity,
            }

            score = 0.0
            total_weight = 0.0
            for metric, weight in weights.items():
                if metric in metric_fns and weight != 0:
                    fn = metric_fns[metric]
                    value = fn(progression)
                    if weight < 0:
                        score += abs(weight) * (1 - value)
                    else:
                        score += weight * value
                    total_weight += abs(weight)
            return score / total_weight if total_weight > 0 else 0.5

    return CustomChordFitness()


# ============================================================================= # PYTHON PRESET GENERATOR
# =============================================================================


def generate_python_preset(
    mode,
    bpm,
    bars,
    beats_per_bar,
    max_subdivision,
    population_size,
    generations,
    fitness_threshold,
    instrument,
    scale_name,
    drum_sound,
    num_chords,
    notes_per_chord,
    r_groove,
    r_complexity,
    r_density,
    r_syncopation,
    r_consistency,
    r_offbeat,
    r_rests,
    r_strong_beat,
    r_backbeat,
    r_sparsity,
    r_simplicity,
    r_drum_offbeat,
    r_perfect_consistency,
    m_note_variety,
    m_interval_smoothness,
    m_scale_adherence,
    m_rest_ratio,
    m_rhythmic_variety,
    c_chord_variety,
    c_chord_type_variety,
    c_root_motion_smoothness,
    c_functional_harmony,
    c_resolution,
    c_triadic,
    c_seventh_chord,
    c_diminished,
    c_close_voicing,
    c_repetitive_pattern,
    c_progression_similarity,
    gain,
    lpf,
    hpf,
    room,
    roomsize,
    delay,
    delaytime,
    delayfeedback,
    distort,
    pan,
    attack,
    decay,
    sustain,
    release,
):
    """Generate Python code preset from current UI settings."""

    scale_import = SCALE_IMPORTS.get(scale_name, "MINOR_SCALE")

    code = f'''"""Generated preset from GeneticMusic UI.

Copy this code into your own script to use these settings.
Mode: {mode}
"""

from fitness.base import (
    FitnessFunction, note_variety, rest_ratio, interval_smoothness,
    scale_adherence, rhythmic_variety, {scale_import},
)
from fitness.rhythm import (
    rhythm_complexity, rhythm_rest_ratio, rhythm_density,
    rhythm_syncopation, rhythm_groove, rhythm_consistency,
    rhythm_offbeat_emphasis,
)
from fitness.drums import (
    strong_beat_emphasis, backbeat_emphasis, sparsity,
    simplicity, offbeat_pattern, perfect_consistency,
)
from fitness.chords import (
    ChordFitnessFunction, chord_variety, chord_type_variety,
    root_motion_smoothness, functional_harmony_score, resolution_bonus,
    triadic_bonus, seventh_chord_bonus, diminished_chord_score,
    close_voicing_score, repetitive_pattern_score, chord_progression_similarity,
)
from layered_composer import LayeredComposer, LayerConfig
from core.music import Layer, Phrase
from core.genome_ops import ChordProgression


# =============================================================================
# MODE SETTINGS
# =============================================================================

MODE = "{mode}"  # "Melody", "Chord", or "Drum"
DRUM_SOUND = "{drum_sound}"  # Used in Drum mode
NUM_CHORDS = {num_chords}  # Number of chords (Chord mode)
NOTES_PER_CHORD = {notes_per_chord}  # Notes per chord (Chord mode)
FITNESS_THRESHOLD = {fitness_threshold}  # Early stop threshold (0 = disabled)


# =============================================================================
# RHYTHM FITNESS WEIGHTS
# =============================================================================

RHYTHM_WEIGHTS = {{
    "groove": {r_groove},
    "complexity": {r_complexity},
    "density": {r_density},
    "syncopation": {r_syncopation},
    "consistency": {r_consistency},
    "offbeat": {r_offbeat},
    "rests": {-r_rests if r_rests > 0 else 0},
    "strong_beat": {r_strong_beat},
    "backbeat": {r_backbeat},
    "sparsity": {r_sparsity},
    "simplicity": {r_simplicity},
    "drum_offbeat": {r_drum_offbeat},
    "perfect_consistency": {r_perfect_consistency},
}}


# =============================================================================
# MELODY FITNESS WEIGHTS
# =============================================================================

MELODY_WEIGHTS = {{
    "note_variety": {m_note_variety},
    "interval_smoothness": {m_interval_smoothness},
    "scale_adherence": {m_scale_adherence},
    "rest_ratio": {-m_rest_ratio if m_rest_ratio > 0 else 0},
    "rhythmic_variety": {m_rhythmic_variety},
}}


# =============================================================================
# CHORD FITNESS WEIGHTS
# =============================================================================

CHORD_WEIGHTS = {{
    "chord_variety": {c_chord_variety},
    "chord_type_variety": {c_chord_type_variety},
    "root_motion_smoothness": {c_root_motion_smoothness},
    "functional_harmony": {c_functional_harmony},
    "resolution": {c_resolution},
    "triadic": {c_triadic},
    "seventh_chord": {c_seventh_chord},
    "diminished": {-c_diminished if c_diminished > 0 else 0},
    "close_voicing": {-c_close_voicing if c_close_voicing > 0 else 0},
    "repetitive_pattern": {-c_repetitive_pattern if c_repetitive_pattern > 0 else 0},
    "progression_similarity": {c_progression_similarity},
}}


# =============================================================================
# EFFECT SETTINGS
# =============================================================================

EFFECTS = {{
    "gain": {gain},
    "lpf": {int(lpf)},
    "hpf": {int(hpf)},
    "room": {room},
    "roomsize": {roomsize},
    "delay": {delay},
    "delaytime": {delaytime},
    "delayfeedback": {delayfeedback},
    "distort": {distort},
    "pan": {pan},
    "attack": {attack},
    "decay": {decay},
    "sustain": {sustain},
    "release": {release},
}}


# =============================================================================
# EVOLUTION SETTINGS
# =============================================================================

BPM = {bpm}
BARS = {bars}
BEATS_PER_BAR = {beats_per_bar}
MAX_SUBDIVISION = {max_subdivision}
POPULATION_SIZE = {population_size}
GENERATIONS = {generations}
INSTRUMENT = "{instrument}"
SCALE = {scale_import}


# =============================================================================
# FITNESS FUNCTION BUILDERS
# =============================================================================

def make_rhythm_fitness(weights):
    from fitness.rhythm import (rhythm_groove, rhythm_complexity, rhythm_density,
        rhythm_syncopation, rhythm_consistency, rhythm_offbeat_emphasis, rhythm_rest_ratio)
    from fitness.drums import (strong_beat_emphasis, backbeat_emphasis, sparsity,
        simplicity, offbeat_pattern, perfect_consistency)

    metric_fns = {{
        "groove": rhythm_groove, "complexity": rhythm_complexity,
        "density": rhythm_density, "syncopation": rhythm_syncopation,
        "consistency": rhythm_consistency, "offbeat": rhythm_offbeat_emphasis,
        "rests": rhythm_rest_ratio, "strong_beat": strong_beat_emphasis,
        "backbeat": backbeat_emphasis, "sparsity": sparsity,
        "simplicity": simplicity, "drum_offbeat": offbeat_pattern,
        "perfect_consistency": perfect_consistency,
    }}

    def fitness(rhythm: str) -> float:
        score, total_weight = 0.0, 0.0
        for metric, weight in weights.items():
            if metric in metric_fns and weight != 0:
                value = metric_fns[metric](rhythm)
                score += abs(weight) * ((1 - value) if weight < 0 else value)
                total_weight += abs(weight)
        return score / total_weight if total_weight > 0 else 0.5
    return fitness


def make_melody_fitness(weights, scale_notes):
    from fitness.base import (FitnessFunction, note_variety, rest_ratio,
        interval_smoothness, scale_adherence, rhythmic_variety)
    from core.music import Layer, Phrase

    class CustomMelodyFitness(FitnessFunction):
        def evaluate(self, layer: Layer) -> float:
            if not layer.phrases: return 0.0
            metric_fns = {{
                "note_variety": note_variety, "interval_smoothness": interval_smoothness,
                "scale_adherence": lambda p: scale_adherence(p, scale_notes),
                "rest_ratio": rest_ratio, "rhythmic_variety": rhythmic_variety,
            }}
            def score_phrase(phrase):
                score, total_weight = 0.0, 0.0
                for metric, weight in weights.items():
                    if metric in metric_fns and weight != 0:
                        value = metric_fns[metric](phrase)
                        score += abs(weight) * ((1 - value) if weight < 0 else value)
                        total_weight += abs(weight)
                return score / total_weight if total_weight > 0 else 0.5
            return sum(score_phrase(p) for p in layer.phrases) / len(layer.phrases)
    return CustomMelodyFitness()


def make_chord_fitness(weights):
    from fitness.chords import (ChordFitnessFunction, chord_variety, chord_type_variety,
        root_motion_smoothness, functional_harmony_score, resolution_bonus,
        triadic_bonus, seventh_chord_bonus, diminished_chord_score,
        close_voicing_score, repetitive_pattern_score, chord_progression_similarity)

    class CustomChordFitness(ChordFitnessFunction):
        def evaluate(self, progression):
            metric_fns = {{
                "chord_variety": chord_variety, "chord_type_variety": chord_type_variety,
                "root_motion_smoothness": root_motion_smoothness,
                "functional_harmony": functional_harmony_score, "resolution": resolution_bonus,
                "triadic": triadic_bonus, "seventh_chord": seventh_chord_bonus,
                "diminished": diminished_chord_score, "close_voicing": close_voicing_score,
                "repetitive_pattern": repetitive_pattern_score,
                "progression_similarity": chord_progression_similarity,
            }}
            score, total_weight = 0.0, 0.0
            for metric, weight in weights.items():
                if metric in metric_fns and weight != 0:
                    value = metric_fns[metric](progression)
                    score += abs(weight) * ((1 - value) if weight < 0 else value)
                    total_weight += abs(weight)
            return score / total_weight if total_weight > 0 else 0.5
    return CustomChordFitness()


# =============================================================================
# MAIN
# =============================================================================

def main():
    rhythm_fn = make_rhythm_fitness(RHYTHM_WEIGHTS)
    melody_fn = make_melody_fitness(MELODY_WEIGHTS, SCALE)
    chord_fn = make_chord_fitness(CHORD_WEIGHTS)

    composer = LayeredComposer(
        population_size=POPULATION_SIZE, mutation_rate=0.25,
        elitism_count=max(2, POPULATION_SIZE // 5),
        rhythm_generations=GENERATIONS, melody_generations=GENERATIONS,
        fitness_threshold=FITNESS_THRESHOLD,
    )

    if MODE == "Drum":
        composer.add_layer(LayerConfig(
            name="drums", instrument=DRUM_SOUND, bars=BARS,
            beats_per_bar=BEATS_PER_BAR, max_subdivision=MAX_SUBDIVISION,
            is_drum=True, drum_sound=DRUM_SOUND,
            rhythm_fitness_fn=rhythm_fn,
            layer_role="drums", **EFFECTS,
        ))
    elif MODE == "Chord":
        composer.add_layer(LayerConfig(
            name="chords", instrument=INSTRUMENT, bars=BARS,
            beats_per_bar=BEATS_PER_BAR, max_subdivision=MAX_SUBDIVISION,
            is_chord_layer=True, num_chords=NUM_CHORDS,
            notes_per_chord=NOTES_PER_CHORD,
            rhythm_fitness_fn=rhythm_fn, chord_fitness_fn=chord_fn,
            layer_role="chords", **EFFECTS,
        ))
    else:  # Melody mode
        composer.add_layer(LayerConfig(
            name="melody", instrument=INSTRUMENT, bars=BARS,
            beats_per_bar=BEATS_PER_BAR, max_subdivision=MAX_SUBDIVISION,
            octave_range=(4, 5), base_octave=4,
            rhythm_fitness_fn=rhythm_fn, melody_fitness_fn=melody_fn,
            layer_role="melody", **EFFECTS,
        ))

    print(f"Evolving {{MODE}} layer...")
    composer.evolve_all_layers(verbose=True)

    composition = composer.get_composition(bpm=BPM, random_scale=True)

    print("\\n" + "=" * 60)
    print("STRUDEL CODE")
    print("=" * 60)
    print(composition.to_strudel())
    print("\\n" + "=" * 60)
    print("STRUDEL LINK")
    print("=" * 60)
    print(composition.to_strudel_link())


if __name__ == "__main__":
    main()
'''
    return code


# =============================================================================
# GENERATION FUNCTION
# =============================================================================


def generate_strudel_iframe(strudel_link: str) -> str:
    """Generate an HTML iframe for Strudel embed with fallback."""
    import time

    # Add cache-busting timestamp to force iframe reload
    cache_bust = int(time.time() * 1000)

    # Try embed mode by adding ?hideHeader to the URL
    # The link format is: https://strudel.cc/#BASE64CODE
    # We convert to: https://strudel.cc/?hideHeader&t=TIMESTAMP#BASE64CODE
    if "#" in strudel_link:
        base, code = strudel_link.split("#", 1)
        embed_link = f"{base}?hideHeader&hideSettings&t={cache_bust}#{code}"
    else:
        embed_link = f"{strudel_link}?t={cache_bust}"

    return f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background: #1a1a2e;">
        <iframe
            id="strudel-frame-{cache_bust}"
            src="{embed_link}"
            width="100%"
            height="450"
            frameborder="0"
            allow="autoplay; microphone"
            style="display: block;"
            sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
        ></iframe>
    </div>
    <div style="display: flex; gap: 10px; margin-top: 10px; align-items: center;">
        <a href="{strudel_link}" target="_blank" rel="noopener"
           style="display: inline-block; padding: 8px 16px; background: #4a90d9; color: white;
                  text-decoration: none; border-radius: 4px; font-size: 14px;">
            Open in Strudel ↗
        </a>
        <span style="font-size: 12px; color: #666;">
            Press <b>Ctrl+Enter</b> to play, <b>Ctrl+.</b> to stop
        </span>
    </div>
    """


def generate_music(
    mode,
    bpm,
    bars,
    beats_per_bar,
    max_subdivision,
    population_size,
    generations,
    fitness_threshold,
    instrument,
    scale_name,
    drum_sound,
    num_chords,
    notes_per_chord,
    r_groove,
    r_complexity,
    r_density,
    r_syncopation,
    r_consistency,
    r_offbeat,
    r_rests,
    r_strong_beat,
    r_backbeat,
    r_sparsity,
    r_simplicity,
    r_drum_offbeat,
    r_perfect_consistency,
    m_note_variety,
    m_interval_smoothness,
    m_scale_adherence,
    m_rest_ratio,
    m_rhythmic_variety,
    c_chord_variety,
    c_chord_type_variety,
    c_root_motion_smoothness,
    c_functional_harmony,
    c_resolution,
    c_triadic,
    c_seventh_chord,
    c_diminished,
    c_close_voicing,
    c_repetitive_pattern,
    c_progression_similarity,
    gain,
    lpf,
    hpf,
    room,
    roomsize,
    delay,
    delaytime,
    delayfeedback,
    distort,
    pan,
    attack,
    decay,
    sustain,
    release,
):
    """Generate music with the given fitness weights and mode."""

    # Build rhythm fitness weights dict
    rhythm_weights = {
        "groove": r_groove,
        "complexity": r_complexity,
        "density": r_density,
        "syncopation": r_syncopation,
        "consistency": r_consistency,
        "offbeat": r_offbeat,
        "rests": -r_rests if r_rests > 0 else 0,
        "strong_beat": r_strong_beat,
        "backbeat": r_backbeat,
        "sparsity": r_sparsity,
        "simplicity": r_simplicity,
        "drum_offbeat": r_drum_offbeat,
        "perfect_consistency": r_perfect_consistency,
    }

    # Build melody fitness weights dict
    melody_weights = {
        "note_variety": m_note_variety,
        "interval_smoothness": m_interval_smoothness,
        "scale_adherence": m_scale_adherence,
        "rest_ratio": -m_rest_ratio if m_rest_ratio > 0 else 0,
        "rhythmic_variety": m_rhythmic_variety,
    }

    # Build chord weights dict
    chord_weights = {
        "chord_variety": c_chord_variety,
        "chord_type_variety": c_chord_type_variety,
        "root_motion_smoothness": c_root_motion_smoothness,
        "functional_harmony": c_functional_harmony,
        "resolution": c_resolution,
        "triadic": c_triadic,
        "seventh_chord": c_seventh_chord,
        "diminished": -c_diminished if c_diminished > 0 else 0,
        "close_voicing": -c_close_voicing if c_close_voicing > 0 else 0,
        "repetitive_pattern": -c_repetitive_pattern if c_repetitive_pattern > 0 else 0,
        "progression_similarity": c_progression_similarity,
    }

    # Get scale
    scale_notes = SCALES.get(scale_name, MINOR_SCALE)

    # Create fitness functions
    rhythm_fn = make_rhythm_fitness(rhythm_weights)
    melody_fn = make_melody_fitness(melody_weights, scale_notes)
    chord_fn = make_chord_fitness(chord_weights)

    # Create composer
    composer = LayeredComposer(
        population_size=int(population_size),
        mutation_rate=0.25,
        elitism_count=max(2, int(population_size) // 5),
        rhythm_generations=int(generations),
        melody_generations=int(generations),
        fitness_threshold=float(fitness_threshold),
    )

    # Add layer based on mode
    layer_name = mode.lower()
    effects_dict = dict(
        gain=gain,
        lpf=int(lpf),
        hpf=int(hpf),
        room=room,
        roomsize=roomsize,
        delay=delay,
        delaytime=delaytime,
        delayfeedback=delayfeedback,
        distort=distort,
        pan=pan,
        attack=attack,
        decay=decay,
        sustain=sustain,
        release=release,
    )

    if mode == "Drum":
        composer.add_layer(
            LayerConfig(
                name="drums",
                instrument=drum_sound,
                bars=int(bars),
                beats_per_bar=int(beats_per_bar),
                max_subdivision=int(max_subdivision),
                is_drum=True,
                drum_sound=drum_sound,
                rhythm_fitness_fn=rhythm_fn,
                layer_role="drums",
                **effects_dict,
            )
        )
        layer_name = "drums"
    elif mode == "Chord":
        composer.add_layer(
            LayerConfig(
                name="chords",
                instrument=instrument,
                bars=int(bars),
                beats_per_bar=int(beats_per_bar),
                max_subdivision=int(max_subdivision),
                is_chord_layer=True,
                num_chords=int(num_chords),
                notes_per_chord=int(notes_per_chord),
                rhythm_fitness_fn=rhythm_fn,
                chord_fitness_fn=chord_fn,
                layer_role="chords",
                **effects_dict,
            )
        )
        layer_name = "chords"
    else:  # Melody mode
        composer.add_layer(
            LayerConfig(
                name="melody",
                instrument=instrument,
                bars=int(bars),
                beats_per_bar=int(beats_per_bar),
                max_subdivision=int(max_subdivision),
                octave_range=(4, 5),
                base_octave=4,
                rhythm_fitness_fn=rhythm_fn,
                melody_fitness_fn=melody_fn,
                layer_role="melody",
                **effects_dict,
            )
        )
        layer_name = "melody"

    # Evolve
    composer.evolve_all_layers(verbose=False)

    # Get composition with the selected scale
    scale_root = "c"
    scale_type = scale_name.lower()
    composition = composer.get_composition(bpm=int(bpm), random_scale=False)

    # Override scale in layer (for non-drum layers)
    if mode != "Drum":
        for layer in composition.layers:
            layer.scale = f"{scale_root}:{scale_type}"

    # Generate Strudel code and link
    strudel_code = composition.to_strudel()
    strudel_link = composition.to_strudel_link()

    # Build summary based on mode
    rhythm = composer.evolved_rhythms.get(layer_name, "N/A")

    summary = f"""**Mode:** {mode}
**Rhythm:** `{rhythm}`

| Rhythm Metric | Value |
|---------------|-------|
| Groove | {rhythm_groove(rhythm):.2f} |
| Complexity | {rhythm_complexity(rhythm):.2f} |
| Density | {rhythm_density(rhythm):.2f} |
| Syncopation | {rhythm_syncopation(rhythm):.2f} |
| Consistency | {rhythm_consistency(rhythm):.2f} |
| Rest Ratio | {rhythm_rest_ratio(rhythm):.2f} |
"""

    if mode == "Melody":
        phrase = composer.evolved_phrases.get(layer_name)
        if phrase:
            summary += f"""
| Melody Metric | Value |
|---------------|-------|
| Note Variety | {note_variety(phrase):.2f} |
| Smoothness | {interval_smoothness(phrase):.2f} |
| Scale Adherence | {scale_adherence(phrase, scale_notes):.2f} |
| Rest Ratio | {rest_ratio(phrase):.2f} |
"""
    elif mode == "Chord":
        chord_prog = composer.evolved_chords.get(layer_name)
        if chord_prog:
            summary += f"""
| Chord Metric | Value |
|--------------|-------|
| Chord Variety | {chord_variety(chord_prog):.2f} |
| Type Variety | {chord_type_variety(chord_prog):.2f} |
| Root Motion | {root_motion_smoothness(chord_prog):.2f} |
| Functional Harmony | {functional_harmony_score(chord_prog):.2f} |
| Resolution | {resolution_bonus(chord_prog):.2f} |
"""
    elif mode == "Drum":
        summary += f"""
| Drum Metric | Value |
|-------------|-------|
| Strong Beat | {strong_beat_emphasis(rhythm):.2f} |
| Backbeat | {backbeat_emphasis(rhythm):.2f} |
| Sparsity | {sparsity(rhythm):.2f} |
| Simplicity | {simplicity(rhythm):.2f} |
"""

    # Add final fitness scores
    fitness_data = composer.final_fitness.get(layer_name, {})
    if fitness_data:
        summary += f"""
---
### Final Fitness Scores

| Phase | Fitness | Generations |
|-------|---------|-------------|
"""
        if "rhythm" in fitness_data:
            r_fit = fitness_data.get("rhythm", 0)
            r_gen = fitness_data.get("rhythm_gen", 0)
            summary += f"| Rhythm | **{r_fit:.4f}** | {r_gen}/{int(generations)} |\n"
        if "melody" in fitness_data:
            m_fit = fitness_data.get("melody", 0)
            m_gen = fitness_data.get("melody_gen", 0)
            summary += f"| Melody | **{m_fit:.4f}** | {m_gen}/{int(generations)} |\n"
        if "chord" in fitness_data:
            c_fit = fitness_data.get("chord", 0)
            c_gen = fitness_data.get("chord_gen", 0)
            summary += f"| Chord | **{c_fit:.4f}** | {c_gen}/{int(generations)} |\n"

        # Show if early stopping was triggered
        if fitness_threshold > 0:
            any_early = any(
                fitness_data.get(f"{phase}_gen", int(generations)) < int(generations)
                for phase in ["rhythm", "melody", "chord"]
                if f"{phase}_gen" in fitness_data
            )
            if any_early:
                summary += (
                    f"\n*Early stopping triggered (threshold: {fitness_threshold:.2f})*"
                )

    # Also generate Python preset
    python_preset = generate_python_preset(
        mode,
        bpm,
        bars,
        beats_per_bar,
        max_subdivision,
        population_size,
        generations,
        fitness_threshold,
        instrument,
        scale_name,
        drum_sound,
        num_chords,
        notes_per_chord,
        r_groove,
        r_complexity,
        r_density,
        r_syncopation,
        r_consistency,
        r_offbeat,
        r_rests,
        r_strong_beat,
        r_backbeat,
        r_sparsity,
        r_simplicity,
        r_drum_offbeat,
        r_perfect_consistency,
        m_note_variety,
        m_interval_smoothness,
        m_scale_adherence,
        m_rest_ratio,
        m_rhythmic_variety,
        c_chord_variety,
        c_chord_type_variety,
        c_root_motion_smoothness,
        c_functional_harmony,
        c_resolution,
        c_triadic,
        c_seventh_chord,
        c_diminished,
        c_close_voicing,
        c_repetitive_pattern,
        c_progression_similarity,
        gain,
        lpf,
        hpf,
        room,
        roomsize,
        delay,
        delaytime,
        delayfeedback,
        distort,
        pan,
        attack,
        decay,
        sustain,
        release,
    )

    # Generate iframe HTML for embedded player
    strudel_iframe = generate_strudel_iframe(strudel_link)

    return strudel_code, strudel_link, summary, python_preset, strudel_iframe


# =============================================================================
# GRADIO UI
# =============================================================================


def create_ui():
    """Create the Gradio interface with vertically scrollable sidebar."""

    # Simplified CSS - remove any height/overflow restrictions
    css = """
    .reset-btn {
        font-size: 11px !important;
        padding: 4px 8px !important;
        min-width: auto !important;
    }
    """

    with gr.Blocks(title="GeneticMusic Composer", css=css) as demo:
        gr.Markdown("# GeneticMusic - Fitness Function Explorer")

        with gr.Row():
            # =================================================================
            # LEFT: OUTPUT AREA (main content)
            # =================================================================
            with gr.Column(scale=3):
                gr.Markdown("## Strudel Player")

                strudel_player = gr.HTML(
                    label="Strudel Player",
                    value="<p style='color:#888; text-align:center; padding:100px;'>Adjust sliders to generate music...</p>",
                )

                with gr.Accordion("Strudel Code", open=False):
                    strudel_code = gr.Code(
                        label="Strudel Code",
                        language="javascript",
                        lines=10,
                    )

                    strudel_link = gr.Textbox(
                        label="Direct Link (open in new tab)",
                        interactive=False,
                        lines=1,
                    )

                with gr.Accordion("Evolution Summary", open=True):
                    summary = gr.Markdown()

                with gr.Accordion("Python Preset (copy to reuse settings)", open=False):
                    python_preset = gr.Code(
                        label="Python Code",
                        language="python",
                        lines=25,
                    )

            # =================================================================
            # RIGHT: SIDEBAR WITH ALL CONTROLS
            # =================================================================
            with gr.Column(scale=2):
                gr.Markdown("## Controls")

                # --- General Settings ---
                with gr.Accordion("General Settings", open=True):
                    mode = gr.Dropdown(
                        choices=["Melody", "Chord", "Drum"],
                        value="Melody",
                        label="Mode",
                        info="Melody=single notes, Chord=progressions, Drum=percussion",
                    )
                    with gr.Row():
                        bpm = gr.Slider(
                            40,
                            200,
                            value=90,
                            step=5,
                            label="BPM",
                            info="Tempo in beats per minute",
                        )
                        bars = gr.Slider(
                            1,
                            4,
                            value=1,
                            step=1,
                            label="Bars",
                            info="Number of bars to generate",
                        )
                    with gr.Row():
                        beats_per_bar = gr.Slider(
                            4,
                            16,
                            value=8,
                            step=1,
                            label="Beats/Bar",
                            info="Beats per bar (8 = two 4/4 bars worth)",
                        )
                        max_subdivision = gr.Slider(
                            1,
                            4,
                            value=2,
                            step=1,
                            label="Max Subdiv",
                            info="1=quarter, 2=eighth, 3=triplet, 4=16th",
                        )
                    with gr.Row():
                        population_size = gr.Slider(
                            10,
                            10000,
                            value=20,
                            step=5,
                            label="Population",
                            info="Larger = better results, slower",
                        )
                        generations = gr.Slider(
                            10,
                            10000,
                            value=20,
                            step=5,
                            label="Generations",
                            info="Evolution iterations per phase",
                        )
                    with gr.Row():
                        fitness_threshold = gr.Slider(
                            0,
                            1,
                            value=0,
                            step=0.05,
                            label="Early Stop Threshold",
                            info="Stop when fitness >= this (0=disabled)",
                        )
                    with gr.Row():
                        instrument = gr.Dropdown(
                            choices=[
                                "piano",
                                "sawtooth",
                                "square",
                                "triangle",
                                "sine",
                                "supersaw",
                            ],
                            value="piano",
                            label="Instrument",
                            info="Synth sound (Melody/Chord modes)",
                        )
                        scale_name = gr.Dropdown(
                            choices=["Minor", "Major", "Pentatonic", "Blues"],
                            value="Minor",
                            label="Scale",
                            info="Musical scale for melody/chords",
                        )
                    with gr.Row():
                        drum_sound = gr.Dropdown(
                            choices=["bd", "hh", "sd", "oh", "cp", "rim", "tom", "cb"],
                            value="bd",
                            label="Drum Sound",
                            info="bd=kick, hh=hihat, sd=snare, oh=open hihat",
                        )
                    gr.Markdown("**Chord Mode Settings**")
                    with gr.Row():
                        num_chords = gr.Slider(
                            2,
                            8,
                            value=4,
                            step=1,
                            label="Num Chords",
                            info="Number of chords in progression",
                        )
                        notes_per_chord = gr.Slider(
                            2,
                            5,
                            value=3,
                            step=1,
                            label="Notes/Chord",
                            info="2=dyad, 3=triad, 4=7th, 5=9th",
                        )

                # --- Rhythm Fitness ---
                with gr.Accordion("Rhythm Fitness", open=False):
                    reset_rhythm_btn = gr.Button(
                        "Reset All to 0", size="sm", elem_classes="reset-btn"
                    )
                    with gr.Row():
                        r_groove = gr.Slider(
                            0,
                            1,
                            value=0.3,
                            step=0.05,
                            label="Groove",
                            info="Alternating strong/weak beats (danceable)",
                        )
                        r_complexity = gr.Slider(
                            0,
                            1,
                            value=0.2,
                            step=0.05,
                            label="Complexity",
                            info="Variety of note subdivisions",
                        )
                    with gr.Row():
                        r_density = gr.Slider(
                            0,
                            1,
                            value=0.2,
                            step=0.05,
                            label="Density",
                            info="More notes per beat (busier)",
                        )
                        r_syncopation = gr.Slider(
                            0,
                            1,
                            value=0.2,
                            step=0.05,
                            label="Syncopation",
                            info="Off-beat accents and surprises",
                        )
                    with gr.Row():
                        r_consistency = gr.Slider(
                            0,
                            1,
                            value=0.2,
                            step=0.05,
                            label="Consistency",
                            info="Repeating patterns (predictable)",
                        )
                        r_offbeat = gr.Slider(
                            0,
                            1,
                            value=0.1,
                            step=0.05,
                            label="Offbeat",
                            info="Emphasis on off-beat positions",
                        )
                    with gr.Row():
                        r_rests = gr.Slider(
                            0,
                            1,
                            value=0.3,
                            step=0.05,
                            label="Penalize Rests",
                            info="Higher = fewer silent beats",
                        )
                        r_strong_beat = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Strong Beat",
                            info="Hits on beats 1 & 5 (kick style)",
                        )
                    with gr.Row():
                        r_backbeat = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Backbeat",
                            info="Hits on beats 3 & 7 (snare style)",
                        )
                        r_sparsity = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Sparsity",
                            info="Fewer notes, more space",
                        )
                    with gr.Row():
                        r_simplicity = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Simplicity",
                            info="Single hits vs subdivided beats",
                        )
                        r_drum_offbeat = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Drum Offbeat",
                            info="Offbeat with rests on downbeats",
                        )
                    r_perfect_consistency = gr.Slider(
                        0,
                        1,
                        value=0.0,
                        step=0.05,
                        label="Perfect Consistency",
                        info="All beats same subdivision (driving)",
                    )

                # --- Melody Fitness ---
                with gr.Accordion("Melody Fitness", open=False):
                    reset_melody_btn = gr.Button(
                        "Reset All to 0", size="sm", elem_classes="reset-btn"
                    )
                    with gr.Row():
                        m_note_variety = gr.Slider(
                            0,
                            1,
                            value=0.3,
                            step=0.05,
                            label="Note Variety",
                            info="More unique pitches used",
                        )
                        m_interval_smoothness = gr.Slider(
                            0,
                            1,
                            value=0.4,
                            step=0.05,
                            label="Smoothness",
                            info="Stepwise motion, small jumps",
                        )
                    with gr.Row():
                        m_scale_adherence = gr.Slider(
                            0,
                            1,
                            value=0.5,
                            step=0.05,
                            label="Scale Adherence",
                            info="Stay in key, avoid wrong notes",
                        )
                        m_rest_ratio = gr.Slider(
                            0,
                            1,
                            value=0.2,
                            step=0.05,
                            label="Penalize Rests",
                            info="Higher = fewer silent notes",
                        )
                    m_rhythmic_variety = gr.Slider(
                        0,
                        1,
                        value=0.1,
                        step=0.05,
                        label="Rhythmic Variety",
                        info="Mix of note durations",
                    )

                # --- Chord Fitness ---
                with gr.Accordion("Chord Fitness (Chord mode)", open=False):
                    reset_chord_btn = gr.Button(
                        "Reset All to 0", size="sm", elem_classes="reset-btn"
                    )
                    with gr.Row():
                        c_chord_variety = gr.Slider(
                            0,
                            1,
                            value=0.3,
                            step=0.05,
                            label="Chord Variety",
                            info="Variety of root notes used",
                        )
                        c_chord_type_variety = gr.Slider(
                            0,
                            1,
                            value=0.2,
                            step=0.05,
                            label="Type Variety",
                            info="Variety of chord qualities (maj/min/7th)",
                        )
                    with gr.Row():
                        c_root_motion_smoothness = gr.Slider(
                            0,
                            1,
                            value=0.3,
                            step=0.05,
                            label="Root Motion",
                            info="Smooth root movement (classical)",
                        )
                        c_functional_harmony = gr.Slider(
                            0,
                            1,
                            value=0.4,
                            step=0.05,
                            label="Functional Harmony",
                            info="Use of I, IV, V chords (tonal)",
                        )
                    with gr.Row():
                        c_resolution = gr.Slider(
                            0,
                            1,
                            value=0.3,
                            step=0.05,
                            label="Resolution",
                            info="V-I and ii-V-I patterns",
                        )
                        c_triadic = gr.Slider(
                            0,
                            1,
                            value=0.2,
                            step=0.05,
                            label="Triadic",
                            info="Prefer simple triads (pop/rock)",
                        )
                    with gr.Row():
                        c_seventh_chord = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="7th Chords",
                            info="Prefer 7th chord extensions (jazz)",
                        )
                        c_diminished = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Penalize Diminished",
                            info="Avoid diminished chords",
                        )
                    with gr.Row():
                        c_close_voicing = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Penalize Close Voicing",
                            info="Avoid clustered/dissonant chords",
                        )
                        c_repetitive_pattern = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Penalize Repetition",
                            info="Avoid A-B-A-B patterns",
                        )
                    c_progression_similarity = gr.Slider(
                        0,
                        1,
                        value=0.2,
                        step=0.05,
                        label="Progression Similarity",
                        info="Similarity between consecutive chords",
                    )

                # --- Effects ---
                with gr.Accordion("Sound Effects", open=False):
                    reset_effects_btn = gr.Button(
                        "Reset to Defaults", size="sm", elem_classes="reset-btn"
                    )
                    with gr.Row():
                        gain = gr.Slider(
                            0,
                            1,
                            value=0.6,
                            step=0.05,
                            label="Gain",
                            info="Output volume level",
                        )
                        pan = gr.Slider(
                            0,
                            1,
                            value=0.5,
                            step=0.05,
                            label="Pan",
                            info="0=left, 0.5=center, 1=right",
                        )
                    with gr.Row():
                        lpf = gr.Slider(
                            0,
                            20000,
                            value=4000,
                            step=100,
                            label="LPF (Hz)",
                            info="Low-pass filter cutoff (darker)",
                        )
                        hpf = gr.Slider(
                            0,
                            5000,
                            value=0,
                            step=50,
                            label="HPF (Hz)",
                            info="High-pass filter cutoff (thinner)",
                        )
                    with gr.Row():
                        room = gr.Slider(
                            0,
                            1,
                            value=0.3,
                            step=0.05,
                            label="Reverb",
                            info="Reverb wet/dry mix",
                        )
                        roomsize = gr.Slider(
                            0,
                            10,
                            value=2.0,
                            step=0.5,
                            label="Room Size",
                            info="Reverb decay time",
                        )
                    with gr.Row():
                        delay = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.05,
                            label="Delay",
                            info="Delay effect amount",
                        )
                        delaytime = gr.Slider(
                            0.0625,
                            1,
                            value=0.25,
                            step=0.0625,
                            label="Delay Time",
                            info="Delay time in cycles (0.25=quarter)",
                        )
                    with gr.Row():
                        delayfeedback = gr.Slider(
                            0,
                            0.9,
                            value=0.5,
                            step=0.05,
                            label="Feedback",
                            info="Delay repeats",
                        )
                        distort = gr.Slider(
                            0,
                            10,
                            value=0.0,
                            step=0.5,
                            label="Distortion",
                            info="Overdrive/distortion amount",
                        )
                    gr.Markdown("**Envelope (ADSR)** - Shape the amplitude over time")
                    with gr.Row():
                        attack = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.01,
                            label="Attack",
                            info="Fade in time",
                        )
                        decay = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.01,
                            label="Decay",
                            info="Time to sustain level",
                        )
                        sustain = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.01,
                            label="Sustain",
                            info="Held volume level",
                        )
                        release = gr.Slider(
                            0,
                            1,
                            value=0.0,
                            step=0.01,
                            label="Release",
                            info="Fade out time",
                        )

        # =================================================================
        # COLLECT ALL INPUTS
        # =================================================================
        all_inputs = [
            mode,
            bpm,
            bars,
            beats_per_bar,
            max_subdivision,
            population_size,
            generations,
            fitness_threshold,
            instrument,
            scale_name,
            drum_sound,
            num_chords,
            notes_per_chord,
            r_groove,
            r_complexity,
            r_density,
            r_syncopation,
            r_consistency,
            r_offbeat,
            r_rests,
            r_strong_beat,
            r_backbeat,
            r_sparsity,
            r_simplicity,
            r_drum_offbeat,
            r_perfect_consistency,
            m_note_variety,
            m_interval_smoothness,
            m_scale_adherence,
            m_rest_ratio,
            m_rhythmic_variety,
            c_chord_variety,
            c_chord_type_variety,
            c_root_motion_smoothness,
            c_functional_harmony,
            c_resolution,
            c_triadic,
            c_seventh_chord,
            c_diminished,
            c_close_voicing,
            c_repetitive_pattern,
            c_progression_similarity,
            gain,
            lpf,
            hpf,
            room,
            roomsize,
            delay,
            delaytime,
            delayfeedback,
            distort,
            pan,
            attack,
            decay,
            sustain,
            release,
        ]

        all_outputs = [
            strudel_code,
            strudel_link,
            summary,
            python_preset,
            strudel_player,
        ]

        # =================================================================
        # RESET BUTTON HANDLERS
        # =================================================================
        rhythm_sliders = [
            r_groove,
            r_complexity,
            r_density,
            r_syncopation,
            r_consistency,
            r_offbeat,
            r_rests,
            r_strong_beat,
            r_backbeat,
            r_sparsity,
            r_simplicity,
            r_drum_offbeat,
            r_perfect_consistency,
        ]

        melody_sliders = [
            m_note_variety,
            m_interval_smoothness,
            m_scale_adherence,
            m_rest_ratio,
            m_rhythmic_variety,
        ]

        chord_sliders = [
            c_chord_variety,
            c_chord_type_variety,
            c_root_motion_smoothness,
            c_functional_harmony,
            c_resolution,
            c_triadic,
            c_seventh_chord,
            c_diminished,
            c_close_voicing,
            c_repetitive_pattern,
            c_progression_similarity,
        ]

        effects_sliders = [
            gain,
            lpf,
            hpf,
            room,
            roomsize,
            delay,
            delaytime,
            delayfeedback,
            distort,
            pan,
            attack,
            decay,
            sustain,
            release,
        ]

        # Default values for effects
        effects_defaults = [
            0.6,
            4000,
            0,
            0.3,
            2.0,
            0.0,
            0.25,
            0.5,
            0.0,
            0.5,
            0.0,
            0.0,
            0.0,
            0.0,
        ]

        reset_rhythm_btn.click(
            fn=lambda: [0.0] * len(rhythm_sliders),
            outputs=rhythm_sliders,
        )

        reset_melody_btn.click(
            fn=lambda: [0.0] * len(melody_sliders),
            outputs=melody_sliders,
        )

        reset_chord_btn.click(
            fn=lambda: [0.0] * len(chord_sliders),
            outputs=chord_sliders,
        )

        reset_effects_btn.click(
            fn=lambda: effects_defaults,
            outputs=effects_sliders,
        )

        # =================================================================
        # AUTO-REFRESH ON ANY INPUT CHANGE (with debounce via Gradio)
        # =================================================================
        for inp in all_inputs:
            inp.change(
                fn=generate_music,
                inputs=all_inputs,
                outputs=all_outputs,
            )

        # Also trigger on load to show initial output
        demo.load(
            fn=generate_music,
            inputs=all_inputs,
            outputs=all_outputs,
        )

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch()