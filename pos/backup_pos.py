from functools import partial
import tkinter as tk
from tkinter import ttk
from tkmacosx import Button
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import datetime
import sqlite3

class POSSystem:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("POS System")
        self.parent.geometry("1366x768")

        # Initialize database connection
        self.conn = sqlite3.connect('pos_system.db')
        self.cursor = self.conn.cursor()
        self.initialize_db()

        # Dictionary to track order quantities and totals
        self.order_summary = {}

        #Login Page
        self.login_frame = tk.Frame(self.parent)  # Initialize login_frame
        self.login_frame.pack(expand=True)
        tk.Label(self.login_frame, text="Login", font=("Times New Roman", 32)).pack(pady=20)
        # Username entry
        tk.Label(self.login_frame, text="Username:", font=("Arial", 14)).pack(pady=5)
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 14), width=25)
        self.username_entry.pack(pady=5)
        # Password entry
        tk.Label(self.login_frame, text="Password:", font=("Arial", 14)).pack(pady=5)
        self.password_entry = tk.Entry(self.login_frame, font=("Arial", 14), width=25, show="*")
        self.password_entry.pack(pady=5)
        # Login button
        tk.Button(self.login_frame, text="Login", font=("Arial", 14), command=self.validate_login).pack(pady=20)
        # Register
        tk.Button(self.login_frame, text="Register", command=self.register_user, font=("Arial", 14)).pack(pady=10)

        # Main Management Frame (to be shown after login)
        self.main_frame = tk.Frame(self.parent)

        # Top display bar within main_frame
        self.top_display_bar = tk.Frame(self.main_frame, bg="lightblue", height=70)
        self.top_display_bar.pack(side="top", fill="x")

        # Clock
        self.time_label = tk.Label(self.top_display_bar, font=("Times New Roman italic", 18), bg="lightblue", fg="black")
        self.time_label.pack(side="right", padx=10)
        
        # System title label
        self.top_label = tk.Label(self.top_display_bar, text="POS System - Nik", font=("Times New Roman bold", 20), bg="lightblue", fg="black")
        self.top_label.pack(side="left", padx=20)
        
        # Configure the style for vertical tabs
        style = ttk.Style()
        style.configure('lefttab.TNotebook', tabposition='wn')

        # Main notebook with "Menu," "Employees," and "Settings" tabs
        sidebar = ttk.Notebook(self.main_frame, style='lefttab.TNotebook')
        sidebar.pack(side="left", fill="both", expand=True, pady=20)

        # Create frames for the main tabs
        menu_tab = ttk.Frame(sidebar)
        employees_tab = ttk.Frame(sidebar)
        sales_tab = ttk.Frame(sidebar)
        product_tab = ttk.Frame(sidebar)
        settings_tab = ttk.Frame(sidebar)
        sidebar.add(menu_tab, text="Menu")
        sidebar.add(employees_tab, text="Employees")
        sidebar.add(product_tab, text="Products")
        sidebar.add(sales_tab, text="Sales")
        sidebar.add(settings_tab, text="Settings")

        # Employees Tab Coming Soon
        cversion = tk.Label(employees_tab, text="Coming Soon", font=("Times New Roman italic", 24))
        cversion.pack()

        # Nested notebook inside the "Menu" tab
        self.menu_notebook = ttk.Notebook(menu_tab)
        self.menu_notebook.pack(expand=True, fill="both")

        # Tab menu
        self.tab_main = ttk.Frame(self.menu_notebook)
        self.tab_sides = ttk.Frame(self.menu_notebook)
        self.tab_drinks = ttk.Frame(self.menu_notebook)
        self.menu_notebook.add(self.tab_main, text="Main")
        self.menu_notebook.add(self.tab_sides, text="Sides")
        self.menu_notebook.add(self.tab_drinks, text="Drinks")

        # Load menu items dynamically from the database
        self.load_menu_items()

        # Add Refresh Menu Button
        self.refresh_menu_btn = Button(menu_tab, text="Refresh Menu", command=self.load_menu_items, font=("Arial", 14), width=110, height=40)
        self.refresh_menu_btn.pack(pady=10)

        # Configure Treeview Style
        style = ttk.Style(self.parent)
        style.configure("Treeview", font=("Times New Roman", 18))  
        style.configure("Treeview.Heading", font=("Times New Roman", 16, "bold"))  

        # Sales History Treeview 
        self.sales_history_label = tk.Label(sales_tab, text="Sales History", font=("Times New Roman", 28))
        self.sales_history_label.pack(pady=10)

        self.sales_tree = ttk.Treeview(sales_tab, columns=("ID", "Items", "Total Price", "Date"), show="headings", height=20)
        self.sales_tree.heading("ID", text="Sale ID")
        self.sales_tree.heading("Items", text="Items Sold")
        self.sales_tree.heading("Total Price", text="Total Price")
        self.sales_tree.heading("Date", text="Sale Date")

        self.sales_tree.column("ID", anchor="center", width=80)
        self.sales_tree.column("Items", anchor="w", width=300)
        self.sales_tree.column("Total Price", anchor="center", width=100)
        self.sales_tree.column("Date", anchor="center", width=150)
        self.sales_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.sales_tree.bind("<Double-1>", self.open_sale_detail)

        # Load sales history at startup
        self.load_sales_history()

        # Product List Treeview in the "Products" Tab
        self.product_list_label = tk.Label(product_tab, text="Product List", font=("Times New Roman", 28))
        self.product_list_label.pack(pady=10)
        self.product_tree = ttk.Treeview(product_tab, columns=("ID", "Name", "Price", "Category"), show="headings", height=20)
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Price", text="Price")
        self.product_tree.heading("Category", text="Category")
        self.product_tree.column("ID", anchor="center", width=50)
        self.product_tree.column("Name", anchor="w", width=200)
        self.product_tree.column("Price", anchor="center", width=100)
        self.product_tree.column("Category", anchor="center", width=100)
        self.product_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Add Product Button
        self.add_product_btn = Button(product_tab, text="Add Product", command=self.add_product, font=("Arial", 14), fg='green',width=150, height=50)
        self.add_product_btn.pack(pady=10,side="left")

        # Delete Product Button
        self.delete_product_btn = Button(product_tab, text="Delete Product", command=self.delete_product, font=("Arial", 14), width=150, height=50)
        self.delete_product_btn.pack(pady=10, side="right")

        # Refresh Button for Product List
        self.refresh_product_btn = Button(product_tab, text="Refresh Product List", command=self.load_product_list, font=("Arial", 14))
        self.refresh_product_btn.pack(pady=10)

        # Load product list at startup
        self.load_product_list()

        # Refresh button to reload sales history
        self.refresh_button = Button(sales_tab, text="Refresh Sales History", command=self.load_sales_history, font=("Arial", 14))
        self.refresh_button.pack(pady=10)

        #order list
        self.order_list_frame = tk.Frame(self.main_frame)
        self.order_list_frame.pack(side="right", fill="y", padx=10, pady=10)
        self.order_list_frame = tk.Frame(self.main_frame)
        self.order_list_frame.pack(side="right", fill="y", padx=10, pady=10)
        self.order_list_label = tk.Label(self.order_list_frame, text="Order List", font=("Times New Roman", 20))
        self.order_list_label.pack(pady=10)

        # Treeview for displaying items in a grid format
        self.order_tree = ttk.Treeview(self.order_list_frame, columns=("Item", "Quantity", "Total"), show="headings", height=20)
        self.order_tree.heading("Item", text="Item")
        self.order_tree.heading("Quantity", text="Quantity")
        self.order_tree.heading("Total", text="Total Price")
        self.order_tree.column("Item", anchor="w", width=150)
        self.order_tree.column("Quantity", anchor="center", width=100)
        self.order_tree.column("Total", anchor="e", width=100)
        self.order_tree.pack()

        # Subtotal, Tax, Discount, and Total stuff
        self.total_price_label = tk.Label(self.order_list_frame, text="Subtotal: $0.00", font=("Arial", 16))
        self.total_price_label.pack(pady=5)
        self.tax_label = tk.Label(self.order_list_frame, text="Tax (4%): $0.00", font=("Arial", 14))
        self.tax_label.pack(pady=5)
        self.discount_label = tk.Label(self.order_list_frame, text="Discount: $0.00", font=("Arial", 14))
        self.discount_label.pack(pady=5)
        self.final_total_label = tk.Label(self.order_list_frame, text="Total: $0.00", font=("Arial bold", 20), fg="light green")
        self.final_total_label.pack(pady=10)
        self.total_price = 0.0
        self.tax_rate = 0.04  # 4% tax rate
        self.discount = 0.0

        # Check out button
        self.checkout_btn = Button(self.order_list_frame, bg="green", relief="groove", text="Check Out", fg="white", font=("Arial bold", 24), width=200, height=80, command=self.checkout)
        self.checkout_btn.pack(side="right", padx=5, pady=10)

        # Cancel button
        self.cancel_btn = Button(self.order_list_frame, bg="red", relief="groove", text="Cancel", fg="white", font=("Arial bold", 24), width=200, height=80, command=self.cancel_order)
        self.cancel_btn.pack(side="left", padx=5, pady=10)

        # Start the clock update
        self.tick()

        # Settings stuff
        cversion = tk.Label(settings_tab, text="Version\n0.5", font=("Times New Roman italic", 20))
        cversion.pack(side="bottom")

        lang = tk.Label(settings_tab, text="Language: English", font=("Times New Roman", 20))
        lang.pack()
                
    def open_main_page(self):  # Hide the login frame and show the main frame
        self.login_frame.pack_forget()
        self.main_frame.pack(expand=True, fill="both")

    def tick(self): # Update the time label with the current time
        self.time_label.config(text=str(datetime.datetime.now()).rpartition('.')[0])
        self.parent.after(1000, self.tick)
    
    def validate_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Input Error", "Please fill in both username and password.")
            return
    
        # Check against the database
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()

        if user:
            self.login_frame.destroy()  # Remove login frame
            self.open_main_page()  # Open the main page
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


    def add_order(self, item_name, price): 
        # Update order quantity and total in order_summary dictionary
        if item_name in self.order_summary:
            self.order_summary[item_name]['quantity'] += 1
            self.order_summary[item_name]['total'] += price
        else:
            self.order_summary[item_name] = {'quantity': 1, 'total': price}

        # Refresh the order list display
        self.update_order_treeview()

        # Update the total price
        self.total_price += price
        self.update_totals()

    def update_order_treeview(self):
        # Clear the treeview and display updated order list with quantities
        self.order_tree.delete(*self.order_tree.get_children())
        for item_name, details in self.order_summary.items():
            quantity = details['quantity']
            total_price = details['total']
            self.order_tree.insert("", "end", values=(item_name, quantity, f"${total_price:.2f}"))

    def update_totals(self):
        # Calculate tax, discount, and final total
        tax = self.total_price * self.tax_rate
        total_with_tax = self.total_price + tax
        final_total = total_with_tax - self.discount

        # Update labels with calculated values
        self.total_price_label.config(text=f"Subtotal: ${self.total_price:.2f}")
        self.tax_label.config(text=f"Tax (4%): ${tax:.2f}")
        self.discount_label.config(text=f"Discount: ${self.discount:.2f}")
        self.final_total_label.config(text=f"Total: ${final_total:.2f}")

    def checkout(self):
        if self.total_price > 0:
            money_given = simpledialog.askfloat("Payment", "Enter amount given:", minvalue=0.0)
            if money_given is None:
                return

            tax = self.total_price * self.tax_rate
            total_with_tax = self.total_price + tax
            final_total = total_with_tax - self.discount
            change = money_given - final_total

            if change < 0:
                messagebox.showwarning("Insufficient Funds", "The amount given is less than the total.")
            else:
                messagebox.showinfo("Change", f"Total: ${final_total:.2f}\nAmount Given: ${money_given:.2f}\nChange: ${change:.2f}")

                # Save the sale in the database
                self.cursor.execute('''
                    INSERT INTO sales (total_amount, amount_paid, change) VALUES (?, ?, ?)
                ''', (final_total, money_given, change))
                sale_id = self.cursor.lastrowid  # Get the ID of the new sale

                # Save each item in the sale to the sale_items table
                for item_name, details in self.order_summary.items():
                    quantity = details['quantity']
                    price = details['total']
                    self.cursor.execute('''
                        INSERT INTO sale_items (sale_id, item_name, quantity, price)
                        VALUES (?, ?, ?, ?)
                    ''', (sale_id, item_name, quantity, price))

                self.conn.commit()
                self.cancel_order()


    def cancel_order(self):
        # Clear the order list, reset the order summary and totals
        self.order_tree.delete(*self.order_tree.get_children())
        self.order_summary.clear()
        self.total_price = 0.0
        self.discount = 0.0
        self.update_totals()

    def initialize_db(self):
        # Create the `users` table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        # default admin credentials
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
        ''', ("admin", "password"))

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_amount REAL NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                amount_paid REAL DEFAULT 0,
                change REAL DEFAULT 0
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id)
            )
        ''')

        # Commit changes
        self.conn.commit()


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

    
    def load_sales_history(self):
        # Retrieve all sales with details
        self.cursor.execute('''
            SELECT sales.id, 
                GROUP_CONCAT(sale_items.item_name || " (x" || sale_items.quantity || ")", ', ') AS items, 
                sales.total_amount, 
                sales.sale_date
            FROM sales
            JOIN sale_items ON sales.id = sale_items.sale_id
            GROUP BY sales.id
            ORDER BY sales.sale_date DESC
        ''')
        sales = self.cursor.fetchall()

        # Clear the existing sales data in the Treeview
        self.sales_tree.delete(*self.sales_tree.get_children())

        # Populate the sales Treeview
        for sale_id, items, total_amount, sale_date in sales:
            self.sales_tree.insert("", "end", values=(sale_id, items, f"${total_amount:.2f}", sale_date))

    def open_sale_detail(self, event):
        selected_item = self.sales_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No sale selected!")
            return

        # Get the sale ID from the selected row
        sale_id = self.sales_tree.item(selected_item[0])["values"][0]

        # Query the full sale details from the database
        self.cursor.execute('''
            SELECT sales.id, 
                GROUP_CONCAT(sale_items.item_name || " (x" || sale_items.quantity || ")", ', ') AS items, 
                sales.total_amount, 
                sales.amount_paid, 
                sales.change, 
                sales.sale_date
            FROM sales
            JOIN sale_items ON sales.id = sale_items.sale_id
            WHERE sales.id = ?
            GROUP BY sales.id
        ''', (sale_id,))
        result = self.cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Sale details not found!")
            return

        sale_id, items, total_price, amount_paid, change, sale_date = result

        # Create a new window for the sale details
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Sale Details - ID: {sale_id}")
        detail_window.geometry("500x500")

        # Display the sale details
        tk.Label(detail_window, text=f"Sale ID: {sale_id}", font=("Arial", 16)).pack(pady=10)
        tk.Label(detail_window, text=f"Date: {sale_date}", font=("Arial", 14)).pack(pady=5)
        tk.Label(detail_window, text=f"Total Price: ${total_price:.2f}", font=("Arial", 14)).pack(pady=5)
        tk.Label(detail_window, text=f"Amount Paid: ${amount_paid:.2f}", font=("Arial", 14)).pack(pady=5)
        tk.Label(detail_window, text=f"Change: ${change:.2f}", font=("Arial", 14)).pack(pady=5)
        tk.Label(detail_window, text="Items Sold:", font=("Arial", 14)).pack(pady=10)

        # Textbox to display items in a readable format
        items_textbox = tk.Text(detail_window, font=("Arial", 12), width=50, height=10, wrap="word")
        items_textbox.insert("1.0", items)
        items_textbox.config(state="disabled")
        items_textbox.pack(pady=10)

        # Button to save the sale details as an image
        save_button = tk.Button(
            detail_window, text="Save as Image", font=("Arial", 14),
            command=lambda: self.save_sale_as_image(sale_id, items, total_price, amount_paid, change, sale_date)
        )
        save_button.pack(pady=10)


    def save_sale_as_image(self, sale_id, items, total_price, amount_paid, change, sale_date):
        image_width = 500
        image_height = 500
        padding = 20

        img = Image.new("RGB", (image_width, image_height), "white")
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)

        # Write the sale details onto the image
        y_position = padding
        draw.text((padding, y_position), f"Sale ID: {sale_id}", font=font, fill="black")
        y_position += 30
        draw.text((padding, y_position), f"Date: {sale_date}", font=font, fill="black")
        y_position += 30
        draw.text((padding, y_position), f"Total Price: {total_price}", font=font, fill="black")
        y_position += 30
        draw.text((padding, y_position), f"Amount Paid: {amount_paid}", font=font, fill="black")
        y_position += 30
        draw.text((padding, y_position), f"Change: {change}", font=font, fill="black")
        y_position += 40
        draw.text((padding, y_position), "Items Sold:", font=font, fill="black")
        y_position += 30

        lines = items.split(", ")
        for line in lines:
            draw.text((padding, y_position), line, font=font, fill="black")
            y_position += 30

        import os
        output_dir = "sales_images"
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
        filename = os.path.join(output_dir, f"sale_{sale_id}.png")
        img.save(filename)
        messagebox.showinfo("Success", f"Sale details saved as '{filename}'!")

    
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

    # Close the database connection when the application is closed
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = POSSystem(root)
    root.mainloop()    