import tkinter as tk
from tkinter import messagebox
import sqlite3

class InventoryManagementSystem:
    def __init__(self):
        self.conn = sqlite3.connect('inventory_management_system.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                part_id INTEGER PRIMARY KEY,
                part_name TEXT,
                quantity INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS finance (
                part_id INTEGER,
                total_cost REAL,
                FOREIGN KEY(part_id) REFERENCES inventory(part_id)
            )
        ''')

        self.conn.commit()

    def check_inventory_availability(self, part_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT quantity FROM inventory WHERE part_id = ?', (part_id,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return 0

    def add_parts_amount(self, part_id, part_name, quantity):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM inventory WHERE part_id = ?', (part_id,))
        result = cursor.fetchone()

        if result:
            new_quantity = result[2] + quantity
            cursor.execute('UPDATE inventory SET quantity = ? WHERE part_id = ?', (new_quantity, part_id))
        else:
            cursor.execute('INSERT INTO inventory (part_id, part_name, quantity) VALUES (?, ?, ?)', (part_id, part_name, quantity))

        self.conn.commit()

    def update_amount_on_finance(self, part_id, total_cost):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO finance (part_id, total_cost) VALUES (?, ?)', (part_id, total_cost))
        self.conn.commit()

    def calculate_total_amount(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(total_cost) FROM finance')
        result = cursor.fetchone()
        return result[0] if result[0] else 0

    def update_finance(self):
        total_amount = self.calculate_total_amount()
        cursor = self.conn.cursor()
        cursor.execute('UPDATE finance SET total_cost = ?', (total_amount,))
        self.conn.commit()


class InventoryManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")

        self.inventory_system = InventoryManagementSystem()

        self.part_id_label = tk.Label(root, text="Part ID:")
        self.part_id_entry = tk.Entry(root)

        self.part_name_label = tk.Label(root, text="Part Name:")
        self.part_name_entry = tk.Entry(root)

        self.quantity_label = tk.Label(root, text="Quantity:")
        self.quantity_entry = tk.Entry(root)

        self.check_availability_button = tk.Button(root, text="Check Availability", command=self.check_availability)
        self.add_parts_button = tk.Button(root, text="Add Parts", command=self.add_parts)
        self.update_finance_button = tk.Button(root, text="Update Finance", command=self.update_finance)

        self.part_id_label.pack(pady=10)
        self.part_id_entry.pack(pady=5)
        self.part_name_label.pack(pady=10)
        self.part_name_entry.pack(pady=5)
        self.quantity_label.pack(pady=10)
        self.quantity_entry.pack(pady=5)
        self.check_availability_button.pack(pady=10)
        self.add_parts_button.pack(pady=10)
        self.update_finance_button.pack(pady=10)

    def check_availability(self):
        part_id = self.part_id_entry.get()

        if not part_id:
            messagebox.showerror("Error", "Part ID is required.")
            return

        try:
            part_id = int(part_id)
        except ValueError:
            messagebox.showerror("Error", "Invalid Part ID. Please enter a number.")
            return

        availability = self.inventory_system.check_inventory_availability(part_id)
        messagebox.showinfo("Availability", f"Available Quantity: {availability}")

    def add_parts(self):
        part_id = self.part_id_entry.get()
        part_name = self.part_name_entry.get()
        quantity_str = self.quantity_entry.get()

        if not part_id or not part_name or not quantity_str:
            messagebox.showerror("Error", "Part ID, Part Name, and Quantity are required.")
            return

        try:
            part_id = int(part_id)
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid Part ID or Quantity. Please enter numbers.")
            return

        self.inventory_system.add_parts_amount(part_id, part_name, quantity)
        messagebox.showinfo("Success", "Parts added successfully.")

        # Clear the entry fields after adding parts
        self.part_id_entry.delete(0, tk.END)
        self.part_name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def update_finance(self):
        self.inventory_system.update_finance()
        messagebox.showinfo("Success", "Finance updated successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManagementApp(root)
    root.mainloop()
