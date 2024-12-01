import sqlite3
from tkinter import messagebox
import tkinter as tk

def validate_login(self):
    username = self.username_entry.get().strip()
    password = self.password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Input Error", "Please fill in both username and password.")
        return

    self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = self.cursor.fetchone()

    if user:
        self.login_frame.destroy()
        self.open_main_page()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def register_user(self):
    register_window = tk.Toplevel(self.parent)
    register_window.title("Register")
    register_window.geometry("350x200")
    register_window.resizable(False, False)

    tk.Label(register_window, text="Username:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    username_entry = tk.Entry(register_window, font=("Arial", 14), width=25)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(register_window, text="Password:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    password_entry = tk.Entry(register_window, font=("Arial", 14), width=25, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    def save_user():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        # Validate input
        if not username or not password:
            messagebox.showerror("Input Error", "Please fill in both username and password.")
            return

        try:
            # Insert new user into the database
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            messagebox.showinfo("Registration Successful", "User registered successfully!")
            register_window.destroy()  # Close registration window
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
    
    def close_register_window():
        register_window.destroy()

    tk.Button(register_window, text="Close", command=close_register_window, font=("Arial", 16)).grid(row=2, column=0, padx=10, pady=20, sticky="ew")
    tk.Button(register_window, text="Register", command=save_user, font=("Arial", 16)).grid(row=2, column=1, pady=20)