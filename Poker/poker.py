# I hardly know her!
# ("A", "♠"), ("10", "♥"), ("K", "♦"), ("7", "♣")

from typing import List, Dict
from enum import Enum, auto
from Poker.chip import Chips, ChipStash, dollar_to_chips
from Poker.deck import Deck, Card
from Poker.player import Player, Action
from Poker.evaluate import Eval

class TexasHoldem:
    def __init__(self, players: List[Player]):
        self.initial_players = players
        self.players = players
        self.active_players = []
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
        self.min_raise = self.small_blind.copy()
        self.evaluator = Eval()
        self.sb_paid = False
        self.street = None

        # setting the players position on the table
        for i, p in enumerate(self.initial_players):
            p.set_pos(i)
            p.player_state['position'] = p.position / len(self.initial_players)
    
    def play(self):

        print("Pre-flop totals:")
        for player in self.players:
            print(f"   {player.name}: ${player.chips.total_value()}")
        # Pre-Flop
        self.street = 'preflop'
        self._deal_round()
        for p in self.players:
            p.evaluate_hand(self.community_cards)
        self._betting_round()


        # Flop
        self.street = 'flop'
        self._deal_flop()
        for p in self.players:
            if not p.folded:
                p.evaluate_hand(self.community_cards)
        self._display_community_cards()
        self._betting_round()

        # Turn
        self.street = 'turn'
        self._deal_turn()
        for p in self.players:
            if not p.folded:
                p.evaluate_hand(self.community_cards)
        self._display_community_cards()
        self._betting_round()

        # River
        self.street = 'river'
        self._deal_river()
        for p in self.players:
            if not p.folded:
                p.evaluate_hand(self.community_cards)
        self._display_community_cards()
        self._betting_round()

        # Showdown
        self._showdown()
        for p in self.players:
            if p.chips.total_value() > 0:
                p.rounds_survived += 1
        print("After totals:")
        for player in self.players:
            print(f"   {player.name}: ${player.chips.total_value()}")

    
    def _deal_round(self):
        # Reset
        self.deck = Deck()
        self.community_cards = []
        self.trash_cards = []
        self.main_pot.reset()
        for pot in self.side_pots:
            pot.reset()
        self.min_raise = self.small_blind.copy()
        self.sb_paid = False
        
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
        # TODO:: May need to remove transferchips depending on place_bet implementation
        
        # self.players[sb_idx].place_bet(self.small_blind.copy())
        # self.main_pot.transfer_chips(self.players[sb_idx].chips, self.small_blind)
        # self.main_pot.transfer_chips(self.players[sb_idx].bet, self.players[sb_idx].bet)
        # print(f"{self.players[sb_idx].name} posts small blind: ${self.small_blind.total_value()}")

        # goes directly into the main pot
        

        # Posts the big blind
        # TODO:: May need to remove transferchips depending on place_bet implementation
        # self.players[bb_idx].place_bet(self.big_blind.copy())
        # self.main_pot.transfer_chips(self.players[bb_idx].chips, self.big_blind)
        # self.main_pot.transfer_chips(self.players[bb_idx].bet, self.players[bb_idx].bet)
        # print(f"{self.players[bb_idx].name} posts big blind: ${self.big_blind.total_value()}")
        
        
        self._deal_cards()

    # Deals 2 cards to each player round robin
    def _deal_cards(self):
        for _ in range(2):
            for player in self.players:
                player.receive_card(self.deck.deal())
        # for player in self.players:
        #     print(f"{player.name} hand: {player.hand[0]}  {player.hand[1]}")

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
    
    def _display_community_cards(self):
        print("Community Cards:", " ".join(str(card) for card in self.community_cards))

    def update_active_players(self, relative_pos_from_dealer=1):
        # Get all active players
        self.active_players = [p for p in self.players if not p.folded and (p.chips.total_value() > 0 or p.bet.total_value() > 0)]
        if not self.active_players:
            return

        # Find the dealer in the active players list
        dealer_player = self.players[self.dealer_idx]
        if dealer_player not in self.active_players:
            # If dealer is not active, just leave order as is
            return

        dealer_active_idx = self.active_players.index(dealer_player)
        # Calculate the index for the desired position (e.g., small blind is +1)
        start_idx = (dealer_active_idx + relative_pos_from_dealer) % len(self.active_players)
        # Rotate so that this player is first
        self.active_players = self.active_players[start_idx:] + self.active_players[:start_idx]

    def update_player_state(self, player: Player, amount_to_call, street: str):
        win_rate, tie_rate, loss_rate = self.evaluator.monte_carlo_odds(player.hand, self.community_cards, len(self.initial_players))
        player.player_state['hand_strength'] = win_rate
        player.player_state['improvement_change'] = self.evaluator.estimate_improvement_chance(player.hand, self.community_cards)
        total_pot_value = self.main_pot.total_value() + sum(pot.total_value() for pot in self.side_pots)
        player.player_state['pot_odds'] = amount_to_call / (total_pot_value + amount_to_call)
        average_stack = sum(p.chips.total_value() for p in self.players if p != player) / (len(self.players) - 1)
        stack_ratio = player.chips.total_value() / average_stack if average_stack != 0 else 1
        player.player_state['stack_ratio'] = stack_ratio if stack_ratio != 0 else 1.0
        player.player_state['can_check'] = True if player.bet.total_value() == amount_to_call else False
        player.player_state['street'] = street

    def _betting_round(self):

        # Players who have money and have not folded
        # print([p.name for p in self.players if (p.chips.total_value() > 0 or p.bet.total_value() > 0)])
        self.update_active_players(1)
        # for p in self.players:
        #     print(f"Player: {p.name}, Folded: {p.folded}, Chips: {p.chips.total_value()}, Bet: {p.bet.total_value()}")
        if len(self.active_players) <= 1:
            return
        player_queue = self.active_players
        # Pre-flop
        to_call = ChipStash()
        if len(self.community_cards) == 0:
            player = player_queue.pop(0)
            print(f"{player.name} posted small blind!")
            player.place_bet(self.small_blind.copy())
            # small blind gets chance to match
            player_queue = player_queue + [player]

            player = player_queue.pop(0)
            print(f"{player.name} posted big blind!")
            player.place_bet(self.big_blind.copy())
            to_call = self.big_blind.copy()
        #     to_call = self.big_blind.copy()
        #     if len(active_players) > 2:
        #         # In games with more than 2 players, start after the big blind
        #         start_idx = (self.dealer_idx + 3) % len(self.players)
        #         player_queue = active_players[start_idx:] + active_players[:start_idx]
        #         # active_players = [p for p in self.players if not p.folded and (p.chips.total_value() > 0 or p.bet.total_value() > 0)]
        #     else:
        #         # In heads-up (2 player) games, dealer acts first pre-flop
        #         # Dealer is the big blind so don't include them in the pre-flop call
        #         start_idx = (self.dealer_idx + 1) % len(active_players)
        #         player_queue = [active_players[start_idx]]
        #         # print([p.name for p in player_queue])
        #         # active_players = [p for p in self.players if not p.folded and (p.chips.total_value() > 0 or p.bet.total_value() > 0)]
        # # Post-flop
        # else:
        #     start_idx = self.dealer_idx
        #     # active_players = [p for p in self.players if not p.folded and p.chips.total_value() > 0]
        #     player_queue = active_players[start_idx:] + active_players[:start_idx]
        #     player_queue = active_players
        #     to_call = ChipStash()
        
        # player_queue = active_players[start_idx:] + active_players[:start_idx]
        
        for player in self.active_players:
            player.raised = False

        while player_queue:
            non_folded_players = [p for p in self.players if not p.folded and (p.chips.total_value() > 0)]
            if len(non_folded_players) == 1:
                break
            player = player_queue.pop(0)
            # action, amount = player.make_decision(to_call, self.min_raise, self.community_cards, self.players[self.dealer_idx].name)
            total_pot_value = self.main_pot.total_value() + sum(pot.total_value() for pot in self.side_pots)
            self.update_player_state(player, to_call.total_value(), self.street)
            action, amount = player.make_decision_v2(total_pot_value, self.min_raise.total_value())
            additional_chips = player.bet.difference_to(to_call)
            print(f"\n\nCurrent bet: {player.bet}")
            print(f"Need to call: {to_call}")
            print(f"Additional chips needed: {additional_chips}")
            print(f"{player.name} chooses to {action.name if action else "No Action"} with amount ${amount if amount else 0}\n")
            # if player.name is active_players[(self.dealer_idx + 1) % len(active_players)].name:
            #     if not self.sb_paid:
            #         trash = ChipStash()
            #         trash.transfer_chips(to_call, self.small_blind)
            #         self.sb_paid = True
            if action == Action.CALL and amount.total_value() >= player.chips.total_value():
                action = Action.ALL_IN
            
            if action == Action.FOLD:
                player.folded = True
                continue

            elif action == Action.CHECK:
                if player.bet.total_value() < to_call.total_value():
                    # Invalid check when call is required
                    player.folded = True
                continue

            elif action == Action.CALL:
                # Calculate what additional chips are needed to match the call
                # additional_chips = player.bet.difference_to(to_call)
                
                # Place the bet with the additional chips
                player.place_bet(additional_chips)
                
            elif action == Action.RAISE or action == Action.BLUFF:
                raise_value = amount
                additional_chips.transfer_chips(amount, amount)
                player.place_bet(additional_chips)
                to_call = ChipStash(player.bet.inventory.copy())
                player.raised = True
                non_folded_players = [p for p in self.players if not p.folded and (p.chips.total_value() > 0)]

                # active_players = [p for p in self.players if not p.folded]
                if player.name not in [p.name for p in non_folded_players]:
                    continue  # Skip this player if they're not in the list

                player_idx = [p.name for p in non_folded_players].index(player.name)
                st_idx = (player_idx + 1) % len(non_folded_players)
                player_queue = non_folded_players[st_idx:] + non_folded_players[:player_idx]

            elif action == Action.ALL_IN:
                additional_chips.transfer_chips(amount, amount)
                # call_stash = to_call.difference_to(player.chips)
                # player.place_bet(call_stash)
                player.place_bet(additional_chips)
                to_call = ChipStash(player.bet.inventory.copy())
                if player.bet.total_value() > to_call.total_value():
                    # active_players = [p for p in self.players if not p.folded]
                    non_folded_players = [p for p in self.players if not p.folded and (p.chips.total_value() > 0)]

                    if player.name not in [p.name for p in non_folded_players]:
                        continue  # Skip this player if they're not in the list

                    player_idx = [p.name for p in non_folded_players].index(player.name)
                    st_idx = (player_idx + 1) % len(non_folded_players)
                    player_queue = non_folded_players[st_idx:] + non_folded_players[:player_idx]

        # print('\n')
        # for p in self.players:
        #     print(f"{p.name} bet a total of ${p.bet.total_value()} this round!: {p.chips}")
            
        # print('\n')
        for player in self.players:
            print(f"{player.name} betted: ${player.bet.total_value()}")
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
        pot = self.main_pot
        pot_idx = 1
        while remaining_players:

            for player in remaining_players:
                # print(f"{player.name} has contributed {player.bet} to pot #{pot_idx}")
                pot.transfer_chips(player.bet, player.bet)
                pot.contributors.append(player.name)

            remaining_players = [p for p in remaining_players if p.bet.total_value() > 0]
            if remaining_players:
                pot = ChipStash()
                self.side_pots.append(pot)
                pot_idx += 1
                

        # print(f"Main pot: ${self.main_pot.total_value()}")
        # for i, side in enumerate(self.side_pots):
        #     print(f"Side pot {i+1}: ${side.total_value()}")

    def _showdown(self):
        # Evaluate hands for all active players
        for player in self.players:
            if not player.folded:
                player.evaluate_hand(self.community_cards)

        finalists = [p for p in self.players if not p.folded]
        if not finalists:
            return

        # Determine the best score
        results = self.evaluator.evaluate_table(finalists, self.community_cards)
        
        # The first entry in results is either the top player or a tie group of top players
        if isinstance(results[0], list):  # It's a tied group
            winners = [player for player, _, _ in results[0]]
        else:  # It's a single winner tuple (player, rank, values)
            winners = [results[0][0]]

        print("\nShowdown Results:")
        self._display_community_cards()

        for player in finalists:
            hand_rank, card_val = player.hand_eval
            print(f"{player.name}:")
            print(f"   Hand: {player.hand[0]} {player.hand[1]}")
            print(f"   Best hand: {hand_rank}")
            print(f"   ", " ".join(str(card) for card in card_val))
        
        for winner in winners:
            hand_rank, card_val = winner.hand_eval
            print(f"{winner.name} has won the round!")
            print(f"   Best hand: {hand_rank}")
            print(f"   Cards: ", " ".join(str(card) for card in card_val))

        # Distribute the main pot - only to winners who contributed to this pot
        eligible_main_pot_winners = [p for p in winners if p.name in self.main_pot.contributors]
        # print(f"Main pot: {self.main_pot.total_value()}")
        self._distribute_pot(self.main_pot, eligible_main_pot_winners)

        # Distribute side pots (if any) - only to winners who contributed to each specific pot
        for pot in self.side_pots:
            # print(f"Side pot: {pot.total_value()}")
            eligible_pot_winners = [p for p in winners if p.name in pot.contributors]
            self._distribute_pot(pot, eligible_pot_winners)

    def _distribute_pot(self, pot: ChipStash, winners: List[Player]):
        if not winners or pot.total_value() == 0:
            return
        
        # Determine winner closest to dealer counter-clockwise (i.e., highest index before dealer_idx)
        winner_indices = [self.players.index(p) for p in winners]
        sorted_winners = sorted(winner_indices, key=lambda i: (i - self.dealer_idx) % len(self.players), reverse=True)
        winner_order = [self.players[i] for i in sorted_winners]
        
        # print(f"Distributing pot of ${pot.total_value()} among {len(winners)} winners")
        
        # Calculate each player's base share
        share_value = pot.total_value() // len(winners)
        remainder_value = pot.total_value() % len(winners)
        
        print(f"Each winner gets ${share_value}, with ${remainder_value} remainder")
        
        # Create a copy of the pot to work with
        remaining_pot = pot.copy()
        
        # Step 1: Give each winner their even share
        for winner in winners:
            # Create a chip stash that is worth exactly share_value
            winner_share = ChipStash()
            
            # Distribute from highest to lowest chips
            remaining_share = share_value
            for chip_value in sorted(remaining_pot.inventory.keys(), reverse=True):
                if remaining_share <= 0:
                    break
                    
                chips_available = remaining_pot.inventory[chip_value]
                chips_needed = remaining_share // chip_value
                chips_to_give = min(chips_available, chips_needed)
                
                if chips_to_give > 0:
                    winner_share.add_chips(chip_value, chips_to_give)
                    remaining_pot.remove_chips(chip_value, chips_to_give)
                    remaining_share -= chip_value * chips_to_give
            
            # If we couldn't make exact change, trade in chips
            if remaining_share > 0 and remaining_pot.total_value() > 0:
                remaining_pot.to_smallest_denomination()
                
                # Try again with smaller denominations
                for chip_value in sorted(remaining_pot.inventory.keys()):
                    if remaining_share <= 0:
                        break
                        
                    chips_available = remaining_pot.inventory[chip_value]
                    chips_needed = remaining_share // chip_value
                    chips_to_give = min(chips_available, chips_needed)
                    
                    if chips_to_give > 0:
                        winner_share.add_chips(chip_value, chips_to_give)
                        remaining_pot.remove_chips(chip_value, chips_to_give)
                        remaining_share -= chip_value * chips_to_give
            
            # Transfer chips to the winner - FIXED: Add chips directly to winner's stash
            # print(f"{winner.name} receives ${winner_share.total_value()}")
            # winner.chips.transfer_chips(winner_share, winner_share)  # THIS IS THE BUG!
            # Correct way: directly add each chip to the winner's stash
            for chip_value, chip_count in winner_share.inventory.items():
                if chip_count > 0:
                    winner.chips.add_chips(chip_value, chip_count)
        # Step 2: Distribute remainder chips one at a time to players in order
        if remaining_pot.total_value() > 0:
            # Convert all remaining chips to smallest denomination for easier distribution
            remaining_pot.to_smallest_denomination()
            
            # Give out one chip at a time
            idx = self.dealer_idx + len(self.players) % len(self.players)
            while remaining_pot.total_value() > 0:
                # Find the smallest chip we have
                for chip_value in sorted(remaining_pot.inventory.keys()):
                    if remaining_pot.inventory[chip_value] > 0:
                        # Give this chip to the next player
                        winner = winner_order[idx % len(winner_order)]
                        winner.chips.add_chips(chip_value, 1)
                        remaining_pot.remove_chips(chip_value, 1)
                        # print(f"{winner.name} receives an extra ${chip_value} chip")
                        
                        # Move to next player
                        idx = idx + 1 % len(self.players)
                        break

        # for p in self.players:
        #     print(f"{p.name} has {p.chips}")