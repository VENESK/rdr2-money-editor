import pymem
import pymem.process

# =================================================================================
# Memory Hacking & Pointers 🔍
# =================================================================================
# These are the pointers and offsets I found for RDR2's money value.
# I used Cheat Engine to find these addresses and tested them thoroughly.
# =================================================================================

# Game process name 🎮
PROCESS_NAME = "RDR2.exe"

# Memory pointers I found 🎯
# Base pointer: RDR2.exe + 0x052A7128 
# Offsets chain: 0x20 -> 0xE60
BASE_ADDRESS_OFFSET = 0x052A7128
POINTER_OFFSETS = [0x20, 0xE60]

# Global vars for process attachment
pm = None 
game_process_attached = False

def attach_to_game():
    """
    Finds and attaches to the game process.
    Returns True on success, False on failure.
    """
    global pm, game_process_attached
    try:
        print(f"Searching for game process: {PROCESS_NAME}...")
        pm = pymem.Pymem(PROCESS_NAME)
        game_process_attached = True
        print(f"Successfully attached to {PROCESS_NAME}!")
        return True
    except pymem.exception.ProcessNotFound:
        print(f"Error: Process '{PROCESS_NAME}' not found. Please make sure the game is running.")
        game_process_attached = False
        return False

def _resolve_pointer(base, offsets):
    """
    (Internal) Follows a chain of pointers to find a final memory address.
    """
    try:
        # Read the base address
        addr = pm.read_longlong(base)
        # Follow the offsets
        for offset in offsets:
            addr = pm.read_longlong(addr + offset)
        return addr
    except pymem.exception.MemoryReadError:
        print("Error: Could not read memory. The pointer or offsets might be incorrect for this game version.")
        return None

def set_money(amount):
    """
    Writes the given amount to the game's memory address for money.
    The value is multiplied by 100 to account for cents.
    """
    global pm, game_process_attached

    if not game_process_attached:
        print("Cannot set money: Not attached to the game process.")
        # Try to attach now if not already attached
        if not attach_to_game():
            return False

    try:
        # Get the base address of the main game module
        game_base = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME).lpBaseOfDll
        
        # The final offset is where the value is stored, so we resolve the pointer up to the second-to-last offset.
        final_offsets = POINTER_OFFSETS[:-1]
        value_offset = POINTER_OFFSETS[-1]
        
        money_address_base = _resolve_pointer(game_base + BASE_ADDRESS_OFFSET, final_offsets)

        if money_address_base:
            final_address = money_address_base + value_offset
            
            # Money in RDR2 is stored with cents (last 2 digits)
            # So we multiply by 100 to handle the decimal places
            # Example: $1500.00 is stored as 150000
            amount_in_cents = amount * 100
            
            print(f"Attempting to write value {amount_in_cents} (${amount}) to address: {hex(final_address)}")
            
            # Write the new money value (4-byte integer)
            pm.write_int(final_address, amount_in_cents)
            
            # Verify the write was successful
            written_value = pm.read_int(final_address)
            print(f"Verification: Value at address is now {written_value}")
            if written_value == amount_in_cents:
                 print("Successfully updated money in game!")
                 return True
            else:
                print("Verification failed. The value was written but did not match.")
                return False
        else:
            print("Failed to resolve the money pointer address. Check your pointers and offsets.")
            return False

    except Exception as e:
        print(f"An unexpected error occurred during memory writing: {e}")
        return False 