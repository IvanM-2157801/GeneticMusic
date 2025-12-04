import itertools
import strudel
import random

BPM = 128
BARS = 2
BEATS_PER_BAR = 4
# NOTES = ["C", "C#", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "B"]
NOTES = ["0", "1", "2", "3", "4", "5", "6", "7", "~"]
POPSIZE = 5
KEEP_SIZE = 4
assert(POPSIZE > KEEP_SIZE)

MIXING_NUMBER = 2
MUTATION_RATE = 0.05

TOTAL_NOTES=BARS*BEATS_PER_BAR


def fitness_score(ind: list[str]):
    strudel.create_strudel(ind, TOTAL_NOTES)
    # Wait for user input between 1 and 5
    while True:
        try:
            user_input = int(input("Enter a number between 1 and 6: "))
            if 1 <= user_input <= 6:
                break
            else:
                print("Please enter a valid number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    return user_input
    

def select_fittest(pop: list[list[str]]) -> tuple[list[list[str]], bool]:
    fitness = []
    for ind in pop:
        score = fitness_score(ind)
        if score > 5:
            return [ind], True
            
        fitness.append((ind, score))
        
    fitness.sort(reverse=True, key=lambda x: x[1])
    return [x[0] for x in fitness[:KEEP_SIZE]], False


def generate_population():
    individuals = []

    for _ in range(POPSIZE):
        ind: list = []
        for _ in range(BARS):
            for _ in range(BEATS_PER_BAR):
                ind.append(random.choice(NOTES))
                
        individuals.append(ind)
    return individuals
                

def crossover(parents):
    cross_points = random.sample(range(TOTAL_NOTES), MIXING_NUMBER - 1)
    cross_points.sort()
    offsprings = []
    permutations = list(itertools.permutations(parents, MIXING_NUMBER))
    
    for perm in permutations:
        offspring = []
        start_pt = 0
        
        for parent_idx, cross_point in enumerate(cross_points):
            parent_part = perm[parent_idx][start_pt:cross_point]
            offspring.append(parent_part)
            start_pt = cross_point
            
        last_parent = perm[-1]
        parent_part = last_parent[cross_point:]
        offspring.append(parent_part)
        offsprings.append(list(itertools.chain(*offspring)))
    
    return offsprings


def mutate(seq):
    for row in range(len(seq)):
        if random.random() < MUTATION_RATE:
            seq[row] = random.choice(NOTES)
    return seq
        

def main():
    idx = 0
    pop = generate_population()
    while True:
        print("POPULATION SIZE", len(pop))
        print(idx)
        best_individuals, solution = select_fittest(pop)

        if solution:
            strudel.create_strudel(best_individuals[0], TOTAL_NOTES)
            break
        
        offspring = crossover(best_individuals)
        pop = [mutate(o) for o in offspring]
        idx += 1
    
if __name__ == "__main__":
    main()