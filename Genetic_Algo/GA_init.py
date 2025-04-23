from Poker.player import Player
from Poker.poker import TexasHoldem
from Genetic_Algo.fitness import calculate_fitness
from typing import List
import uuid
from math import ceil


def run_sim(players: List[Player], player_per_game: int):
    num_games = ceil(len(players) / player_per_game)
    game = {}
    new_population = []

    for game_round in range(num_games):
        start_idx = game_round * player_per_game
        end_idx = start_idx + player_per_game
        game[f"game_{game_round}"] = players[start_idx:end_idx]

    for player_list in game.values():
        print(f"Starting game with players: {[p.name for p in player_list]}")
        poker = TexasHoldem(player_list)

        # play until this game has one winner
        while sum(player.chips.total_value() > 0 for player in poker.players) > 1:
            poker.play()
        for player in poker.players:
            new_population.append(player)
        calculate_fitness(poker)
    return new_population
        

def initiate_player(size: int, mode: str = "rand") -> list:
    players = []
    if mode == "rand" or mode == "random":
        for _ in range(size):
            p = Player(str(uuid.uuid4())[:8])
            p.initialize_traits()
            players.append(p)
        return players
    return None