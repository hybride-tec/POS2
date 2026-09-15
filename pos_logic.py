# pos_logic.py
# ------------------------------------------------------------
# Core POS logic.
#
# This file runs on the Ubuntu server.
# It contains:
#   1. User login rules
#   2. Product data rules
#   3. CSV file reading and writing
#   4. Sales storage in JSON
#   5. Dashboard helpers
#
# It does NOT contain GUI code.
# It does NOT contain Flask API route code.
# ------------------------------------------------------------

import csv
import json
import os
import datetime

# ------------------------------------------------------------
# DATA FILE LOCATIONS
# ------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.json")

PRODUCT_FIELDS = [
    "product_id",
    "barcode",
    "description",
    "selling_price",
    "cost_price",
    "stock_qty",
]


# ------------------------------------------------------------
# TEMPORARY USER DATA
# ------------------------------------------------------------

USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
    },
    "cashier1": {
        "password": "cash123",
        "role": "cashier",
    },
}


# ------------------------------------------------------------
# LOGIN FUNCTIONS
# ------------------------------------------------------------

def get_user_role(choice: str) -> str:
    if choice == "1":
        return "admin"
    elif choice == "2":
        return "cashier"
    return "unknown"


def login(username: str, password: str) -> str | None:
    user = USERS.get(username)
    if user is None:
        return None
    if user["password"] == password:
        return user["role"]
    return None


# ------------------------------------------------------------
# FILE / FOLDER FUNCTIONS
# ------------------------------------------------------------

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_products():
    ensure_data_dir()
    products = {}

    if not os.path.exists(PRODUCTS_FILE):
        return products

    with open(PRODUCTS_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["product_id"] = int(row["product_id"])
            row["selling_price"] = float(row["selling_price"])
            row["cost_price"] = float(row["cost_price"])
            row["stock_qty"] = int(row["stock_qty"])
            products[row["product_id"]] = row

    return products


def load_sales() -> dict:
    if not os.path.exists(SALES_FILE):
        return {}
    with open(SALES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_sales(sales: dict) -> None:
    with open(SALES_FILE, "w", encoding="utf-8") as f:
        json.dump(sales, f, indent=2, ensure_ascii=False)


def save_products(products: dict):
    ensure_data_dir()
    with open(PRODUCTS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=PRODUCT_FIELDS)
        writer.writeheader()
        writer.writerows(products.values())


# ------------------------------------------------------------
# PRODUCT FUNCTIONS
# ------------------------------------------------------------

def get_products_list():
    products = load_products()
    return list(products.values())


def add_product(
    barcode: str,
    description: str,
    selling_price: float,
    cost_price: float,
    stock_qty: int = 0,
):
    barcode = str(barcode).strip()
    description = str(description).strip()

    if not barcode:
        raise ValueError("Barcode is required.")
    if not description:
        raise ValueError("Product description is required.")

    selling_price = float(selling_price)
    cost_price = float(cost_price)
    stock_qty = int(stock_qty)

    if selling_price < 0:
        raise ValueError("Selling price cannot be negative.")
    if cost_price < 0:
        raise ValueError("Cost price cannot be negative.")
    if stock_qty < 0:
        raise ValueError("Stock quantity cannot be negative.")

    products = load_products()

    for existing_product in products.values():
        if existing_product["barcode"] == barcode:
            raise ValueError("A product with this barcode already exists.")

    new_product_id = max(products.keys(), default=0) + 1

    product = {
        "product_id": new_product_id,
        "barcode": barcode,
        "description": description,
        "selling_price": selling_price,
        "cost_price": cost_price,
        "stock_qty": stock_qty,
    }

    products[new_product_id] = product
    save_products(products)
    return product


def update_product(
    product_id: int,
    barcode: str | None = None,
    description: str | None = None,
    selling_price: float | None = None,
    cost_price: float | None = None,
    stock_qty: int | None = None,
):
    if product_id is None:
        raise ValueError("product_id is required.")

    products = load_products()
    if product_id not in products:
        raise ValueError(f"Product with id {product_id} not found.")

    product = products[product_id]

    if barcode is not None:
        barcode = str(barcode).strip()
        if not barcode:
            raise ValueError("Barcode cannot be empty.")
        product["barcode"] = barcode

    if description is not None:
        description = str(description).strip()
        if not description:
            raise ValueError("Description cannot be empty.")
        product["description"] = description

    if selling_price is not None:
        selling_price = float(selling_price)
        if selling_price < 0:
            raise ValueError("Selling price cannot be negative.")
        product["selling_price"] = selling_price

    if cost_price is not None:
        cost_price = float(cost_price)
        if cost_price < 0:
            raise ValueError("Cost price cannot be negative.")
        product["cost_price"] = cost_price

    if stock_qty is not None:
        stock_qty = int(stock_qty)
        if stock_qty < 0:
            raise ValueError("Stock quantity cannot be negative.")
        product["stock_qty"] = stock_qty

    save_products(products)
    return product


def delete_product(product_id: int):
    if product_id is None:
        raise ValueError("product_id is required.")

    products = load_products()
    if product_id not in products:
        raise ValueError(f"Product with id {product_id} not found.")

    del products[product_id]
    save_products(products)
    return {"status": "ok", "deleted_id": product_id}


def receive_stock(product_id: int, quantity_received: int):
    product_id = int(product_id)
    quantity_received = int(quantity_received)

    if quantity_received <= 0:
        raise ValueError("Received quantity must be greater than zero.")

    products = load_products()
    if product_id not in products:
        raise ValueError(f"Product with id {product_id} not found.")

    product = products[product_id]
    current_stock = int(product.get("stock_qty", 0))
    product["stock_qty"] = current_stock + quantity_received

    save_products(products)
    return product


def create_sale(items: list[dict]) -> dict:
    products = load_products()
    processed_items = []
    total_amount = 0.0

    for item in items:
        product_id = int(item["product_id"])
        quantity = int(item["quantity"])
        selling_price = float(item["selling_price"])

        if product_id not in products:
            raise ValueError(f"Product {product_id} not found.")

        product = products[product_id]
        current_stock = int(product.get("stock_qty", 0))

        if quantity <= 0:
            raise ValueError(f"Quantity must be greater than zero for product {product_id}.")
        if quantity > current_stock:
            raise ValueError(
                f"Not enough stock for product {product['description']}. "
                f"Available: {current_stock}, requested: {quantity}."
            )

        line_total = quantity * selling_price
        total_amount += line_total
        product["stock_qty"] = current_stock - quantity

        processed_items.append({
            "product_id": product_id,
            "barcode": product["barcode"],
            "description": product["description"],
            "quantity": quantity,
            "selling_price": selling_price,
            "line_total": line_total,
        })

    save_products(products)
    sales = load_sales()

    if not sales:
        next_id = 1
    else:
        next_id = max(int(k) for k in sales.keys()) + 1

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")

    sale_record = {
        "sale_id": next_id,
        "items": processed_items,
        "total_amount": round(total_amount, 2),
        "timestamp": timestamp,
    }

    sales[next_id] = sale_record
    save_sales(sales)
    return sale_record


# ------------------------------------------------------------
# DASHBOARD FUNCTIONS
# ------------------------------------------------------------

def get_today_sales_summary():
    sales = load_sales()
    today = datetime.datetime.now().date()
    total_amount = 0.0
    count = 0

    for sale in sales.values():
        ts = sale.get("timestamp", "")
        if not ts:
            continue
        try:
            sale_date = datetime.datetime.fromisoformat(ts).date()
        except ValueError:
            continue

        if sale_date == today:
            total_amount += sale.get("total_amount", 0)
            count += 1

    return {
        "total_amount": round(total_amount, 2),
        "count": count,
    }


def get_month_sales_summary():
    sales = load_sales()
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    total_amount = 0.0
    count = 0

    for sale in sales.values():
        ts = sale.get("timestamp", "")
        if not ts:
            continue
        try:
            sale_dt = datetime.datetime.fromisoformat(ts)
        except ValueError:
            continue

        if sale_dt.year == current_year and sale_dt.month == current_month:
            total_amount += sale.get("total_amount", 0)
            count += 1

    return {
        "total_amount": round(total_amount, 2),
        "count": count,
    }


def get_product_sales_stats(days: int = 30):
    sales = load_sales()
    products = load_products()
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=days)
    stats = {}

    for sale in sales.values():
        ts = sale.get("timestamp", "")
        if not ts:
            continue
        try:
            sale_dt = datetime.datetime.fromisoformat(ts)
        except ValueError:
            continue

        if sale_dt < cutoff:
            continue

        for item in sale.get("items", []):
            pid = item.get("product_id")
            if pid is None:
                continue

            product = products.get(pid)
            if not product:
                continue

            qty = int(item.get("quantity", 0))
            selling_price = float(item.get("selling_price", 0))
            cost_price = float(product.get("cost_price", 0))

            if pid not in stats:
                stats[pid] = {
                    "product_id": pid,
                    "description": product["description"],
                    "barcode": product["barcode"],
                    "quantity_sold": 0,
                    "revenue": 0.0,
                    "profit": 0.0,
                    "current_stock": int(product.get("stock_qty", 0)),
                }

            stats[pid]["quantity_sold"] += qty
            stats[pid]["revenue"] += qty * selling_price
            stats[pid]["profit"] += qty * (selling_price - cost_price)

    return stats


def get_low_stock_products(threshold: int = 10):
    products = load_products()
    low_stock = []

    for product in products.values():
        qty = int(product.get("stock_qty", 0))
        if qty <= threshold:
            low_stock.append({
                "product_id": product["product_id"],
                "barcode": product["barcode"],
                "description": product["description"],
                "stock_qty": qty,
                "cost_price": float(product.get("cost_price", 0)),
                "selling_price": float(product.get("selling_price", 0)),
            })

    low_stock.sort(key=lambda p: p["stock_qty"])
    return low_stock
