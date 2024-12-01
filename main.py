import tkinter as tk
from tkinter import ttk
from tkmacosx import Button
import sqlite3

from pos.db import initialize_db
from pos.login import validate_login, register_user
from pos.orders import add_order, update_order_treeview, update_totals, checkout, cancel_order
from pos.sales import load_sales_history, open_sale_detail, save_sale_as_image
from pos.products import load_menu_items, add_product, save_product_window, delete_product, load_product_list
from pos.others import open_main_page, tick, __del__

class POSSystem:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("POS System")
        self.parent.geometry("1366x768")

        # Initialize database connection
        self.conn = sqlite3.connect('pos_system.db')
        self.cursor = self.conn.cursor()

        # Bind external methods to the class instance
        self.initialize_db = lambda: initialize_db(self)
        self.validate_login = lambda: validate_login(self)
        self.register_user = lambda: register_user(self)
        self.add_order = lambda item_name, price: add_order(self, item_name, price)
        self.update_order_treeview = lambda: update_order_treeview(self)
        self.update_totals = lambda: update_totals(self)
        self.checkout = lambda: checkout(self)
        self.cancel_order = lambda: cancel_order(self)
        self.load_sales_history = lambda: load_sales_history(self)
        self.open_sale_detail = lambda event: open_sale_detail(self, event)
        self.save_sale_as_image = lambda sale_id, items, total_price, amount_paid, change, sale_date: save_sale_as_image(
            self, sale_id, items, total_price, amount_paid, change, sale_date
        )
        self.load_menu_items = lambda: load_menu_items(self)
        self.add_product = lambda: add_product(self)
        self.save_product_window = lambda: save_product_window(self)
        self.delete_product = lambda: delete_product(self)
        self.load_product_list = lambda: load_product_list(self)
        self.open_main_page = lambda: open_main_page(self)
        self.tick = lambda: tick(self)

        # Initialize the database
        self.initialize_db()

        # Dictionary to track order quantities and totals
        self.order_summary = {}

        # Login Page
        self.login_frame = tk.Frame(self.parent)  # Initialize login_frame
        self.login_frame.pack(expand=True)
        tk.Label(self.login_frame, text="Login", font=("Times New Roman", 32)).pack(pady=20)
        tk.Label(self.login_frame, text="Username:", font=("Arial", 14)).pack(pady=5)
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 14), width=25)
        self.username_entry.pack(pady=5)
        tk.Label(self.login_frame, text="Password:", font=("Arial", 14)).pack(pady=5)
        self.password_entry = tk.Entry(self.login_frame, font=("Arial", 14), width=25, show="*")
        self.password_entry.pack(pady=5)
        tk.Button(self.login_frame, text="Login", font=("Arial", 14), command=self.validate_login).pack(pady=20)
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
        tk.Label(employees_tab, text="Coming Soon", font=("Times New Roman italic", 24)).pack()

        # Nested notebook inside the "Menu" tab
        self.menu_notebook = ttk.Notebook(menu_tab)
        self.menu_notebook.pack(expand=True, fill="both")

        self.tab_main = ttk.Frame(self.menu_notebook)
        self.tab_sides = ttk.Frame(self.menu_notebook)
        self.tab_drinks = ttk.Frame(self.menu_notebook)
        self.menu_notebook.add(self.tab_main, text="Main")
        self.menu_notebook.add(self.tab_sides, text="Sides")
        self.menu_notebook.add(self.tab_drinks, text="Drinks")

        # Load menu items dynamically from the database
        self.load_menu_items()

        # Add Refresh Menu Button
        Button(menu_tab, text="Refresh Menu", command=self.load_menu_items, font=("Arial", 14), width=110, height=40).pack(pady=10)

        # Configure Treeview Style
        style = ttk.Style(self.parent)
        style.configure("Treeview", font=("Times New Roman", 18))
        style.configure("Treeview.Heading", font=("Times New Roman", 16, "bold"))

        # Sales History Treeview
        tk.Label(sales_tab, text="Sales History", font=("Times New Roman", 28)).pack(pady=10)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = POSSystem(root)
    root.mainloop()