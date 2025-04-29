# main.py

from Poker.player import Player
from Poker.poker import TexasHoldem


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
    for player in game.players:
        print(f"{player.name}: ${player.chips.total_value()}")

    # Print final chip counts
    print("\n=== Final Chip Counts ===")
    for player in game.players:
        print(f"{player.name}: ${player.chips.total_value()}")


def test_chip_consistency(num_tournaments=10):
    print(f"\n=== Testing Chip Consistency Over {num_tournaments} Tournaments ===")
    
    
    # Track total statistics across all tournaments
    total_rounds_played = 0
    total_consistent_rounds = 0
    
    for tournament in range(1, num_tournaments + 1):
        print(f"\n=== Starting Tournament {tournament} ===")
        
        # Initialize new players for each tournament
        player_names = ["Alice", "Bob", "Charlie", "Diana"]
        # Initialize players and set their positions
        players = [Player(name) for i, name in enumerate(player_names)]
        
        # Create the game instance
        game = TexasHoldem(players)
        print(f"Total chip value: ${sum(player.chips.total_value() for player in game.players)} (start)")
        for player in game.players:
            print(f"  {player.name}: ${player.chips.total_value()}")        # Calculate initial total chip value
        initial_total = sum(player.chips.total_value() for player in game.players)
        print(f"Initial total chip value: ${initial_total}")
        
        # Record round-by-round totals
        round_totals = []
        round_num = 1
        
        # Play until only one player has chips
        while sum(player.chips.total_value() > 0 for player in game.players) > 1:
            print(f"\n--- Tournament {tournament}, Round {round_num} ---")
            game.play()
            
            # Calculate total chip value after this round
            current_total = sum(player.chips.total_value() for player in game.players)
            round_totals.append(current_total)
            
            # Check if total matches initial total
            if current_total != initial_total:
                print(f"WARNING: Total chip value changed to ${current_total}!")
                return
            else:
                print(f"Total chip value: ${current_total} (consistent)")
                
            # Show individual player totals
            for player in game.players:
                print(f"  {player.name}: ${player.chips.total_value()}")
            
            round_num += 1
        
        # Tournament complete - tally results
        rounds_this_tournament = len(round_totals)
        consistent_rounds = sum(1 for total in round_totals if total == initial_total)
        
        print(f"\n=== Tournament {tournament} Results ===")
        print(f"Total rounds played: {rounds_this_tournament}")
        print(f"Rounds with consistent chip total: {consistent_rounds}")
        print(f"Rounds with inconsistent chip total: {rounds_this_tournament - consistent_rounds}")
        
        if consistent_rounds == rounds_this_tournament:
            print("TOURNAMENT PASSED: Total chip value remained consistent throughout all rounds.")
        else:
            print(f"TOURNAMENT FAILED: Total chip value changed in {rounds_this_tournament - consistent_rounds} rounds.")
            # Show the different totals we encountered
            unique_totals = sorted(set(round_totals))
            print(f"Unique totals encountered: {unique_totals}")
        
        # Update overall statistics
        total_rounds_played += rounds_this_tournament
        total_consistent_rounds += consistent_rounds
    
    for p in game.initial_players:
        print(f"   {p.name} lasted {p.rounds_survived} rounds!")
        for action, count in p.actions_called.items():
            print(f"      {p.name} {action} {count} times!")
            # Print player traits
    print("\n=== Player Traits ===")
    for player in game.initial_players:
        print(f"Player: {player.name}")
        for trait, value in player.traits.items():
            print(f"  {trait}: {value}")
    # Final overall consistency check
    print(f"\n=== Overall Results Across {num_tournaments} Tournaments ===")
    print(f"Total rounds played: {total_rounds_played}")
    print(f"Rounds with consistent chip total: {total_consistent_rounds}")
    print(f"Rounds with inconsistent chip total: {total_rounds_played - total_consistent_rounds}")
    
    consistency_percentage = (total_consistent_rounds / total_rounds_played) * 100 if total_rounds_played > 0 else 0
    print(f"Chip consistency: {consistency_percentage:.2f}%")
    
    if total_consistent_rounds == total_rounds_played:
        print("OVERALL TEST PASSED: Total chip value remained consistent throughout all tournaments.")
    else:
        print(f"OVERALL TEST FAILED: Total chip value changed in {total_rounds_played - total_consistent_rounds} rounds.")


if __name__ == "__main__":
    # Uncomment to run the normal game
    # main()
    
    # Run the chip consistency test
    test_chip_consistency(100)
