# pos_logic.py
"""Business logic and data access, backed by PostgreSQL instead of CSV/JSON."""

import datetime
from werkzeug.security import check_password_hash

from db import get_connection, dict_cursor


# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------

def login(username: str, password: str) -> str | None:
    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute(
            "SELECT password_hash, role FROM users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        if check_password_hash(row["password_hash"], password):
            return row["role"]
        return None
    finally:
        conn.close()


# ------------------------------------------------------------
# PRODUCTS
# ------------------------------------------------------------

def _product_to_dict(row) -> dict:
    return {
        "product_id": row["product_id"],
        "barcode": row["barcode"],
        "description": row["description"],
        "selling_price": float(row["selling_price"]),
        "cost_price": float(row["cost_price"]),
        "stock_qty": row["stock_qty"],
    }


def get_products_list():
    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute("SELECT * FROM products ORDER BY product_id")
        return [_product_to_dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


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

    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute("SELECT 1 FROM products WHERE barcode = %s", (barcode,))
        if cur.fetchone():
            raise ValueError("A product with this barcode already exists.")

        cur.execute(
            """
            INSERT INTO products (barcode, description, selling_price, cost_price, stock_qty)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (barcode, description, selling_price, cost_price, stock_qty),
        )
        row = cur.fetchone()
        conn.commit()
        return _product_to_dict(row)
    finally:
        conn.close()


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

    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        existing = cur.fetchone()
        if existing is None:
            raise ValueError(f"Product with id {product_id} not found.")

        new_barcode = existing["barcode"]
        new_description = existing["description"]
        new_selling_price = existing["selling_price"]
        new_cost_price = existing["cost_price"]
        new_stock_qty = existing["stock_qty"]

        if barcode is not None:
            barcode = str(barcode).strip()
            if not barcode:
                raise ValueError("Barcode cannot be empty.")
            new_barcode = barcode

        if description is not None:
            description = str(description).strip()
            if not description:
                raise ValueError("Description cannot be empty.")
            new_description = description

        if selling_price is not None:
            selling_price = float(selling_price)
            if selling_price < 0:
                raise ValueError("Selling price cannot be negative.")
            new_selling_price = selling_price

        if cost_price is not None:
            cost_price = float(cost_price)
            if cost_price < 0:
                raise ValueError("Cost price cannot be negative.")
            new_cost_price = cost_price

        if stock_qty is not None:
            stock_qty = int(stock_qty)
            if stock_qty < 0:
                raise ValueError("Stock quantity cannot be negative.")
            new_stock_qty = stock_qty

        cur.execute(
            """
            UPDATE products
            SET barcode = %s, description = %s, selling_price = %s,
                cost_price = %s, stock_qty = %s
            WHERE product_id = %s
            RETURNING *
            """,
            (new_barcode, new_description, new_selling_price, new_cost_price, new_stock_qty, product_id),
        )
        row = cur.fetchone()
        conn.commit()
        return _product_to_dict(row)
    finally:
        conn.close()


def delete_product(product_id: int):
    if product_id is None:
        raise ValueError("product_id is required.")

    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute("SELECT 1 FROM products WHERE product_id = %s", (product_id,))
        if cur.fetchone() is None:
            raise ValueError(f"Product with id {product_id} not found.")

        cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        return {"status": "ok", "deleted_id": product_id}
    finally:
        conn.close()


def receive_stock(product_id: int, quantity_received: int):
    product_id = int(product_id)
    quantity_received = int(quantity_received)

    if quantity_received <= 0:
        raise ValueError("Received quantity must be greater than zero.")

    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        existing = cur.fetchone()
        if existing is None:
            raise ValueError(f"Product with id {product_id} not found.")

        cur.execute(
            """
            UPDATE products SET stock_qty = stock_qty + %s
            WHERE product_id = %s
            RETURNING *
            """,
            (quantity_received, product_id),
        )
        row = cur.fetchone()
        conn.commit()
        return _product_to_dict(row)
    finally:
        conn.close()


# ------------------------------------------------------------
# SALES
# ------------------------------------------------------------

def create_sale(items: list[dict]) -> dict:
    conn = get_connection()
    try:
        cur = dict_cursor(conn)

        processed_items = []
        total_amount = 0.0

        # Lock the rows we're about to update, so two simultaneous sales
        # can't both read the same stock_qty and oversell.
        for item in items:
            product_id = int(item["product_id"])
            quantity = int(item["quantity"])
            selling_price = float(item["selling_price"])

            cur.execute(
                "SELECT * FROM products WHERE product_id = %s FOR UPDATE",
                (product_id,),
            )
            product = cur.fetchone()
            if product is None:
                raise ValueError(f"Product {product_id} not found.")

            current_stock = product["stock_qty"]

            if quantity <= 0:
                raise ValueError(f"Quantity must be greater than zero for product {product_id}.")
            if quantity > current_stock:
                raise ValueError(
                    f"Not enough stock for product {product['description']}. "
                    f"Available: {current_stock}, requested: {quantity}."
                )

            line_total = quantity * selling_price
            total_amount += line_total

            cur.execute(
                "UPDATE products SET stock_qty = stock_qty - %s WHERE product_id = %s",
                (quantity, product_id),
            )

            processed_items.append({
                "product_id": product_id,
                "barcode": product["barcode"],
                "description": product["description"],
                "quantity": quantity,
                "selling_price": selling_price,
                "line_total": line_total,
            })

        cur.execute(
            "INSERT INTO sales (total_amount) VALUES (%s) RETURNING sale_id, \"timestamp\"",
            (round(total_amount, 2),),
        )
        sale_row = cur.fetchone()
        sale_id = sale_row["sale_id"]
        timestamp = sale_row["timestamp"].isoformat(timespec="seconds")

        for item in processed_items:
            cur.execute(
                """
                INSERT INTO sale_items
                    (sale_id, product_id, barcode, description, quantity, selling_price, line_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    sale_id,
                    item["product_id"],
                    item["barcode"],
                    item["description"],
                    item["quantity"],
                    item["selling_price"],
                    item["line_total"],
                ),
            )

        conn.commit()

        return {
            "sale_id": sale_id,
            "items": processed_items,
            "total_amount": round(total_amount, 2),
            "timestamp": timestamp,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _sale_row_to_dict(sale_row, items_rows) -> dict:
    return {
        "sale_id": sale_row["sale_id"],
        "timestamp": sale_row["timestamp"].isoformat(timespec="seconds"),
        "total_amount": float(sale_row["total_amount"]),
        "items": [
            {
                "product_id": r["product_id"],
                "barcode": r["barcode"],
                "description": r["description"],
                "quantity": r["quantity"],
                "selling_price": float(r["selling_price"]),
                "line_total": float(r["line_total"]),
            }
            for r in items_rows
        ],
    }


def load_sales() -> dict:
    """Return all sales as {sale_id: sale_dict}, matching the old JSON shape."""
    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute("SELECT * FROM sales ORDER BY sale_id")
        sales_rows = cur.fetchall()

        result = {}
        for sale_row in sales_rows:
            cur.execute(
                "SELECT * FROM sale_items WHERE sale_id = %s ORDER BY id",
                (sale_row["sale_id"],),
            )
            items_rows = cur.fetchall()
            result[sale_row["sale_id"]] = _sale_row_to_dict(sale_row, items_rows)
        return result
    finally:
        conn.close()


# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------

def get_today_sales_summary():
    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute(
            """
            SELECT COUNT(*) AS count, COALESCE(SUM(total_amount), 0) AS total
            FROM sales
            WHERE "timestamp"::date = CURRENT_DATE
            """
        )
        row = cur.fetchone()
        return {"total_amount": round(float(row["total"]), 2), "count": row["count"]}
    finally:
        conn.close()


def get_month_sales_summary():
    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute(
            """
            SELECT COUNT(*) AS count, COALESCE(SUM(total_amount), 0) AS total
            FROM sales
            WHERE date_trunc('month', "timestamp") = date_trunc('month', CURRENT_DATE)
            """
        )
        row = cur.fetchone()
        return {"total_amount": round(float(row["total"]), 2), "count": row["count"]}
    finally:
        conn.close()


def get_product_sales_stats(days: int = 30):
    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute(
            """
            SELECT
                si.product_id,
                p.description,
                p.barcode,
                p.stock_qty AS current_stock,
                p.cost_price,
                SUM(si.quantity) AS quantity_sold,
                SUM(si.line_total) AS revenue
            FROM sale_items si
            JOIN sales s ON s.sale_id = si.sale_id
            JOIN products p ON p.product_id = si.product_id
            WHERE s."timestamp" >= now() - (%s || ' days')::interval
            GROUP BY si.product_id, p.description, p.barcode, p.stock_qty, p.cost_price
            """,
            (days,),
        )
        rows = cur.fetchall()

        stats = {}
        for r in rows:
            quantity_sold = int(r["quantity_sold"])
            revenue = float(r["revenue"])
            cost_price = float(r["cost_price"])
            profit = revenue - (quantity_sold * cost_price)
            stats[r["product_id"]] = {
                "product_id": r["product_id"],
                "description": r["description"],
                "barcode": r["barcode"],
                "quantity_sold": quantity_sold,
                "revenue": revenue,
                "profit": profit,
                "current_stock": r["current_stock"],
            }
        return stats
    finally:
        conn.close()


def get_low_stock_products(threshold: int = 10):
    conn = get_connection()
    try:
        cur = dict_cursor(conn)
        cur.execute(
            """
            SELECT product_id, barcode, description, stock_qty, cost_price, selling_price
            FROM products
            WHERE stock_qty <= %s
            ORDER BY stock_qty ASC
            """,
            (threshold,),
        )
        rows = cur.fetchall()
        return [
            {
                "product_id": r["product_id"],
                "barcode": r["barcode"],
                "description": r["description"],
                "stock_qty": r["stock_qty"],
                "cost_price": float(r["cost_price"]),
                "selling_price": float(r["selling_price"]),
            }
            for r in rows
        ]
    finally:
        conn.close()
