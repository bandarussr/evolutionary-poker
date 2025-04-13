# I hardly know her!
# ("A", "♠"), ("10", "♥"), ("K", "♦"), ("7", "♣")
from typing import List, Dict
from enum import Enum, auto
from chip import Chips, ChipStash
from deck import Deck, Card
from player import Player, Action
from evaluate import Eval

class TexasHoldem:
    def __init__(self, players: List[Player]):
        self.players = players
        self.small_blind = ChipStash()
        self.small_blind.add_chips(Chips.White, 1)
        self.big_blind = ChipStash()
        self.big_blind.add_chips(Chips.Red, 1)
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.trash_cards: List[Card] = []
        self.main_pot = ChipStash()
        self.side_pots: List[ChipStash] = []
        self.dealer_idx = 0
        self.min_raise = self.small_blind
        self.evaluator = Eval()
    
    def play(self):

        # Pre-Flop
        self._deal_round()
        for p in self.players:
            p.evaluate_hand(self.community_cards)
        self._betting_round()

        # Flop
        self._deal_flop()
        for p in self.players:
            if not p.folded:
                p.evaluate_hand(self.community_cards)
        self._betting_round()

        # Turn
        self._deal_turn()
        for p in self.players:
            if not p.folded:
                p.evaluate_hand(self.community_cards)
        self._betting_round()

        # River
        self._deal_river()
        for p in self.players:
            if not p.folded:
                p.evaluate_hand(self.community_cards)
        self._betting_round()

        # Showdown
        self._showdown()
    
    def _deal_round(self):
        # Reset
        self.deck = Deck()
        self.community_cards = []
        self.trash_cards = []
        self.main_pot.reset()
        for pot in self.side_pots:
            pot.reset()
        self.min_raise = self.small_blind
        
        # Remove players that have no money
        self.players = [player for player in self.players if player.chips.total_value() > 0]
        # Reset player round information
        for player in self.players:
            player.reset()

        # Move dealer, small blind, big blind
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        sb_idx = (self.dealer_idx + 1) % len(self.players)
        bb_idx = (sb_idx + 1) % len(self.players)

        print(f"\n{self.players[self.dealer_idx].name} is the dealer")

        # Posts the small blind
        self.main_pot.transfer_chips(self.players[sb_idx].chips, self.small_blind)
        print(f"{self.players[sb_idx].name} posts small blind: ${self.small_blind.total_value()}")

        # Posts the big blind
        self.main_pot.transfer_chips(self.players[bb_idx].chips, self.big_blind)
        print(f"{self.players[bb_idx].name} posts big blind: ${self.big_blind.total_value()}")
        
        self._deal_cards()

    # Deals 2 cards to each player round robin
    def _deal_cards(self):
        for _ in range(2):
            for player in self.players:
                player.receive_card(self.deck.deal())

    # Burns 1 card
    def _burn_card(self):
        self.trash_cards.append(self.deck.deal())
    
    def _deal_flop(self):
        self._burn_card()
        for _ in range(3):
            self.community_cards.append(self.deck.deal())
        
    def _deal_turn(self):
        self._burn_card()
        self.community_cards.append(self.deck.deal())

    def _deal_river(self):
        self._burn_card()
        self.community_cards.append(self.deck.deal())

    def _betting_round(self):
        active_players = [p for p in self.players if not p.folded and p.chips.total_value() > 0]
        if len(active_players) <= 1:
            return

        to_call = 0
        player_queue = active_players[:]

        while player_queue:
            player = player_queue.pop(0)
            if player.folded:
                continue

            action, amount = player.make_decision(to_call, self.min_raise, self.community_cards)

            if action == Action.FOLD:
                player.folded = True
                continue

            elif action == Action.CHECK:
                if player.bet.total_value() < to_call:
                    # Invalid check when call is required
                    player.folded = True
                continue

            elif action == Action.CALL:
                call_value = to_call - player.bet.total_value()
                player.place_bet(call_value)

            elif action == Action.RAISE:
                raise_value = amount
                call_value = to_call - player.bet.total_value() + raise_value
                player.place_bet(call_value)
                to_call = player.bet.total_value()
                player_queue = [p for p in self.players if not p.folded and p != player]

            elif action == Action.ALL_IN:
                all_in_value = player.chips.total_value()
                player.place_bet(all_in_value)
                if player.bet.total_value() > to_call:
                    to_call = player.bet.total_value()
                    player_queue = [p for p in self.players if not p.folded and p != player]

        self._resolve_pots()

    def _resolve_pots(self):
        # Gather players who bet > 0
        bettors = [p for p in self.players if p.bet.total_value() > 0]
        if not bettors:
            return

        # Sort by total bet size (lowest to highest)
        bettors.sort(key=lambda p: p.bet.total_value())
        remaining_players = bettors[:]

        prev_bet = 0
        while remaining_players:
            # Lowest contribution among remaining
            current_bet = remaining_players[0].bet.total_value()
            contribution = current_bet - prev_bet

            pot = ChipStash()

            for player in remaining_players:
                portion = ChipStash()
                remaining = contribution

                for chip_value in sorted(player.bet.inventory.keys(), reverse=True):
                    available = player.bet.inventory[chip_value]
                    take = min(available, remaining // chip_value)
                    if take > 0:
                        portion.add_chips(chip_value, take)
                        player.bet.remove_chips(chip_value, take)
                        remaining -= chip_value * take

                pot.transfer_chips(portion, portion)

            if not self.main_pot.total_value():
                self.main_pot = pot
            else:
                self.side_pots.append(pot)

            prev_bet = current_bet
            remaining_players = [p for p in remaining_players if p.bet.total_value() > 0]

        print(f"Main pot: ${self.main_pot.total_value()}")
        for i, side in enumerate(self.side_pots):
            print(f"Side pot {i+1}: ${side.total_value()}")

    def _showdown(self):
        # Evaluate hands for all active players
        for player in self.players:
            if not player.folded:
                player.evaluate_hand(self.community_cards)

        finalists = [p for p in self.players if not p.folded]
        if not finalists:
            return

        # Determine the best score
        best_score = self.evaluator.evaluate_table(finalists)
        winners = [p for p in finalists if p.hand_eval == best_score]

        print("\nShowdown Results:")
        for player in finalists:
            print(f"{player.name}: {player.hand_eval}")

        # Distribute the main pot
        self._distribute_pot(self.main_pot, winners)

        # Distribute side pots (if any)
        for pot in self.side_pots:
            eligible = [p for p in winners if p in finalists]
            self._distribute_pot(pot, eligible)

    

    def _distribute_pot(self, pot: ChipStash, winners: List[Player]):
        if not winners or pot.total_value() == 0:
            return

        total = pot.total_value()
        base_share = total // len(winners)
        remainder = total % len(winners)

        # Determine winner closest to dealer counter-clockwise (i.e., highest index before dealer_idx)
        winner_indices = [self.players.index(p) for p in winners]
        sorted_winners = sorted(winner_indices, key=lambda i: (i - self.dealer_idx) % len(self.players), reverse=True)
        winner_order = [self.players[i] for i in sorted_winners]

        for winner in winners:
            payout = ChipStash()
            remaining = base_share

            for chip_value in sorted(pot.inventory.keys(), reverse=True):
                count = min(pot.inventory[chip_value], remaining // chip_value)
                if count > 0:
                    payout.add_chips(chip_value, count)
                    pot.remove_chips(chip_value, count)
                    remaining -= chip_value * count

            winner.chips.transfer_chips(payout, payout)

            actual_value = payout.total_value()
            if actual_value == base_share:
                print(f"{winner.name} wins ${actual_value} from the pot")
            else:
                print(f"{winner.name} wins approximately ${actual_value} from the pot (rounded by chip limits)")

        # Distribute remainder chips to the closest winner counter-clockwise from dealer
        for _ in range(remainder):
            for chip_value in sorted(pot.inventory.keys(), reverse=True):
                for winner in winner_order:
                    if pot.inventory[chip_value] > 0:
                        pot.remove_chips(chip_value, 1)
                        winner.chips.add_chips(chip_value, 1)
                        print(f"{winner.name} receives an extra ${chip_value} chip from the remainder")
                        break
                else:
                    continue
                break

