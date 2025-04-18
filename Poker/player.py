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
        self.hand = []
        self.hand_eval = (None, None)
        self.bet = ChipStash()
        self.folded = False

    # Function to receive cards 
    def receive_card(self, card: Card):
        self.hand.append(card)

    # Logic for player decision
    # bet_size: the bet that the round is on
    # min_raise: the minimum amount that the player can raise to
    # community_cards: the cards that are on the table
    # Should return the action and the bet, None for bet if the action does not call for it
    def make_decision(self, bet_size, min_raise, community_cards):
        if self.bet.total_value() < bet_size.total_value():
            return Action.CALL, bet_size
        return Action.CHECK, 0

    # Allows player to place a bet
    # Takes care of logic for needing to go all in if they have less than the amount they need to bet
    # Takes care of logic for exchanging their chip for other chips to make exact amount
    def place_bet(self, bet):
        money_amnt = self.chips.total_value()
        # Handles instance of player having less money than another put in
        if(money_amnt >= bet.total_value()):
            amnt_to_bet = bet.total_value()
        else:
            amnt_to_bet = money_amnt
        
        try:
            chips_to_bet = self.chips.dollar_to_chips(amnt_to_bet)
        except ValueError:
            # Trade it in for the smallest amount of chips we have
            self.chips.trade_in(Chips.White, 1)
            chips_to_bet = self.chips.dollar_to_chips(amnt_to_bet)

        self.bet += chips_to_bet
        print(f"----{self.name} placed a bet of {self.bet}")


    def evaluate_hand(self, community_cards: List[Card]):
        self.hand_eval = self.evaluator.evaluate_hand(self.hand + community_cards)
