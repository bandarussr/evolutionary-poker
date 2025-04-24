from Poker.player import Player
import uuid
import random

# Implement mutation strategy and return a player object
# Mutation will take a player's traits and adjust them randomly by a random amount (0-0.9 in a circular way)
def mutate(player: Player) -> Player:
    mutated_player = Player(str(uuid.uuid4())[:8])
    mutated_player.traits = player.traits.copy()

    for trait in mutated_player.traits:
        amnt_change_trait_by = random.random()
        # Circular wrap 
        mutated_player.traits[trait] = (mutated_player.traits[trait] + amnt_change_trait_by) % 1.0

    return mutated_player