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
        Trades chips to achieve the specified target count of chips with the specified value.
        Can break down larger denominations or combine smaller ones as needed.
        """
        if target_chip_value is None or target_count <= 0:
            return
        
        # Store initial total value for validation
        initial_total_value = self.total_value()
            
        # Check if we already have enough of the target chips
        existing_count = self.get_chip_count(target_chip_value)
        if existing_count >= target_count:
            return  # We already have enough
        
        # How many more target chips we need
        remaining_to_create = target_count - existing_count
        
        # Sort chips by value (highest to lowest)
        chip_hier = sorted(self.inventory.keys(), reverse=True)
        
        # Phase 1: Convert higher denominations down to target value
        for chip in chip_hier:
            # Skip chips with same or lower value than target
            if chip <= target_chip_value:
                continue
                
            available = self.get_chip_count(chip)
            if available <= 0:
                continue
                
            # How many target chips we can get from this denomination
            target_chips_per_high_chip = chip // target_chip_value
            
            # How many high chips we need to trade to meet our target (but no more than available)
            high_chips_to_trade = min(available, (remaining_to_create + target_chips_per_high_chip - 1) // target_chips_per_high_chip)
            
            if high_chips_to_trade > 0:
                # Calculate how many target chips we'll get and remaining value
                total_value_traded = high_chips_to_trade * chip
                target_chips_to_receive = total_value_traded // target_chip_value
                remainder_value = total_value_traded % target_chip_value
                
                # Update our inventory
                self.remove_chips(chip, high_chips_to_trade)
                self.add_chips(target_chip_value, target_chips_to_receive)
                
                # Handle remainder by adding smaller denomination chips
                if remainder_value > 0:
                    # Find appropriate smaller denominations for the remainder
                    for smaller_chip in sorted(self.inventory.keys(), reverse=True):
                        if smaller_chip < target_chip_value and remainder_value >= smaller_chip:
                            chips_to_add = remainder_value // smaller_chip
                            if chips_to_add > 0:
                                self.add_chips(smaller_chip, chips_to_add)
                                remainder_value -= chips_to_add * smaller_chip
                                
                                # Get chip name for output
                                smaller_chip_name = [name for name, value in Chips.__dict__.items() 
                                                if value == smaller_chip][0]
                                print(f"Added {chips_to_add} {smaller_chip_name} chip(s) from remainder")
                        
                        if remainder_value == 0:
                            break
                
                # Update our remaining need
                remaining_to_create -= target_chips_to_receive
                
                # Get readable chip names for output
                chip_name = [name for name, value in Chips.__dict__.items() if value == chip][0]
                target_chip_name = [name for name, value in Chips.__dict__.items() if value == target_chip_value][0]
                print(f"Traded in {high_chips_to_trade} {chip_name} chip(s) to get {target_chips_to_receive} {target_chip_name} chip(s)!")
                
            # Check if we've met our target
            if remaining_to_create <= 0:
                break
        
        # Phase 2: Combine smaller denominations up to target value
        if remaining_to_create > 0:
            # First calculate total value available from smaller chips
            total_small_value = 0
            smaller_chips_inventory = {}  # Keep track of available smaller chips
            
            for chip in sorted(self.inventory.keys()):  # Lowest to highest
                if chip < target_chip_value:
                    available_count = self.get_chip_count(chip)
                    if available_count > 0:
                        total_small_value += chip * available_count
                        smaller_chips_inventory[chip] = available_count
            
            # How many target chips can we make from smaller denominations
            possible_target_chips = total_small_value // target_chip_value
            
            if possible_target_chips > 0:
                # We can make some target chips from smaller denominations
                to_create = min(possible_target_chips, remaining_to_create)
                value_needed = to_create * target_chip_value
                value_used = 0
                
                # Make a copy of the inventory to track what we'll use
                chips_to_use = {}
                
                # Use chips from largest to smallest (more efficient)
                for chip in sorted(smaller_chips_inventory.keys(), reverse=True):
                    available = smaller_chips_inventory[chip]
                    
                    # How many of this chip can we use
                    max_value_from_chip = available * chip
                    value_to_use = min(max_value_from_chip, value_needed - value_used)
                    chips_needed = value_to_use // chip
                    
                    if chips_needed > 0:
                        value_used += chips_needed * chip
                        chips_to_use[chip] = chips_needed
                        
                        # Get chip name for output
                        chip_name = [name for name, value in Chips.__dict__.items() if value == chip][0]
                        if chips_needed == available:
                            print(f"Combined all {chips_needed} {chip_name} chip(s) toward {to_create} {[name for name, value in Chips.__dict__.items() if value == target_chip_value][0]} chip(s)")
                        else:
                            print(f"Combined {chips_needed} {chip_name} chip(s) toward {to_create} {[name for name, value in Chips.__dict__.items() if value == target_chip_value][0]} chip(s)")
                    
                    if value_used >= value_needed:
                        break
                
                # Only if we've collected enough value, perform the trade
                if value_used >= value_needed:
                    # Remove the used chips
                    for chip, count in chips_to_use.items():
                        self.remove_chips(chip, count)
                    
                    # Add the target chips
                    self.add_chips(target_chip_value, to_create)
                    print(f"Created {to_create} {[name for name, value in Chips.__dict__.items() if value == target_chip_value][0]} chip(s) from smaller denominations")
                    
                    # Update remaining need
                    remaining_to_create -= to_create
        
        # Validate that the total value hasn't changed
        final_total_value = self.total_value()
        if initial_total_value != final_total_value:
            print(f"WARNING: Total chip value changed during trade! Before: ${initial_total_value}, After: ${final_total_value}")
            difference = final_total_value - initial_total_value
            if difference > 0:
                print(f"Value increased by ${difference}")
            else:
                print(f"Value decreased by ${-difference}")
        else:
            # Only print this in debug mode or when explicitly requested
            # print(f"Trade validation successful: Total value maintained at ${initial_total_value}")
            pass

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

    #TODO:: when a person doesn't have that spcific chips, can't transfer
    def transfer_chips(self, other_stash: "ChipStash", chips_to_transfer: "ChipStash"):
        if other_stash.total_value() < chips_to_transfer.total_value():
            raise ValueError("Insufficient chips to fulfill the request.")
        sorted_chips = sorted(self.inventory.keys(), reverse=True)
        # transfer = {chip: 0 for chip in self.inventory}
        transfer = ChipStash()
        # print(f"\nBefore: {other_stash}")
        for chip in sorted_chips:
            requested_chips = chips_to_transfer.get_chip_count(chip)
            available_chips = other_stash.get_chip_count(chip)
            if requested_chips > 0:
                to_transfer = min(requested_chips, available_chips)
                # transfer[chip] = chips_to_transfer
                if to_transfer <= 0:
                    print(f"Requesting to trade in: {chip} for {requested_chips}")
                    other_stash.trade_in(chip, requested_chips)
                    available_chips = other_stash.get_chip_count(chip)
                    to_transfer = min(requested_chips, available_chips)
                    if available_chips <= 0:
                        continue
                transfer.add_chips(chip, to_transfer)
                # self.inventory[chip] -= chips_to_transfer
                other_stash.remove_chips(chip, to_transfer)
        total_value = transfer.total_value()
        # print(transfer)
        for chip, amount in transfer.inventory.items():
            self.add_chips(chip, amount)
        # print(f"Request of ${total_value} successful!")
        # print(f"After: {other_stash}\n")



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
    
    # def redistribute(self):


def dollar_to_chips(value):
    bet_chips = ChipStash()
    remaining = value
    
    # Get chip values sorted from highest to lowest
    chip_values = []
    for attr_name, attr_value in vars(Chips).items():
        if not attr_name.startswith('__') and isinstance(attr_value, int):
            chip_values.append(attr_value)
    chip_values.sort(reverse=True)
    
    # Create optimal denomination mix
    for chip_value in chip_values:
        if remaining <= 0:
            break
            
        count = remaining // chip_value
        if count > 0:
            bet_chips.add_chips(chip_value, count)
            remaining -= chip_value * count
    
    return bet_chips