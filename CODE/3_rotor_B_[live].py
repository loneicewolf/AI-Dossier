import ipywidgets as widgets
from IPython.display import display

# --- Helper Functions ---

def letter_to_pos(letter):
    """
    Convert 'A' -> 0, 'B' -> 1, ... 'Z' -> 25
    """
    return ord(letter.upper()) - 65

def pos_to_letter(pos):
    """
    Convert 0 -> 'A', 1 -> 'B', ... 25 -> 'Z'
    """
    return chr((pos % 26) + 65)

def encrypt_char(ch, rotor_positions):
    """
    Pass character 'ch' through 3 rotors in sequence (encrypting).
    - rotor_positions[i] in [0..25]
    - We add the shift from rotor1, then rotor2, then rotor3.
    """
    if not ch.isalpha():
        return ch
    pos = letter_to_pos(ch)
    # Forward path: rotor1 -> rotor2 -> rotor3
    for shift in rotor_positions:
        pos = (pos + shift) % 26
    return pos_to_letter(pos)

def decrypt_char(ch, rotor_positions):
    """
    Pass character 'ch' backward through the 3 rotors (decrypting).
    - We subtract the shift from rotor3, then rotor2, then rotor1.
    """
    if not ch.isalpha():
        return ch
    pos = letter_to_pos(ch)
    # Reverse path: rotor3 -> rotor2 -> rotor1
    for shift in reversed(rotor_positions):
        pos = (pos - shift) % 26
    return pos_to_letter(pos)

def step_rotors(rotor_positions):
    """
    Step rotor1 every time.
    If rotor1 completes a full cycle, step rotor2, etc.
    rotor_positions is [r1, r2, r3].
    """
    rotor_positions[0] = (rotor_positions[0] + 1) % 26
    # If rotor1 rolled over from Z->A, step rotor2
    if rotor_positions[0] == 0:
        rotor_positions[1] = (rotor_positions[1] + 1) % 26
        # If rotor2 rolled over, step rotor3
        if rotor_positions[1] == 0:
            rotor_positions[2] = (rotor_positions[2] + 1) % 26


# --- Widgets ---

rotor1_dropdown = widgets.Dropdown(options=[chr(i) for i in range(65, 91)],
                                   value='A', description="Rotor 1:")
rotor2_dropdown = widgets.Dropdown(options=[chr(i) for i in range(65, 91)],
                                   value='A', description="Rotor 2:")
rotor3_dropdown = widgets.Dropdown(options=[chr(i) for i in range(65, 91)],
                                   value='A', description="Rotor 3:")

mode_dropdown = widgets.Dropdown(options=["Encrypt", "Decrypt"],
                                 value="Encrypt", description="Mode:")

input_text = widgets.Text(value="", description="Input:")
reset_button = widgets.Button(description="Reset", button_style='warning')
output_area = widgets.Output()

# We'll track the old_value of input_text to process only newly typed characters
old_input_value = ""

# We'll store the dynamic rotor positions in a list [r1, r2, r3] as 0..25
rotor_positions = [0, 0, 0]

def on_text_change(change):
    """
    This triggers whenever input_text.value changes.
    We process newly typed chars only.
    """
    global old_input_value, rotor_positions

    new_value = change['new']
    old_value = change['old']

    # If user typed some new characters at the end
    if len(new_value) > len(old_value):
        added_substring = new_value[len(old_value):]
        current_mode = mode_dropdown.value  # "Encrypt" or "Decrypt"
        with output_area:
            for ch in added_substring:
                # Grab old rotor positions in letter form
                pos_before = (pos_to_letter(rotor_positions[0]),
                              pos_to_letter(rotor_positions[1]),
                              pos_to_letter(rotor_positions[2]))
                
                if ch.isalpha():
                    if current_mode == "Encrypt":
                        out_ch = encrypt_char(ch, rotor_positions)
                    else:
                        out_ch = decrypt_char(ch, rotor_positions)
                    
                    # Print transformation
                    print(f"{ch} (rotors {pos_before}, mode={current_mode}) -> {out_ch}", end="")
                    
                    # Step rotors AFTER processing a letter
                    step_rotors(rotor_positions)
                    
                    # Show new positions
                    pos_after = (pos_to_letter(rotor_positions[0]),
                                 pos_to_letter(rotor_positions[1]),
                                 pos_to_letter(rotor_positions[2]))
                    print(f"  => rotors now {pos_after}")
                else:
                    # Non-alpha, just print
                    print(f"{ch} (no step - non-alpha)")

    old_input_value = new_value

def on_reset_button_clicked(b):
    """
    Reset input_text, rotor_positions, and output_area.
    """
    global old_input_value, rotor_positions
    # Clear input
    input_text.value = ""
    old_input_value = ""
    # Reset rotor positions from user-chosen dropdown
    rotor_positions[0] = letter_to_pos(rotor1_dropdown.value)
    rotor_positions[1] = letter_to_pos(rotor2_dropdown.value)
    rotor_positions[2] = letter_to_pos(rotor3_dropdown.value)
    # Clear output area
    output_area.clear_output()

def on_rotor_change(change):
    """
    If user changes rotor position or mode in the dropdown while typing,
    it won't retroactively affect the stepped positions,
    but will apply after the next reset.
    """
    pass

rotor1_dropdown.observe(on_rotor_change, names='value')
rotor2_dropdown.observe(on_rotor_change, names='value')
rotor3_dropdown.observe(on_rotor_change, names='value')
mode_dropdown.observe(on_rotor_change, names='value')

input_text.observe(on_text_change, names='value')
reset_button.on_click(on_reset_button_clicked)

# Initialize rotor_positions from the default dropdown values
rotor_positions = [
    letter_to_pos(rotor1_dropdown.value),
    letter_to_pos(rotor2_dropdown.value),
    letter_to_pos(rotor3_dropdown.value)
]

# Layout
ui = widgets.VBox([
    widgets.HBox([rotor1_dropdown, rotor2_dropdown, rotor3_dropdown, mode_dropdown, reset_button]),
    input_text,
    output_area
])

display(ui)
