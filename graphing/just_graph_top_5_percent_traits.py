import os
import re
import pandas as pd
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.abspath(__file__))
output_root = os.path.join(current_dir, '..', 'output')  # adjust if needed

trait_columns = [
    'avg_trait_aggressiveness',
    'avg_trait_risk_tolerance',
    'avg_trait_bluff_tendency',
    'avg_trait_position_awareness',
    'avg_trait_chip_size_awareness'
]

# Accumulate all CSV data
all_data = []

for folder_name in os.listdir(output_root):
    folder_path = os.path.join(output_root, folder_name)
    stats_path = os.path.join(folder_path, 'population_stats', 'population_stats.csv')

    if os.path.isfile(stats_path):
        df = pd.read_csv(stats_path)
        df['experiment'] = folder_name  # Optional: add source tag
        all_data.append(df)

# Combine all rows into one DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Get top 5% by fitness
top_n = int(len(combined_df) * 0.05)
top_5_df = combined_df.sort_values(by='fitness', ascending=False).head(top_n)

# Compute average traits of top 5%
trait_means = top_5_df[trait_columns].mean()
trait_means.index = [col.replace('avg_trait_', '') for col in trait_means.index]

# Plot
plt.figure(figsize=(10, 6))
trait_means.plot(kind='bar', color='steelblue')
plt.title("Traits of Top 5% Players Across All Experiments")
plt.ylabel("Average Trait Value")
plt.xticks(rotation=0, ha='center')
plt.grid(True, axis='y')
plt.tight_layout()

# Save plot
plot_path = os.path.join(current_dir, 'top_5_percent_traits.png')
#plt.savefig(plot_path, dpi=300)
plt.show()