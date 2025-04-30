import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, 'heatmap')
os.makedirs(output_dir, exist_ok=True)

base_output_folder = os.path.join(current_dir, '..', 'output')

# Put all player data in one dataframe
all_data = []

for folder_name in os.listdir(base_output_folder):
    folder_path = os.path.join(base_output_folder, folder_name)
    pop_stat_file = os.path.join(folder_path, 'population_stats', 'population_stats.csv')

    if os.path.isfile(pop_stat_file):
        df = pd.read_csv(pop_stat_file)
        df['folder'] = folder_name
        all_data.append(df)

combined_df = pd.concat(all_data, ignore_index=True)

# Select Top 5% by Fitness
top_5_count = int(len(combined_df) * 0.05)
top_5_df = combined_df.sort_values(by='fitness', ascending=False).head(top_5_count)

# Traits and renaming
trait_columns = [
    'avg_trait_aggressiveness',
    'avg_trait_risk_tolerance',
    'avg_trait_bluff_tendency',
    'avg_trait_position_awareness',
    'avg_trait_chip_size_awareness'
]
trait_map = dict(zip(trait_columns, [col.replace('avg_trait_', '').replace('_', ' ').title() for col in trait_columns]))
trait_map['fitness'] = 'Fitness'

traits_df = top_5_df[trait_columns + ['fitness']].rename(columns=trait_map)

# Recompute correlation matrix and format
corr_matrix = traits_df.corr()
fitness_corr = corr_matrix.loc['Fitness'].drop('Fitness')
fitness_corr_df = pd.DataFrame(fitness_corr)

# Plot horizontal heatmap
plt.figure(figsize=(10, 4))
sns.heatmap(
    fitness_corr_df.T,  # Transpose
    annot=True,
    cmap='coolwarm',
    center=0,
    vmin=-1, vmax=1,
    linewidths=0.5,
    cbar_kws={'label': 'Correlation'},
    fmt=".2f",
    annot_kws={"size":12}
)

plt.title('Traits vs Fitness Correlation (Top 5% Players)', fontsize=16)
plt.xlabel('Trait', fontsize=14)
plt.xticks(rotation=0)
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()