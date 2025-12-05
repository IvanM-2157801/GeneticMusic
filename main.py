import strudel
from core.genetic import GeneticAlgorithm, Individual
from core.music import Phrase, NoteName, Layer
from core.genome_ops import (
    random_rhythm, mutate_rhythm, crossover_rhythm,
    rhythm_to_phrase, phrase_with_rhythm,
    mutate_phrase, crossover_phrase
)
from fitness.genres import PopFitness

# Constants
BPM = 128
BARS = 2
BEATS_PER_BAR = 4
TOTAL_BEATS = BARS * BEATS_PER_BAR
MAX_SUBDIVISION = 4  # Max notes per beat (1=quarter, 2=eighth, 3=triplet, 4=sixteenth)

POPULATION_SIZE = 25
MUTATION_RATE = 0.25
ELITISM_COUNT = 6

# Scale to use (C major)
SCALE = [NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B]


def rhythm_to_strudel(rhythm: str) -> list[str]:
    """Convert rhythm pattern to strudel notation for preview."""
    notes = []
    for beat_char in rhythm:
        subdivisions = int(beat_char)
        if subdivisions == 0:
            notes.append("~")
        elif subdivisions == 1:
            notes.append("0")
        else:
            # Group subdivided notes in brackets
            notes.append("[" + " ".join(["0"] * subdivisions) + "]")
    return notes


def phrase_to_strudel_notes(phrase: Phrase) -> list[str]:
    """Convert a Phrase to strudel notation, respecting note durations."""
    # Group notes by beats based on their duration
    result = []
    current_beat_notes = []
    current_beat_duration = 0.0
    
    for note in phrase.notes:
        if note.pitch == NoteName.REST:
            note_str = "~"
        elif note.pitch in SCALE:
            degree = SCALE.index(note.pitch)
            note_str = str(degree)
        else:
            # For notes not in scale, find closest scale degree
            note_str = str(note.pitch.value % 7)
        
        current_beat_notes.append(note_str)
        current_beat_duration += note.duration
        
        # When we complete a beat, flush the notes
        if current_beat_duration >= 0.999:  # Small epsilon for float comparison
            if len(current_beat_notes) == 1:
                result.append(current_beat_notes[0])
            else:
                result.append("[" + " ".join(current_beat_notes) + "]")
            current_beat_notes = []
            current_beat_duration = 0.0
    
    # Handle any remaining notes
    if current_beat_notes:
        if len(current_beat_notes) == 1:
            result.append(current_beat_notes[0])
        else:
            result.append("[" + " ".join(current_beat_notes) + "]")
    
    return result


def user_fitness_fn(genome, to_strudel_fn) -> float:
    """Get fitness score from user input."""
    notes = to_strudel_fn(genome)
    strudel.create_strudel(notes, TOTAL_BEATS)
    
    while True:
        try:
            user_input = int(input("Enter a number between 1 and 6: "))
            if 1 <= user_input <= 6:
                return float(user_input)
            else:
                print("Please enter a valid number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


# === Phase 1: Rhythm Evolution ===

def evolve_rhythm() -> str:
    """Evolve a rhythm pattern and return the best one."""
    print("\n" + "="*50)
    print("PHASE 1: EVOLVING RHYTHM")
    print("="*50)
    
    ga = GeneticAlgorithm[str](
        population_size=POPULATION_SIZE,
        mutation_rate=MUTATION_RATE,
        elitism_count=ELITISM_COUNT,
    )
    
    population = [Individual(random_rhythm(TOTAL_BEATS, MAX_SUBDIVISION)) for _ in range(POPULATION_SIZE)]
    generation = 0
    
    while True:
        print(f"\n=== Rhythm Generation {generation} ===")
        
        def rhythm_fitness(rhythm: str) -> float:
            return user_fitness_fn(rhythm, rhythm_to_strudel)
        
        population = ga.evolve(
            population=population,
            fitness_fn=rhythm_fitness,
            mutate_fn=lambda r: mutate_rhythm(r, MUTATION_RATE, MAX_SUBDIVISION),
            crossover_fn=crossover_rhythm,
        )
        
        best = population[0]
        print(f"Best rhythm: {best.genome} (fitness: {best.fitness})")
        
        if best.fitness >= 6:
            print("\n✓ Rhythm selected!")
            return best.genome
        
        generation += 1


# === Phase 2: Melody Evolution with Fixed Rhythm ===

def evolve_melody(rhythm: str) -> Phrase:
    """Evolve melody pitches using the fixed rhythm pattern."""
    print("\n" + "="*50)
    print("PHASE 2: EVOLVING MELODY")
    print(f"Using rhythm: {rhythm}")
    print("="*50)
    
    ga = GeneticAlgorithm[Phrase](
        population_size=POPULATION_SIZE,
        mutation_rate=MUTATION_RATE,
        elitism_count=ELITISM_COUNT,
    )
    
    # Generate initial population with the rhythm
    population = [
        Individual(rhythm_to_phrase(rhythm, scale=SCALE, octave_range=(4, 5)))
        for _ in range(POPULATION_SIZE)
    ]
    
    popfit = PopFitness()
    generation = 0
    
    while True:
        print(f"\n=== Melody Generation {generation} ===")
        
        def melody_fitness(phrase: Phrase) -> float:
            return popfit.evaluate(Layer(name="melody", phrases=[phrase]))
        
        def melody_mutate(phrase: Phrase) -> Phrase:
            # Mutate the phrase but keep the rhythm
            mutated = mutate_phrase(phrase, mutation_rate=MUTATION_RATE)
            return phrase_with_rhythm(mutated, rhythm)
        
        def melody_crossover(p1: Phrase, p2: Phrase) -> Phrase:
            # Crossover and reapply rhythm
            child = crossover_phrase(p1, p2)
            return phrase_with_rhythm(child, rhythm)
        
        population = ga.evolve(
            population=population,
            fitness_fn=melody_fitness,
            mutate_fn=melody_mutate,
            crossover_fn=melody_crossover,
        )
        
        best = population[0]
        print(f"Best fitness: {best.fitness}")
        
        # Show the current best melody
        notes = phrase_to_strudel_notes(best.genome)
        print(f"Best melody: {' '.join(notes)}")
        strudel.create_strudel(notes, TOTAL_BEATS)
        
        if best.fitness >= 0.95:
            print("\n🎵 Found a satisfying melody!")
            return best.genome
        
        generation += 1


def main():
    # Phase 1: Evolve rhythm
    rhythm = evolve_rhythm()
    
    # Phase 2: Evolve melody with that rhythm
    melody = evolve_melody(rhythm)
    
    # Final output
    print("\n" + "="*50)
    print("FINAL RESULT")
    print("="*50)
    notes = phrase_to_strudel_notes(melody)
    strudel.create_strudel(notes, TOTAL_BEATS)


if __name__ == "__main__":
    main()