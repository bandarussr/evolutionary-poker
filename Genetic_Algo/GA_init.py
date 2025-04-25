from Poker.player import Player
from Poker.poker import TexasHoldem
from Genetic_Algo.fitness import calculate_fitness
from typing import List
import uuid
from math import ceil
import sys
def run_sim(players: List[Player], max_player_per_game: int, round_cutoff: int = sys.maxsize):
    num_games = ceil(len(players) / max_player_per_game)
    game = {}
    new_population = []
    for game_round, player in enumerate(players):
        round = game_round % num_games
        if f"game_{round}" not in game:
            game[f"game_{round}"] = []
        game[f"game_{round}"].append(player)

    for player_list in game.values():
        poker = TexasHoldem(player_list)
        rounds_played = 0
        # play until this game has one winner or round cutoff reached
        while sum(player.chips.total_value() > 0 for player in poker.players) > 1 and rounds_played < round_cutoff:
            poker.play()
            rounds_played += 1

        for player in poker.initial_players:
            new_population.append(player)
        calculate_fitness(poker)
    return new_population
        

def initiate_player(size: int, mode: str = "rand") -> list:
    players = []
    if mode == "rand" or mode == "random":
        for _ in range(size):
            p = Player(str(uuid.uuid4())[:8])
            p.initialize_traits()
            p.lineage = str(uuid.uuid4())[:12]
            players.append(p)
        return players
    return None