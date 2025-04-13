# main.py

from player import Player
from poker import TexasHoldem


def main():
    print("\n=== Welcome to Poker AI Tournament ===")

    # Initialize player names (could be AI strategies in the future)
    player_names = ["Alice", "Bob", "Charlie", "Diana"]
    players = [Player(name) for name in player_names]

    for player in players:
        print(player.name)
    # Create the game instance
    game = TexasHoldem(players)

    # Run one full game (one round of Texas Hold'em)
    game.play()
    game.play()
    game.play()
    game.play()
    # Print final chip counts
    print("\n=== Final Chip Counts ===")
    for player in game.players:
        print(f"{player.name}: ${player.chips.total_value()}")


if __name__ == "__main__":
    main()
