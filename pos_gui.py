# pos_gui.py

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import requests
import datetime
import csv
import os

SERVER_URL = "http://192.168.149.130:5000"

# Global dashboard variables (used by open_dashboard_window and load_dashboard)
today_date_var = None
today_total_var = None
today_count_var = None
month_name_var = None
month_total_var = None
month_count_var = None
profit_title_var = None
profit_var = None
fast_tree = None
slow_tree = None
low_tree = None


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
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()

            if "error" in data:
                result_var.set(f"Error: {data['error']}")
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
        resp = requests.get(f"{SERVER_URL}/products", timeout=5)
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
        resp = requests.get(f"{SERVER_URL}/products", timeout=5)
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
            }, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                result_var.set(f"Error: {data['error']}")
            else:
                result_var.set("Product updated successfully.")
                for row in tree.get_children():
                    tree.delete(row)
                refreshed = requests.get(f"{SERVER_URL}/products", timeout=5).json()
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
        if pwd != "admin123":
            result_var.set("Wrong admin password.")
            return
        try:
            pid = int(pid_text)
        except Exception:
            result_var.set("Invalid product ID.")
            return
        try:
            resp = requests.delete(f"{SERVER_URL}/product/{pid}", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                result_var.set(f"Error: {data['error']}")
            else:
                result_var.set("Product deleted successfully.")
                for row in tree.get_children():
                    tree.delete(row)
                refreshed = requests.get(f"{SERVER_URL}/products", timeout=5).json()
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

def open_receive_stock_window():
    """Open an admin window to add received stock to a product."""
    win = tk.Toplevel()
    win.title("Receive Stock")
    win.geometry("820x500")

    columns = (
        "product_id",
        "barcode",
        "description",
        "cost_price",
        "selling_price",
        "stock_qty",
    )

    tree = ttk.Treeview(
        win,
        columns=columns,
        show="headings",
        height=14,
    )

    tree.heading("product_id", text="ID")
    tree.heading("barcode", text="Barcode")
    tree.heading("description", text="Description")
    tree.heading("cost_price", text="Cost Price")
    tree.heading("selling_price", text="Selling Price")
    tree.heading("stock_qty", text="Current Stock")

    tree.column("product_id", width=50)
    tree.column("barcode", width=130)
    tree.column("description", width=250)
    tree.column("cost_price", width=90)
    tree.column("selling_price", width=90)
    tree.column("stock_qty", width=100)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    selected_id_var = tk.StringVar()
    selected_product_var = tk.StringVar()
    quantity_var = tk.StringVar()
    result_var = tk.StringVar()

    form = tk.Frame(win)
    form.pack(fill="x", padx=10, pady=5)

    tk.Label(form, text="Selected product:").grid(
        row=0,
        column=0,
        sticky="w",
        padx=5,
        pady=5,
    )
    tk.Label(
        form,
        textvariable=selected_product_var,
        width=45,
        anchor="w",
    ).grid(
        row=0,
        column=1,
        columnspan=3,
        sticky="w",
        padx=5,
        pady=5,
    )

    tk.Label(form, text="Quantity received:").grid(
        row=1,
        column=0,
        sticky="w",
        padx=5,
        pady=5,
    )
    quantity_entry = tk.Entry(
        form,
        textvariable=quantity_var,
        width=12,
    )
    quantity_entry.grid(
        row=1,
        column=1,
        sticky="w",
        padx=5,
        pady=5,
    )

    tk.Label(
        win,
        textvariable=result_var,
        fg="red",
    ).pack(pady=5)

    def load_products():
        """Reload the product list from the server."""
        for row in tree.get_children():
            tree.delete(row)

        try:
            response = requests.get(
                f"{SERVER_URL}/products",
                timeout=5,
            )
            response.raise_for_status()
            products = response.json()

            for product in products:
                tree.insert(
                    "",
                    "end",
                    values=(
                        product.get("product_id", ""),
                        product.get("barcode", ""),
                        product.get("description", ""),
                        f"{product.get('cost_price', 0):.2f}",
                        f"{product.get('selling_price', 0):.2f}",
                        product.get("stock_qty", 0),
                    ),
                )
        except Exception as error:
            result_var.set(f"Could not load products: {error}")

    def on_select(event):
        selection = tree.selection()

        if not selection:
            return

        values = tree.item(selection[0])["values"]

        product_id = values[0]
        barcode = values[1]
        description = values[2]
        current_stock = values[5]

        selected_id_var.set(str(product_id))
        selected_product_var.set(
            f"{description} | Barcode: {barcode} | Current stock: {current_stock}"
        )
        result_var.set("")
        quantity_var.set("")
        quantity_entry.focus_set()

    def receive_selected_stock():
        product_id = selected_id_var.get().strip()
        quantity_text = quantity_var.get().strip()

        if not product_id:
            result_var.set("Select a product first.")
            return

        try:
            quantity = int(quantity_text)
        except ValueError:
            result_var.set("Quantity must be a whole number.")
            return

        if quantity <= 0:
            result_var.set("Quantity must be greater than zero.")
            return

        try:
            response = requests.post(
                f"{SERVER_URL}/product/{product_id}/receive-stock",
                json={"quantity_received": quantity},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                result_var.set(f"Error: {data['error']}")
                return

            updated = data["product"]
            result_var.set(
                f"Stock received. New stock quantity: {updated['stock_qty']}"
            )

            selected_id_var.set("")
            selected_product_var.set("")
            quantity_var.set("")
            load_products()

        except Exception as error:
            result_var.set(f"Error: {error}")

    tree.bind("<<TreeviewSelect>>", on_select)

    tk.Button(
        form,
        text="Receive stock",
        command=receive_selected_stock,
        width=18,
        height=2,
        font=("Arial", 11),
    ).grid(
        row=1,
        column=2,
        padx=15,
        pady=5,
    )

    tk.Button(
        form,
        text="Refresh list",
        command=load_products,
        width=14,
        height=2,
        font=("Arial", 11),
    ).grid(
        row=1,
        column=3,
        padx=5,
        pady=5,
    )

    load_products()

def open_cashier_window():
    """Open the cashier sales window with editable cart and payment popup."""
    win = tk.Toplevel()
    win.title("Cashier")
    win.geometry("1000x700")

    columns = (
        "product_id",
        "barcode",
        "description",
        "cost_price",
        "selling_price",
        "stock_qty",
    )

    tree = ttk.Treeview(
        win,
        columns=columns,
        show="headings",
        height=10,
    )

    tree.heading("product_id", text="ID")
    tree.heading("barcode", text="Barcode")
    tree.heading("description", text="Description")
    tree.heading("cost_price", text="Cost")
    tree.heading("selling_price", text="Selling")
    tree.heading("stock_qty", text="Stock")

    tree.column("product_id", width=50)
    tree.column("barcode", width=130)
    tree.column("description", width=220)
    tree.column("cost_price", width=70)
    tree.column("selling_price", width=80)
    tree.column("stock_qty", width=70)

    tree.pack(fill="both", expand=True, padx=10, pady=5)

    search_var = tk.StringVar()
    selected_id_var = tk.StringVar()
    selected_product_var = tk.StringVar()
    quantity_var = tk.StringVar(value="1")
    result_var = tk.StringVar()

    search_frame = tk.Frame(win)
    search_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(search_frame, text="Search:").grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=35)
    search_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(search_frame, text="Selected:").grid(
        row=0, column=2, sticky="w", padx=15, pady=5
    )
    tk.Label(
        search_frame,
        textvariable=selected_product_var,
        width=45,
        anchor="w",
    ).grid(row=0, column=3, sticky="w", padx=5, pady=5)

    qty_frame = tk.Frame(win)
    qty_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(qty_frame, text="Quantity:").grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    quantity_entry = tk.Entry(qty_frame, textvariable=quantity_var, width=10)
    quantity_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(qty_frame, textvariable=result_var, fg="red").grid(
        row=0, column=2, sticky="w", padx=20, pady=5
    )

    # ---------- Cart with editable quantity ----------
    cart_frame = tk.LabelFrame(win, text="Cart", padx=10, pady=10)
    cart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    cart_columns = ("product_id", "description", "quantity", "selling_price", "line_total")
    cart_tree = ttk.Treeview(
        cart_frame,
        columns=cart_columns,
        show="headings",
        height=6,
    )

    cart_tree.heading("product_id", text="ID")
    cart_tree.heading("description", text="Description")
    cart_tree.heading("quantity", text="Qty")
    cart_tree.heading("selling_price", text="Price")
    cart_tree.heading("line_total", text="Line total")

    cart_tree.column("product_id", width=50)
    cart_tree.column("description", width=260)
    cart_tree.column("quantity", width=60)
    cart_tree.column("selling_price", width=80)
    cart_tree.column("line_total", width=90)

    cart_tree.pack(fill="both", expand=True)

    summary_frame = tk.Frame(cart_frame)
    summary_frame.pack(fill="x", pady=5)

    total_items_var = tk.StringVar(value="Total items: 0")
    total_amount_var = tk.StringVar(value="Total amount: 0.00")

    tk.Label(summary_frame, textvariable=total_items_var).pack(side="left", padx=5)
    tk.Label(summary_frame, textvariable=total_amount_var).pack(side="left", padx=20)

    # Cart data: list of dicts
    cart = []

    def load_products():
        """Reload the product list from the server."""
        for row in tree.get_children():
            tree.delete(row)

        try:
            response = requests.get(f"{SERVER_URL}/products", timeout=5)
            response.raise_for_status()
            products = response.json()

            for product in products:
                tree.insert(
                    "",
                    "end",
                    values=(
                        product.get("product_id", ""),
                        product.get("barcode", ""),
                        product.get("description", ""),
                        f"{product.get('cost_price', 0):.2f}",
                        f"{product.get('selling_price', 0):.2f}",
                        product.get("stock_qty", 0),
                    ),
                )
        except Exception as error:
            result_var.set(f"Could not load products: {error}")

    def on_select(event):
        selection = tree.selection()
        if not selection:
            return

        values = tree.item(selection[0])["values"]
        product_id = values[0]
        barcode = values[1]
        description = values[2]
        current_stock = values[5]

        selected_id_var.set(str(product_id))
        selected_product_var.set(
            f"{description} | Barcode: {barcode} | Stock: {current_stock}"
        )
        result_var.set("")

    def filter_products(*args):
        search_text = search_var.get().strip().lower()

        for row in tree.get_children():
            tree.delete(row)

        try:
            response = requests.get(f"{SERVER_URL}/products", timeout=5)
            response.raise_for_status()
            products = response.json()
        except Exception:
            result_var.set("Could not load products for search.")
            return

        filtered = [
            p
            for p in products
            if (
                search_text in str(p.get("barcode", "")).lower()
                or search_text in str(p.get("description", "")).lower()
            )
        ]

        for product in filtered:
            tree.insert(
                "",
                "end",
                values=(
                    product.get("product_id", ""),
                    product.get("barcode", ""),
                    product.get("description", ""),
                    f"{product.get('cost_price', 0):.2f}",
                    f"{product.get('selling_price', 0):.2f}",
                    product.get("stock_qty", 0),
                ),
            )

    def add_to_cart():
        product_id_text = selected_id_var.get().strip()
        quantity_text = quantity_var.get().strip()

        if not product_id_text:
            result_var.set("Select a product first.")
            return

        try:
            quantity = int(quantity_text)
        except ValueError:
            result_var.set("Quantity must be a whole number.")
            return

        if quantity <= 0:
            result_var.set("Quantity must be greater than zero.")
            return

        selection = tree.selection()
        if not selection:
            result_var.set("Select a product in the list.")
            return

        values = tree.item(selection[0])["values"]
        product_id = int(values[0])
        barcode = values[1]
        description = values[2]
        selling_price = float(values[4])
        current_stock = int(values[5])

        existing = next((item for item in cart if item["product_id"] == product_id), None)
        current_in_cart = existing["quantity"] if existing else 0

        if quantity + current_in_cart > current_stock:
            result_var.set(
                f"Not enough stock. Available: {current_stock}, in cart: {current_in_cart}."
            )
            return

        if existing:
            existing["quantity"] += quantity
            existing["line_total"] = existing["quantity"] * existing["selling_price"]
        else:
            cart.append(
                {
                    "product_id": product_id,
                    "barcode": barcode,
                    "description": description,
                    "quantity": quantity,
                    "selling_price": selling_price,
                    "line_total": quantity * selling_price,
                }
            )

        render_cart()
        result_var.set("")
        quantity_var.set("1")
        search_var.set("")
        selected_id_var.set("")
        selected_product_var.set("")
        filter_products()

    def render_cart():
        for row in cart_tree.get_children():
            cart_tree.delete(row)

        total_items = 0
        total_amount = 0.0

        for item in cart:
            total_items += item["quantity"]
            total_amount += item["line_total"]

            cart_tree.insert(
                "",
                "end",
                values=(
                    item["product_id"],
                    item["description"],
                    item["quantity"],
                    f"{item['selling_price']:.2f}",
                    f"{item['line_total']:.2f}",
                ),
            )

        total_items_var.set(f"Total items: {total_items}")
        total_amount_var.set(f"Total amount: {total_amount:.2f}")

    def clear_cart():
        cart.clear()
        render_cart()
        result_var.set("")

    def on_cart_item_double_click(event):
        """Allow editing quantity by double-clicking a cart row."""
        selection = cart_tree.selection()
        if not selection:
            return

        values = cart_tree.item(selection[0])["values"]
        product_id = int(values[0])
        current_qty = int(values[2])

        # Find product in cart
        item = next((i for i in cart if i["product_id"] == product_id), None)
        if not item:
            return

        # Load current stock from products table (search in tree)
        all_products = {}
        for row in tree.get_children():
            v = tree.item(row)["values"]
            pid = int(v[0])
            stock = int(v[5])
            all_products[pid] = stock

        current_stock = all_products.get(product_id, 0)

        # Simple dialog to edit quantity
        dlg = tk.Toplevel(win)
        dlg.title("Edit Quantity")
        dlg.geometry("300x120")
        dlg.transient(win)
        dlg.grab_set()

        tk.Label(dlg, text=f"Product: {item['description']}").pack(pady=5)

        qty_var = tk.StringVar(value=str(current_qty))
        tk.Label(dlg, text="New quantity:").pack()
        qty_entry = tk.Entry(dlg, textvariable=qty_var, width=10)
        qty_entry.pack()

        msg_var = tk.StringVar()
        tk.Label(dlg, textvariable=msg_var, fg="red").pack(pady=3)

        def save_qty():
            try:
                new_qty = int(qty_var.get().strip())
            except ValueError:
                msg_var.set("Quantity must be a whole number.")
                return

            if new_qty <= 0:
                msg_var.set("Quantity must be greater than zero.")
                return

            if new_qty > current_stock:
                msg_var.set(f"Not enough stock. Available: {current_stock}")
                return

            item["quantity"] = new_qty
            item["line_total"] = new_qty * item["selling_price"]
            render_cart()
            dlg.destroy()

        tk.Button(dlg, text="Save", command=save_qty).pack(pady=5)

        qty_entry.focus_set()
        qty_entry.bind("<Return>", lambda e: save_qty())

    cart_tree.bind("<Double-Button-1>", on_cart_item_double_click)

    # ---------- Payment popup ----------
    def open_payment_popup():
        if not cart:
            result_var.set("Cart is empty. Add items before checkout.")
            return

        total = sum(item["line_total"] for item in cart)

        popup = tk.Toplevel(win)
        popup.title("Payment")
        popup.geometry("420x260")
        popup.transient(win)
        popup.grab_set()

        tk.Label(popup, text=f"Total: {total:.2f}", font=("Arial", 12, "bold")).pack(pady=8)

        payment_method_var = tk.StringVar(value="cash")

        method_frame = tk.Frame(popup)
        method_frame.pack(pady=5)

        tk.Radiobutton(
            method_frame,
            text="Cash",
            variable=payment_method_var,
            value="cash",
            command=lambda: amount_entry.config(state="normal"),
        ).pack(side="left", padx=10)

        tk.Radiobutton(
            method_frame,
            text="Card",
            variable=payment_method_var,
            value="card",
            command=lambda: amount_entry.config(state="disabled"),
        ).pack(side="left", padx=10)

        tk.Label(popup, text="Amount tendered:").pack()
        amount_var = tk.StringVar()
        amount_entry = tk.Entry(popup, textvariable=amount_var, width=12)
        amount_entry.pack()

        warning_var = tk.StringVar()
        tk.Label(popup, textvariable=warning_var, fg="red").pack(pady=3)

        admin_pwd_var = tk.StringVar()
        admin_frame = tk.Frame(popup)
        admin_frame.pack(pady=5)

        tk.Label(admin_frame, text="Admin password:").grid(row=0, column=0, padx=5)
        admin_entry = tk.Entry(admin_frame, textvariable=admin_pwd_var, show="*", width=12)
        admin_entry.grid(row=0, column=1, padx=5)

        result_msg_var = tk.StringVar()

        def complete_sale(override_admin_ok=False):
            method = payment_method_var.get()
            amount_text = amount_var.get().strip()

            amount_tendered = 0.0
            if method == "cash":
                try:
                    amount_tendered = float(amount_text)
                except ValueError:
                    warning_var.set("Enter a valid amount.")
                    return

                if amount_tendered < total and not override_admin_ok:
                    warning_var.set("Amount less than total. Admin password required.")
                    return

            # Prepare items for API
            payload = [
                {
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "selling_price": item["selling_price"],
                }
                for item in cart
            ]

            try:
                response = requests.post(
                    f"{SERVER_URL}/sale",
                    json={"items": payload},
                    timeout=8,
                )
                response.raise_for_status()
                data = response.json()

                if "error" in data:
                    result_msg_var.set(f"Error: {data['error']}")
                    return

                sale = data["sale"]
                result_msg_var.set("Sale completed. Printing receipt...")

                popup.destroy()

                show_receipt_popup(sale, amount_tendered if method == "cash" else total)

            except Exception as error:
                result_msg_var.set(f"Error: {error}")

        def try_complete():
            method = payment_method_var.get()
            amount_text = amount_var.get().strip()

            if method == "cash":
                try:
                    amount_tendered = float(amount_text)
                except ValueError:
                    warning_var.set("Enter a valid amount.")
                    return

                if amount_tendered < total:
                    pwd = admin_pwd_var.get()
                    if pwd != "admin123":
                        warning_var.set("Admin password incorrect.")
                        return
                    # Admin approved short payment
                    complete_sale(override_admin_ok=True)
                    return

            # Normal path: amount >= total or card
            complete_sale(override_admin_ok=False)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Pay", command=try_complete, width=10).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="Cancel", command=popup.destroy, width=10).pack(
            side="left", padx=5
        )

        amount_entry.focus_set()
        amount_entry.bind("<Return>", lambda e: try_complete())


    # ---------------------------------------------------------- Receipt popup ----------------------------------------------------------------------------

    def show_receipt_popup(sale, amount_tendered):
        total = sale["total_amount"]
        change = amount_tendered - total if amount_tendered > 0 else 0.0

        receipt_win = tk.Toplevel(win)
        receipt_win.title("Receipt")
        receipt_win.geometry("420x520")
        receipt_win.transient(win)

        main_frame = tk.Frame(receipt_win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            main_frame,
            text="AAABB STORE",
            font=("Arial", 14, "bold"),
        ).pack(pady=5)

        # Header for item table
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(5, 0))

        tk.Label(header_frame, text="ID", width=6, anchor="w", font=("Arial", 9, "bold")).pack(
            side="left", padx=2
        )
        tk.Label(header_frame, text="Name", width=22, anchor="w", font=("Arial", 9, "bold")).pack(
            side="left", padx=2
        )
        tk.Label(header_frame, text="Qty", width=6, anchor="w", font=("Arial", 9, "bold")).pack(
            side="left", padx=2
        )
        tk.Label(header_frame, text="Price", width=8, anchor="e", font=("Arial", 9, "bold")).pack(
            side="left", padx=2
        )
        tk.Label(header_frame, text="Total", width=8, anchor="e", font=("Arial", 9, "bold")).pack(
            side="left", padx=2
        )

        # Scrollable frame for items
        items_canvas_frame = tk.Frame(main_frame)
        items_canvas_frame.pack(fill="both", expand=True, pady=5)

        items_canvas = tk.Canvas(items_canvas_frame, highlightthickness=0)
        items_scrollbar = ttk.Scrollbar(items_canvas_frame, orient="vertical", command=items_canvas.yview)
        items_inner_frame = tk.Frame(items_canvas)

        items_inner_frame.bind(
            "<Configure>",
            lambda e: items_canvas.configure(scrollregion=items_canvas.bbox("all")),
        )

        items_canvas.create_window((0, 0), window=items_inner_frame, anchor="nw")
        items_canvas.configure(yscrollcommand=items_scrollbar.set)

        items_canvas.pack(side="left", fill="both", expand=True)
        items_scrollbar.pack(side="right", fill="y")

        # Add item rows as labels (non-selectable, non-editable)
        for item in sale["items"]:
            row_frame = tk.Frame(items_inner_frame)
            row_frame.pack(fill="x")

            tk.Label(
                row_frame,
                text=str(item["product_id"]),
                width=6,
                anchor="w",
                font=("Arial", 9),
            ).pack(side="left", padx=2)

            tk.Label(
                row_frame,
                text=item["description"],
                width=22,
                anchor="w",
                font=("Arial", 9),
            ).pack(side="left", padx=2)

            tk.Label(
                row_frame,
                text=str(item["quantity"]),
                width=6,
                anchor="w",
                font=("Arial", 9),
            ).pack(side="left", padx=2)

            tk.Label(
                row_frame,
                text=f"{item['selling_price']:.2f}",
                width=8,
                anchor="e",
                font=("Arial", 9),
            ).pack(side="left", padx=2)

            tk.Label(
                row_frame,
                text=f"{item['line_total']:.2f}",
                width=8,
                anchor="e",
                font=("Arial", 9),
            ).pack(side="left", padx=2)

        # Totals section (labels, not selectable)
        summary_frame = tk.Frame(main_frame)
        summary_frame.pack(fill="x", pady=5)

        tk.Label(
            summary_frame,
            text=f"Total: {total:.2f}",
            font=("Arial", 11),
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            summary_frame,
            text=f"Amount tendered: {amount_tendered:.2f}",
            font=("Arial", 11),
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            summary_frame,
            text=f"Change: {change:.2f}",
            font=("Arial", 11),
            anchor="w",
        ).pack(fill="x")

        footer_frame = tk.Frame(main_frame)
        footer_frame.pack(fill="x", pady=10)

        doc_number = sale.get("sale_id", "")
        timestamp = sale.get("timestamp", "")

        tk.Label(
            footer_frame,
            text=f"Doc No: {doc_number}",
            font=("Arial", 9),
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            footer_frame,
            text=f"Date & Time: {timestamp}",
            font=("Arial", 9),
            anchor="w",
        ).pack(fill="x")

        tk.Button(
            receipt_win,
            text="Close",
            command=receipt_win.destroy,
        ).pack(pady=5)

        # Clear cart after successful sale
        cart.clear()
        render_cart()
        load_products()

    def do_checkout():
        open_payment_popup()

    # ---------- Buttons ----------
    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", padx=10, pady=8)

    tk.Button(
        btn_frame,
        text="Add to cart",
        command=add_to_cart,
        width=16,
        height=2,
        font=("Arial", 11),
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Clear cart",
        command=clear_cart,
        width=14,
        height=2,
        font=("Arial", 11),
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Checkout",
        command=do_checkout,
        width=14,
        height=2,
        font=("Arial", 11),
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Refresh",
        command=load_products,
        width=12,
        height=2,
        font=("Arial", 11),
    ).pack(side="left", padx=5)

    # Space bar to checkout
    win.bind("<space>", lambda e: do_checkout())

    search_var.trace_add("write", filter_products)
    tree.bind("<<TreeviewSelect>>", on_select)

    load_products()

def open_view_sales_window():
    """Open a window to view sales with date filter and CSV export."""
    win = tk.Toplevel()
    win.title("View Sales")
    win.geometry("1000x700")

    # ---------- Filters ----------
    filter_frame = tk.Frame(win)
    filter_frame.pack(fill="x", padx=10, pady=8)

    tk.Label(filter_frame, text="From (YYYY-MM-DD):").grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    from_date_var = tk.StringVar()
    from_date_entry = tk.Entry(filter_frame, textvariable=from_date_var, width=12)
    from_date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(filter_frame, text="To (YYYY-MM-DD):").grid(
        row=0, column=2, sticky="w", padx=15, pady=5
    )
    to_date_var = tk.StringVar()
    to_date_entry = tk.Entry(filter_frame, textvariable=to_date_var, width=12)
    to_date_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

    result_var = tk.StringVar()

    tk.Label(
        filter_frame,
        textvariable=result_var,
        fg="blue",
    ).grid(row=0, column=4, sticky="w", padx=20, pady=5)

    # ---------- Sales list ----------
    sales_frame = tk.LabelFrame(win, text="Sales", padx=5, pady=5)
    sales_frame.pack(fill="both", expand=True, padx=10, pady=5)

    sales_columns = ("sale_id", "timestamp", "total_amount", "items_count")
    sales_tree = ttk.Treeview(
        sales_frame,
        columns=sales_columns,
        show="headings",
        height=10,
    )

    sales_tree.heading("sale_id", text="Sale ID")
    sales_tree.heading("timestamp", text="Timestamp")
    sales_tree.heading("total_amount", text="Total")
    sales_tree.heading("items_count", text="Items")

    sales_tree.column("sale_id", width=80)
    sales_tree.column("timestamp", width=180)
    sales_tree.column("total_amount", width=100)
    sales_tree.column("items_count", width=70)

    sales_tree.pack(fill="both", expand=True)

    # ---------- Sale details ----------
    details_frame = tk.LabelFrame(win, text="Sale Details", padx=5, pady=5)
    details_frame.pack(fill="both", expand=True, padx=10, pady=5)

    details_columns = ("description", "quantity", "selling_price", "line_total")
    details_tree = ttk.Treeview(
        details_frame,
        columns=details_columns,
        show="headings",
        height=6,
    )

    details_tree.heading("description", text="Product")
    details_tree.heading("quantity", text="Qty")
    details_tree.heading("selling_price", text="Price")
    details_tree.heading("line_total", text="Line total")

    details_tree.column("description", width=320)
    details_tree.column("quantity", width=60)
    details_tree.column("selling_price", width=80)
    details_tree.column("line_total", width=90)

    details_tree.pack(fill="both", expand=True)

    details_info_var = tk.StringVar()

    details_info_frame = tk.Frame(details_frame)
    details_info_frame.pack(fill="x", pady=5)

    tk.Label(
        details_info_frame,
        textvariable=details_info_var,
        fg="blue",
    ).pack(side="left", padx=5)

    all_sales_cache = []  # full list from server
    filtered_sales_cache = []  # after date filter

    def parse_date(date_text: str):
        """Parse YYYY-MM-DD to a date object, or return None if invalid."""
        if not date_text.strip():
            return None
        try:
            return datetime.datetime.strptime(date_text.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    def load_sales():
        """Load all sales from the server."""
        nonlocal all_sales_cache, filtered_sales_cache

        for row in sales_tree.get_children():
            sales_tree.delete(row)
        for row in details_tree.get_children():
            details_tree.delete(row)

        details_info_var.set("")
        result_var.set("")

        try:
            response = requests.get(
                f"{SERVER_URL}/sales",
                timeout=6,
            )
            response.raise_for_status()
            sales_list = response.json()

            all_sales_cache = sales_list
            apply_date_filter()

        except Exception as error:
            result_var.set(f"Could not load sales: {error}")

    def apply_date_filter():
        """Filter sales by date range and refresh the sales table."""
        from_date = parse_date(from_date_var.get())
        to_date = parse_date(to_date_var.get())

        filtered = []

        for sale in all_sales_cache:
            timestamp_str = sale.get("timestamp", "")
            if not timestamp_str:
                continue

            try:
                sale_date = datetime.datetime.fromisoformat(timestamp_str).date()
            except ValueError:
                continue

            if from_date and sale_date < from_date:
                continue
            if to_date and sale_date > to_date:
                continue

            filtered.append(sale)

        filtered_sales_cache = filtered

        for row in sales_tree.get_children():
            sales_tree.delete(row)

        for sale in filtered_sales_cache:
            sale_id = sale.get("sale_id", "")
            timestamp = sale.get("timestamp", "")
            total_amount = sale.get("total_amount", 0)
            items = sale.get("items", [])
            items_count = len(items)

            sales_tree.insert(
                "",
                "end",
                values=(
                    sale_id,
                    timestamp,
                    f"{total_amount:.2f}",
                    items_count,
                ),
            )

        result_var.set(
            f"Showing {len(filtered_sales_cache)} of {len(all_sales_cache)} sales."
        )

    def on_select_sale(event):
        """When a sale is selected, show its details with product names."""
        selection = sales_tree.selection()

        if not selection:
            return

        values = sales_tree.item(selection[0])["values"]
        sale_id = int(values[0])

        for row in details_tree.get_children():
            details_tree.delete(row)

        sale = next(
            (s for s in filtered_sales_cache if s.get("sale_id") == sale_id), None
        )
        if sale is None:
            sale = next((s for s in all_sales_cache if s.get("sale_id") == sale_id), None)

        if sale is None:
            details_info_var.set("Sale details not found.")
            return

        items = sale.get("items", [])
        total_amount = sale.get("total_amount", 0)
        timestamp = sale.get("timestamp", "")

        details_info_var.set(
            f"Sale ID: {sale_id} | Time: {timestamp} | Total: {total_amount:.2f}"
        )

        for item in items:
            details_tree.insert(
                "",
                "end",
                values=(
                    item.get("description", ""),
                    item.get("quantity", 0),
                    f"{item.get('selling_price', 0):.2f}",
                    f"{item.get('line_total', 0):.2f}",
                ),
            )

    def export_sales_to_csv():
        """Export currently filtered sales (with line items) to CSV."""
        if not filtered_sales_cache:
            result_var.set("No sales to export. Adjust filters or load sales.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Sales to CSV",
            initialfile="sales_export.csv",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                fieldnames = [
                    "sale_id",
                    "timestamp",
                    "product_description",
                    "quantity",
                    "selling_price",
                    "line_total",
                    "total_amount",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for sale in filtered_sales_cache:
                    sale_id = sale.get("sale_id", "")
                    timestamp = sale.get("timestamp", "")
                    total_amount = sale.get("total_amount", 0)

                    items = sale.get("items", [])
                    if not items:
                        writer.writerow({
                            "sale_id": sale_id,
                            "timestamp": timestamp,
                            "product_description": "",
                            "quantity": 0,
                            "selling_price": 0,
                            "line_total": 0,
                            "total_amount": total_amount,
                        })
                    else:
                        for item in items:
                            writer.writerow({
                                "sale_id": sale_id,
                                "timestamp": timestamp,
                                "product_description": item.get("description", ""),
                                "quantity": item.get("quantity", 0),
                                "selling_price": item.get("selling_price", 0),
                                "line_total": item.get("line_total", 0),
                                "total_amount": total_amount,
                            })

            result_var.set(f"Exported to: {file_path}")

        except Exception as error:
            result_var.set(f"Export failed: {error}")

    # ---------- Buttons ----------
    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", padx=10, pady=8)

    tk.Button(
        btn_frame,
        text="Apply Filter",
        command=apply_date_filter,
        width=14,
        height=2,
        font=("Arial", 11),
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Refresh",
        command=load_sales,
        width=12,
        height=2,
        font=("Arial", 11),
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Export to CSV",
        command=export_sales_to_csv,
        width=14,
        height=2,
        font=("Arial", 11),
    ).pack(side="left", padx=5)

    from_date_entry.bind("<Return>", lambda e: apply_date_filter())
    to_date_entry.bind("<Return>", lambda e: apply_date_filter())

    sales_tree.bind("<<TreeviewSelect>>", on_select_sale)

    load_sales()

def open_manager_auth_window():
    #""""""""""""""""""""""""""Open the manager password prompt.""""""""""""""""""""""""""""""""""""""
    dlg = tk.Toplevel()
    dlg.title("Manager Login")
    dlg.geometry("380x230")
    dlg.resizable(False, False)
    dlg.configure(padx=20, pady=20)

    # Keep it in front of the POS main window.
    dlg.transient()
    dlg.grab_set()

    tk.Label(
        dlg,
        text="Manager Dashboard",
        font=("Arial", 15, "bold"),
    ).pack(pady=(0, 15))

    tk.Label(
        dlg,
        text="Enter manager password:",
        font=("Arial", 11),
    ).pack(anchor="w")

    password_var = tk.StringVar()

    password_entry = tk.Entry(
        dlg,
        textvariable=password_var,
        show="*",
        width=30,
        font=("Arial", 12),
    )
    password_entry.pack(fill="x", pady=(5, 8))

    message_var = tk.StringVar()

    tk.Label(
        dlg,
        textvariable=message_var,
        fg="red",
        font=("Arial", 10),
    ).pack(anchor="w", pady=(0, 10))

    button_frame = tk.Frame(dlg)
    button_frame.pack(fill="x", pady=(5, 0))

    def check_password():
        password = password_var.get().strip()

        if password == "manager123":
            dlg.grab_release()
            dlg.destroy()
            open_dashboard_window()
        else:
            message_var.set("Incorrect manager password.")
            password_entry.focus_set()
            password_entry.select_range(0, tk.END)

    tk.Button(
        button_frame,
        text="Login",
        command=check_password,
        width=14,
        height=1,
        font=("Arial", 10, "bold"),
    ).pack(side="left", padx=(0, 10))

    tk.Button(
        button_frame,
        text="Cancel",
        command=dlg.destroy,
        width=14,
        height=1,
        font=("Arial", 10),
    ).pack(side="left")

    password_entry.focus_set()

    dlg.bind("<Return>", lambda event: check_password())
    dlg.bind("<Escape>", lambda event: dlg.destroy())

    # Centre the pop-up after it has been drawn.
    dlg.update_idletasks()

    width = dlg.winfo_width()
    height = dlg.winfo_height()

    x = (dlg.winfo_screenwidth() // 2) - (width // 2)
    y = (dlg.winfo_screenheight() // 2) - (height // 2)

    dlg.geometry(f"{width}x{height}+{x}+{y}")


def open_dashboard_window():
    """Open the manager dashboard window."""
    global today_date_var, today_total_var, today_count_var
    global month_name_var, month_total_var, month_count_var
    global profit_title_var, profit_var
    global fast_tree, slow_tree, low_tree

    win = tk.Toplevel()
    win.title("Manager Dashboard")
    win.geometry("1100x700")

    # ---------- Top: dashboard cards and live clock ----------
    top_frame = tk.Frame(win)
    top_frame.pack(fill="x", padx=10, pady=10)

    cards_frame = tk.Frame(top_frame)
    cards_frame.pack(side="left", fill="x", expand=True)

    # The card labels are updated by load_dashboard().
    today_date_var = tk.StringVar()
    today_total_var = tk.StringVar(value="Sales: 0.00")
    today_count_var = tk.StringVar(value="Count: 0")

    month_name_var = tk.StringVar()
    month_total_var = tk.StringVar(value="Sales: 0.00")
    month_count_var = tk.StringVar(value="Count: 0")

    profit_title_var = tk.StringVar(value="Profit Against Cost")
    profit_var = tk.StringVar(value="0.00")

    def make_dashboard_card(parent, title_var, value_var, count_var=None, bg="#eaf3ff"):
        """Create a non-editable button-style dashboard card."""
        card = tk.Button(
            parent,
            text="",
            state="disabled",
            width=23,
            height=6,
            relief="raised",
            bg=bg,
            disabledforeground="#000000",
            font=("Arial", 10, "bold"),
            justify="center",
        )

        def refresh_card(*args):
            lines = [title_var.get(), value_var.get()]
            if count_var is not None:
                lines.append(count_var.get())
            card.config(text="\n".join(lines))

        title_var.trace_add("write", refresh_card)
        value_var.trace_add("write", refresh_card)
        if count_var is not None:
            count_var.trace_add("write", refresh_card)

        refresh_card()
        return card

    # Card 1: Date, today sales, today count
    today_card = make_dashboard_card(
        cards_frame,
        today_date_var,
        today_total_var,
        today_count_var,
        bg="#d8f3dc",
    )
    today_card.pack(side="left", padx=5, pady=5)

    # Card 2: Month, monthly sales, monthly count
    month_card = make_dashboard_card(
        cards_frame,
        month_name_var,
        month_total_var,
        month_count_var,
        bg="#dbeafe",
    )
    month_card.pack(side="left", padx=5, pady=5)

    # Card 3: Profit
    profit_card = make_dashboard_card(
        cards_frame,
        profit_title_var,
        profit_var,
        None,
        bg="#fef3c7",
    )
    profit_card.pack(side="left", padx=5, pady=5)

    # Live clock
    clock_frame = tk.Frame(top_frame)
    clock_frame.pack(side="right", padx=15, pady=5)

    clock_title_var = tk.StringVar(value="Live Time")
    clock_var = tk.StringVar(value="00:00:00")

    tk.Label(
        clock_frame,
        textvariable=clock_title_var,
        font=("Arial", 10, "bold"),
    ).pack()

    tk.Label(
        clock_frame,
        textvariable=clock_var,
        font=("Arial", 19, "bold"),
        fg="#1d4ed8",
    ).pack()

    def update_clock():
        now = datetime.datetime.now()
        clock_var.set(now.strftime("%H:%M:%S"))
        win.after(1000, update_clock)

    update_clock()

    # ---------- Middle: Fast movers and Slow sellers ----------
    middle_frame = tk.Frame(win)
    middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Fast movers
    fast_frame = tk.LabelFrame(middle_frame, text="Fast Moving Products (Last 30 Days)", font=("Arial", 12, "bold"))
    fast_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    fast_tree = ttk.Treeview(
        fast_frame,
        columns=("Description", "Qty Sold", "Revenue", "Profit"),
        show="headings",
        height=10,
    )
    fast_tree.heading("Description", text="Description")
    fast_tree.heading("Qty Sold", text="Qty Sold")
    fast_tree.heading("Revenue", text="Revenue")
    fast_tree.heading("Profit", text="Profit")

    fast_tree.column("Description", width=200)
    fast_tree.column("Qty Sold", width=80, anchor="center")
    fast_tree.column("Revenue", width=100, anchor="e")
    fast_tree.column("Profit", width=100, anchor="e")

    fast_scroll_y = ttk.Scrollbar(fast_frame, orient="vertical", command=fast_tree.yview)
    fast_tree.configure(yscrollcommand=fast_scroll_y.set)

    fast_tree.pack(side="left", fill="both", expand=True)
    fast_scroll_y.pack(side="right", fill="y")

    # Slow sellers
    slow_frame = tk.LabelFrame(middle_frame, text="Slow Selling Products (Last 30 Days)", font=("Arial", 12, "bold"))
    slow_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    slow_tree = ttk.Treeview(
        slow_frame,
        columns=("Description", "Qty Sold", "Revenue", "Profit"),
        show="headings",
        height=10,
    )
    slow_tree.heading("Description", text="Description")
    slow_tree.heading("Qty Sold", text="Qty Sold")
    slow_tree.heading("Revenue", text="Revenue")
    slow_tree.heading("Profit", text="Profit")

    slow_tree.column("Description", width=200)
    slow_tree.column("Qty Sold", width=80, anchor="center")
    slow_tree.column("Revenue", width=100, anchor="e")
    slow_tree.column("Profit", width=100, anchor="e")

    slow_scroll_y = ttk.Scrollbar(slow_frame, orient="vertical", command=slow_tree.yview)
    slow_tree.configure(yscrollcommand=slow_scroll_y.set)

    slow_tree.pack(side="left", fill="both", expand=True)
    slow_scroll_y.pack(side="right", fill="y")

    # ---------- Bottom: Low stock alert ----------
    low_frame = tk.LabelFrame(win, text="Low Stock Alert (Qty ≤ 10)", font=("Arial", 12, "bold"))
    low_frame.pack(fill="both", expand=True, padx=10, pady=5)

    low_tree = ttk.Treeview(
        low_frame,
        columns=("Description", "Barcode", "Qty", "Cost", "Price"),
        show="headings",
        height=8,
    )
    low_tree.heading("Description", text="Description")
    low_tree.heading("Barcode", text="Barcode")
    low_tree.heading("Qty", text="Qty")
    low_tree.heading("Cost", text="Cost")
    low_tree.heading("Price", text="Price")

    low_tree.column("Description", width=250)
    low_tree.column("Barcode", width=120, anchor="center")
    low_tree.column("Qty", width=70, anchor="center")
    low_tree.column("Cost", width=90, anchor="e")
    low_tree.column("Price", width=90, anchor="e")

    low_scroll_y = ttk.Scrollbar(low_frame, orient="vertical", command=low_tree.yview)
    low_tree.configure(yscrollcommand=low_scroll_y.set)

    low_tree.pack(side="left", fill="both", expand=True)
    low_scroll_y.pack(side="right", fill="y")

    # Style low-stock rows in red
    low_tree.tag_configure("low_stock", background="#ffcccc")

    # Optional refresh button
    def refresh_dashboard():
        print(">>> Refreshing dashboard...")
        load_dashboard()

    tk.Button(
        win,
        text="Refresh Dashboard",
        command=refresh_dashboard,
        font=("Arial", 11, "bold"),
    ).pack(pady=8)

    # Initial load of dashboard data
    print(">>> open_dashboard_window: calling load_dashboard()")
    load_dashboard()


def load_dashboard():
    """Load all manager dashboard data from the Ubuntu server."""
    # Guard: if UI not created yet, do nothing
    if today_date_var is None or fast_tree is None:
        print(">>> load_dashboard(): UI not ready yet")
        return

    current_now = datetime.datetime.now()

    # ----------------------------------------------------
    # CARD 1: TODAY'S DATE, TODAY SALES, SALE COUNT
    # ----------------------------------------------------
    today_date_var.set(
        current_now.strftime("%A, %d %b %Y")
    )

    try:
        response = requests.get(
            f"{SERVER_URL}/dashboard/today",
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()

        today_total = float(data.get("total_amount", 0))
        today_count = int(data.get("count", 0))

        today_total_var.set(
            f"Sales: {today_total:.2f}"
        )
        today_count_var.set(
            f"Count: {today_count}"
        )

    except Exception as e:
        print(">>> Error loading today dashboard:", e)
        today_total_var.set("Sales: --")
        today_count_var.set("Count: --")

    # ----------------------------------------------------
    # CARD 2: CURRENT MONTH, SALES, SALE COUNT
    # ----------------------------------------------------
    month_name_var.set(
        current_now.strftime("%B %Y")
    )

    try:
        response = requests.get(
            f"{SERVER_URL}/dashboard/month",
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()

        month_total = float(data.get("total_amount", 0))
        month_count = int(data.get("count", 0))

        month_total_var.set(
            f"Sales: {month_total:.2f}"
        )
        month_count_var.set(
            f"Count: {month_count}"
        )

    except Exception as e:
        print(">>> Error loading month dashboard:", e)
        month_total_var.set("Sales: --")
        month_count_var.set("Count: --")

    # ----------------------------------------------------
    # CARD 3: PROFIT, FAST MOVERS, SLOW SELLERS
    # ----------------------------------------------------
    try:
        response = requests.get(
            f"{SERVER_URL}/dashboard/product-stats?days=30",
            timeout=6,
        )
        response.raise_for_status()

        stats = response.json()

        # Ensure stats is a valid list.
        if not isinstance(stats, list):
            stats = []

        total_profit = sum(
            float(item.get("profit", 0))
            for item in stats
        )

        profit_var.set(f"{total_profit:.2f}")

        # Higher quantity sold = fast moving.
        sorted_fast = sorted(
            stats,
            key=lambda item: int(item.get("quantity_sold", 0)),
            reverse=True,
        )

        # Clear old fast-moving rows.
        for row in fast_tree.get_children():
            fast_tree.delete(row)

        # Show top 10 fast-moving products.
        for item in sorted_fast[:10]:
            fast_tree.insert(
                "",
                "end",
                values=(
                    item.get("description", ""),
                    item.get("quantity_sold", 0),
                    f"{float(item.get('revenue', 0)):.2f}",
                    f"{float(item.get('profit', 0)):.2f}",
                ),
            )

        # Slow sellers: only products that have at least one sale.
        products_with_sales = [
            item
            for item in stats
            if int(item.get("quantity_sold", 0)) > 0
        ]

        sorted_slow = sorted(
            products_with_sales,
            key=lambda item: int(item.get("quantity_sold", 0)),
        )

        # Clear old slow-selling rows.
        for row in slow_tree.get_children():
            slow_tree.delete(row)

        # Show lowest 10 products by quantity sold.
        for item in sorted_slow[:10]:
            slow_tree.insert(
                "",
                "end",
                values=(
                    item.get("description", ""),
                    item.get("quantity_sold", 0),
                    f"{float(item.get('revenue', 0)):.2f}",
                    f"{float(item.get('profit', 0)):.2f}",
                ),
            )

    except Exception as e:
        print(">>> Error loading product stats:", e)
        profit_var.set("--")

        # Clear old product statistics if server request fails.
        for row in fast_tree.get_children():
            fast_tree.delete(row)

        for row in slow_tree.get_children():
            slow_tree.delete(row)

    # ----------------------------------------------------
    # LOW STOCK ALERT: ALL ROWS APPEAR RED
    # ----------------------------------------------------
    try:
        response = requests.get(
            f"{SERVER_URL}/dashboard/low-stock?threshold=10",
            timeout=5,
        )
        response.raise_for_status()

        low_stock_list = response.json()

        if not isinstance(low_stock_list, list):
            low_stock_list = []

        # Clear old low-stock rows.
        for row in low_tree.get_children():
            low_tree.delete(row)

        # Insert every low-stock product using the red row tag.
        for product in low_stock_list:
            low_tree.insert(
                "",
                "end",
                values=(
                    product.get("description", ""),
                    product.get("barcode", ""),
                    product.get("stock_qty", 0),
                    f"{float(product.get('cost_price', 0)):.2f}",
                    f"{float(product.get('selling_price', 0)):.2f}",
                ),
                tags=("low_stock",),
            )

    except Exception as e:
        print(">>> Error loading low stock:", e)
        # Clear old rows so stale low-stock information is not shown.
        for row in low_tree.get_children():
            low_tree.delete(row)
def main():
    root = tk.Tk()
    root.title("POS – Login")
    root.geometry("800x600")

    login_frame = tk.Frame(root)
    login_frame.pack(fill="both", expand=True)

    tk.Label(login_frame, text="POS Login", font=("Arial", 16, "bold")).pack(pady=15)

    tk.Label(login_frame, text="Username:", font=("Arial", 12)).pack()
    username_var = tk.StringVar()
    tk.Entry(login_frame, textvariable=username_var, width=30, font=("Arial", 12)).pack(pady=5)

    tk.Label(login_frame, text="Password:", font=("Arial", 12)).pack()
    password_var = tk.StringVar()
    tk.Entry(login_frame, textvariable=password_var, width=30, font=("Arial", 12), show="*").pack(pady=5)

    result_var = tk.StringVar()
    tk.Label(login_frame, textvariable=result_var, font=("Arial", 11)).pack(pady=10)

    admin_frame = tk.Frame(root)
    tk.Label(admin_frame, text="Admin Menu", font=("Arial", 16, "bold")).pack(pady=15)

    def placeholder_action(action_name):
        messagebox.showinfo("Admin Action", f"{action_name}\n(Not implemented yet)")
  
    tk.Button(admin_frame, text="Cashier", width=25, height=2,font=("Arial", 12),
              command=open_cashier_window,).pack(pady=8)

    tk.Button( admin_frame, text="View sales", width=25, height=2, font=("Arial", 12),
       command=open_view_sales_window,).pack(pady=8)

    tk.Button(admin_frame, text="Add new products", width=25, height=2, font=("Arial", 12),
              command=open_add_products_window).pack(pady=8)

    tk.Button(admin_frame, text="View current stock", width=25, height=2, font=("Arial", 12),
              command=open_view_stock_window).pack(pady=8)

    tk.Button(admin_frame, text="Edit products", width=25, height=2, font=("Arial", 12),
              command=open_edit_products_window).pack(pady=8)

    tk.Button(admin_frame, text="Receive stock", width=25, height=2,font=("Arial", 12),
              command=open_receive_stock_window,).pack(pady=8)

    tk.Button(admin_frame, text="Reprint a receipt", width=25, height=2, font=("Arial", 12),
              command=lambda: placeholder_action("Reprint a receipt")).pack(pady=8)

    tk.Button(admin_frame, text="View sales report", width=25, height=2, font=("Arial", 12),
              command=lambda: placeholder_action("View sales report")).pack(pady=8)

    tk.Button(admin_frame, text="See stock qty", width=25, height=2, font=("Arial", 12),
              command=lambda: placeholder_action("See stock qty")).pack(pady=8)
    
    tk.Button(admin_frame,text="Manager", width=20,height=2,font=("Arial", 12),
        command=open_manager_auth_window ).pack(pady=10)
   

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