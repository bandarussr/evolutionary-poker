class Chips:
    White = 50
    Red = 100
    Green = 250
    Blue = 500
    Black = 1000

class ChipStash(Chips):
    def __init__(self, initial_inventory=None):
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
        if target_chip_value and target_count > 0:
            can_trade, _, trade_plan = self._calculate_trade_in(target_chip_value, target_count)
            if not can_trade:
                raise ValueError(f"Cannot achieve {target_count} chips of value {target_chip_value} through trade-in.")

            # Execute the trade plan
            for higher_value, chips_to_trade in trade_plan.items():
                self.inventory[higher_value] -= chips_to_trade
                self.inventory[target_chip_value] += chips_to_trade

            # Stop if the target is met
            if self.inventory[target_chip_value] >= target_count:
                return

        # General trade-in logic (existing behavior)
        chip_hierarchy = sorted(self.inventory.keys(), reverse=True)  # Highest to lowest value
        for i in range(len(chip_hierarchy) - 1):  # Skip the lowest denomination
            higher_value = chip_hierarchy[i]
            lower_value = chip_hierarchy[i + 1]

            # Convert higher denomination chips to lower denomination chips
            while self.inventory[higher_value] > 0:
                chips_to_add = higher_value // lower_value
                self.inventory[higher_value] -= 1
                self.inventory[lower_value] += chips_to_add

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
        for chip_value, requested_count in chips_to_transfer.inventory.items():
            if requested_count <= 0:
                continue  # Skip zero or negative counts
                
            if chip_value not in other_stash.inventory:
                raise ValueError(f"Invalid chip value in the source stash: {chip_value}")
                
            # Check if source has enough of this chip type
            if other_stash.inventory[chip_value] < requested_count:
                # Try to trade in higher denominations
                other_stash.trade_in(chip_value, requested_count)
                
                # Check again after trade-in
                if other_stash.inventory[chip_value] < requested_count:
                    raise ValueError(f"Not enough chips of value {chip_value} to transfer after trade-in attempt.")
            
            # Keep track of total value for reporting
            total_value += chip_value * requested_count
        
        # Perform the transfer for each chip type
        for chip_value, requested_count in chips_to_transfer.inventory.items():
            if requested_count <= 0:
                continue
                
            # Transfer the chips
            other_stash.remove_chips(chip_value, requested_count)
            self.add_chips(chip_value, requested_count)
        
        if total_value > 0:
            print(f"Transfer of ${total_value} successful!")

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

    def __sub__(self, other: "ChipStash") -> "ChipStash":
        if not isinstance(other, ChipStash):
            raise TypeError("Subtraction only supported between ChipStash objects.")

        # Create a copy of our chips to work with
        result = self.copy()
        
        # Check if we have enough total value
        if result.total_value() < other.total_value():
            raise ValueError(f"Cannot subtract ${other.total_value()} from ${result.total_value()}")
            
        # Process each chip denomination from the other stash
        for chip_value, count in other.inventory.items():
            if count == 0:
                continue  # Skip if no chips of this value to subtract
                
            # If we don't have enough of this specific denomination
            if result.inventory[chip_value] < count:
                # Make change from higher denominations
                result.trade_in(chip_value, count)
                
                # If we still don't have enough after making change
                if result.inventory[chip_value] < count:
                    raise ValueError(f"Cannot subtract {count} chips of value {chip_value}. Only {result.inventory[chip_value]} available after trade-in.")
            
            # Now subtract the chips
            result.remove_chips(chip_value, count)
            
        return result

    def __add__(self, other: "ChipStash") -> "ChipStash":
        if not isinstance(other, ChipStash):
            raise TypeError("Addition only supported between ChipStash objects.")

        result = ChipStash(self.inventory.copy())
        for chip_value, count in other.inventory.items():
            result.inventory[chip_value] += count

        return result

    def __iadd__(self, other: "ChipStash") -> "ChipStash":
        if not isinstance(other, ChipStash):
            raise TypeError("In-place addition only supported between ChipStash objects.")

        for chip_value, count in other.inventory.items():
            self.inventory[chip_value] += count

        return self

    def __isub__(self, other: "ChipStash") -> "ChipStash":
        if not isinstance(other, ChipStash):
            raise TypeError("In-place subtraction only supported between ChipStash objects.")

        chip_hierarchy = sorted(self.inventory.keys(), reverse=True)

        for chip_value in chip_hierarchy:
            need = other.inventory.get(chip_value, 0)
            have = self.inventory.get(chip_value, 0)

            if need > have:
                self.trade_in(target_chip_value=chip_value, target_count=need)
                have = self.inventory.get(chip_value, 0)

            if need > have:
                raise ValueError(f"Cannot subtract {need} chips of value {chip_value}. Only {have} available after trade-in.")

            self.remove_chips(chip_value, need)

        return self
    
    def difference_to(self, other: "ChipStash") -> "ChipStash":
        """
        Calculate the ChipStash needed to reach the value of 'other' from this stash.
        
        This is particularly useful for betting scenarios where we need to know what
        additional chips a player needs to add to their bet to match a call amount.
        
        Args:
            other: The target ChipStash to match
            
        Returns:
            A new ChipStash containing the chips needed to match the target value
        """
        # Calculate the difference in total value
        value_difference = other.total_value() - self.total_value()
        
        # If this stash is already higher value than the other, no additional chips needed
        if value_difference <= 0:
            return ChipStash()
            
        # Create a new stash to hold the optimal combination of chips for the difference
        result = ChipStash()
        
        # Fill in chips from highest to lowest denomination
        remaining = value_difference
        for chip_value in sorted([Chips.Black, Chips.Blue, Chips.Green, Chips.Red, Chips.White], reverse=True):
            # How many of this chip can we use
            chip_count = remaining // chip_value
            if chip_count > 0:
                result.add_chips(chip_value, chip_count)
                remaining -= chip_value * chip_count
                
            # If we've matched the value exactly, we're done
            if remaining == 0:
                break
                
        return result
