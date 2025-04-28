# This code only looks at the last 5 generations of the CSV files- we can
# change it so it looks at all
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import re

# Path to your output folders
current_dir = os.path.dirname(os.path.abspath(__file__))

output_dir = os.path.join(current_dir, 'traits')
os.makedirs(output_dir, exist_ok=True)

base_output_folder = os.path.join(current_dir, '..', 'output')

# Folder to save graphs
output_folder = 'traits_and_population_analysis'
os.makedirs(output_folder, exist_ok=True)

data = []

for folder_name in os.listdir(base_output_folder):
    folder_path = os.path.join(base_output_folder, folder_name)
    pop_stat_file = os.path.join(folder_path, 'population_stats', 'population_stats.csv')

    if os.path.isfile(pop_stat_file):
        match = re.match(r'combination_(\d+)_([\d.]+)_([\d.]+)_(\d+)_(\d+)_(\d+)', folder_name)
        if match:
            N, p_c, p_m, max_players, tournament_k, round_cutoff = match.groups()
            pop_stats = pd.read_csv(pop_stat_file)
            max_gen = pop_stats['generation'].max()
            last_5 = pop_stats[pop_stats['generation'] >= (max_gen - 4)]
            best_fitness = last_5['fitness'].max()

            data.append({
                'folder': folder_name,
                'N': int(N),
                'p_c': float(p_c),
                'p_m': float(p_m),
                'k': int(tournament_k),
                'best_fitness': best_fitness
            })


# Sort and find top experiments
fitness_df = fitness_df.sort_values(by='best_fitness', ascending=False)
top_5_percent = int(len(fitness_df) * 0.05)
top_experiments = fitness_df.head(top_5_percent)

# Traits from the experiment
avg_traits = [
    'avg_trait_aggressiveness',
    'avg_trait_risk_tolerance',
    'avg_trait_bluff_tendency',
    'avg_trait_position_awareness',
    'avg_trait_chip_size_awareness'
]

all_traits = []

for folder_name in top_experiments['folder']:
    folder_path = os.path.join(base_output_folder, folder_name)
    pop_stat_file = os.path.join(folder_path, 'population_stats', 'population_stats.csv')
    pop_stats = pd.read_csv(pop_stat_file)
    max_gen = pop_stats['generation'].max()
    last_5 = pop_stats[pop_stats['generation'] >= (max_gen - 4)]
    trait_averages = last_5[avg_traits].mean()
    all_traits.append(trait_averages)

traits_df = pd.DataFrame(all_traits)
final_trait_profile = traits_df.mean()

parameters = ['N', 'p_c', 'p_m', 'k']

for param in parameters:
    plt.figure(figsize=(10, 6))
    
    # Scatterplot
    sns.scatterplot(x=fitness_df[param], y=fitness_df['best_fitness'], alpha=0.6)

    # Trend Line
    sns.regplot(x=fitness_df[param], y=fitness_df['best_fitness'], scatter=False, ci=None, color='red', line_kws={"linewidth":2})
    
    plt.xlabel(param, fontsize=14)
    plt.ylabel('Best Fitness', fontsize=14)
    plt.title(f'Best Fitness vs {param}', fontsize=16)
    plt.grid(True)
    plt.tight_layout()

    # Save each plot separately
    plt.savefig(os.path.join(output_dir, f'best_fitness_vs_{param}.png'), dpi=300)
    plt.show()

# Winning Traits Bar Chart Separately
final_trait_profile.index = [trait.replace('avg_trait_', '') for trait in final_trait_profile.index]

plt.figure(figsize=(10,6))
final_trait_profile.plot(kind='bar')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Average Trait Value')
plt.title('Winning Traits (Top 5% Players)')
plt.grid(True, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f"bar_chart_for_best_traits.png"), dpi=300)

plt.show()