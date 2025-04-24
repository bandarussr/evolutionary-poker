from Genetic_Algo.GA_init import initiate_player, run_sim
from Genetic_Algo.selection import tournament_selection
from Genetic_Algo.crossover import crossover
from Genetic_Algo.mutation import mutate
from Poker.player import Action

import uuid
import random
import numpy as np
import pandas as pd
import os
import json
import sys

# Configuration
POPULATION_SIZE = 50
GENERATIONS = 100
CROSSOVER_PROBABILITY = 0.9
MUTATION_PROBABILITY = 0.1
MAX_PLAYERS_PER_GAME = 7
TOURNAMENT_K = 20

def print_progress_bar(current, total, bar_length=40):
    percent = float(current) / total
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write(f'\rProgress: [{arrow}{spaces}] {int(percent * 100)}% ({current}/{total})')
    sys.stdout.flush()
    if current == total:
        print()

def get_unique_folder(base):
    i = 1
    folder = base
    while os.path.exists(folder):
        folder = f"{base}_{i}"
        i += 1
    os.makedirs(folder)
    return folder

def flatten_population_stats(pop_stats):
    flat = []
    for gen, stats in pop_stats.items():
        row = {
            "generation": gen,
            "fitness": stats["fitness"],
            "avg_rounds_lasted": stats["avg_rounds_lasted"],
        }
        for trait, value in stats["avg_traits"].items():
            row[f"avg_trait_{trait}"] = value
        for action, value in stats["avg_actions"].items():
            row[f"avg_action_{action}"] = value
        flat.append(row)
    return flat

def flatten_lineage_history(lineage_hist):
    flat = []
    for lineage, gens in lineage_hist.items():
        for gen, entries in gens.items():
            for entry in entries:
                row = {
                    "lineage": lineage,
                    "generation": gen,
                    "id": entry["id"],
                    "fitness": entry["fitness"],
                    "lineage_fitness": entry["lineage_fitness"],
                    "lineage_avg_fitness": entry["lineage_avg_fitness"],
                    "rounds_lasted": entry["rounds_lasted"],
                    "table_position": entry["table_position"],
                }
                for trait, value in entry["traits"].items():
                    row[f"trait_{trait}"] = value
                for action, value in entry["actions_made"].items():
                    action_str = action.name if hasattr(action, "name") else str(action)
                    row[f"action_{action_str.lower()}"] = value
                flat.append(row)
    return flat

def evolve_population(population):
    new_population = []
    while len(new_population) < len(population):
        parent1 = tournament_selection(TOURNAMENT_K, population)
        parent2 = tournament_selection(TOURNAMENT_K, population)
        if random.random() < CROSSOVER_PROBABILITY:
            child = crossover(parent1, parent2)
        else:
            child = parent1.copy()
        if parent1.fitness >= parent2.fitness:
            child.lineage = parent1.lineage
        else:
            child.lineage = parent2.lineage
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
            "aggressiveness": np.average([p.traits["aggressiveness"] for p in population]),
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
            "fitness": p.fitness,
            "lineage_fitness": p.lineage_fitness,
            "lineage_avg_fitness": lineage_avg_fitness,
            "rounds_lasted": p.rounds_survived,
            "table_position": p.position,
            "traits": p.traits.copy(),
            "actions_made": p.actions_called.copy()
        })

def main():
    population = initiate_player(POPULATION_SIZE)
    population_stats = {}
    lineage_history = {}
    set_individual_history(lineage_history, -1, population)

    for generation in range(GENERATIONS):
        print_progress_bar(generation + 1, GENERATIONS)
        evaluated_population = run_sim(population, MAX_PLAYERS_PER_GAME)
        set_population_stats(population_stats, generation, population)
        set_individual_history(lineage_history, generation, population)
        population = evolve_population(evaluated_population)

    print("\nEvolution complete.")

    # Flatten and save
    generation_avg = pd.DataFrame(flatten_population_stats(population_stats))
    lineage_data = pd.DataFrame(flatten_lineage_history(lineage_history))

    base_folder = get_unique_folder("output/run")
    pop_stat_folder = os.path.join(base_folder, "population_stats")
    lineage_folder = os.path.join(base_folder, "lineage_history")
    os.makedirs(pop_stat_folder)
    os.makedirs(lineage_folder)

    config = {
        "POPULATION_SIZE": POPULATION_SIZE,
        "GENERATIONS": GENERATIONS,
        "CROSSOVER_PROBABILITY": CROSSOVER_PROBABILITY,
        "MUTATION_PROBABILITY": MUTATION_PROBABILITY,
        "MAX_PLAYERS_PER_GAME": MAX_PLAYERS_PER_GAME,
        "TOURNAMENT_K": TOURNAMENT_K
    }
    with open(os.path.join(base_folder, "config.json"), "w") as f:
        json.dump(config, f, indent=4)

    generation_avg.to_csv(os.path.join(pop_stat_folder, "population_stats.csv"), index=False)
    lineage_data.to_csv(os.path.join(lineage_folder, "lineage_history.csv"), index=False)

if __name__ == "__main__":
    main()