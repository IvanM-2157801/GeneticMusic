import strudel
from core.genetic import GeneticAlgorithm, Individual
from core.music import Phrase, NoteName, Layer
from core.genome_ops import random_phrase, mutate_phrase, crossover_phrase
from fitness.genres import PopFitness

# Constants
BPM = 128
BARS = 2
BEATS_PER_BAR = 4
TOTAL_NOTES = BARS * BEATS_PER_BAR

POPULATION_SIZE = 25
MUTATION_RATE = 0.25
ELITISM_COUNT = 6

# Scale to use (C major)
SCALE = [NoteName.C, NoteName.D, NoteName.E, NoteName.F, NoteName.G, NoteName.A, NoteName.B]


def phrase_to_strudel_notes(phrase: Phrase) -> list[str]:
    notes = []
    for note in phrase.notes:
        if note.pitch == NoteName.REST:
            notes.append("~")
        else:
            # Convert pitch to scale degree (0-7)
            if note.pitch in SCALE:
                degree = SCALE.index(note.pitch)
                notes.append(str(degree))
            else:
                notes.append("0")
    return notes


def user_fitness_fn(phrase: Phrase) -> float:
    notes = phrase_to_strudel_notes(phrase)
    strudel.create_strudel(notes, TOTAL_NOTES)
    
    while True:
        try:
            user_input = int(input("Enter a number between 1 and 6: "))
            if 1 <= user_input <= 6:
                return float(user_input)
            else:
                print("Please enter a valid number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def mutate_fn(phrase: Phrase) -> Phrase:
    return mutate_phrase(phrase, mutation_rate=MUTATION_RATE)


def crossover_fn(p1: Phrase, p2: Phrase) -> Phrase:
    return crossover_phrase(p1, p2)


def generate_initial_population() -> list[Individual[Phrase]]:
    return [
        Individual(random_phrase(
            length=TOTAL_NOTES,
            scale=SCALE,
            octave_range=(4, 5)
        ))
        for _ in range(POPULATION_SIZE)
    ]


def main():
    ga = GeneticAlgorithm[Phrase](
        population_size=POPULATION_SIZE,
        mutation_rate=MUTATION_RATE,
        elitism_count=ELITISM_COUNT,
    )
    
    population = generate_initial_population()
    generation = 0
    
    while True:
        print(f"\n=== Generation {generation} ===")
        print(f"Population size: {len(population)}")
        
        popfit = PopFitness()
        def pop_fitness_fn(phrase: Phrase) -> float:
            return popfit.evaluate(Layer(name="melody", phrases=[phrase]))
        
        # Evolve one generation
        population = ga.evolve(
            population=population,
            fitness_fn=pop_fitness_fn,
            mutate_fn=mutate_fn,
            crossover_fn=crossover_fn,
        )

        # population is sorted by fitness after evolve
        best = population[0]
        print(f"Best fitness: {best.fitness}")
        
        if best.fitness >= 0.97:
            print("\n🎵 Found a satisfying melody!")
            notes = phrase_to_strudel_notes(best.genome)
            strudel.create_strudel(notes, TOTAL_NOTES)
            break
        
        generation += 1


if __name__ == "__main__":
    main()