
import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
BG = "#F0F0F0"
WHITE = "#FFFFFF"
history = []

AMBIGUOUS = "0Ol1I"

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
NUMBERS = string.digits
SYMBOLS = string.punctuation

def generate_password():
    try:
        length = int(length_var.get())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid password length.")
        return

    if length < 8:
        messagebox.showwarning(
            "Invalid Length",
            "Password length must be at least 8 characters."
        )
        return

    selected_sets = []

    if uppercase_var.get():
        selected_sets.append(UPPERCASE)

    if lowercase_var.get():
        selected_sets.append(LOWERCASE)

    if numbers_var.get():
        selected_sets.append(NUMBERS)

    if symbols_var.get():
        selected_sets.append(SYMBOLS)

    if not selected_sets:
        messagebox.showwarning(
            "Character Types",
            "Please select at least one character type."
        )
        return

    if exclude_var.get():
        selected_sets = [
            "".join(c for c in chars if c not in AMBIGUOUS)
            for chars in selected_sets
        ]

    selected_sets = [chars for chars in selected_sets if chars]

    if not selected_sets:
        messagebox.showerror(
            "Error",
            "No valid characters are available."
        )
        return

    if length < len(selected_sets):
        messagebox.showwarning(
            "Password Length",
            "Length is too short for all selected character types."
        )
        return

    password_chars = [
        secrets.choice(chars) for chars in selected_sets
    ]

    # Fill the remaining length from the combined character pool
    all_chars = "".join(selected_sets)

    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(password_chars)

    password = "".join(password_chars)
    password_entry.config(state="normal")
    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

    update_strength(password, len(selected_sets))
    copy_password(show_message=False)
    history.insert(0, password)
    del history[5:]

    update_history()

def update_strength(password, diversity):
    length = len(password)

    if length >= 16 and diversity >= 3:
        strength = "Strong"
        value = 100
        color = "#168B45"

    elif length >= 12 and diversity >= 2:
        strength = "Medium"
        value = 65
        color = "#E5A000"

    else:
        strength = "Weak"
        value = 30
        color = "#D93025"

    strength_label.config(
        text=f"Strength: {strength}",
        foreground=color
    )

    strength_bar["value"] = value
    strength_bar.configure(style=f"{strength}.Horizontal.TProgressbar")

def copy_password(show_message=True):
    password = password_entry.get()

    if not password:
        if show_message:
            messagebox.showwarning(
                "No Password",
                "Generate a password first."
            )
        return

    try:
        import pyperclip
        pyperclip.copy(password)

    except Exception:
    
        try:
            root.clipboard_clear()
            root.clipboard_append(password)
            root.update()
        except tk.TclError:
            if show_message:
                messagebox.showerror(
                    "Clipboard Error",
                    "Could not copy the password."
                )
            return

    if show_message:
        messagebox.showinfo(
            "Copied",
            "Password copied to clipboard!"
        )

def update_history():
    history_list.delete(0, tk.END)

    for index, password in enumerate(history, start=1):
        history_list.insert(
            tk.END,
            f"{index}. {password}"
        )


def use_history_password(event):
    selection = history_list.curselection()

    if selection:
        password = history[selection[0]]
        password_entry.config(state="normal")
        password_entry.delete(0, tk.END)
        password_entry.insert(0, password)
        update_strength(password, count_selected_types())


def count_selected_types():
    return sum([
        uppercase_var.get(),
        lowercase_var.get(),
        numbers_var.get(),
        symbols_var.get()
    ])

root = tk.Tk()
root.title("Advanced Random Password Generator")
root.geometry("620x650")
root.minsize(560, 600)
root.configure(bg=BG)

# Theme and styles
style = ttk.Style(root)
style.theme_use("clam")

style.configure(
    "TFrame",
    background=BG
)

style.configure(
    "TLabel",
    background=BG,
    font=("Arial", 10)
)

style.configure(
    "TLabelframe",
    background=BG
)

style.configure(
    "TLabelframe.Label",
    background=BG,
    font=("Arial", 10, "bold")
)

style.configure(
    "TButton",
    font=("Arial", 10, "bold"),
    padding=8
)

style.configure(
    "Weak.Horizontal.TProgressbar",
    troughcolor="#D9D9D9",
    background="#D93025"
)

style.configure(
    "Medium.Horizontal.TProgressbar",
    troughcolor="#D9D9D9",
    background="#E5A000"
)

style.configure(
    "Strong.Horizontal.TProgressbar",
    troughcolor="#D9D9D9",
    background="#168B45"
)

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

title_label = ttk.Label(
    main_frame,
    text="Random Password Generator",
    font=("Arial", 20, "bold"),
    anchor="center"
)
title_label.pack(fill="x", pady=(0, 18))

length_frame = ttk.Frame(main_frame)
length_frame.pack(pady=(0, 15))

ttk.Label(
    length_frame,
    text="Password Length:",
    font=("Arial", 10)
).pack(side="left", padx=5)

length_var = tk.IntVar(value=12)

length_spinbox = tk.Spinbox(
    length_frame,
    from_=8,
    to=128,
    textvariable=length_var,
    width=5,
    font=("Arial", 10)
)
length_spinbox.pack(side="left")

character_frame = ttk.LabelFrame(
    main_frame,
    text="Character Types",
    padding=12
)
character_frame.pack(fill="x", pady=(0, 15))

uppercase_var = tk.BooleanVar(value=True)
lowercase_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

ttk.Checkbutton(
    character_frame,
    text="Uppercase (A-Z)",
    variable=uppercase_var
).pack(anchor="w", pady=2)

ttk.Checkbutton(
    character_frame,
    text="Lowercase (a-z)",
    variable=lowercase_var
).pack(anchor="w", pady=2)

ttk.Checkbutton(
    character_frame,
    text="Numbers (0-9)",
    variable=numbers_var
).pack(anchor="w", pady=2)

ttk.Checkbutton(
    character_frame,
    text="Symbols (!@#$%)",
    variable=symbols_var
).pack(anchor="w", pady=2)

security_frame = ttk.LabelFrame(
    main_frame,
    text="Security Options",
    padding=12
)
security_frame.pack(fill="x", pady=(0, 18))

exclude_var = tk.BooleanVar(value=True)

ttk.Checkbutton(
    security_frame,
    text="Exclude ambiguous characters (0, O, l, 1, I)",
    variable=exclude_var
).pack(anchor="w")

password_entry = tk.Entry(
    main_frame,
    font=("Arial", 13),
    justify="center",
    relief="solid",
    bd=1
)
password_entry.pack(fill="x", padx=25, pady=(0, 15), ipady=4)

button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=(0, 12))

generate_button = ttk.Button(
    button_frame,
    text="Generate Password",
    command=generate_password
)
generate_button.pack(side="left", padx=5)

copy_button = ttk.Button(
    button_frame,
    text="Copy to Clipboard",
    command=lambda: copy_password(show_message=True)
)
copy_button.pack(side="left", padx=5)

strength_label = ttk.Label(
    main_frame,
    text="Strength: Not Generated",
    font=("Arial", 11, "bold"),
    anchor="center"
)
strength_label.pack(fill="x", pady=(0, 5))

strength_bar = ttk.Progressbar(
    main_frame,
    orient="horizontal",
    mode="determinate",
    maximum=100,
    value=0,
    length=150,
    style="Weak.Horizontal.TProgressbar"
)
strength_bar.pack(pady=(0, 18))

history_frame = ttk.LabelFrame(
    main_frame,
    text="Last 5 Generated Passwords",
    padding=10
)
history_frame.pack(fill="both", expand=True)

history_scrollbar = ttk.Scrollbar(
    history_frame,
    orient="vertical"
)

history_list = tk.Listbox(
    history_frame,
    font=("Consolas", 10),
    height=5,
    yscrollcommand=history_scrollbar.set,
    selectmode=tk.SINGLE
)

history_scrollbar.config(command=history_list.yview)

history_scrollbar.pack(side="right", fill="y")
history_list.pack(side="left", fill="both", expand=True)

history_list.bind(
    "<<ListboxSelect>>",
    use_history_password
)
root.mainloop()
