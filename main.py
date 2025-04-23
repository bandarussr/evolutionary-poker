from Genetic_Algo.GA_init import initiate_player, run_sim
from Genetic_Algo.selection import tournament_selection
from Genetic_Algo.crossover import crossover
from Genetic_Algo.mutation import mutate
from Genetic_Algo.fitness import calculate_fitness
from Poker.player import Action
from collections import defaultdict

import random
import numpy as np
import pprint

# Configuration
POPULATION_SIZE = 5
GENERATIONS = 1
ROUNDS_PER_SIMULATION = 50
CROSSOVER_PROBABILITY = 0.9
MUTATION_PROBABILITY = 0.1
PLAYERS_PER_GAME = 7
TOURNAMENT_K = 5

def evolve_population(population):
    new_population = []
    while len(new_population) < len(population):
        parent1 = tournament_selection(TOURNAMENT_K, population)
        parent2 = tournament_selection(TOURNAMENT_K, population)

        if random.random() < CROSSOVER_PROBABILITY:
            child = crossover(parent1, parent2)
        else:
            child = parent1.copy()

        if random.random() < MUTATION_PROBABILITY:
            child = mutate(child)

        new_population.append(child)

    return new_population

def set_population_stats(pop_arr, generation, population):
    pop_arr[generation] = {
        "fitness": np.average([p.fitness for p in population]),
        "agressiveness": np.average([p.traits["aggressiveness"] for p in population]),
        "risk_tolerance": np.average([p.traits["risk_tolerance"] for p in population]),
        "bluff_tendency": np.average([p.traits["bluff_tendency"] for p in population]),
        "adaptability": np.average([p.traits["adaptability"] for p in population]),
        "position_awareness": np.average([p.traits["position_awareness"] for p in population]),
        "chip_size_awareness": np.average([p.traits["chip_size_awareness"] for p in population]),
        "bluff_attempts": np.average([p.actions_called[Action.BLUFF] for p in population]),
        "fold": np.average([p.actions_called[Action.FOLD] for p in population]),
        "raise": np.average([p.actions_called[Action.RAISE] for p in population]),
        "call": np.average([p.actions_called[Action.CALL] for p in population]),
        "all_in": np.average([p.actions_called[Action.ALL_IN] for p in population]),
        "check": np.average([p.actions_called[Action.CHECK] for p in population])
    }

def set_individual_history(individual_hist, generation, population):
    # if not isinstance(individual_hist, defaultdict):
    #     individual_hist = defaultdict(list)
    for p in population:
        if p.lineage not in individual_hist:
            individual_hist[p.lineage] = []
        individual_hist[p.lineage].append({
            "id": p.name,
            "generation": generation,
            "fitness": p.fitness,
            "rounds_lasted": p.rounds_survived,
            "table_position": p.position,
            "traits": p.traits.copy(),
            "actions_made": p.actions_called.copy()
        })

def main():
    # Step 1: Generate initial population
    population = initiate_player(POPULATION_SIZE)

    population_stats = {}
    individual_history = {}

    for generation in range(GENERATIONS):
        print(f"\n=== Generation {generation + 1} ===")

        evaluated_population = run_sim(population, player_per_game = PLAYERS_PER_GAME)
        set_population_stats(population_stats, generation, population)
        set_individual_history(individual_history, generation, population)
        print()
        pprint.pprint(population_stats)
        print()
        pprint.pprint(individual_history)
        population = evolve_population(evaluated_population)

    print("\nEvolution complete.")

if __name__ == "__main__":
    main()