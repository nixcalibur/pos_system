from functools import partial
import tkinter as tk
from tkinter import ttk
from tkmacosx import Button
from tkinter import simpledialog, messagebox
import sqlite3

def load_menu_items(self):
    # Fetch menu items from the database and organize by category
    self.cursor.execute("SELECT name, price, category FROM menu_items ORDER BY category, name")
    menu_items = self.cursor.fetchall()

    # Clear existing buttons in menu tabs
    for tab in [self.tab_main, self.tab_sides, self.tab_drinks]:
        for widget in tab.winfo_children():
            widget.destroy()

    columns_per_row = 3  # Adjustable

    # Add menu items to corresponding tabs
    category_tabs = {
        "main": self.tab_main,
        "sides": self.tab_sides,
        "drinks": self.tab_drinks
    }

    # Organize buttons in a grid layout
    for category, parent_tab in category_tabs.items():
        # Filter items for the current category
        items_in_category = [(name, price) for (name, price, item_category) in menu_items if item_category.lower() == category]
        for index, (name, price) in enumerate(items_in_category):
            row = index // columns_per_row
            col = index % columns_per_row
            Button(
                parent_tab,
                text=f"{name}\n${price:.2f}",
                command=partial(self.add_order, name, price),
                font=("Arial", 20),
                width=100,
                height=70
            ).grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Configure column weights to make buttons expand evenly
        for col in range(columns_per_row):
            parent_tab.columnconfigure(col, weight=1)

def add_product(self):
    #if the window is already opened
    if hasattr(self, "add_product_window_instance") and self.add_product_window_instance.winfo_exists():
        self.add_product_window_instance.lift()  # Bring it to the front
        return
    
    # Create a new window for adding products
    self.add_product_window_instance = tk.Toplevel(self.parent)
    self.add_product_window_instance.title("Add Product")
    self.add_product_window_instance.geometry("350x230")
    self.add_product_window_instance.resizable(False, False)

    # Product Name Label and Entry
    tk.Label(self.add_product_window_instance, text="Product Name:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    self.product_name_entry = tk.Entry(self.add_product_window_instance, font=("Arial", 14), width=25)
    self.product_name_entry.grid(row=0, column=1, padx=10, pady=10)

    # Product Price Label and Entry
    tk.Label(self.add_product_window_instance, text="Product Price:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    self.product_price_entry = tk.Entry(self.add_product_window_instance, font=("Arial", 14), width=25)
    self.product_price_entry.grid(row=1, column=1, padx=10, pady=10)

    # Category Label and Dropdown
    tk.Label(self.add_product_window_instance, text="Category:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    self.category_var = tk.StringVar()
    self.category_dropdown = ttk.Combobox(self.add_product_window_instance, textvariable=self.category_var, font=("Arial", 14), state="readonly", width=22)
    self.category_dropdown['values'] = ["Main", "Sides", "Drinks"]  # Add categories as needed
    self.category_dropdown.grid(row=2, column=1, padx=10, pady=10)

    # Add Product Button
    self.add_product_btn = Button(self.add_product_window_instance, text="Save Product", command=self.save_product_window, font=("Arial", 14), width=150, height=40, bg="green", fg="white")
    self.add_product_btn.grid(row=3, column=0, columnspan=2, pady=20)

def save_product_window(self):
    # Retrieve input values
    product_name = self.product_name_entry.get().strip()
    product_price = self.product_price_entry.get().strip()
    category = self.category_var.get()

    # Validate inputs
    if not product_name or not product_price or not category:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return

    try:
        product_price = float(product_price)  # Validate price as a float
    except ValueError:
        messagebox.showwarning("Input Error", "Product price must be a number.")
        return

    # Insert the product into the database
    try:
        self.cursor.execute('''
            INSERT INTO menu_items (name, price, category)
            VALUES (?, ?, ?)
        ''', (product_name, product_price, category))
        self.conn.commit()
        messagebox.showinfo("Success", "Product added successfully!")
        self.load_product_list()  # Refresh the product list in the Treeview

        # Close the window after successful addition
        if hasattr(self, "add_product_window_instance") and self.add_product_window_instance.winfo_exists():
            self.add_product_window_instance.destroy()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Product '{product_name}' already exists.")

def delete_product(self):
    # Get selected product from the Treeview
    selected_item = self.product_tree.selection()
    if not selected_item:
        messagebox.showwarning("Delete Product", "No product selected!")
        return

    try:
        # Get the product ID from the selected row
        product_id = self.product_tree.item(selected_item[0], 'values')[0]

        # Confirm deletion
        confirm = messagebox.askyesno("Delete Product", "Are you sure you want to delete this product?")
        if confirm:
            # Delete the product from the database
            self.cursor.execute('DELETE FROM menu_items WHERE id = ?', (product_id,))
            self.conn.commit()

            messagebox.showinfo("Success", "Product deleted successfully!")
            self.load_product_list()  # Refresh the product list

    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete product: {e}")

def load_product_list(self):
    # Fetch all products from the menu_items table
    self.cursor.execute("SELECT id, name, price, category FROM menu_items ORDER BY id ASC")
    products = self.cursor.fetchall()

    # Clear the Treeview
    self.product_tree.delete(*self.product_tree.get_children())

    # Populate the Treeview with products
    for product in products:
        product_id, name, price, category = product
        self.product_tree.insert("", "end", values=(product_id, name, f"${price:.2f}", category))
