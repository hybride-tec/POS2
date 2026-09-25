# stock.py
"""Receive-stock window: add received stock quantities to existing products."""

import tkinter as tk
from tkinter import ttk
import requests

from config import SERVER_URL


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
