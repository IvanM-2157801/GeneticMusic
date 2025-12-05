"""Test and demonstrate rhythm fitness functions for different genres."""
from fitness.rhythm import (
    RHYTHM_FITNESS_FUNCTIONS,
    rhythm_complexity,
    rhythm_density,
    rhythm_syncopation,
    rhythm_groove,
    rhythm_rest_ratio,
    rhythm_consistency,
)
from core.genetic import GeneticAlgorithm, Individual
from core.genome_ops import random_rhythm, mutate_rhythm, crossover_rhythm


def analyze_rhythm(rhythm: str, genre: str) -> None:
    """Print detailed analysis of a rhythm pattern."""
    fitness_fn = RHYTHM_FITNESS_FUNCTIONS[genre]
    fitness = fitness_fn(rhythm)

    print(f"\nRhythm: {rhythm}")
    print(f"Genre: {genre.upper()}")
    print(f"Overall Fitness: {fitness:.3f}")
    print(f"Metrics:")
    print(f"  - Complexity:    {rhythm_complexity(rhythm):.3f}")
    print(f"  - Density:       {rhythm_density(rhythm):.3f}")
    print(f"  - Syncopation:   {rhythm_syncopation(rhythm):.3f}")
    print(f"  - Groove:        {rhythm_groove(rhythm):.3f}")
    print(f"  - Consistency:   {rhythm_consistency(rhythm):.3f}")
    print(f"  - Rest Ratio:    {rhythm_rest_ratio(rhythm):.3f}")


def evolve_genre_rhythm(genre: str, beats: int = 8, generations: int = 30) -> str:
    """Evolve a rhythm pattern for a specific genre."""
    print(f"\n{'='*60}")
    print(f"EVOLVING {genre.upper()} RHYTHM")
    print(f"{'='*60}")

    ga = GeneticAlgorithm[str](
        population_size=20,
        mutation_rate=0.3,
        elitism_count=6,
    )

    fitness_fn = RHYTHM_FITNESS_FUNCTIONS[genre]

    # Initialize population
    population = [Individual(random_rhythm(beats, 4)) for _ in range(20)]

    # Evolve
    for gen in range(generations):
        population = ga.evolve(
            population=population,
            fitness_fn=fitness_fn,
            mutate_fn=lambda r: mutate_rhythm(r, 0.3, 4),
            crossover_fn=crossover_rhythm,
        )

        if gen % 10 == 0:
            best = population[0]
            print(f"Gen {gen:2d}: fitness={best.fitness:.3f}, rhythm={best.genome}")

    best = population[0]
    print(f"FINAL: fitness={best.fitness:.3f}, rhythm={best.genome}")

    return best.genome


def main():
    print("\n" + "="*60)
    print("RHYTHM FITNESS DEMONSTRATION")
    print("="*60)

    genres = ["pop", "jazz", "funk", "ambient", "rock"]

    print("\n" + "="*60)
    print("EVOLVING RHYTHMS FOR EACH GENRE")
    print("="*60)

    evolved_rhythms = {}
    for genre in genres:
        rhythm = evolve_genre_rhythm(genre, beats=8, generations=30)
        evolved_rhythms[genre] = rhythm

    print("\n" + "="*60)
    print("COMPARISON OF EVOLVED RHYTHMS")
    print("="*60)

    for genre in genres:
        analyze_rhythm(evolved_rhythms[genre], genre)

    print("\n" + "="*60)
    print("EXAMPLE IDEAL PATTERNS (hand-crafted)")
    print("="*60)

    examples = {
        "pop": "22222222",      # Consistent eighth notes
        "jazz": "31402413",     # Complex, varied
        "funk": "42142214",     # Groovy, syncopated
        "ambient": "10001000",  # Sparse, meditative
        "rock": "24242424",     # Driving, powerful
    }

    for genre, rhythm in examples.items():
        analyze_rhythm(rhythm, genre)


if __name__ == "__main__":
    main()
