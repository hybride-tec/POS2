# pos_gui.py
"""Entry point: login screen, admin menu, and role-based routing to the other windows."""

import tkinter as tk
from tkinter import messagebox
import requests

from config import SERVER_URL
from products import open_add_products_window, open_view_stock_window, open_edit_products_window
from stock import open_receive_stock_window
from cashier import open_cashier_window
from sales import open_view_sales_window
from manager import open_manager_auth_window


def main():
    root = tk.Tk()
    root.title("HYBRIDE-TEC")
    root.geometry("800x600")

    login_frame = tk.Frame(root)
    login_frame.pack(fill="both", expand="True")

    tk.Label(login_frame, text="ED SUPERMARKET", font=("Arial", 16, "bold")).pack(pady=15)

    tk.Label(login_frame, text="USERNAME", font=("Arial", 10)).pack()
    username_var = tk.StringVar()
    tk.Entry(login_frame, textvariable=username_var, width=30, font=("Arial", 12)).pack(pady=5)

    tk.Label(login_frame, text="PASSWORD", font=("Arial", 10)).pack()
    password_var = tk.StringVar()
    tk.Entry(login_frame, textvariable=password_var, width=30, font=("Arial", 12), show="*").pack(pady=5)

    result_var = tk.StringVar()
    tk.Label(login_frame, textvariable=result_var, font=("Arial", 11)).pack(pady=10)

    admin_frame = tk.Frame(root)
    tk.Label(admin_frame, text="MENU", font=("Arial", 18, "bold")).pack(pady=15)

    def placeholder_action(action_name):
        messagebox.showinfo("Admin Action", f"{action_name}\n(Not implemented yet)")

    tk.Button(admin_frame, text="Cashier", width=25, height=2, font=("Arial", 12),
              command=open_cashier_window).pack(pady=8)

    tk.Button(admin_frame, text="View sales", width=25, height=2, font=("Arial", 12),
              command=open_view_sales_window).pack(pady=8)

    tk.Button(admin_frame, text="Add new products", width=25, height=2, font=("Arial", 12),
              command=open_add_products_window).pack(pady=8)

    tk.Button(admin_frame, text="View current stock", width=25, height=2, font=("Arial", 12),
              command=open_view_stock_window).pack(pady=8)

    tk.Button(admin_frame, text="Edit products", width=25, height=2, font=("Arial", 12),
              command=open_edit_products_window).pack(pady=8)

    tk.Button(admin_frame, text="Receive stock", width=25, height=2, font=("Arial", 12),
              command=open_receive_stock_window).pack(pady=8)

    tk.Button(admin_frame, text="Reprint a receipt", width=25, height=2, font=("Arial", 12),
              command=lambda: placeholder_action("Reprint a receipt")).pack(pady=8)

    tk.Button(admin_frame, text="View sales report", width=25, height=2, font=("Arial", 12),
              command=lambda: placeholder_action("View sales report")).pack(pady=8)

    tk.Button(admin_frame, text="See stock qty", width=25, height=2, font=("Arial", 12),
              command=lambda: placeholder_action("See stock qty")).pack(pady=8)

    tk.Button(admin_frame, text="Manager", width=20, height=2, font=("Arial", 12),
              command=open_manager_auth_window).pack(pady=10)

    def do_login():
        username = username_var.get().strip()
        password = password_var.get()
        try:
            resp = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password}, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if "role" in data:
                role = data["role"]
                if role == "admin":
                    login_frame.pack_forget()
                    admin_frame.pack(fill="both", expand=True)
                    result_var.set(f"Logged in as: {role}")
                elif role == "cashier":
                    root.withdraw()
                    open_cashier_window()
                else:
                    result_var.set(f"Logged in as: {role} (no menu yet)")
            else:
                result_var.set("Login failed")
        except Exception as e:
            result_var.set(f"Error: {e}")

    tk.Button(login_frame, text="Login", width=20, height=2, font=("Arial", 12), command=do_login).pack(pady=10)
    tk.Button(login_frame, text="Exit", width=20, height=2, font=("Arial", 12), command=root.destroy).pack(pady=5)

    manager_button_frame = tk.Frame(root)
    manager_button_frame.pack(
        side="bottom",
        fill="x",
        padx=10,
        pady=12,
    )

    tk.Button(
        manager_button_frame,
        text="Manager Dashboard",
        width=25,
        height=2,
        font=("Arial", 12, "bold"),
        command=open_manager_auth_window,
    ).pack()

    root.mainloop()


if __name__ == "__main__":
    main()
