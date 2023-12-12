import tkinter as tk
from tkinter import messagebox
import sqlite3

class FinanceManager:
    def __init__(self):
        self.conn = sqlite3.connect('finance.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_name TEXT,
                amount REAL,
                purchase_type TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                amount REAL
            )
        ''')

        self.conn.commit()

    def add_purchase(self, part_name: str, amount: float, purchase_type: str):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO purchases (part_name, amount, purchase_type) VALUES (?, ?, ?)', (part_name, amount, purchase_type))
        self.conn.commit()

    def add_service(self, service_name: str, amount: float):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO services (service_name, amount) VALUES (?, ?)', (service_name, amount))
        self.conn.commit()

    def generate_report(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT part_name, amount, purchase_type FROM purchases')
        part_records = cursor.fetchall()

        cursor.execute('SELECT service_name, amount FROM services')
        service_records = cursor.fetchall()

        self.conn.commit()

        return part_records, service_records

def calculate_profit_margin(part_records, service_records):
    total_cost = sum(record[1] for record in part_records)
    total_revenue = total_cost * 1.2  # Assuming a profit margin of 20%

    # Include service income
    total_revenue += sum(record[1] for record in service_records)

    profit_margin = (total_revenue - total_cost) / total_cost * 100 if total_cost != 0 else 0
    return profit_margin

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motorcycle Finance Manager")
        self.root.geometry("600x400")  # Increase the window size

        self.finance_manager = FinanceManager()

        self.part_label = tk.Label(root, text="Part Name:")
        self.part_entry = tk.Entry(root)

        self.amount_label = tk.Label(root, text="Amount:")
        self.amount_entry = tk.Entry(root)

        self.purchase_type_label = tk.Label(root, text="Purchase Type:")
        self.purchase_type_entry = tk.Entry(root)

        self.service_label = tk.Label(root, text="Service Name:")
        self.service_entry = tk.Entry(root)

        self.service_amount_label = tk.Label(root, text="Service Amount:")
        self.service_amount_entry = tk.Entry(root)

        # Make buttons blue
        self.add_part_button = tk.Button(root, text="Add Part Purchase", command=self.add_part_purchase, bg="blue", fg="white")
        self.add_service_button = tk.Button(root, text="Add Service", command=self.add_service, bg="blue", fg="white")
        self.generate_report_button = tk.Button(root, text="Generate Report", command=self.generate_report, bg="blue", fg="white")

        self.part_label.pack(pady=10)
        self.part_entry.pack(pady=5)
        self.amount_label.pack(pady=10)
        self.amount_entry.pack(pady=5)
        self.purchase_type_label.pack(pady=10)
        self.purchase_type_entry.pack(pady=5)
        self.add_part_button.pack(pady=10)
        self.service_label.pack(pady=10)
        self.service_entry.pack(pady=5)
        self.service_amount_label.pack(pady=10)
        self.service_amount_entry.pack(pady=5)
        self.add_service_button.pack(pady=10)
        self.generate_report_button.pack(pady=10)

    def add_part_purchase(self):
        part_name = self.part_entry.get()
        amount_str = self.amount_entry.get()
        purchase_type = self.purchase_type_entry.get()

        if not part_name or not amount_str or not purchase_type:
            messagebox.showerror("Error", "Part Name, Amount, and Purchase Type are required.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid Amount. Please enter a number.")
            return

        self.finance_manager.add_purchase(part_name, amount, purchase_type)
        messagebox.showinfo("Success", "Part Purchase added successfully.")

        # Clear the entry fields after adding a part purchase
        self.part_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.purchase_type_entry.delete(0, tk.END)

    def add_service(self):
        service_name = self.service_entry.get()
        amount_str = self.service_amount_entry.get()

        if not service_name or not amount_str:
            messagebox.showerror("Error", "Service Name and Amount are required.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid Amount. Please enter a number.")
            return

        self.finance_manager.add_service(service_name, amount)
        messagebox.showinfo("Success", "Service added successfully.")

        # Clear the entry fields after adding a service
        self.service_entry.delete(0, tk.END)
        self.service_amount_entry.delete(0, tk.END)

    def generate_report(self):
        part_records, service_records = self.finance_manager.generate_report()

        if not part_records and not service_records:
            messagebox.showinfo("Report", "No purchases or services found.")
            return

        report_text = "\nFinancial Report:\n"
        total_part_cost = sum(record[1] for record in part_records)
        total_service_income = sum(record[1] for record in service_records)

        for record in part_records:
            part_name, amount, purchase_type = record
            report_text += f"{part_name} ({purchase_type}): ${amount}\n"

        for record in service_records:
            service_name, amount = record
            report_text += f"{service_name} (Service): ${amount}\n"

        total_cost = total_part_cost
        total_revenue = total_part_cost + total_service_income

        profit_margin = calculate_profit_margin(part_records, service_records)
        report_text += "\nTotal Cost: ${}".format(total_cost)
        report_text += "\nTotal Revenue: ${}".format(total_revenue)
        report_text += "\nProfit Margin: {:.2f}%".format(profit_margin)

        messagebox.showinfo("Financial Report", report_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
