from deck import Card
from typing import List, Tuple
from itertools import combinations

class Eval:
    def __init__(self):
        pass

    def evaluate_hand(self, cards: List[Card]):
        # calculate the highest hand that a player can make
        best_hand = ""
        best_hand_rank = 0

        for hand in combinations(cards, 5):
            rank = self._rank_hand(hand)
            
            if rank > best_hand_rank:
                best_hand_rank = rank
                best_hand = hand

        return (best_hand_rank, best_hand)
    
    def _rank_hand(self, hand) -> int:
        # Check royal flush
        ranks = sorted([card.rank.value for card in hand])
        suits = [card.suit for card in hand]

        is_same_suit = len(set(suits)) == 1

        if is_same_suit and ranks == [10, 11, 12, 13, 14]:
            return 10
        
        # Check straight flush
        if is_same_suit and ranks == list(range(min(ranks), max(ranks) + 1)):
            return 9
        
        # Check four of a kind
        # ERROR::can't use sets
        # rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        # Check four of a kind
        rank_counts = {}
        for rank in ranks:
            if rank in rank_counts:
                rank_counts[rank] += 1
            else:
                rank_counts[rank] = 1
        if 4 in rank_counts.values():
            return 8
        
        # Check full house
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            return 7
        
        # Check flush
        if is_same_suit:
            return 6
        
        # Check straight
        if ranks == list(range(min(ranks), max(ranks) + 1)):
            return 5
        
        # Check three of a kind
        if 3 in rank_counts.values():
            return 4
        
        # Check two pair
        if list(rank_counts.values()).count(2) == 2:
            return 3
        
        # Check one pair
        if 2 in rank_counts.values():
            return 2
        
        # High card
        return 1
    
    def evaluate_table(self, players, community_cards):
        # evaluate the hands of each player and give them a rank of who's winning
        # NOTE:: there can be multiple winners so need to differentiate for that

        table_ranks: List[Tuple[str, int]] = []

        for player in players:
            player.evaluate_hand(community_cards)

            table_ranks.append((player.name, player.hand_eval[0]))

        return table_ranks
