import random
from enum import Enum, auto
import ascii_cards.cards as dealer

class Suit(Enum):
    HEART = "♥"
    DIAMOND = "♦"
    SPADE = "♠"
    CLOVER = "♣"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    
    def __str__(self):
        if self.value <= 10:
            return str(self.value)
        if self == Rank.JACK:
            return "J"
        if self == Rank.QUEEN:
            return "Q"
        if self == Rank.KING:
            return "K"
        return "A"
    
    def __lt__(self, other):
        if isinstance(other, Rank):
            return self.value < other.value
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Rank):
            return self.value > other.value
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, Rank):
            return self.value == other.value
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, Rank):
            return self.value <= other.value
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, Rank):
            return self.value >= other.value
        return NotImplemented

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
        
    def __str__(self):
        return f"{self.rank}{self.suit.value}"
    
    def display(self):
        if self.rank and self.suit:
            dealer.print_card(self.rank, self.suit)
    

class Deck():
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop()