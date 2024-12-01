import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageDraw, ImageFont


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