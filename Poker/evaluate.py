from Poker.deck import Card, Deck
from typing import List, Tuple
from itertools import combinations
import random

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
    
    # def evaluate_table(self, players, community_cards):
    #     # evaluate the hands of each player and give them a rank of who's winning
    #     # NOTE:: there can be multiple winners so need to differentiate for that

    #     table_ranks: List[Tuple[str, int]] = []

    #     for player in players:
    #         player.evaluate_hand(community_cards)

    #         table_ranks.append((player.name, player.hand_eval[0]))

    #     return table_ranks

    def evaluate_table(self, players, community_cards):
        """
        Evaluate all players' hands and rank them.
        Handles tie-breaking by evaluating full hand values.
        Returns a sorted list of (player, hand_rank, hand_value), with ties considered.
        """
        ranked_players = []

        for player in players:
            player.evaluate_hand(community_cards)
            rank, cards = player.hand_eval

            # Convert hand cards to sorted list of rank values (high to low)
            values = sorted([card.rank.value for card in cards], reverse=True)
            ranked_players.append((player, rank, values))

        # Sort by hand rank first, then by kicker card values
        ranked_players.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Tie detection
        results = []
        i = 0
        while i < len(ranked_players):
            tied_group = [ranked_players[i]]
            while (
                i + 1 < len(ranked_players) and
                ranked_players[i][1] == ranked_players[i + 1][1] and
                ranked_players[i][2] == ranked_players[i + 1][2]
            ):
                tied_group.append(ranked_players[i + 1])
                i += 1
            results.append(tied_group if len(tied_group) > 1 else tied_group[0])
            i += 1

        return results

    # Will simulate multiple 'games' with the current community cards + hands and give the win/tie/loss rates
    def monte_carlo_odds(self, hand, community_cards, num_opponents, num_simulations = 50):
        full_deck = Deck()
        known_cards = hand + community_cards
        deck = [card for card in full_deck.cards if card not in known_cards]

        wins = 0
        ties = 0
        losses = 0

        for _ in range(num_simulations):
            random.shuffle(deck)

            # Deal opponents' hands
            opponents_holes = [deck[i*2:(i+1)*2] for i in range(num_opponents)]

            # Deal missing community cards
            total_community = community_cards.copy()
            needed = 5 - len(community_cards)
            total_community += deck[2*num_opponents:2*num_opponents+needed]

            # Evaluate your hand
            my_hand_rank, my_best_hand = self.evaluate_hand(hand + total_community)
            my_values = sorted([card.rank.value for card in my_best_hand], reverse=True)

            # Evaluate opponents' hands
            opponents_best = []
            for hole in opponents_holes:
                rank, cards = self.evaluate_hand(hole + total_community)
                values = sorted([card.rank.value for card in cards], reverse=True)
                opponents_best.append((rank, values))

            # Find the best opponent hand
            best_among_opponents = max(opponents_best)

        my_tuple = (my_hand_rank, my_values)
        if my_tuple > best_among_opponents:
            wins += 1
        elif my_tuple == best_among_opponents:
            ties += 1
        else:
            losses += 1

        total = wins + ties + losses
        return wins/total, ties/total, losses/total
    
    def estimate_improvement_chance(self, hole_cards: List[Card], community_cards: List[Card]) -> float:
        """
        Estimate the chance that the hand improves based on current cards.

        Args:
        - hole_cards: Player's two private cards
        - community_cards: Known community cards (can be empty)

        Returns:
        - Estimated improvement chance (float between 0 and 1)
        """

        known_cards = hole_cards + community_cards
        num_known = len(known_cards)

        remaining_cards = 52 - num_known

        # Detect draws
        suits = [card.suit for card in known_cards]
        ranks = sorted([card.rank.value for card in known_cards])

        outs = 0

        # --- Flush draw ---
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1

        for suit, count in suit_counts.items():
            if count == 4:  # 4 to a flush
                outs += 9  # 13 cards of a suit - 4 already seen = 9 outs

        # --- Straight draw ---
        # Handle Ace as both high and low
        adjusted_ranks = ranks + ([1] if 14 in ranks else [])

        unique_ranks = sorted(set(adjusted_ranks))
        
        # Look for open-ended straight draws
        for i in range(len(unique_ranks) - 3):
            window = unique_ranks[i:i+4]
            if window[-1] - window[0] == 3:  # 4 cards in a row
                outs += 8  # 2 cards complete the straight, 4 cards of each value

        # --- Gutshot straight draw (inside straight) ---
        for i in range(len(unique_ranks) - 3):
            window = unique_ranks[i:i+4]
            if window[-1] - window[0] == 4 and len(window) == 4:  # missing one in middle
                outs += 4  # Only 1 rank missing, 4 cards of it

        # --- Pair/Set improvement (if one pair) ---
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        has_pair = any(count == 2 for count in rank_counts.values())
        if has_pair:
            outs += 2  # 2 cards left to hit trips (3-of-a-kind)

        # --- Overcards (optional) ---
        # If both hole cards are higher than any community cards, consider outs
        if community_cards:
            board_ranks = [card.rank.value for card in community_cards]
            if all(hole.rank.value > max(board_ranks) for hole in hole_cards):
                outs += 6  # 3 outs for each overcard (but this is loose)

        # If no outs detected, return very low chance
        if outs == 0:
            return 0.0

        # --- Calculate improvement chance ---
        # How many cards left to come?
        street = len(community_cards)
        if street == 0:
            cards_to_come = 5  # Preflop
        elif street == 3:
            cards_to_come = 2  # After flop
        elif street == 4:
            cards_to_come = 1  # After turn
        else:
            cards_to_come = 0  # After river

        # Basic probability math:
        # chance = 1 - probability of missing all outs
        chance = 1 - ((remaining_cards - outs) / remaining_cards) ** cards_to_come
        chance = max(0.0, min(1.0, chance))  # Clamp between 0 and 1

        return chance
