# sales.py
"""View sales window: date-filtered sales list, sale detail view, and CSV export."""

import tkinter as tk
from tkinter import ttk, filedialog
import requests
import datetime
import csv

from config import SERVER_URL
from auth_state import get_headers


def open_view_sales_window():
    """Open a window to view sales with date filter and CSV export."""
    win = tk.Toplevel()
    win.title("View Sales")
    win.geometry("1000x700")

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

    tk.Label(filter_frame, textvariable=result_var, fg="blue").grid(
        row=0, column=4, sticky="w", padx=20, pady=5
    )

    sales_frame = tk.LabelFrame(win, text="Sales", padx=5, pady=5)
    sales_frame.pack(fill="both", expand=True, padx=10, pady=5)

    sales_columns = ("sale_id", "timestamp", "total_amount", "items_count")
    sales_tree = ttk.Treeview(sales_frame, columns=sales_columns, show="headings", height=10)

    sales_tree.heading("sale_id", text="Sale ID")
    sales_tree.heading("timestamp", text="Timestamp")
    sales_tree.heading("total_amount", text="Total")
    sales_tree.heading("items_count", text="Items")

    sales_tree.column("sale_id", width=80)
    sales_tree.column("timestamp", width=180)
    sales_tree.column("total_amount", width=100)
    sales_tree.column("items_count", width=70)

    sales_tree.pack(fill="both", expand=True)

    details_frame = tk.LabelFrame(win, text="Sale Details", padx=5, pady=5)
    details_frame.pack(fill="both", expand=True, padx=10, pady=5)

    details_columns = ("description", "quantity", "selling_price", "line_total")
    details_tree = ttk.Treeview(details_frame, columns=details_columns, show="headings", height=6)

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

    tk.Label(details_info_frame, textvariable=details_info_var, fg="blue").pack(side="left", padx=5)

    all_sales_cache = []
    filtered_sales_cache = []

    def parse_date(date_text: str):
        if not date_text.strip():
            return None
        try:
            return datetime.datetime.strptime(date_text.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    def load_sales():
        nonlocal all_sales_cache, filtered_sales_cache

        for row in sales_tree.get_children():
            sales_tree.delete(row)
        for row in details_tree.get_children():
            details_tree.delete(row)

        details_info_var.set("")
        result_var.set("")

        try:
            response = requests.get(f"{SERVER_URL}/sales", headers=get_headers(), timeout=6)
            response.raise_for_status()
            sales_list = response.json()

            all_sales_cache = sales_list
            apply_date_filter()

        except Exception as error:
            result_var.set(f"Could not load sales: {error}")

    def apply_date_filter():
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

        filtered_sales_cache.clear()
        filtered_sales_cache.extend(filtered)

        for row in sales_tree.get_children():
            sales_tree.delete(row)

        for sale in filtered_sales_cache:
            sale_id = sale.get("sale_id", "")
            timestamp = sale.get("timestamp", "")
            total_amount = sale.get("total_amount", 0)
            items = sale.get("items", [])
            items_count = len(items)

            sales_tree.insert("", "end", values=(sale_id, timestamp, f"{total_amount:.2f}", items_count))

        result_var.set(f"Showing {len(filtered_sales_cache)} of {len(all_sales_cache)} sales.")

    def on_select_sale(event):
        selection = sales_tree.selection()
        if not selection:
            return

        values = sales_tree.item(selection[0])["values"]
        sale_id = int(values[0])

        for row in details_tree.get_children():
            details_tree.delete(row)

        sale = next((s for s in filtered_sales_cache if s.get("sale_id") == sale_id), None)
        if sale is None:
            sale = next((s for s in all_sales_cache if s.get("sale_id") == sale_id), None)

        if sale is None:
            details_info_var.set("Sale details not found.")
            return

        items = sale.get("items", [])
        total_amount = sale.get("total_amount", 0)
        timestamp = sale.get("timestamp", "")

        details_info_var.set(f"Sale ID: {sale_id} | Time: {timestamp} | Total: {total_amount:.2f}")

        for item in items:
            details_tree.insert("", "end", values=(
                item.get("description", ""),
                item.get("quantity", 0),
                f"{item.get('selling_price', 0):.2f}",
                f"{item.get('line_total', 0):.2f}",
            ))

    def export_sales_to_csv():
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
                    "sale_id", "timestamp", "product_description",
                    "quantity", "selling_price", "line_total", "total_amount",
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
                            "sale_id": sale_id, "timestamp": timestamp,
                            "product_description": "", "quantity": 0,
                            "selling_price": 0, "line_total": 0, "total_amount": total_amount,
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

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", padx=10, pady=8)

    tk.Button(btn_frame, text="Apply Filter", command=apply_date_filter, width=14, height=2, font=("Arial", 11)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Refresh", command=load_sales, width=12, height=2, font=("Arial", 11)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export to CSV", command=export_sales_to_csv, width=14, height=2, font=("Arial", 11)).pack(side="left", padx=5)

    from_date_entry.bind("<Return>", lambda e: apply_date_filter())
    to_date_entry.bind("<Return>", lambda e: apply_date_filter())

    sales_tree.bind("<<TreeviewSelect>>", on_select_sale)

    load_sales()
