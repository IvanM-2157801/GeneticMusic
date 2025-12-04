import itertools
import random
import matplotlib.pyplot as plt

NUM_QUEENS = 8
MUTATION_RATE = 0.05
MIXING_NUMBER = 4
POPULATION_SIZE = 10


def fitness_score(seq):
    score = 0
    for row in range(NUM_QUEENS):
        col = seq[row]
        for other_row in range(NUM_QUEENS):
            if other_row == row:
                continue
            if seq[other_row] == col:
                continue
            if other_row + seq[other_row] == row + col:
                continue
            if other_row - seq[other_row] == row - col:
                continue
            score += 1
    return score/2


def mutate(seq):
    for row in range(len(seq)):
        if random.random() < MUTATION_RATE:
            seq[row] = random.randrange(NUM_QUEENS)
    return seq


def crossover(parents):
    cross_points = random.sample(range(NUM_QUEENS), MIXING_NUMBER - 1)
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


def select_and_check(pop):
    fitness = [(ind, fitness_score(ind)) for ind in pop]
    
    # Check for solution
    for ind, score in fitness:
        if score >= 28:
            return None, ind
    
    # Select best
    fitness.sort(reverse=True, key=lambda x: x[1])
    return [x[0] for x in fitness[:MIXING_NUMBER]], None


def generate_population():
    return [[random.randrange(NUM_QUEENS) for _ in range(NUM_QUEENS)] 
            for _ in range(POPULATION_SIZE)]


def visualize(seq):
    n = len(seq)
    fig, ax = plt.subplots(figsize=(8, 8))
    
    for r in range(n):
        for c in range(n):
            color = '#F0D9B5' if (r + c) % 2 == 0 else '#B58863'
            ax.add_patch(plt.Rectangle((c, n-1-r), 1, 1, facecolor=color))
            if seq[r] == c:
                ax.text(c + 0.5, n-1-r + 0.5, '╰⋃╯', ha='center', va='center', fontsize=40)
    
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title("EIGHTDIHHS")
    plt.tight_layout()
    plt.show()
    
    
def main():
    idx = 0
    pop = generate_population()
    while True:
        print(idx)
        best_individuals, solution = select_and_check(pop)
        
        if solution:
            visualize(solution)
            break
        
        offspring = crossover(best_individuals)
        pop = [mutate(o) for o in offspring]
        idx += 1
        
        
if __name__ == "__main__":
    main()