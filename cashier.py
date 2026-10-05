# cashier.py
"""Cashier checkout window: search/select products, build a cart, take payment, print receipt."""

import tkinter as tk
from tkinter import ttk, messagebox
import requests

from config import SERVER_URL
from auth_state import get_headers


def open_cashier_window():
    """Open the cashier sales window with editable cart and payment popup."""
    win = tk.Toplevel()

    def on_cashier_close():
        if messagebox.askokcancel("Quit", "Are you sure you want to close this window?"):
            win.destroy()
            try:
                win.master.deiconify()
            except Exception:
                pass

    win.protocol("WM_DELETE_WINDOW", on_cashier_close)
    win.title("Cashier")
    win.geometry("1000x700")

    columns = (
        "product_id", "barcode", "description", "cost_price", "selling_price", "stock_qty",
    )

    tree = ttk.Treeview(win, columns=columns, show="headings", height=10)

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

    tk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=35)
    search_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(search_frame, text="Selected:").grid(row=0, column=2, sticky="w", padx=15, pady=5)
    tk.Label(search_frame, textvariable=selected_product_var, width=45, anchor="w").grid(
        row=0, column=3, sticky="w", padx=5, pady=5
    )

    qty_frame = tk.Frame(win)
    qty_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(qty_frame, text="Quantity:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    quantity_entry = tk.Entry(qty_frame, textvariable=quantity_var, width=10)
    quantity_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(qty_frame, textvariable=result_var, fg="red").grid(row=0, column=2, sticky="w", padx=20, pady=5)

    cart_frame = tk.LabelFrame(win, text="Cart", padx=10, pady=10)
    cart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    cart_columns = ("product_id", "description", "quantity", "selling_price", "line_total")
    cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show="headings", height=6)

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

    cart = []

    def load_products():
        for row in tree.get_children():
            tree.delete(row)

        try:
            response = requests.get(f"{SERVER_URL}/products", headers=get_headers(), timeout=5)
            response.raise_for_status()
            products = response.json()

            for product in products:
                tree.insert("", "end", values=(
                    product.get("product_id", ""),
                    product.get("barcode", ""),
                    product.get("description", ""),
                    f"{product.get('cost_price', 0):.2f}",
                    f"{product.get('selling_price', 0):.2f}",
                    product.get("stock_qty", 0),
                ))
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
        selected_product_var.set(f"{description} | Barcode: {barcode} | Stock: {current_stock}")
        result_var.set("")

    def filter_products(*args):
        search_text = search_var.get().strip().lower()

        for row in tree.get_children():
            tree.delete(row)

        try:
            response = requests.get(f"{SERVER_URL}/products", headers=get_headers(), timeout=5)
            response.raise_for_status()
            products = response.json()
        except Exception:
            result_var.set("Could not load products for search.")
            return

        filtered = [
            p for p in products
            if (
                search_text in str(p.get("barcode", "")).lower()
                or search_text in str(p.get("description", "")).lower()
            )
        ]

        for product in filtered:
            tree.insert("", "end", values=(
                product.get("product_id", ""),
                product.get("barcode", ""),
                product.get("description", ""),
                f"{product.get('cost_price', 0):.2f}",
                f"{product.get('selling_price', 0):.2f}",
                product.get("stock_qty", 0),
            ))

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
            result_var.set(f"Not enough stock. Available: {current_stock}, in cart: {current_in_cart}.")
            return

        if existing:
            existing["quantity"] += quantity
            existing["line_total"] = existing["quantity"] * existing["selling_price"]
        else:
            cart.append({
                "product_id": product_id,
                "barcode": barcode,
                "description": description,
                "quantity": quantity,
                "selling_price": selling_price,
                "line_total": quantity * selling_price,
            })

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

            cart_tree.insert("", "end", values=(
                item["product_id"], item["description"], item["quantity"],
                f"{item['selling_price']:.2f}", f"{item['line_total']:.2f}",
            ))

        total_items_var.set(f"Total items: {total_items}")
        total_amount_var.set(f"Total amount: {total_amount:.2f}")

    def clear_cart():
        cart.clear()
        render_cart()
        result_var.set("")

    def on_cart_item_double_click(event):
        selection = cart_tree.selection()
        if not selection:
            return

        values = cart_tree.item(selection[0])["values"]
        product_id = int(values[0])
        current_qty = int(values[2])

        item = next((i for i in cart if i["product_id"] == product_id), None)
        if not item:
            return

        all_products = {}
        for row in tree.get_children():
            v = tree.item(row)["values"]
            pid = int(v[0])
            stock = int(v[5])
            all_products[pid] = stock

        current_stock = all_products.get(product_id, 0)

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
            method_frame, text="Cash", variable=payment_method_var, value="cash",
            command=lambda: amount_entry.config(state="normal"),
        ).pack(side="left", padx=10)

        tk.Radiobutton(
            method_frame, text="Card", variable=payment_method_var, value="card",
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

            payload = [
                {"product_id": item["product_id"], "quantity": item["quantity"], "selling_price": item["selling_price"]}
                for item in cart
            ]

            try:
                response = requests.post(
                    f"{SERVER_URL}/sale", json={"items": payload}, headers=get_headers(), timeout=8,
                )
                data = response.json()

                if response.status_code >= 400 or "error" in data:
                    result_msg_var.set(f"Error: {data.get('error', 'Request failed.')}")
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
                    try:
                        resp = requests.post(f"{SERVER_URL}/login", json={"username": "admin", "password": pwd}, timeout=5)
                        if resp.status_code != 200 or resp.json().get("role") != "admin":
                            warning_var.set("Admin password incorrect.")
                            return
                    except requests.exceptions.RequestException:
                        warning_var.set("Could not reach server to verify password.")
                        return
                    complete_sale(override_admin_ok=True)
                    return

            complete_sale(override_admin_ok=False)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Pay", command=try_complete, width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=popup.destroy, width=10).pack(side="left", padx=5)

        amount_entry.focus_set()
        amount_entry.bind("<Return>", lambda e: try_complete())

    def show_receipt_popup(sale, amount_tendered):
        total = sale["total_amount"]
        change = amount_tendered - total if amount_tendered > 0 else 0.0

        receipt_win = tk.Toplevel(win)
        receipt_win.title("Receipt")
        receipt_win.geometry("420x520")
        receipt_win.transient(win)

        main_frame = tk.Frame(receipt_win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(main_frame, text="ED SUPERMARKET", font=("Arial", 14, "bold")).pack(pady=5)

        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(5, 0))

        tk.Label(header_frame, text="ID", width=6, anchor="w", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Label(header_frame, text="Name", width=22, anchor="w", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Label(header_frame, text="Qty", width=6, anchor="w", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Label(header_frame, text="Price", width=8, anchor="e", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Label(header_frame, text="Total", width=8, anchor="e", font=("Arial", 9, "bold")).pack(side="left", padx=2)

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

        for item in sale["items"]:
            row_frame = tk.Frame(items_inner_frame)
            row_frame.pack(fill="x")

            tk.Label(row_frame, text=str(item["product_id"]), width=6, anchor="w", font=("Arial", 9)).pack(side="left", padx=2)
            tk.Label(row_frame, text=item["description"], width=22, anchor="w", font=("Arial", 9)).pack(side="left", padx=2)
            tk.Label(row_frame, text=str(item["quantity"]), width=6, anchor="w", font=("Arial", 9)).pack(side="left", padx=2)
            tk.Label(row_frame, text=f"{item['selling_price']:.2f}", width=8, anchor="e", font=("Arial", 9)).pack(side="left", padx=2)
            tk.Label(row_frame, text=f"{item['line_total']:.2f}", width=8, anchor="e", font=("Arial", 9)).pack(side="left", padx=2)

        summary_frame = tk.Frame(main_frame)
        summary_frame.pack(fill="x", pady=5)

        tk.Label(summary_frame, text=f"Total: {total:.2f}", font=("Arial", 11), anchor="w").pack(fill="x")
        tk.Label(summary_frame, text=f"Amount tendered: {amount_tendered:.2f}", font=("Arial", 11), anchor="w").pack(fill="x")
        tk.Label(summary_frame, text=f"Change: {change:.2f}", font=("Arial", 11), anchor="w").pack(fill="x")

        footer_frame = tk.Frame(main_frame)
        footer_frame.pack(fill="x", pady=10)

        doc_number = sale.get("sale_id", "")
        timestamp = sale.get("timestamp", "")

        tk.Label(footer_frame, text=f"Doc No: {doc_number}", font=("Arial", 9), anchor="w").pack(fill="x")
        tk.Label(footer_frame, text=f"Date & Time: {timestamp}", font=("Arial", 9), anchor="w").pack(fill="x")

        tk.Button(receipt_win, text="Close", command=receipt_win.destroy).pack(pady=5)

        cart.clear()
        render_cart()
        load_products()

    def do_checkout():
        open_payment_popup()

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", padx=10, pady=8)

    tk.Button(btn_frame, text="Add to cart", command=add_to_cart, width=16, height=2, font=("Arial", 11)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Clear cart", command=clear_cart, width=14, height=2, font=("Arial", 11)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Checkout", command=do_checkout, width=14, height=2, font=("Arial", 11)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Refresh", command=load_products, width=12, height=2, font=("Arial", 11)).pack(side="left", padx=5)

    win.bind("<space>", lambda e: do_checkout())

    search_var.trace_add("write", filter_products)
    tree.bind("<<TreeviewSelect>>", on_select)

    load_products()
