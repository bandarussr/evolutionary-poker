import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import numpy as np

# --- Setup Paths ---
current_dir = os.path.dirname(os.path.abspath(__file__))

output_dir = os.path.join(current_dir, 'heatmap')
os.makedirs(output_dir, exist_ok=True)

base_output_folder = os.path.join(current_dir, '..', 'output')

# --- Step 1: Read Best Experiments ---

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

fitness_df = pd.DataFrame(data)
fitness_df = fitness_df.sort_values(by='best_fitness', ascending=False)

# Pick top 5% experiments
top_5_percent = int(len(fitness_df) * 0.05)
top_experiments = fitness_df.head(top_5_percent)

# --- Step 2: Extract Traits from Top Experiments ---

avg_traits = [
    'avg_trait_aggressiveness',
    'avg_trait_risk_tolerance',
    'avg_trait_bluff_tendency',
    'avg_trait_position_awareness',
    'avg_trait_chip_size_awareness'
]

all_traits = []
top_fitness = []

for folder_name in top_experiments['folder']:
    folder_path = os.path.join(base_output_folder, folder_name)
    pop_stat_file = os.path.join(folder_path, 'population_stats', 'population_stats.csv')
    pop_stats = pd.read_csv(pop_stat_file)
    max_gen = pop_stats['generation'].max()
    last_5 = pop_stats[pop_stats['generation'] >= (max_gen - 4)]
    
    trait_averages = last_5[avg_traits].mean()
    all_traits.append(trait_averages)
    
    best_fit = last_5['fitness'].max()
    top_fitness.append(best_fit)

traits_df = pd.DataFrame(all_traits)

# Add fitness column
traits_df['fitness'] = top_fitness

# Clean up the trait names for easier reading
traits_df.rename(columns=lambda x: x.replace('avg_trait_', '').replace('_', ' ').title(), inplace=True)

# --- Step 3: Build the Correlation Matrix ---

corr_matrix = traits_df.corr()

# Optional: Mask upper triangle for cleaner look
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

fitness_corr = corr_matrix.loc['Fitness'].drop('Fitness')

# Convert it into a DataFrame for heatmap
fitness_corr_df = pd.DataFrame(fitness_corr)

fitness_corr_df.columns = ['Correlation with Fitness'] 

# --- Step 5: Plot Simple Heatmap ---

plt.figure(figsize=(6, 8))
sns.heatmap(
    fitness_corr_df,
    annot=True,
    cmap='coolwarm',
    center=0,
    vmin=-1, vmax=1,
    linewidths=0.5,
    cbar_kws={'label': 'Correlation'},
    fmt=".2f",
    annot_kws={"size":12}
)

plt.title('Traits vs Fitness Correlation (Top 5%)', fontsize=16)
plt.ylabel('Trait', fontsize=14)
plt.xlabel('Fitness', fontsize=14)
plt.xticks(rotation=0)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, f"heatmap_correlation.png"), dpi=300)
plt.show()