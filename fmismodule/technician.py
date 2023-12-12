import tkinter as tk
from tkinter import messagebox
import sqlite3

class TechnicianManager:
    def __init__(self):
        self.conn = sqlite3.connect('technician.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technicians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                technician_id INTEGER,
                service_type TEXT,
                amount REAL,
                FOREIGN KEY (technician_id) REFERENCES technicians(id)
            )
        ''')

        self.conn.commit()

    def add_technician(self, username: str, password: str):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO technicians (username, password) VALUES (?, ?)', (username, password))
        self.conn.commit()

    def login(self, username: str, password: str):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM technicians WHERE username = ? AND password = ?', (username, password))
        result = cursor.fetchone()
        return result is not None

    def add_service(self, technician_id: int, service_type: str, amount: float):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO services (technician_id, service_type, amount) VALUES (?, ?, ?)',
                       (technician_id, service_type, amount))
        self.conn.commit()

class TechnicianInterface:
    def __init__(self, root, technician_manager):
        self.root = root
        self.root.title("Technician Interface")

        self.technician_manager = technician_manager

        self.username_label = tk.Label(root, text="Username:")
        self.username_entry = tk.Entry(root)

        self.password_label = tk.Label(root, text="Password:")
        self.password_entry = tk.Entry(root, show="*")

        self.login_button = tk.Button(root, text="Login", command=self.login, bg="blue", fg="white")
        self.new_account_button = tk.Button(root, text="Create New Account", command=self.create_account, bg="blue", fg="white")

        self.username_label.pack(pady=10)
        self.username_entry.pack(pady=5)
        self.password_label.pack(pady=10)
        self.password_entry.pack(pady=5)
        self.login_button.pack(pady=10)
        self.new_account_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required.")
            return

        if self.technician_manager.login(username, password):
            messagebox.showinfo("Success", "Login successful.")
            self.root.destroy()  # Close login interface upon successful login
            self.show_service_interface()
        else:
            messagebox.showerror("Error", "Invalid credentials. Please try again.")

    def create_account(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required.")
            return

        # Check if the username already exists
        cursor = self.technician_manager.conn.cursor()
        cursor.execute('SELECT id FROM technicians WHERE username = ?', (username,))
        result = cursor.fetchone()

        if result:
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")
        else:
            self.technician_manager.add_technician(username, password)
            messagebox.showinfo("Success", "Account created successfully. You can now log in.")

    def show_service_interface(self):
        service_interface = ServiceInterface(self.technician_manager)

class ServiceInterface:
    def __init__(self, technician_manager):
        self.root = tk.Tk()
        self.root.title("Service Entry")

        self.technician_manager = technician_manager

        self.service_type_label = tk.Label(self.root, text="Service Type:")
        self.service_type_entry = tk.Entry(self.root)

        self.amount_label = tk.Label(self.root, text="Amount:")
        self.amount_entry = tk.Entry(self.root)

        self.add_service_button = tk.Button(self.root, text="Add Service", command=self.add_service, bg="blue", fg="white")
        self.generate_receipt_button = tk.Button(self.root, text="Generate Receipt", command=self.generate_receipt, bg="blue", fg="white")

        self.service_type_label.pack(pady=10)
        self.service_type_entry.pack(pady=5)
        self.amount_label.pack(pady=10)
        self.amount_entry.pack(pady=5)
        self.add_service_button.pack(pady=10)
        self.generate_receipt_button.pack(pady=10)

        self.total_amount = 0  # To accumulate service amounts for receipt

    def add_service(self):
        service_type = self.service_type_entry.get()
        amount_str = self.amount_entry.get()

        if not service_type or not amount_str:
            messagebox.showerror("Error", "Service Type and Amount are required.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid Amount. Please enter a number.")
            return

        # Assuming technician_id is 1 for simplicity, you may need to modify this based on your database structure
        technician_id = 1

        self.technician_manager.add_service(technician_id, service_type, amount)
        messagebox.showinfo("Success", "Service added successfully.")

        # Clear the entry fields after adding a service
        self.service_type_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

        # Accumulate the amount for receipt generation
        self.total_amount += amount

    def generate_receipt(self):
        receipt_text = f"\nReceipt\n\nTotal Service Amount: ${self.total_amount}"
        messagebox.showinfo("Receipt", receipt_text)
        self.total_amount = 0  # Reset total amount after generating the receipt
        self.root.destroy()  # Close the service interface after generating the receipt

if __name__ == "__main__":
    technician_manager = TechnicianManager()

    root = tk.Tk()
    technician_interface = TechnicianInterface(root, technician_manager)
    root.mainloop()
