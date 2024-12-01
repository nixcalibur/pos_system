from tkinter import messagebox, simpledialog


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
