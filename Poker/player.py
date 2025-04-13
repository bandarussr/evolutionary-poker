from enum import Enum, auto
from typing import List

from chip import Chips, ChipStash
from deck import Card
from evaluate import Eval

# Player actions
class Action(Enum):
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    BET = auto()
    RAISE = auto()
    ALL_IN = auto()

class Player:
    def __init__(self, name: str):
        player_starting_chips = {
            Chips.White: 20,
            Chips.Red: 10,
            Chips.Green: 4,
            Chips.Blue: 2,
            Chips.Black: 1
        }

        self.chips = ChipStash(player_starting_chips)
        self.name = name
        self.evaluator = Eval()
        self.hand: List[Card] = [] # Players hand
        self.hand_eval = (None, None) # Evaluation of players hand based on table cards format: (hand rank, [list, of value, of top, five])
        self.bet = ChipStash()
        self.folded = False


    def __str__(self):
        return f"{self.name} (${self.chips.total_value})"
    
    # Function to reset the players info after each round
    def reset(self):
        pass

    # Function to receive cards 
    def receive_card(self, card: Card):
        pass

    # Logic for player decision
    # bet_size: the bet that the round is on
    # min_raise: the minimum amount that the player can raise to
    # community_cards: the cards that are on the table
    # Should return the action and the bet, None for bet if the action does not call for it
    def make_decision(self, bet_size, min_raise, community_cards: List[Card]):
        #return action, bet
        # action = Action.CHECK
        action = None
        bet = 0
        return action, bet

    # TODO:: make a check to see if the player can even put down the bet based on their stash of chips
    # NOTE:: even if they don't have enough of the same chip, they can always trade in chips to match if needed
    # NOTE:: the bet is in $ amounts and not chip amounts use the dollar_to_chips function if needed
    def place_bet(self, bet):
        self.bet = bet

    def evaluate_hand(self, community_cards: List[Card]):
        self.hand_eval = self.evaluator.evaluate_hand(self.hand + community_cards)
