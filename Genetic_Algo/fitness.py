
# Players are ranked on a scale of 1 to 0, 1 being the winner, to 0 last place, with ranks in between
def calculate_fitness(game):
    player_rank = sorted(game.initial_players, key=lambda p: p.rounds_survived, reverse=True)
    table_size = len(game.initial_players)
    for i, k in enumerate(player_rank):
        k.fitness = (table_size - i - 1) / (table_size - 1)
