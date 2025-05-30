from enum import Enum, auto
from typing import List
import random

from Poker.chip import Chips, ChipStash
from Poker.deck import Card
from Poker.evaluate import Eval

# Player actions
class Action(Enum):
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    RAISE = auto()
    ALL_IN = auto()
    BLUFF = auto()

class Player:
    def __init__(self, name: str):
        self.initial_chips = ChipStash({
            Chips.White: 20,
            Chips.Red: 10,
            Chips.Green: 4,
            Chips.Blue: 2,
            Chips.Black: 1
        })

        self.chips = self.initial_chips.copy()
        self.name = name
        self.evaluator = Eval()
        self.hand: List[Card] = []
        self.hand_eval = (None, None)
        self.bet = ChipStash()
        self.folded = False
        self.raised = False
        self.traits = self.initialize_traits()
        self.rounds_survived = 0
        self.actions_called = {action: 0 for action in Action}
        self.position = None
        self.parent1 = None
        self.parent2 = None
        self.lineage = None
        self.lineage_fitness = 0
        self.fitness = 0
    
    def set_pos(self, pos):
        self.position = pos

    def __str__(self):
        return f"{self.name} (${self.chips.total_value})"
    
    def initialize_traits(self):
        return {
            "aggressiveness": float(f"{random.uniform(0, 1):.2f}"),
            "risk_tolerance": float(f"{random.uniform(0, 1):.2f}"),
            "bluff_tendency": float(f"{random.uniform(0, 1):.2f}"),
            # "adaptability": float(f"{random.uniform(0, 1):.2f}"),
            "position_awareness": float(f"{random.uniform(0, 1):.2f}"),
            "chip_size_awareness": float(f"{random.uniform(0, 1):.2f}")
        }
    
    # Function to reset the players info after each round
    def reset(self):
        self.hand = []
        self.hand_eval = (None, None)
        self.bet = ChipStash()
        self.folded = False
        self.raised = False


    # Function to receive cards 
    def receive_card(self, card: Card):
        self.hand.append(card)

    # Logic for player decision
    # bet_size: the bet that the round is on
    # min_raise: the minimum amount that the player can raise to
    # community_cards: the cards that are on the table
    # Should return the action and the bet, None for bet if the action does not call for it
    # How we made decisions based on our traits
    # Need to multiply the rank of the card in evaluate.py by the trait
    # Could have a threshold or like percents of how likely they are to fold, call, raise
    def make_decision(self, bet_size: ChipStash, min_raise, community_cards, dealer_name):
        if self.folded:
            return Action.FOLD, None
        
        # print(f"Traits for {self.name}:")
        # for trait, value in self.traits.items():
        #     print(f"  {trait}: {value:.2f}")

        # See how good the cards are
        self.evaluate_hand(community_cards)
        hand_rank = self.hand_eval[0]
        player_call = (None, None)


        # Strong hand (7-10)
        if(hand_rank >= 7):
            # Will bet aggressively- if agressiveness > 70% - raise $200
            if(self.traits["aggressiveness"] >= 0.7):
                if(self.chips.total_value() + bet_size.total_value() >= (min_raise.total_value() * 2)):
                    player_call = Action.RAISE, (min_raise.total_value() * 2)
                # else:
                #     player_call = Action.ALL_IN, self.chips
            elif(self.traits["aggressiveness"] >= 0.5):
                if(self.chips.total_value() + bet_size.total_value() >= min_raise.total_value()):
                    player_call =  Action.RAISE, min_raise.total_value()
                # else:
                #     player_call = Action.ALL_IN, self.chips
            elif bet_size.total_value() == 0:
                player_call = Action.CHECK, None
            else:
                player_call = Action.CALL, bet_size
        # Medium hand (4-6)
        elif(hand_rank >= 4):
            # Will take a risk to raise if high risk tolerance
            if(self.traits["risk_tolerance"] >= 0.7):
                if(self.chips.total_value() + bet_size.total_value() >= (min_raise.total_value() * 2)):
                    player_call = Action.RAISE, (min_raise.total_value() * 2)
                # else:
                #     player_call = Action.ALL_IN, self.chips
            elif(self.traits["risk_tolerance"] >= 0.5):
                if(self.chips.total_value() + bet_size.total_value() >= min_raise.total_value()):
                    player_call =  Action.RAISE, min_raise.total_value()
                # else:
                #     player_call = Action.ALL_IN, self.chips
            else:
                if bet_size.total_value == 0:
                    player_call = Action.CHECK, None
                if(bet_size.total_value() < 200 and self.chips.total_value() >= 200):
                    player_call  = Action.CALL, bet_size
                elif len(community_cards) <= 3:
                    player_call = Action.CALL, bet_size
                else:
                    player_call = Action.FOLD, None
        # Weak hand (1-3)
        else:
            # Will raise if high bluff tolerance
            if(self.traits["bluff_tendency"] >= 0.7):
                if(self.chips.total_value() + bet_size.total_value() >= (min_raise.total_value() * 2)):
                    player_call =  Action.BLUFF, (min_raise.total_value() * 2)
                # else:
                #     player_call = Action.ALL_IN, self.chips
            elif(self.traits["bluff_tendency"] >= 0.5):
                if(self.chips.total_value() + bet_size.total_value() >= min_raise.total_value()):
                    player_call =  Action.BLUFF, min_raise.total_value()
                # else:
                #     player_call = Action.ALL_IN, self.chips
            elif bet_size.total_value() == 0:
                player_call = Action.CHECK, None
            elif len(community_cards) <= 3:
                player_call = Action.CALL, bet_size
            else:
                player_call  = Action.FOLD, None

        # Then change betting based on chip size and position awareness
        # The more chips a player has, a more they bet based on chip size awareness
        if(player_call[0] == Action.RAISE):
            if(self.traits["chip_size_awareness"] >= 0.7):
                if(self.chips.total_value() >= 5000):
                    if(player_call[1] + 100 <= self.chips.total_value()):
                        player_call = Action.RAISE, player_call[1] + 100
                    # else:
                    #     player_call = Action.ALL_IN, self.chips
                else:
                    if(player_call[1] - 100 > 0): 
                        player_call = Action.RAISE, player_call[1] - 100
            elif(self.traits["chip_size_awareness"] >= 0.5):
                if(self.chips.total_value() >= 5000):
                    if(player_call[1] + 50 <= self.chips.total_value()):
                        player_call = Action.RAISE, player_call[1] + 50
                else:
                    if(player_call[1] - 50 > 0): 
                        player_call = Action.RAISE, player_call[1] - 50

            # If player is the last to go (dealer), they should bet more
            if(self.name == dealer_name and self.traits["position_awareness"] > 0.6):
                if(player_call[1] + 50 <= self.chips.total_value()):
                    player_call = Action.RAISE, player_call[1] + 50
                # else:
                #     player_call = Action.ALL_IN, self.chips

        if(player_call[0] == Action.RAISE or player_call[0] == Action.BLUFF):
            if not self.raised:
                try:
                    bet_stash = self.chips.copy().dollar_to_chips(player_call[1])
                    player_call = (Action.RAISE, bet_stash)
                except ValueError:
                    player_call = (Action.CALL, bet_size)
            else:
                # print("***Player has already raised, can only call now***")
                player_call = (Action.CALL, bet_size)
        
        # Catch-all
        if not player_call[0]:
            player_call = (Action.FOLD, None)


        if player_call[0]:
            self.actions_called[player_call[0]] += 1
        return player_call

    # Allows player to place a bet
    # Takes care of logic for needing to go all in if they have less than the amount they need to bet
    # Takes care of logic for exchanging their chip for other chips to make exact amount
    # Now: bet will be chip 
    # Add bet into self.chips and then take how much I'm betting and put it into self.bet
    def place_bet(self, bet):
        self_total_amnt_money = self.chips.total_value()
        # If user has enough money for the bet
        if(self_total_amnt_money >= bet.total_value()):
        #     for chip_value, count in bet.inventory.items():
        #         if count <= 0:
        #             continue
                        
        #         # If not enough of this chip, attempt trade-in
        #         if self.chips.inventory.get(chip_value, 0) < count:
        #             self.chips.trade_in(target_chip_value=chip_value, target_count=count)

        #     for chip_value, count in bet.inventory.items():
        #         if count > 0:
        #             self.chips.remove_chips(chip_value, count)
        #             self.bet.add_chips(chip_value, count)
            self.bet.transfer_chips(self.chips, bet)
        else:
            # All in
            # all_in_chips = self.chips.dollar_to_chips(self_total_amnt_money)

        # Deduct chips from player and add to their current bet
            # for chip_value, count in all_in_chips.inventory.items():
            #     if count > 0:
            #         self.chips.remove_chips(chip_value, count)
            #         self.bet.add_chips(chip_value, count)
            # transfer all the money in the player inventory to their betting hand
            self.bet.transfer_chips(self.chips, self.chips)

        # print(f"--After place_bet func: {self.name} has {self.chips}" )
        # print(f"--After place_bet func: {self.name} has bet {self.bet}")

    def evaluate_hand(self, community_cards: List[Card]):
        self.hand_eval = self.evaluator.evaluate_hand(self.hand + community_cards)

    def copy(self):
        new_player = Player(self.name)
        new_player.initial_chips = self.initial_chips.copy()
        new_player.chips = self.chips.copy()
        new_player.evaluator = self.evaluator  # Assuming Eval has no state
        new_player.hand = self.hand.copy()
        new_player.hand_eval = self.hand_eval
        new_player.bet = self.bet.copy()
        new_player.folded = self.folded
        new_player.raised = self.raised
        new_player.traits = self.traits.copy()
        new_player.rounds_survived = self.rounds_survived
        new_player.actions_called = self.actions_called.copy()
        new_player.position = self.position
        new_player.parent1 = self.parent1
        new_player.parent2 = self.parent2
        new_player.lineage = self.lineage
        new_player.lineage_fitness = self.lineage_fitness
        new_player.fitness = self.fitness
        return new_player