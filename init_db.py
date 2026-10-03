# init_db.py
"""
Run once to set up the database:
  1. Creates the tables (from schema.sql).
  2. Seeds the admin and cashier1 users with hashed passwords from .env.
  3. Imports existing data from data/products.csv and sales.json, if present.

Usage:
    python3 init_db.py
"""

import os
import csv
import json
import datetime

from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

from db import get_connection

load_dotenv()

PRODUCTS_CSV = os.path.join(os.path.dirname(__file__), "data", "products.csv")
SALES_JSON = os.path.join(os.path.dirname(__file__), "sales.json")


def run_schema(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print("Schema created (or already existed).")


def seed_users(conn):
    admin_password = os.environ.get("ADMIN_PASSWORD", "changeme")
    cashier_password = os.environ.get("CASHIER1_PASSWORD", "changeme")

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, 'admin')
        ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash
        """,
        ("admin", generate_password_hash(admin_password)),
    )
    cur.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, 'cashier')
        ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash
        """,
        ("cashier1", generate_password_hash(cashier_password)),
    )
    conn.commit()
    print("Users seeded: admin, cashier1 (passwords from .env).")


def migrate_products(conn):
    if not os.path.exists(PRODUCTS_CSV):
        print(f"No products.csv found at {PRODUCTS_CSV}, skipping product migration.")
        return

    cur = conn.cursor()
    count = 0
    with open(PRODUCTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                """
                INSERT INTO products (barcode, description, selling_price, cost_price, stock_qty)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (barcode) DO NOTHING
                """,
                (
                    row["barcode"],
                    row["description"],
                    float(row["selling_price"]),
                    float(row["cost_price"]),
                    int(row["stock_qty"]),
                ),
            )
            count += 1
    conn.commit()
    print(f"Migrated {count} products from products.csv.")


def migrate_sales(conn):
    if not os.path.exists(SALES_JSON):
        print(f"No sales.json found at {SALES_JSON}, skipping sales migration.")
        return

    with open(SALES_JSON, "r", encoding="utf-8") as f:
        try:
            sales = json.load(f)
        except json.JSONDecodeError:
            print("sales.json was empty or invalid, skipping.")
            return

    cur = conn.cursor()

    # Map old barcodes to new product_ids, in case IDs shifted during migration.
    cur.execute("SELECT product_id, barcode FROM products")
    barcode_to_id = {row[1]: row[0] for row in cur.fetchall()}

    count = 0
    for sale in sales.values():
        timestamp_str = sale.get("timestamp")
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
        except (TypeError, ValueError):
            timestamp = datetime.datetime.now()

        cur.execute(
            """
            INSERT INTO sales (total_amount, "timestamp")
            VALUES (%s, %s)
            RETURNING sale_id
            """,
            (sale.get("total_amount", 0), timestamp),
        )
        new_sale_id = cur.fetchone()[0]

        for item in sale.get("items", []):
            barcode = item.get("barcode")
            product_id = barcode_to_id.get(barcode)
            if product_id is None:
                # Product no longer exists; skip this line item rather than fail the whole migration.
                print(f"  Skipping sale item for missing barcode: {barcode}")
                continue

            cur.execute(
                """
                INSERT INTO sale_items
                    (sale_id, product_id, barcode, description, quantity, selling_price, line_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    new_sale_id,
                    product_id,
                    barcode,
                    item.get("description", ""),
                    item.get("quantity", 0),
                    item.get("selling_price", 0),
                    item.get("line_total", 0),
                ),
            )
        count += 1

    conn.commit()
    print(f"Migrated {count} sales from sales.json.")


def main():
    conn = get_connection()
    try:
        run_schema(conn)
        seed_users(conn)
        migrate_products(conn)
        migrate_sales(conn)
        print("\nDatabase setup complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
