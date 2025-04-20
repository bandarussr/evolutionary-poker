from collections import deque
class Chips:
    White = 50
    Red = 100
    Green = 250
    Blue = 500
    Black = 1000

class ChipStash:
    def __init__(self, initial_inventory=None):
        # list of people who've contributed to this pot
        self.contributors = []
        # Initialize the inventory with default values of 0 for each chip type unless given a dict
        self.inventory = {}
        for chip_value in (Chips.White, Chips.Red, Chips.Green, Chips.Blue, Chips.Black):
            self.inventory[chip_value] = initial_inventory.get(chip_value, 0) if initial_inventory else 0

    def add_chips(self, chip_value: int, count: int):
        if chip_value in self.inventory:
            self.inventory[chip_value] += count
        else:
            raise ValueError(f"Invalid chip value: {chip_value}")

    def remove_chips(self, chip_value: int, count: int):
        if chip_value in self.inventory:
            if self.inventory[chip_value] >= count:
                self.inventory[chip_value] -= count
            else:
                raise ValueError(f"Not enough chips of value {chip_value} to remove.")
        else:
            raise ValueError(f"Invalid chip value: {chip_value}")

    def _calculate_trade_in(self, target_chip_value: int, target_count: int):
        """
        Helper function to calculate the number of chips needed to meet the target.
        Returns a tuple (can_trade, required_count, trade_plan).
        - can_trade: Whether the target can be achieved.
        - required_count: Remaining chips needed to meet the target.
        - trade_plan: A dictionary of higher chip values and how many to trade in.
        """
        chip_hierarchy = sorted(self.inventory.keys(), reverse=True)  # Highest to lowest value
        required_count = target_count - self.inventory.get(target_chip_value, 0)
        trade_plan = {}

        if required_count <= 0:
            return True, 0, trade_plan  # Already have enough chips of the target value

        for higher_value in chip_hierarchy:
            if higher_value <= target_chip_value:
                continue  # Skip lower or equal denominations

            # Calculate how many target chips can be obtained from the current higher denomination
            chips_available = self.inventory[higher_value] * (higher_value // target_chip_value)
            chips_to_trade = min(chips_available, required_count)
            required_count -= chips_to_trade

            if chips_to_trade > 0:
                trade_plan[higher_value] = chips_to_trade

            if required_count <= 0:
                return True, 0, trade_plan  # Target can be achieved

        return False, required_count, trade_plan  # Not enough higher denomination chips to meet the target

    def trade_in(self, target_chip_value: int = None, target_count: int = 0):
        """
        Trades in higher denomination chips to lower denominations.
        If target_chip_value and target_count are provided, prioritizes trading in chips to meet the target.
        """
        
        # if target_chip_value and target_count > 0:
        #     can_trade, _, trade_plan = self._calculate_trade_in(target_chip_value, target_count)
        #     if not can_trade:
        #         raise ValueError(f"Cannot achieve {target_count} chips of value {target_chip_value} through trade-in.")

        #     # Execute the trade plan
        #     for higher_value, chips_to_trade in trade_plan.items():
        #         self.inventory[higher_value] -= chips_to_trade
        #         self.inventory[target_chip_value] += chips_to_trade

        #     # Stop if the target is met
        #     if self.inventory[target_chip_value] >= target_count:
        #         return

        # # General trade-in logic (existing behavior)
        # chip_hierarchy = sorted(self.inventory.keys(), reverse=True)  # Highest to lowest value
        # for i in range(len(chip_hierarchy) - 1):  # Skip the lowest denomination
        #     higher_value = chip_hierarchy[i]
        #     lower_value = chip_hierarchy[i + 1]

        #     # Convert higher denomination chips to lower denomination chips
        #     while self.inventory[higher_value] > 0:
        #         chips_to_add = higher_value // lower_value
        #         self.inventory[higher_value] -= 1
        #         self.inventory[lower_value] += chips_to_add

    def total_value(self) -> int:
        return sum(value * count for value, count in self.inventory.items())

    def reset(self):
        """Resets the chip inventory to zero for all chip values."""
        for chip_value in self.inventory:
            self.inventory[chip_value] = 0

    def get_chip_count(self, chip_value: int) -> int:
        """Gets the count of chips in the inventory corresponding to the given chip value."""
        if chip_value in self.inventory:
            return self.inventory[chip_value]
        raise ValueError(f"No chip found for value: {chip_value}")

    def transfer_chips(self, other_stash: "ChipStash", chips_to_transfer: "ChipStash"):
        total_value = 0
        
        # Validate that the other stash has enough of each chip type to transfer
        # for chip_value, requested_count in chips_to_transfer.inventory.items():
        #     if requested_count <= 0:
        #         continue  # Skip zero or negative counts
                
        #     if chip_value not in other_stash.inventory:
        #         raise ValueError(f"Invalid chip value in the source stash: {chip_value}")
                
        #     # Check if source has enough of this chip type
        #     if other_stash.inventory[chip_value] < requested_count:
        #         # Try to trade in higher denominations
        #         other_stash.trade_in(chip_value, requested_count)
                
        #         # Check again after trade-in
        #         if other_stash.inventory[chip_value] < requested_count:
        #             raise ValueError(f"Not enough chips of value {chip_value} to transfer after trade-in attempt.")
            
        #     # Keep track of total value for reporting
        #     total_value += chip_value * requested_count

        # total_value = chips_to_transfer.total_value()
        # if total_value == 0:
        #     return

        # target_combo = chips_to_transfer.inventory.copy()
        # available = other_stash.inventory.copy()
        # chip_values = sorted(available.keys(), reverse=True)

        # best_match = None
        # best_diff_score = float('inf')

        # queue = deque()
        # queue.append((0, available.copy(), {k: 0 for k in chip_values}))
        # visited = set()

        # while True:
        #     available = other_stash.inventory.copy()
        #     queue = deque()
        #     queue.append((0, available.copy(), {k: 0 for k in chip_values}))
        #     visited = set()
        #     found = False

        #     while queue:
        #         current_value, current_inv, used_chips = queue.popleft()
        #         state_key = (current_value, tuple(current_inv.items()))
        #         if state_key in visited:
        #             continue
        #         visited.add(state_key)

        #         if current_value == total_value:
        #             diff_score = sum(abs(used_chips[k] - target_combo.get(k, 0)) for k in chip_values)
        #             if diff_score < best_diff_score:
        #                 best_diff_score = diff_score
        #                 best_match = used_chips.copy()
        #                 found = True
        #             continue

        #         for chip in chip_values:
        #             if current_inv[chip] > 0 and current_value + chip <= total_value:
        #                 next_inv = current_inv.copy()
        #                 next_used = used_chips.copy()
        #                 next_inv[chip] -= 1
        #                 next_used[chip] += 1
        #                 queue.append((current_value + chip, next_inv, next_used))

        #     if found or other_stash.total_value() < total_value:
        #         break

        #     try:
        #         other_stash.trade_in()
        #     except ValueError:
        #         break
        
        # Perform the transfer for each chip type
        # for chip_value, requested_count in chips_to_transfer.inventory.items():
        #     if requested_count <= 0:
        #         continue
                
        #     # Transfer the chips
        #     other_stash.remove_chips(chip_value, requested_count)
        #     self.add_chips(chip_value, requested_count)
        
        # for chip_value, count in best_match.items():
        #     if count > 0:
        #         other_stash.remove_chips(chip_value, count)
        #         self.add_chips(chip_value, count)
        # if total_value > 0:
        #     print(f"Transfer of ${total_value} successful!")
        if other_stash.total_value() < chips_to_transfer.total_value():
            raise ValueError("Insufficient chips to fulfill the request.")
        sorted_chips = sorted(self.inventory.keys(), reverse=True)
        transfer = {chip: 0 for chip in self.inventory}
        
        for chip in sorted_chips:
            requested_chips = other_stash.get(chip, 0)
            available_chips = self.inventory[chip]
            if requested_chips > 0:
                chips_to_transfer = min(requested_chips, available_chips)
                transfer[chip] = chips_to_transfer
                self.inventory[chip] -= chips_to_transfer
        total_value = sum(chip * count for chip, count in transfer.items())
        self.add_chips(transfer)
        print(f"Request of ${chips_to_transfer.total_value()} successful!: {total_value}")

    def dollar_to_chips(self, value):
        bet_chips = ChipStash()
        remaining = value

        for chip_value in sorted(self.inventory.keys(), reverse=True):
            if remaining <= 0:
                break
            available = self.inventory[chip_value]
            needed = remaining // chip_value
            use = min(available, needed)
            if use > 0:
                bet_chips.add_chips(chip_value, use)
                self.remove_chips(chip_value, use)  # Correct method call
                remaining -= chip_value * use

        if remaining > 0:
            raise ValueError(f"Insufficient chips to convert ${value}. Remaining: ${remaining}")

        return bet_chips

    def copy(self):
        """Creates a new ChipStash with the same chip inventory as this one"""
        new_stash = ChipStash()
        # Copy all chip counts to the new stash
        for chip_value, count in self.inventory.items():
            new_stash.inventory[chip_value] = count
        return new_stash

    def __str__(self):
        return f"Chip Inventory: {self.inventory}, Total Value: {self.total_value()}"

    
    # def difference_to(self, other: "ChipStash") -> "ChipStash":
    #     """
    #     Calculate the ChipStash needed to reach the value of 'other' from this stash.
        
    #     This is particularly useful for betting scenarios where we need to know what
    #     additional chips a player needs to add to their bet to match a call amount.
        
    #     Args:
    #         other: The target ChipStash to match
            
    #     Returns:
    #         A new ChipStash containing the chips needed to match the target value
    #     """
    #     # Calculate the difference in total value
    #     value_difference = other.total_value() - self.total_value()
        
    #     # If this stash is already higher value than the other, no additional chips needed
    #     if value_difference <= 0:
    #         return ChipStash()
            
    #     # Create a new stash to hold the optimal combination of chips for the difference
    #     result = ChipStash()
        
    #     # Fill in chips from highest to lowest denomination
    #     remaining = value_difference
    #     for chip_value in sorted([Chips.Black, Chips.Blue, Chips.Green, Chips.Red, Chips.White], reverse=True):
    #         # How many of this chip can we use
    #         chip_count = remaining // chip_value
    #         if chip_count > 0:
    #             result.add_chips(chip_value, chip_count)
    #             remaining -= chip_value * chip_count
                
    #         # If we've matched the value exactly, we're done
    #         if remaining == 0:
    #             break
                
    #     return result
    def difference_to(self, other: "ChipStash") -> "ChipStash":
        value_difference = other.total_value() - self.total_value()
        
        # If this stash is already equal or higher value than the other, no additional chips needed
        if value_difference <= 0:
            return ChipStash()
            
        # Create a new stash to hold the chip combination for the difference
        result = ChipStash()
        
        # Fill in chips from highest to lowest denomination
        remaining = value_difference
        chip_values = sorted(self.inventory.keys(), reverse=True)  # Sorted high to low
        
        for chip_value in chip_values:
            # How many of this chip denomination do we need
            chip_count = remaining // chip_value
            if chip_count > 0:
                result.add_chips(chip_value, chip_count)
                remaining -= chip_value * chip_count
                
            # If we've matched the value exactly, we're done
            if remaining == 0:
                break
                
        # If we couldn't match exactly with the available denominations
        if remaining > 0:
            # Find smallest denomination to handle the remainder
            smallest_denom = min(self.inventory.keys())
            extra_chips = (remaining + smallest_denom - 1) // smallest_denom  # Ceiling division
            result.add_chips(smallest_denom, extra_chips)
            
        return result
    def to_smallest_denomination(self) -> "ChipStash":
        """
        Returns a new ChipStash containing all value converted to the smallest denomination chips.
        
        Returns:
            A new ChipStash with only the smallest denomination chips
        """
        # Get all valid chip denominations from the inventory keys
        if not self.inventory:
            return ChipStash()  # Return empty stash if inventory is empty
            
        # Find the smallest denomination available in the inventory
        smallest_denomination = min(self.inventory.keys())
        
        # Calculate the total value of all chips
        total_value = self.total_value()
        
        # Create a new ChipStash with all value in smallest denomination
        result = ChipStash()
        chip_count = total_value // smallest_denomination
        if chip_count > 0:
            result.add_chips(smallest_denomination, chip_count)
        
        return result
