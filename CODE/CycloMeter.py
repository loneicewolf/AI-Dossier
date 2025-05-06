# Thanks to:
# Marian Rejewski
# GPT Pro 
# https://en.wikipedia.org/wiki/Marian_Rejewski

from ipywidgets import interact, Dropdown, ToggleButtons
import string

# Enigma machine components (same as before)

rotor_wiring = {
    "I":  "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II": "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III":"BDFHJLCPRTXVZNYEIWGAKMUSQO",
}
rotor_notch = {"I": "Q", "II": "E", "III": "V"}

reflector_wiring = {
    "A": {
        'A':'E','E':'A', 'B':'J','J':'B', 'C':'M','M':'C', 'D':'Z','Z':'D',
        'F':'L','L':'F', 'G':'Y','Y':'G', 'H':'X','X':'H', 'I':'V','V':'I',
        'K':'W','W':'K', 'N':'O','O':'N', 'P':'Q','Q':'P', 'R':'U','U':'R', 'S':'T','T':'S'
    },
    "B": {
        'A':'Y','Y':'A', 'B':'R','R':'B', 'C':'U','U':'C', 'D':'H','H':'D',
        'E':'Q','Q':'E', 'F':'S','S':'F', 'G':'L','L':'G', 'I':'P','P':'I',
        'J':'X','X':'J', 'K':'N','N':'K', 'M':'O','O':'M', 'T':'Z','Z':'T', 'V':'W','W':'V'
    }
}

plugboard_map = {ch: ch for ch in string.ascii_uppercase}

def encrypt_letter(letter, rotor_order, rotor_positions, reflector_type="A"):
    left_rotor, mid_rotor, right_rotor = rotor_order
    pos_left, pos_mid, pos_right = rotor_positions

    # Step rotors (Enigma stepping rules)
    if (string.ascii_uppercase[pos_mid] == rotor_notch[mid_rotor]):
        pos_left = (pos_left + 1) % 26

    if (string.ascii_uppercase[pos_right] == rotor_notch[right_rotor]) or \
       (string.ascii_uppercase[pos_mid] == rotor_notch[mid_rotor]):
        pos_mid = (pos_mid + 1) % 26

    pos_right = (pos_right + 1) % 26

    def char_to_index(ch): return ord(ch) - ord('A')
    def index_to_char(i): return chr(i + ord('A'))

    # Plugboard in
    c = plugboard_map[letter]

    # --- Forward through rotors (Right -> Middle -> Left) ---
    # Right rotor
    in_idx = char_to_index(c)
    offset = pos_right
    wiring_str = rotor_wiring[right_rotor]
    out_idx = (char_to_index(wiring_str[(in_idx + offset) % 26]) - offset) % 26

    # Middle rotor
    c = index_to_char(out_idx)
    in_idx = char_to_index(c)
    offset = pos_mid
    wiring_str = rotor_wiring[mid_rotor]
    out_idx = (char_to_index(wiring_str[(in_idx + offset) % 26]) - offset) % 26

    # Left rotor
    c = index_to_char(out_idx)
    in_idx = char_to_index(c)
    offset = pos_left
    wiring_str = rotor_wiring[left_rotor]
    out_idx = (char_to_index(wiring_str[(in_idx + offset) % 26]) - offset) % 26

    # --- Reflector ---
    c = index_to_char(out_idx)
    c = reflector_wiring[reflector_type][c]

    # --- Back through rotors (Left -> Middle -> Right) ---
    # Left rotor (reverse)
    in_idx = char_to_index(c)
    offset = pos_left
    wiring_str = rotor_wiring[left_rotor]
    out_idx = (wiring_str.index(chr(((in_idx + offset) % 26) + ord('A'))) - offset) % 26

    # Middle rotor (reverse)
    c = string.ascii_uppercase[out_idx]
    in_idx = ord(c) - ord('A')
    offset = pos_mid
    wiring_str = rotor_wiring[mid_rotor]
    out_idx = (wiring_str.index(chr(((in_idx + offset) % 26) + ord('A'))) - offset) % 26

    # Right rotor (reverse)
    c = string.ascii_uppercase[out_idx]
    in_idx = ord(c) - ord('A')
    offset = pos_right
    wiring_str = rotor_wiring[right_rotor]
    out_idx = (wiring_str.index(chr(((in_idx + offset) % 26) + ord('A'))) - offset) % 26

    # Plugboard out
    c = string.ascii_uppercase[out_idx]
    c = plugboard_map[c]

    # Return encrypted letter + new rotor positions
    return c, (pos_left, pos_mid, pos_right)

def get_cycle_structure(rotor_order, start_positions, reflector_type="A"):
    """
    Compute the cycle structure for the double-encryption mapping (like Rejewski’s cyclometer).
    Returns a list of cycles, where each cycle is a list of letters [A, G, X, A].
    """
    cycles = []
    seen = set()

    for letter in string.ascii_uppercase:
        if letter in seen:
            continue
        cycle = []
        start_letter = letter
        current_letter = letter

        # For each new letter that hasn't yet appeared in any cycle:
        while True:
            # Step 1: Press the letter (1st of the 4-letter indicator)
            _, (pos_left1, pos_mid1, pos_right1) = encrypt_letter(
                current_letter, rotor_order, start_positions, reflector_type)

            # Steps 2 & 3: Press two dummy letters to replicate the Enigma stepping
            dummy = 'A'
            _, (pos_left2, pos_mid2, pos_right2) = encrypt_letter(
                dummy, rotor_order, (pos_left1, pos_mid1, pos_right1), reflector_type)
            _, (pos_left3, pos_mid3, pos_right3) = encrypt_letter(
                dummy, rotor_order, (pos_left2, pos_mid2, pos_right2), reflector_type)

            # Step 4: Press the same letter again (4th of the indicator)
            output_letter, _ = encrypt_letter(
                current_letter, rotor_order, (pos_left3, pos_mid3, pos_right3), reflector_type)

            cycle.append(current_letter)
            seen.add(current_letter)
            current_letter = output_letter

            if current_letter == start_letter:
                cycle.append(current_letter)  # close the loop
                break
            else:
                # Reset rotor positions to the *original* start positions
                # so each mapping is consistent with how the cyclometer sees letter→letter
                # as a pure permutation from 1st to 4th letter of the indicator
                continue
        cycles.append(cycle)
    return cycles

# Create interactive UI

rotor_options = ["I", "II", "III"]
position_choices = [(ch, i) for i, ch in enumerate(string.ascii_uppercase)]
reflector_options = ["A", "B"]

left_dropdown   = Dropdown(options=rotor_options, value="I", description="Left Rotor")
middle_dropdown = Dropdown(options=rotor_options, value="II", description="Middle Rotor")
right_dropdown  = Dropdown(options=rotor_options, value="III", description="Right Rotor")

left_pos_dd   = Dropdown(options=position_choices, value=0, description="Left Pos")
middle_pos_dd = Dropdown(options=position_choices, value=0, description="Middle Pos")
right_pos_dd  = Dropdown(options=position_choices, value=0, description="Right Pos")

reflector_toggle = ToggleButtons(options=reflector_options, value="A", description="Reflector")

def display_cycles(left_rotor, middle_rotor, right_rotor, 
                   left_pos, middle_pos, right_pos, 
                   reflector):
    if len({left_rotor, middle_rotor, right_rotor}) < 3:
        print("**Please select three distinct rotors.**")
        return
    
    rotor_order = (left_rotor, middle_rotor, right_rotor)
    start_positions = (left_pos, middle_pos, right_pos)

    cycles = get_cycle_structure(rotor_order, start_positions, reflector)

    # Sort cycles by their first letter so they have a consistent order
    # (skip the repeated last element in the sort key)
    cycles_sorted = sorted(cycles, key=lambda cyc: cyc[0])

    # Print info
    print(f"**Rotor Order:** {left_rotor}-{middle_rotor}-{right_rotor}")
    print(f"**Start Positions:** {string.ascii_uppercase[left_pos]} "
          f"{string.ascii_uppercase[middle_pos]} {string.ascii_uppercase[right_pos]}")
    print(f"**Reflector:** {reflector}")
    print()

    # List-like visualization: one cycle per line
    for i, cyc in enumerate(cycles_sorted, start=1):
        # cyc includes last letter repeated, e.g. [A, G, X, A]
        # Let’s separate out the repeated letter
        cycle_body = cyc[:-1]  # all but the last repeated element
        cycle_str = " -> ".join(cycle_body) + f" -> {cyc[-1]}"
        # length is the number of transitions (which is len(cyc_body))
        length = len(cycle_body)
        print(f"Cycle {i}: {cycle_str}  (length = {length})")

    # Summarize cycle lengths
    cycle_lengths = [len(cyc) - 1 for cyc in cycles]
    print()
    print("**Cycle lengths:**", cycle_lengths, f"(sum={sum(cycle_lengths)})")

interact(
    display_cycles,
    left_rotor=left_dropdown,
    middle_rotor=middle_dropdown,
    right_rotor=right_dropdown,
    left_pos=left_pos_dd,
    middle_pos=middle_pos_dd,
    right_pos=right_pos_dd,
    reflector=reflector_toggle
);
