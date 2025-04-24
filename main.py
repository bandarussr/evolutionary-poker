from Genetic_Algo.GA_init import initiate_player, run_sim
from Genetic_Algo.selection import tournament_selection
from Genetic_Algo.crossover import crossover
from Genetic_Algo.mutation import mutate
from Genetic_Algo.fitness import calculate_fitness
from Poker.player import Action

import uuid
import random
import numpy as np
import pprint

# Configuration
POPULATION_SIZE = 50
GENERATIONS = 30
ROUNDS_PER_SIMULATION = 50
CROSSOVER_PROBABILITY = 0.9
MUTATION_PROBABILITY = 0.1
MAX_PLAYERS_PER_GAME = 7
TOURNAMENT_K = 10

def evolve_population(population):
    new_population = []
    while len(new_population) < len(population):
        # print(len(population))
        parent1 = tournament_selection(TOURNAMENT_K, population)
        parent2 = tournament_selection(TOURNAMENT_K, population)

        # A child player object is created
        if random.random() < CROSSOVER_PROBABILITY:
            child = crossover(parent1, parent2)
        else:
            child = parent1.copy()

        # randomly chooses a parent to be apart of their lineage tree
        if parent1.fitness >= parent2.fitness:
            child.lineage = parent1.lineage
        else:
            child.lineage = parent2.lineage

        # child player is mutated
        if random.random() < MUTATION_PROBABILITY:
            child = mutate(child)
            child.lineage = str(uuid.uuid4())[:12]

        new_population.append(child)

    return new_population

def set_population_stats(pop_arr, generation, population):
    pop_arr[generation] = {
        "fitness": np.average([p.fitness for p in population]),
        "avg_rounds_lasted": np.average([p.rounds_survived for p in population]),
        "avg_traits": {
            "agressiveness": np.average([p.traits["aggressiveness"] for p in population]),
            "risk_tolerance": np.average([p.traits["risk_tolerance"] for p in population]),
            "bluff_tendency": np.average([p.traits["bluff_tendency"] for p in population]),
            "adaptability": np.average([p.traits["adaptability"] for p in population]),
            "position_awareness": np.average([p.traits["position_awareness"] for p in population]),
            "chip_size_awareness": np.average([p.traits["chip_size_awareness"] for p in population])
        },
        "avg_actions":{
            "bluff_attempts": np.average([p.actions_called[Action.BLUFF] for p in population]),
            "fold": np.average([p.actions_called[Action.FOLD] for p in population]),
            "raise": np.average([p.actions_called[Action.RAISE] for p in population]),
            "call": np.average([p.actions_called[Action.CALL] for p in population]),
            "all_in": np.average([p.actions_called[Action.ALL_IN] for p in population]),
            "check": np.average([p.actions_called[Action.CHECK] for p in population])
        }
    }

def set_individual_history(individual_hist, generation, population):
    for p in population:
        if p.lineage not in individual_hist:
            individual_hist[p.lineage] = {}
        if f"generation_{generation}" not in individual_hist[p.lineage]:
            individual_hist[p.lineage][f"generation_{generation}"] = []
        fitness_values = [entry["lineage_fitness"] for entry in individual_hist[p.lineage][f"generation_{generation}"]]
        lineage_avg_fitness = np.average(fitness_values) if fitness_values or len(fitness_values) > 0 else 0
        individual_hist[p.lineage][f"generation_{generation}"].append({
            "id": p.name,
            # "generation": generation,
            "fitness": p.fitness,
            "lineage_fitness": p.lineage_fitness,
            "lineage_avg_fitness": lineage_avg_fitness,
            "rounds_lasted": p.rounds_survived,
            "table_position": p.position,
            "traits": p.traits.copy(),
            "actions_made": p.actions_called.copy()
        })

def main():
    # Step 1: Generate initial population
    population = initiate_player(POPULATION_SIZE)

    population_stats = {}
    lineage_history = {}
    set_individual_history(lineage_history, -1, population)

    for generation in range(GENERATIONS):
        print(f"\n=== Generation {generation + 1} ===")
        evaluated_population = run_sim(population, MAX_PLAYERS_PER_GAME)
        set_population_stats(population_stats, generation, population)
        set_individual_history(lineage_history, generation, population)
        population = evolve_population(evaluated_population)


    pprint.pprint(population_stats)
    pprint.pprint(lineage_history)
    print("\nEvolution complete.")

if __name__ == "__main__":
    main()