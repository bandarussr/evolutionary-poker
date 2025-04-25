from Poker.player import Player
import random
import uuid
# Using arithmetic crossover because of our real-valued parameters 
# Returns a new player object
def crossover(player1, player2) -> Player:
    alpha = 0.5 # Perfect average instead of weighing one's parents traits too highly 
    mutated_player = Player(str(uuid.uuid4())[:8])
    mutated_player.traits = player1.traits.copy()
    mutated_player.parent1 = player1.name
    mutated_player.parent2 = player2.name

    for trait in mutated_player.traits:
        mutated_player.traits[trait] = alpha * player1.traits[trait] + (1 - alpha) * player2.traits[trait] 

    return mutated_player