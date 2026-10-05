# manager.py
"""Manager auth dialog and the manager dashboard (today/month sales, fast/slow movers, low stock)."""

import tkinter as tk
from tkinter import ttk
import requests
import datetime

from config import SERVER_URL
from auth_state import get_headers, set_token

# Module-level dashboard widget/variable references, set up in open_dashboard_window()
# and read by load_dashboard(). These persist for as long as the dashboard window is open.
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


def open_manager_auth_window():
    """Open the manager password prompt."""
    dlg = tk.Toplevel()
    dlg.title("Manager Login")
    dlg.geometry("380x230")
    dlg.resizable(False, False)
    dlg.configure(padx=20, pady=20)

    dlg.transient()
    dlg.grab_set()

    tk.Label(dlg, text="Manager Dashboard", font=("Arial", 15, "bold")).pack(pady=(0, 15))
    tk.Label(dlg, text="Enter manager password:", font=("Arial", 11)).pack(anchor="w")

    password_var = tk.StringVar()

    password_entry = tk.Entry(dlg, textvariable=password_var, show="*", width=30, font=("Arial", 12))
    password_entry.pack(fill="x", pady=(5, 8))

    message_var = tk.StringVar()

    tk.Label(dlg, textvariable=message_var, fg="red", font=("Arial", 10)).pack(anchor="w", pady=(0, 10))

    button_frame = tk.Frame(dlg)
    button_frame.pack(fill="x", pady=(5, 0))

    def check_password():
        password = password_var.get().strip()

        try:
            resp = requests.post(f"{SERVER_URL}/login", json={"username": "admin", "password": password}, timeout=5)
            data = resp.json()
            if resp.status_code == 200 and data.get("role") == "admin":
                set_token(data.get("token"))  # store the token so dashboard requests are authorized
                dlg.grab_release()
                dlg.destroy()
                open_dashboard_window()
            else:
                message_var.set("Incorrect manager password.")
                password_entry.focus_set()
                password_entry.select_range(0, tk.END)
        except requests.exceptions.RequestException:
            message_var.set("Could not reach server. Check connection.")

    tk.Button(
        button_frame, text="Login", command=check_password,
        width=14, height=1, font=("Arial", 10, "bold"),
    ).pack(side="left", padx=(0, 10))

    tk.Button(
        button_frame, text="Cancel", command=dlg.destroy,
        width=14, height=1, font=("Arial", 10),
    ).pack(side="left")

    password_entry.focus_set()

    dlg.bind("<Return>", lambda event: check_password())
    dlg.bind("<Escape>", lambda event: dlg.destroy())

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

    top_frame = tk.Frame(win)
    top_frame.pack(fill="x", padx=10, pady=10)

    cards_frame = tk.Frame(top_frame)
    cards_frame.pack(side="left", fill="x", expand=True)

    today_date_var = tk.StringVar()
    today_total_var = tk.StringVar(value="Sales: 0.00")
    today_count_var = tk.StringVar(value="Count: 0")

    month_name_var = tk.StringVar()
    month_total_var = tk.StringVar(value="Sales: 0.00")
    month_count_var = tk.StringVar(value="Count: 0")

    profit_title_var = tk.StringVar(value="Profit Against Cost")
    profit_var = tk.StringVar(value="0.00")

    def make_dashboard_card(parent, title_var, value_var, count_var=None, bg="#eaf3ff"):
        card = tk.Button(
            parent, text="", state="disabled", width=23, height=6, relief="raised",
            bg=bg, disabledforeground="#000000", font=("Arial", 10, "bold"), justify="center",
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

    today_card = make_dashboard_card(cards_frame, today_date_var, today_total_var, today_count_var, bg="#d8f3dc")
    today_card.pack(side="left", padx=5, pady=5)

    month_card = make_dashboard_card(cards_frame, month_name_var, month_total_var, month_count_var, bg="#dbeafe")
    month_card.pack(side="left", padx=5, pady=5)

    profit_card = make_dashboard_card(cards_frame, profit_title_var, profit_var, None, bg="#fef3c7")
    profit_card.pack(side="left", padx=5, pady=5)

    clock_frame = tk.Frame(top_frame)
    clock_frame.pack(side="right", padx=15, pady=5)

    clock_title_var = tk.StringVar(value="Live Time")
    clock_var = tk.StringVar(value="00:00:00")

    tk.Label(clock_frame, textvariable=clock_title_var, font=("Arial", 10, "bold")).pack()
    tk.Label(clock_frame, textvariable=clock_var, font=("Arial", 19, "bold"), fg="#1d4ed8").pack()

    def update_clock():
        now = datetime.datetime.now()
        clock_var.set(now.strftime("%H:%M:%S"))
        win.after(1000, update_clock)

    update_clock()

    middle_frame = tk.Frame(win)
    middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

    fast_frame = tk.LabelFrame(middle_frame, text="Fast Moving Products (Last 30 Days)", font=("Arial", 12, "bold"))
    fast_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    fast_tree = ttk.Treeview(fast_frame, columns=("Description", "Qty Sold", "Revenue", "Profit"), show="headings", height=10)
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

    slow_frame = tk.LabelFrame(middle_frame, text="Slow Selling Products (Last 30 Days)", font=("Arial", 12, "bold"))
    slow_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    slow_tree = ttk.Treeview(slow_frame, columns=("Description", "Qty Sold", "Revenue", "Profit"), show="headings", height=10)
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

    low_frame = tk.LabelFrame(win, text="Low Stock Alert (Qty <= 10)", font=("Arial", 12, "bold"))
    low_frame.pack(fill="both", expand=True, padx=10, pady=5)

    low_tree = ttk.Treeview(low_frame, columns=("Description", "Barcode", "Qty", "Cost", "Price"), show="headings", height=8)
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

    low_tree.tag_configure("low_stock", background="#ffcccc")

    def refresh_dashboard():
        print(">>> Refreshing dashboard...")
        load_dashboard()

    tk.Button(win, text="Refresh Dashboard", command=refresh_dashboard, font=("Arial", 11, "bold")).pack(pady=8)

    print(">>> open_dashboard_window: calling load_dashboard()")
    load_dashboard()


def load_dashboard():
    """Load all manager dashboard data from the Ubuntu server."""
    if today_date_var is None or fast_tree is None:
        print(">>> load_dashboard(): UI not ready yet")
        return

    current_now = datetime.datetime.now()

    today_date_var.set(current_now.strftime("%A, %d %b %Y"))

    try:
        response = requests.get(f"{SERVER_URL}/dashboard/today", headers=get_headers(), timeout=5)
        response.raise_for_status()
        data = response.json()

        today_total = float(data.get("total_amount", 0))
        today_count = int(data.get("count", 0))

        today_total_var.set(f"Sales: {today_total:.2f}")
        today_count_var.set(f"Count: {today_count}")

    except Exception as e:
        print(">>> Error loading today dashboard:", e)
        today_total_var.set("Sales: --")
        today_count_var.set("Count: --")

    month_name_var.set(current_now.strftime("%B %Y"))

    try:
        response = requests.get(f"{SERVER_URL}/dashboard/month", headers=get_headers(), timeout=5)
        response.raise_for_status()
        data = response.json()

        month_total = float(data.get("total_amount", 0))
        month_count = int(data.get("count", 0))

        month_total_var.set(f"Sales: {month_total:.2f}")
        month_count_var.set(f"Count: {month_count}")

    except Exception as e:
        print(">>> Error loading month dashboard:", e)
        month_total_var.set("Sales: --")
        month_count_var.set("Count: --")

    try:
        response = requests.get(f"{SERVER_URL}/dashboard/product-stats?days=30", headers=get_headers(), timeout=6)
        response.raise_for_status()
        stats = response.json()

        if not isinstance(stats, list):
            stats = []

        total_profit = sum(float(item.get("profit", 0)) for item in stats)
        profit_var.set(f"{total_profit:.2f}")

        sorted_fast = sorted(stats, key=lambda item: int(item.get("quantity_sold", 0)), reverse=True)

        for row in fast_tree.get_children():
            fast_tree.delete(row)

        for item in sorted_fast[:10]:
            fast_tree.insert("", "end", values=(
                item.get("description", ""),
                item.get("quantity_sold", 0),
                f"{float(item.get('revenue', 0)):.2f}",
                f"{float(item.get('profit', 0)):.2f}",
            ))

        products_with_sales = [item for item in stats if int(item.get("quantity_sold", 0)) > 0]
        sorted_slow = sorted(products_with_sales, key=lambda item: int(item.get("quantity_sold", 0)))

        for row in slow_tree.get_children():
            slow_tree.delete(row)

        for item in sorted_slow[:10]:
            slow_tree.insert("", "end", values=(
                item.get("description", ""),
                item.get("quantity_sold", 0),
                f"{float(item.get('revenue', 0)):.2f}",
                f"{float(item.get('profit', 0)):.2f}",
            ))

    except Exception as e:
        print(">>> Error loading product stats:", e)
        profit_var.set("--")
        for row in fast_tree.get_children():
            fast_tree.delete(row)
        for row in slow_tree.get_children():
            slow_tree.delete(row)

    try:
        response = requests.get(f"{SERVER_URL}/dashboard/low-stock?threshold=10", headers=get_headers(), timeout=5)
        response.raise_for_status()
        low_stock_list = response.json()

        if not isinstance(low_stock_list, list):
            low_stock_list = []

        for row in low_tree.get_children():
            low_tree.delete(row)

        for product in low_stock_list:
            low_tree.insert("", "end", values=(
                product.get("description", ""),
                product.get("barcode", ""),
                product.get("stock_qty", 0),
                f"{float(product.get('cost_price', 0)):.2f}",
                f"{float(product.get('selling_price', 0)):.2f}",
            ), tags=("low_stock",))

    except Exception as e:
        print(">>> Error loading low stock:", e)
        for row in low_tree.get_children():
            low_tree.delete(row)
