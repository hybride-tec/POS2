# products.py
"""Product management windows: add, view, and edit products."""

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import requests

from config import SERVER_URL
from auth_state import get_headers


def open_add_products_window():
    win = tk.Toplevel()
    win.title("Add New Product")
    win.geometry("450x400")

    barcode_var = tk.StringVar()
    description_var = tk.StringVar()
    cost_price_var = tk.DoubleVar(value=0.0)
    selling_price_var = tk.DoubleVar(value=0.0)
    stock_qty_var = tk.IntVar(value=0)
    result_var = tk.StringVar()

    def add_product():
        barcode = barcode_var.get().strip()
        description = description_var.get().strip()

        try:
            sp = selling_price_var.get()
            cp = cost_price_var.get()
            selling_price = float(sp) if sp not in ("", None) else 0.0
            cost_price = float(cp) if cp not in ("", None) else 0.0
        except Exception as e:
            result_var.set(f"Price error: {e}")
            return

        if not barcode:
            result_var.set("Barcode is required.")
            return
        if not description:
            result_var.set("Description is required.")
            return

        try:
            resp = requests.post(
                f"{SERVER_URL}/product",
                json={
                    "barcode": barcode,
                    "description": description,
                    "selling_price": selling_price,
                    "cost_price": cost_price,
                    "stock_qty": int(stock_qty_var.get()),
                },
                headers=get_headers(),
                timeout=5,
            )
            data = resp.json()

            if resp.status_code >= 400 or "error" in data:
                result_var.set(f"Error: {data.get('error', 'Request failed.')}")
            else:
                result_var.set("Product added successfully.")
                barcode_var.set("")
                description_var.set("")
                cost_price_var.set(0.0)
                selling_price_var.set(0.0)
                stock_qty_var.set(0)
        except Exception as e:
            result_var.set(f"Error: {e}")

    tk.Label(win, text="Barcode:", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(10, 0))
    tk.Entry(win, textvariable=barcode_var, width=40, font=("Arial", 11)).pack(padx=20, pady=5)

    tk.Label(win, text="Description:", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(10, 0))
    tk.Entry(win, textvariable=description_var, width=40, font=("Arial", 11)).pack(padx=20, pady=5)

    tk.Label(win, text="Cost price:", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(10, 0))
    tk.Entry(win, textvariable=cost_price_var, width=40, font=("Arial", 11)).pack(padx=20, pady=5)

    tk.Label(win, text="Selling price:", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(10, 0))
    tk.Entry(win, textvariable=selling_price_var, width=40, font=("Arial", 11)).pack(padx=20, pady=5)

    tk.Label(win, text="Stock qty:", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(10, 0))
    tk.Entry(win, textvariable=stock_qty_var, width=40, font=("Arial", 11)).pack(padx=20, pady=5)

    tk.Button(win, text="Add product", command=add_product, width=20, height=2, font=("Arial", 11)).pack(pady=15)
    tk.Label(win, textvariable=result_var, font=("Arial", 10), fg="red").pack(pady=5)


def open_view_stock_window():
    win = tk.Toplevel()
    win.title("Current Stock")
    win.geometry("700x400")

    columns = ("barcode", "description", "cost_price", "selling_price", "stock_qty")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=15)

    tree.heading("barcode", text="Barcode")
    tree.heading("description", text="Description")
    tree.heading("cost_price", text="Cost Price")
    tree.heading("selling_price", text="Selling Price")
    tree.heading("stock_qty", text="Stock Qty")

    tree.column("barcode", width=130)
    tree.column("description", width=250)
    tree.column("cost_price", width=90)
    tree.column("selling_price", width=90)
    tree.column("stock_qty", width=80)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    try:
        resp = requests.get(f"{SERVER_URL}/products", headers=get_headers(), timeout=5)
        resp.raise_for_status()
        products = resp.json()
        for p in products:
            tree.insert("", "end", values=(
                p.get("barcode", ""),
                p.get("description", ""),
                f"{p.get('cost_price', 0):.2f}",
                f"{p.get('selling_price', 0):.2f}",
                p.get("stock_qty", 0),
            ))
    except Exception as e:
        messagebox.showerror("Error", f"Could not load products:\n{e}")


def open_edit_products_window():
    win = tk.Toplevel()
    win.title("Edit Products")
    win.geometry("900x560")

    columns = ("product_id", "barcode", "description", "cost_price", "selling_price", "stock_qty")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=15)

    tree.heading("product_id", text="ID")
    tree.heading("barcode", text="Barcode")
    tree.heading("description", text="Description")
    tree.heading("cost_price", text="Cost Price")
    tree.heading("selling_price", text="Selling Price")
    tree.heading("stock_qty", text="Stock Qty")

    tree.column("product_id", width=50)
    tree.column("barcode", width=130)
    tree.column("description", width=250)
    tree.column("cost_price", width=90)
    tree.column("selling_price", width=90)
    tree.column("stock_qty", width=80)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    try:
        resp = requests.get(f"{SERVER_URL}/products", headers=get_headers(), timeout=5)
        resp.raise_for_status()
        products = resp.json()
        for p in products:
            tree.insert("", "end", values=(
                p.get("product_id", ""),
                p.get("barcode", ""),
                p.get("description", ""),
                f"{p.get('cost_price', 0):.2f}",
                f"{p.get('selling_price', 0):.2f}",
                p.get("stock_qty", 0),
            ))
    except Exception as e:
        messagebox.showerror("Error", f"Could not load products:\n{e}")
        return

    edit_frame = tk.Frame(win)
    edit_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(edit_frame, text="Selected ID:").grid(row=0, column=0, sticky="w")
    selected_id_var = tk.StringVar()
    tk.Entry(edit_frame, textvariable=selected_id_var, width=8, state="readonly").grid(row=0, column=1, padx=5, pady=5)

    tk.Label(edit_frame, text="Description:").grid(row=0, column=2, sticky="w", padx=(15, 0))
    description_var = tk.StringVar()
    description_entry = tk.Entry(edit_frame, textvariable=description_var, width=35)
    description_entry.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(edit_frame, text="Cost:").grid(row=1, column=0, sticky="w")
    cost_var = tk.StringVar()
    cost_entry = tk.Entry(edit_frame, textvariable=cost_var, width=10)
    cost_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(edit_frame, text="Selling:").grid(row=1, column=2, sticky="w", padx=(15, 0))
    sell_var = tk.StringVar()
    sell_entry = tk.Entry(edit_frame, textvariable=sell_var, width=10)
    sell_entry.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(edit_frame, text="Stock:").grid(row=1, column=4, sticky="w", padx=(15, 0))
    stock_var = tk.StringVar()
    tk.Entry(edit_frame, textvariable=stock_var, width=8, state="readonly").grid(row=1, column=5, padx=5, pady=5)

    result_var = tk.StringVar()
    tk.Label(win, textvariable=result_var, fg="red").pack(pady=5)

    def on_select(event):
        sel = tree.selection()
        if not sel:
            return
        item = tree.item(sel[0])
        vals = item["values"]
        pid, desc, cost, sell, stock = vals[0], vals[2], vals[3], vals[4], vals[5]
        selected_id_var.set(str(pid))
        description_var.set(str(desc))
        cost_var.set(str(cost))
        sell_var.set(str(sell))
        stock_var.set(str(stock))
        result_var.set("")

    tree.bind("<<TreeviewSelect>>", on_select)

    def save_changes():
        pid_text = selected_id_var.get().strip()
        if not pid_text:
            result_var.set("No product selected.")
            return
        try:
            pid = int(pid_text)
        except Exception:
            result_var.set("Invalid product ID.")
            return

        desc = description_var.get().strip()
        if not desc:
            result_var.set("Description cannot be empty.")
            return
        try:
            cost = float(cost_var.get())
            sell = float(sell_var.get())
        except Exception:
            result_var.set("Cost and selling price must be numbers.")
            return

        try:
            resp = requests.put(f"{SERVER_URL}/product/{pid}", json={
                "description": desc,
                "cost_price": cost,
                "selling_price": sell,
            }, headers=get_headers(), timeout=5)
            data = resp.json()
            if resp.status_code >= 400 or "error" in data:
                result_var.set(f"Error: {data.get('error', 'Request failed.')}")
            else:
                result_var.set("Product updated successfully.")
                for row in tree.get_children():
                    tree.delete(row)
                refreshed = requests.get(f"{SERVER_URL}/products", headers=get_headers(), timeout=5).json()
                for p in refreshed:
                    tree.insert("", "end", values=(
                        p.get("product_id", ""),
                        p.get("barcode", ""),
                        p.get("description", ""),
                        f"{p.get('cost_price', 0):.2f}",
                        f"{p.get('selling_price', 0):.2f}",
                        p.get("stock_qty", 0),
                    ))
        except Exception as e:
            result_var.set(f"Error: {e}")

    def confirm_and_delete():
        pid_text = selected_id_var.get().strip()
        if not pid_text:
            result_var.set("No product selected.")
            return
        pwd = simpledialog.askstring("Admin password", "Enter admin password to confirm deletion:", show="*", parent=win)
        if pwd is None:
            return

        try:
            resp = requests.post(f"{SERVER_URL}/login", json={"username": "admin", "password": pwd}, timeout=5)
            if resp.status_code != 200 or resp.json().get("role") != "admin":
                result_var.set("Wrong admin password.")
                return
        except requests.exceptions.RequestException:
            result_var.set("Could not reach server to verify password.")
            return

        try:
            pid = int(pid_text)
        except Exception:
            result_var.set("Invalid product ID.")
            return
        try:
            resp = requests.delete(f"{SERVER_URL}/product/{pid}", headers=get_headers(), timeout=5)
            data = resp.json()
            if resp.status_code >= 400 or "error" in data:
                result_var.set(f"Error: {data.get('error', 'Request failed.')}")
            else:
                result_var.set("Product deleted successfully.")
                for row in tree.get_children():
                    tree.delete(row)
                refreshed = requests.get(f"{SERVER_URL}/products", headers=get_headers(), timeout=5).json()
                for p in refreshed:
                    tree.insert("", "end", values=(
                        p.get("product_id", ""),
                        p.get("barcode", ""),
                        p.get("description", ""),
                        f"{p.get('cost_price', 0):.2f}",
                        f"{p.get('selling_price', 0):.2f}",
                        p.get("stock_qty", 0),
                    ))
                selected_id_var.set("")
                description_var.set("")
                cost_var.set("")
                sell_var.set("")
                stock_var.set("")
        except Exception as e:
            result_var.set(f"Error: {e}")

    tk.Button(win, text="Save changes", command=save_changes, width=20, height=2, font=("Arial", 11)).pack(pady=5)
    tk.Button(win, text="Delete product", command=confirm_and_delete, width=20, height=2, font=("Arial", 11), fg="red").pack(pady=5)
