#!/usr/bin/env python3
"""Interactive UI for GeneticMusic using Gradio.

Run with: python ui_demo.py

Provides sliders for ALL available fitness functions to experiment
with how different weights affect the evolved music.

Requirements:
    pip install gradio
"""

import gradio as gr
from core.music import Phrase, Layer, NoteName
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


# =============================================================================
# PYTHON PRESET GENERATOR
# =============================================================================


def generate_python_preset(
    bpm, bars, beats_per_bar, max_subdivision,
    population_size, generations, instrument, scale_name,
    r_groove, r_complexity, r_density, r_syncopation,
    r_consistency, r_offbeat, r_rests,
    r_strong_beat, r_backbeat, r_sparsity,
    r_simplicity, r_drum_offbeat, r_perfect_consistency,
    m_note_variety, m_interval_smoothness, m_scale_adherence,
    m_rest_ratio, m_rhythmic_variety,
    gain, lpf, hpf, room, roomsize,
    delay, delaytime, delayfeedback,
    distort, pan,
    attack, decay, sustain, release,
):
    """Generate Python code preset from current UI settings."""

    scale_import = SCALE_IMPORTS.get(scale_name, "MINOR_SCALE")

    code = f'''"""Generated preset from GeneticMusic UI.

Copy this code into your own script to use these settings.
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
from layered_composer import LayeredComposer, LayerConfig
from core.music import Layer, Phrase


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


# =============================================================================
# MAIN
# =============================================================================

def main():
    rhythm_fn = make_rhythm_fitness(RHYTHM_WEIGHTS)
    melody_fn = make_melody_fitness(MELODY_WEIGHTS, SCALE)

    composer = LayeredComposer(
        population_size=POPULATION_SIZE, mutation_rate=0.25,
        elitism_count=max(2, POPULATION_SIZE // 5),
        rhythm_generations=GENERATIONS, melody_generations=GENERATIONS,
    )

    composer.add_layer(LayerConfig(
        name="melody", instrument=INSTRUMENT, bars=BARS,
        beats_per_bar=BEATS_PER_BAR, max_subdivision=MAX_SUBDIVISION,
        octave_range=(4, 5), base_octave=4,
        rhythm_fitness_fn=rhythm_fn, melody_fitness_fn=melody_fn,
        layer_role="melody", **EFFECTS,
    ))

    print("Evolving...")
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


def generate_music(
    bpm, bars, beats_per_bar, max_subdivision,
    population_size, generations, instrument, scale_name,
    r_groove, r_complexity, r_density, r_syncopation,
    r_consistency, r_offbeat, r_rests,
    r_strong_beat, r_backbeat, r_sparsity,
    r_simplicity, r_drum_offbeat, r_perfect_consistency,
    m_note_variety, m_interval_smoothness, m_scale_adherence,
    m_rest_ratio, m_rhythmic_variety,
    gain, lpf, hpf, room, roomsize,
    delay, delaytime, delayfeedback,
    distort, pan,
    attack, decay, sustain, release,
):
    """Generate music with the given fitness weights."""

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

    # Get scale
    scale_notes = SCALES.get(scale_name, MINOR_SCALE)

    # Create fitness functions
    rhythm_fn = make_rhythm_fitness(rhythm_weights)
    melody_fn = make_melody_fitness(melody_weights, scale_notes)

    # Create composer
    composer = LayeredComposer(
        population_size=int(population_size),
        mutation_rate=0.25,
        elitism_count=max(2, int(population_size) // 5),
        rhythm_generations=int(generations),
        melody_generations=int(generations),
    )

    # Add single layer with effects
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
    )

    # Evolve
    composer.evolve_all_layers(verbose=False)

    # Get composition with the selected scale
    scale_root = "c"
    scale_type = scale_name.lower()
    composition = composer.get_composition(bpm=int(bpm), random_scale=False)

    # Override scale in layer
    for layer in composition.layers:
        layer.scale = f"{scale_root}:{scale_type}"

    # Generate Strudel code and link
    strudel_code = composition.to_strudel()
    strudel_link = composition.to_strudel_link()

    # Build summary
    rhythm = composer.evolved_rhythms.get("melody", "N/A")
    phrase = composer.evolved_phrases.get("melody")

    summary = f"""**Rhythm:** `{rhythm}`

| Rhythm Metric | Value |
|---------------|-------|
| Groove | {rhythm_groove(rhythm):.2f} |
| Complexity | {rhythm_complexity(rhythm):.2f} |
| Density | {rhythm_density(rhythm):.2f} |
| Syncopation | {rhythm_syncopation(rhythm):.2f} |
| Consistency | {rhythm_consistency(rhythm):.2f} |
| Rest Ratio | {rhythm_rest_ratio(rhythm):.2f} |
"""

    if phrase:
        summary += f"""
| Melody Metric | Value |
|---------------|-------|
| Note Variety | {note_variety(phrase):.2f} |
| Smoothness | {interval_smoothness(phrase):.2f} |
| Scale Adherence | {scale_adherence(phrase, scale_notes):.2f} |
| Rest Ratio | {rest_ratio(phrase):.2f} |
"""

    # Also generate Python preset
    python_preset = generate_python_preset(
        bpm, bars, beats_per_bar, max_subdivision,
        population_size, generations, instrument, scale_name,
        r_groove, r_complexity, r_density, r_syncopation,
        r_consistency, r_offbeat, r_rests,
        r_strong_beat, r_backbeat, r_sparsity,
        r_simplicity, r_drum_offbeat, r_perfect_consistency,
        m_note_variety, m_interval_smoothness, m_scale_adherence,
        m_rest_ratio, m_rhythmic_variety,
        gain, lpf, hpf, room, roomsize,
        delay, delaytime, delayfeedback,
        distort, pan,
        attack, decay, sustain, release,
    )

    return strudel_code, strudel_link, summary, python_preset


# =============================================================================
# GRADIO UI
# =============================================================================


def create_ui():
    """Create the Gradio interface with sidebar layout."""

    css = """
    .sidebar { background: #f7f7f7; padding: 10px; border-radius: 8px; }
    .output-area { min-height: 600px; }
    .small-slider { max-width: 100%; }
    """

    with gr.Blocks(title="GeneticMusic Composer", css=css) as demo:
        gr.Markdown("# GeneticMusic - Fitness Function Explorer")

        with gr.Row():
            # =================================================================
            # LEFT: OUTPUT AREA (main content)
            # =================================================================
            with gr.Column(scale=3, elem_classes="output-area"):
                gr.Markdown("## Output")

                strudel_code = gr.Code(
                    label="Strudel Code",
                    language="javascript",
                    lines=12,
                )

                strudel_link = gr.Textbox(
                    label="Strudel Link (copy and open in browser)",
                    interactive=False,
                    lines=2,
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
            with gr.Column(scale=2, elem_classes="sidebar"):
                gr.Markdown("## Controls")

                # --- General Settings ---
                with gr.Accordion("General Settings", open=True):
                    with gr.Row():
                        bpm = gr.Slider(40, 200, value=90, step=5, label="BPM")
                        bars = gr.Slider(1, 4, value=1, step=1, label="Bars")
                    with gr.Row():
                        beats_per_bar = gr.Slider(4, 16, value=8, step=1, label="Beats/Bar")
                        max_subdivision = gr.Slider(1, 4, value=2, step=1, label="Max Subdiv")
                    with gr.Row():
                        population_size = gr.Slider(10, 100, value=20, step=5, label="Population")
                        generations = gr.Slider(10, 100, value=20, step=5, label="Generations")
                    with gr.Row():
                        instrument = gr.Dropdown(
                            choices=["piano", "sawtooth", "square", "triangle", "sine", "supersaw"],
                            value="piano", label="Instrument",
                        )
                        scale_name = gr.Dropdown(
                            choices=["Minor", "Major", "Pentatonic", "Blues"],
                            value="Minor", label="Scale",
                        )

                # --- Rhythm Fitness ---
                with gr.Accordion("Rhythm Fitness", open=True):
                    with gr.Row():
                        r_groove = gr.Slider(0, 1, value=0.3, step=0.05, label="Groove")
                        r_complexity = gr.Slider(0, 1, value=0.2, step=0.05, label="Complexity")
                    with gr.Row():
                        r_density = gr.Slider(0, 1, value=0.2, step=0.05, label="Density")
                        r_syncopation = gr.Slider(0, 1, value=0.2, step=0.05, label="Syncopation")
                    with gr.Row():
                        r_consistency = gr.Slider(0, 1, value=0.2, step=0.05, label="Consistency")
                        r_offbeat = gr.Slider(0, 1, value=0.1, step=0.05, label="Offbeat")
                    with gr.Row():
                        r_rests = gr.Slider(0, 1, value=0.3, step=0.05, label="Penalize Rests")
                        r_strong_beat = gr.Slider(0, 1, value=0.0, step=0.05, label="Strong Beat")
                    with gr.Row():
                        r_backbeat = gr.Slider(0, 1, value=0.0, step=0.05, label="Backbeat")
                        r_sparsity = gr.Slider(0, 1, value=0.0, step=0.05, label="Sparsity")
                    with gr.Row():
                        r_simplicity = gr.Slider(0, 1, value=0.0, step=0.05, label="Simplicity")
                        r_drum_offbeat = gr.Slider(0, 1, value=0.0, step=0.05, label="Drum Offbeat")
                    r_perfect_consistency = gr.Slider(0, 1, value=0.0, step=0.05, label="Perfect Consistency")

                # --- Melody Fitness ---
                with gr.Accordion("Melody Fitness", open=True):
                    with gr.Row():
                        m_note_variety = gr.Slider(0, 1, value=0.3, step=0.05, label="Note Variety")
                        m_interval_smoothness = gr.Slider(0, 1, value=0.4, step=0.05, label="Smoothness")
                    with gr.Row():
                        m_scale_adherence = gr.Slider(0, 1, value=0.5, step=0.05, label="Scale Adherence")
                        m_rest_ratio = gr.Slider(0, 1, value=0.2, step=0.05, label="Penalize Rests")
                    m_rhythmic_variety = gr.Slider(0, 1, value=0.1, step=0.05, label="Rhythmic Variety")

                # --- Effects ---
                with gr.Accordion("Sound Effects", open=False):
                    with gr.Row():
                        gain = gr.Slider(0, 1, value=0.6, step=0.05, label="Gain")
                        pan = gr.Slider(0, 1, value=0.5, step=0.05, label="Pan")
                    with gr.Row():
                        lpf = gr.Slider(0, 20000, value=4000, step=100, label="LPF (Hz)")
                        hpf = gr.Slider(0, 5000, value=0, step=50, label="HPF (Hz)")
                    with gr.Row():
                        room = gr.Slider(0, 1, value=0.3, step=0.05, label="Reverb")
                        roomsize = gr.Slider(0, 10, value=2.0, step=0.5, label="Room Size")
                    with gr.Row():
                        delay = gr.Slider(0, 1, value=0.0, step=0.05, label="Delay")
                        delaytime = gr.Slider(0.0625, 1, value=0.25, step=0.0625, label="Delay Time")
                    with gr.Row():
                        delayfeedback = gr.Slider(0, 0.9, value=0.5, step=0.05, label="Feedback")
                        distort = gr.Slider(0, 10, value=0.0, step=0.5, label="Distortion")
                    gr.Markdown("**Envelope (ADSR)**")
                    with gr.Row():
                        attack = gr.Slider(0, 1, value=0.0, step=0.01, label="A")
                        decay = gr.Slider(0, 1, value=0.0, step=0.01, label="D")
                        sustain = gr.Slider(0, 1, value=0.0, step=0.01, label="S")
                        release = gr.Slider(0, 1, value=0.0, step=0.01, label="R")

        # =================================================================
        # COLLECT ALL INPUTS
        # =================================================================
        all_inputs = [
            bpm, bars, beats_per_bar, max_subdivision,
            population_size, generations, instrument, scale_name,
            r_groove, r_complexity, r_density, r_syncopation,
            r_consistency, r_offbeat, r_rests,
            r_strong_beat, r_backbeat, r_sparsity,
            r_simplicity, r_drum_offbeat, r_perfect_consistency,
            m_note_variety, m_interval_smoothness, m_scale_adherence,
            m_rest_ratio, m_rhythmic_variety,
            gain, lpf, hpf, room, roomsize,
            delay, delaytime, delayfeedback,
            distort, pan,
            attack, decay, sustain, release,
        ]

        all_outputs = [strudel_code, strudel_link, summary, python_preset]

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
