# Graphing the parameters varying- similar to what we did on assignment 2 in COSC 420
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import re


# Get the absolute path to the current script (graph_traits.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Creating directory to store the images this code produces
output_dir = os.path.join(current_dir, 'varying_parameters')
os.makedirs(output_dir, exist_ok=True)

base_output_folder = os.path.join(current_dir, '..', 'output')

data = []

# Read through the files in population_stats
for folder_name in os.listdir(base_output_folder):
    folder_path = os.path.join(base_output_folder, folder_name)
    pop_stat_file = os.path.join(folder_path, 'population_stats', 'population_stats.csv')

    if os.path.isfile(pop_stat_file):
        # Extract parameters from folder name using regex
        match = re.match(r'combination_(\d+)_([\d.]+)_([\d.]+)_(\d+)_(\d+)_(\d+)', folder_name)
        if match:
            N, p_c, p_m, max_players, tournament_k, round_cutoff = match.groups()
            params = {
                'folder': folder_path,
                'N': int(N),
                'p_c': float(p_c),
                'p_m': float(p_m),
                'k': int(tournament_k)
            }
            df = pd.read_csv(pop_stat_file)
            params['data'] = df
            data.append(params)

# Plot the parameter we have varies
def plot_variable(data, group_key, title, save_name):
    grouped = {}
    
    for entry in data:
        key = entry[group_key]
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(entry['data'])
    
    plt.figure(figsize=(12, 8))
    
    for key, dfs in grouped.items():
        all_runs = pd.concat(dfs)

        # # Uncomment below if only want the last 5 generations of each CSV
        # # (I just didn't like how it looked for a poster or reserach paper)
        # max_generation = all_runs['generation'].max()
        # last_5_gens = all_runs[all_runs['generation'] >= (max_generation - 4)]
        # grouped_data = last_5_gens.groupby('generation')['fitness']
        # mean = grouped_data.mean()
        # std = grouped_data.std()
        # generations = mean.index

        all_runs = pd.concat(dfs)
        grouped_data = all_runs.groupby('generation')['fitness']
        mean = grouped_data.mean()
        std = grouped_data.std()
        generations = mean.index
        
        plt.plot(generations, mean, label=f"{group_key}={key}")
        plt.fill_between(generations, mean - std, mean + std, alpha=0.3)
    
    plt.title(title)
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, f"{save_name}.png"), dpi=300)
    plt.show()

# Plotting each parameter (similar to our assignment 2)
plot_variable(data, 'N', 'Average Fitness vs Generation for Varying N', 'varying_N')
plot_variable(data, 'p_c', 'Average Fitness vs Generation for Varying p_c', 'varying_p_c')
plot_variable(data, 'p_m', 'Average Fitness vs Generation for Varying p_m', 'varying_p_m')
plot_variable(data, 'k', 'Average Fitness vs Generation for Varying Tournament Size', 'varying_k')