import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load your data
lineage_history = pd.read_csv('output/run/lineage_history/lineage_history.csv')
population_stats = pd.read_csv('output/run/population_stats/population_stats.csv')

# List of traits to graph
traits = [
    'avg_trait_aggressiveness',
    'avg_trait_risk_tolerance',
    'avg_trait_bluff_tendency',
    'avg_trait_position_awareness',
    'avg_trait_chip_size_awareness'
]

window_size = 15 

for trait in traits:
    plt.figure(figsize=(8, 6))

    # Sort data by trait value
    sorted_data = population_stats.sort_values(by=trait)
    x = sorted_data[trait].values
    y = sorted_data['fitness'].values

    # Calculate moving average manually
    y_moving_avg = np.convolve(y, np.ones(window_size)/window_size, mode='same')

    plt.scatter(x, y, alpha=0.5, label='Fitness')

    # Average line
    plt.plot(x, y_moving_avg, color='orange', linewidth=2, label=f'Average')

    plt.xlabel(trait.replace('_', ' ').title())
    plt.ylabel('Fitness')
    plt.title(f'Fitness vs {trait.replace("_", " ").title()}')
    plt.legend()
    plt.grid(True)
    plt.show()