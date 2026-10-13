import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
DATABASE = "bmi_records.db"

def initialize_database():
    """Create the database and table if they don't already exist."""
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date_time TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not initialize the database:\n{error}"
        )


def save_record(user_name, weight, height, bmi, category):
    """Save a BMI record to SQLite."""
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO bmi_records
            (user_name, weight, height, bmi, category, date_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_name,
            weight,
            height,
            bmi,
            category,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        connection.close()

        return True

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not save the BMI record:\n{error}"
        )
        return False


def get_users():
    """Return all saved user names."""
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT DISTINCT user_name
            FROM bmi_records
            ORDER BY user_name
        """)

        users = [row[0] for row in cursor.fetchall()]

        connection.close()
        return users

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not read users from the database:\n{error}"
        )
        return []


def get_user_records(user_name):
    """Return BMI history for a specific user."""
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT bmi, date_time
            FROM bmi_records
            WHERE user_name = ?
            ORDER BY date_time
        """, (user_name,))

        records = cursor.fetchall()

        connection.close()
        return records

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not read BMI history:\n{error}"
        )
        return []

def calculate_bmi(weight, height):
    """
    Calculate BMI.

    Weight is in kilograms.
    Height is in centimetres.
    """
    height_meters = height / 100
    bmi = weight / (height_meters ** 2)

    return bmi


def classify_bmi(bmi):
    """Return the BMI category."""
    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal"

    elif bmi < 30:
        return "Overweight"

    else:
        return "Obese"

def calculate_and_save():
    """Read input, calculate BMI, display result and save it."""
    user_name = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()

    # Validate name
    if not user_name:
        messagebox.showwarning(
            "Input Error",
            "Please enter a user name."
        )
        return

    try:
        weight = float(weight_text)
        height = float(height_text)

    except ValueError:
        messagebox.showwarning(
            "Input Error",
            "Weight and height must be valid numbers."
        )
        return

    if weight <= 0:
        messagebox.showwarning(
            "Input Error",
            "Weight must be greater than zero."
        )
        return

    if height <= 0:
        messagebox.showwarning(
            "Input Error",
            "Height must be greater than zero."
        )
        return

    bmi = calculate_bmi(weight, height)
    category = classify_bmi(bmi)

    # Display result
    result_label.config(
        text=f"BMI: {bmi:.2f}\nCategory: {category}"
    )

    if category == "Underweight":
        result_label.config(
            fg="#e67e22",
            bg="#fff3e0"
        )

    elif category == "Normal":
        result_label.config(
            fg="#27ae60",
            bg="#e8f8f0"
        )

    elif category == "Overweight":
        result_label.config(
            fg="#f39c12",
            bg="#fff8e1"
        )

    else:
        result_label.config(
            fg="#e74c3c",
            bg="#fdecea"
        )
    if save_record(user_name, weight, height, bmi, category):
        messagebox.showinfo(
            "Success",
            "BMI record saved successfully."
        )

        update_user_list()

        user_combo.set(user_name)

def update_user_list():
    """Refresh the user dropdown."""
    users = get_users()
    user_combo["values"] = users

def show_history():
    """Display BMI history for the selected user."""
    user_name = user_combo.get().strip()

    if not user_name:
        messagebox.showwarning(
            "User Required",
            "Please select a user."
        )
        return

    records = get_user_records(user_name)

    if not records:
        messagebox.showinfo(
            "No Records",
            f"No BMI records found for {user_name}."
        )
        return

    for item in history_tree.get_children():
        history_tree.delete(item)

    # Add records to table
    for bmi, date_time in records:
        category = classify_bmi(bmi)

        history_tree.insert(
            "",
            tk.END,
            values=(
                date_time,
                f"{bmi:.2f}",
                category
            )
        )


def show_graph():
    """Display a BMI trend graph for the selected user."""
    user_name = user_combo.get().strip()

    if not user_name:
        messagebox.showwarning(
            "User Required",
            "Please select a user."
        )
        return

    records = get_user_records(user_name)

    if not records:
        messagebox.showinfo(
            "No Records",
            f"No BMI records found for {user_name}."
        )
        return

    dates = [
        datetime.strptime(record[1], "%Y-%m-%d %H:%M:%S")
        for record in records
    ]

    bmi_values = [record[0] for record in records]

    plt.figure(figsize=(9, 5))

    plt.plot(
        dates,
        bmi_values,
        marker="o",
        linewidth=2,
        color="royalblue"
    )

    plt.axhspan(
        18.5,
        24.9,
        color="green",
        alpha=0.10,
        label="Normal BMI range"
    )

    plt.axhline(
        18.5,
        color="orange",
        linestyle="--",
        alpha=0.7
    )

    plt.axhline(
        25,
        color="green",
        linestyle="--",
        alpha=0.7
    )

    plt.axhline(
        30,
        color="red",
        linestyle="--",
        alpha=0.7
    )

    plt.title(f"BMI Trend - {user_name}")
    plt.xlabel("Date")
    plt.ylabel("BMI")

    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()

root = tk.Tk()
root.title("BMI Calculator")
root.geometry("650x650")
root.resizable(False, False)

# Main heading
title_label = tk.Label(
    root,
    text="BMI Calculator",
    font=("Arial", 24, "bold"),
    pady=15
)
title_label.pack
input_frame = tk.LabelFrame(
    root,
    text="BMI Information",
    font=("Arial", 12, "bold"),
    padx=20,
    pady=15
)

input_frame.pack(
    padx=20,
    pady=10,
    fill="x"
)


# Name
tk.Label(
    input_frame,
    text="User Name:"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=8,
    sticky="w"
)

name_entry = tk.Entry(
    input_frame,
    width=30
)

name_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=8
)

tk.Label(
    input_frame,
    text="Weight (kg):"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=8,
    sticky="w"
)

weight_entry = tk.Entry(
    input_frame,
    width=30
)

weight_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=8
)

tk.Label(
    input_frame,
    text="Height (cm):"
).grid(
    row=2,
    column=0,
    padx=10,
    pady=8,
    sticky="w"
)

height_entry = tk.Entry(
    input_frame,
    width=30
)

height_entry.grid(
    row=2,
    column=1,
    padx=10,
    pady=8
)

calculate_button = tk.Button(
    input_frame,
    text="Calculate BMI",
    command=calculate_and_save,
    bg="#3498db",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=15,
    pady=5
)

calculate_button.grid(
    row=3,
    column=0,
    columnspan=2,
    pady=15
)

result_label = tk.Label(
    root,
    text="BMI: --\nCategory: --",
    font=("Arial", 16, "bold"),
    width=30,
    pady=12,
    bg="#eeeeee"
)

result_label.pack(pady=10)
history_frame = tk.LabelFrame(
    root,
    text="BMI History",
    font=("Arial", 12, "bold"),
    padx=15,
    pady=10
)

history_frame.pack(
    padx=20,
    pady=10,
    fill="both",
    expand=True
)

tk.Label(
    history_frame,
    text="Select User:"
).pack(side="left", padx=5)

user_combo = ttk.Combobox(
    history_frame,
    width=20,
    state="readonly"
)

user_combo.pack(side="left", padx=5)
history_button = tk.Button(
    history_frame,
    text="View History",
    command=show_history
)

history_button.pack(side="left", padx=5)
graph_button = tk.Button(
    history_frame,
    text="Show BMI Graph",
    command=show_graph,
    bg="#9b59b6",
    fg="white"
)

graph_button.pack(side="left", padx=5)
columns = (
    "Date",
    "BMI",
    "Category"
)

history_tree = ttk.Treeview(
    history_frame,
    columns=columns,
    show="headings",
    height=8
)

history_tree.heading(
    "Date",
    text="Date"
)

history_tree.heading(
    "BMI",
    text="BMI"
)

history_tree.heading(
    "Category",
    text="Category"
)

history_tree.column(
    "Date",
    width=160
)

history_tree.column(
    "BMI",
    width=80
)

history_tree.column(
    "Category",
    width=120
)

history_tree.pack(
    side="bottom",
    pady=10
)

initialize_database()
update_user_list()

root.mainloop()
