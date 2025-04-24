from Poker.player import Player
import random
import uuid
# Using arithmetic crossover because of our real-valued parameters 
# Returns a new player object
def crossover(player1, player2) -> Player:
    alpha = 0.5 # Perfect average instead of weighing one's parents traits too highly 
    mutated_player = Player(str(uuid.uuid4())[:8])
    mutated_player.traits = player1.traits.copy()

    for trait in mutated_player.traits:
        mutated_player.traits[trait] = alpha * player1[trait] + (1 - alpha) * player2[trait] 

    return mutated_player