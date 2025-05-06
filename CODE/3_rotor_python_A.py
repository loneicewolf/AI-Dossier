# Simplified Enigma-style 3-rotor encryption/decryption simulator using ipywidgets
import ipywidgets as widgets
from IPython.display import display

# Create input widgets for message and rotor initial positions (A-Z) and mode
text_input = widgets.Text(value="HELLO", description="Message:")
rotor1_dropdown = widgets.Dropdown(options=[chr(i) for i in range(65, 91)], value='A', description="Rotor 1:")
rotor2_dropdown = widgets.Dropdown(options=[chr(i) for i in range(65, 91)], value='A', description="Rotor 2:")
rotor3_dropdown = widgets.Dropdown(options=[chr(i) for i in range(65, 91)], value='A', description="Rotor 3:")
mode_dropdown = widgets.Dropdown(options=["Encrypt", "Decrypt"], value="Encrypt", description="Mode:")
button = widgets.Button(description="Run")
output = widgets.Output()

# Define the rotor encryption/decryption logic and UI update in the button click handler
def on_button_click(_):
    output.clear_output()  # clear previous output
    with output:  # capture prints in the output widget
        message = text_input.value
        mode = mode_dropdown.value
        r1 = rotor1_dropdown.value  # current positions of rotors
        r2 = rotor2_dropdown.value
        r3 = rotor3_dropdown.value
        # Convert message to uppercase (Enigma typically works on uppercase A-Z)
        message = message.upper()
        result_chars = []  # store output characters to build final result string
        # Print a header for clarity
        print(f"{mode}ing message: \"{message}\"")
        print(f"Initial rotor positions: {r1}, {r2}, {r3}\n")
        # Process each character in the message
        for char in message:
            # If character is not A-Z, leave it unchanged and do not advance rotors
            if not char.isalpha():
                if char == ' ':
                    print("(space) (no change, no rotor step)")
                else:
                    print(f"({char}) (no change, no rotor step)")
                result_chars.append(char)
                continue
            # Calculate the shift values for each rotor (A=1, B=2, ..., Z=26)
            shift1 = ord(r1) - 65 + 1  # rotor1 shift
            shift2 = ord(r2) - 65 + 1  # rotor2 shift
            shift3 = ord(r3) - 65 + 1  # rotor3 shift
            if mode == "Encrypt":
                # Encrypt: pass the character through Rotor 1, then 2, then 3 (adding shifts)
                mid1 = chr((ord(char) - 65 + shift1) % 26 + 65)  # after rotor1
                mid2 = chr((ord(mid1) - 65 + shift2) % 26 + 65)   # after rotor2
                out_char = chr((ord(mid2) - 65 + shift3) % 26 + 65)  # after rotor3 (final)
                # Show the transformation path through the rotors
                path_str = f"{char} -> {mid1} -> {mid2} -> {out_char}"
            else:
                # Decrypt: pass the character through Rotor 3, then 2, then 1 (subtracting shifts)
                mid3 = chr((ord(char) - 65 - shift3) % 26 + 65)   # after rotor3 (going backwards)
                mid2 = chr((ord(mid3) - 65 - shift2) % 26 + 65)   # after rotor2
                out_char = chr((ord(mid2) - 65 - shift1) % 26 + 65)  # after rotor1 (final)
                path_str = f"{char} -> {mid3} -> {mid2} -> {out_char}"
            # Record the output character
            result_chars.append(out_char)
            # Save old rotor positions for display, then step rotors for the next character
            old_positions = f"{r1},{r2},{r3}"
            # Advance rotor 1 every time; if it wraps from Z to A, advance rotor 2, etc.
            if r1 == 'Z':
                r1 = 'A'
                # Rotor 1 completed a full rotation, step rotor 2
                if r2 == 'Z':
                    r2 = 'A'
                    # Rotor 2 also completed a full rotation, step rotor 3
                    if r3 == 'Z':
                        r3 = 'A'
                    else:
                        r3 = chr(ord(r3) + 1)
                else:
                    r2 = chr(ord(r2) + 1)
            else:
                r1 = chr(ord(r1) + 1)
            new_positions = f"{r1},{r2},{r3}"
            # Print the transformation path and rotor position change for this character
            print(f"{path_str} (rotors: {old_positions} -> {new_positions})")
        # After processing all characters, print the final output string
        output_text = "".join(result_chars)
        print(f"\nOutput: {output_text}")

# Attach the event handler to the button
button.on_click(on_button_click)

# Arrange widgets in a layout
ui = widgets.VBox([
    text_input,
    widgets.HBox([rotor1_dropdown, rotor2_dropdown, rotor3_dropdown]),
    widgets.HBox([mode_dropdown, button]),
    output
])

# Display the UI components
text_input.value = "HELLO WORLD!"   # example message for demonstration
rotor1_dropdown.value = 'A'         # example rotor positions
rotor2_dropdown.value = 'A'
rotor3_dropdown.value = 'A'
mode_dropdown.value = 'Encrypt'     # example mode
on_button_click(None)               # run once to show example transformation in output
display(ui)
