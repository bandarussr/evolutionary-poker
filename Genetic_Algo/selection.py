from Poker.player import Player
import random
#Select a random group of k players within population List[Player] and within that return the player with the best fitness
def tournament_selection(k, population) -> Player:
    randomly_chosen_players = random.sample(population, k)
    # Chooses and returns player with highest fitness score
    return max(randomly_chosen_players, key=lambda player: player.fitness)