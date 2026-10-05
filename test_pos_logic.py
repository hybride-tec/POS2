# tests/test_pos_logic.py
"""
Tests for pos_logic.py -- the business logic layer.

Run with:  pytest
Run just this file:  pytest tests/test_pos_logic.py
Run with more detail:  pytest -v
"""

import pytest
from werkzeug.security import generate_password_hash

import pos_logic


# ------------------------------------------------------------
# PRODUCTS
# ------------------------------------------------------------

def test_add_product_appears_in_products_list(db):
    pos_logic.add_product(
        barcode="TEST-0001",
        description="Test Product",
        selling_price=19.99,
        cost_price=10.00,
        stock_qty=5,
    )

    products = pos_logic.get_products_list()
    barcodes = [p["barcode"] for p in products]

    assert "TEST-0001" in barcodes


def test_add_product_rejects_negative_selling_price(db):
    with pytest.raises(ValueError):
        pos_logic.add_product(
            barcode="TEST-0002",
            description="Bad Price Product",
            selling_price=-5.00,
            cost_price=1.00,
            stock_qty=1,
        )


def test_add_product_rejects_duplicate_barcode(db):
    pos_logic.add_product(
        barcode="TEST-0003",
        description="First Product",
        selling_price=10.00,
        cost_price=5.00,
        stock_qty=1,
    )

    with pytest.raises(ValueError):
        pos_logic.add_product(
            barcode="TEST-0003",  # same barcode again
            description="Duplicate Product",
            selling_price=20.00,
            cost_price=10.00,
            stock_qty=1,
        )


def test_update_product_changes_values(db):
    product = pos_logic.add_product(
        barcode="TEST-0004",
        description="Original Name",
        selling_price=10.00,
        cost_price=5.00,
        stock_qty=1,
    )

    updated = pos_logic.update_product(
        product_id=product["product_id"],
        description="Updated Name",
        selling_price=15.00,
    )

    assert updated["description"] == "Updated Name"
    assert updated["selling_price"] == 15.00
    assert updated["cost_price"] == 5.00  # unchanged fields stay the same


def test_receive_stock_increases_quantity(db):
    product = pos_logic.add_product(
        barcode="TEST-0005",
        description="Stock Product",
        selling_price=10.00,
        cost_price=5.00,
        stock_qty=10,
    )

    updated = pos_logic.receive_stock(product["product_id"], quantity_received=25)

    assert updated["stock_qty"] == 35


# ------------------------------------------------------------
# SALES
# ------------------------------------------------------------

def test_create_sale_deducts_stock(db):
    product = pos_logic.add_product(
        barcode="TEST-0006",
        description="Sale Product",
        selling_price=10.00,
        cost_price=5.00,
        stock_qty=20,
    )

    pos_logic.create_sale([
        {"product_id": product["product_id"], "quantity": 3, "selling_price": 10.00},
    ])

    products = pos_logic.get_products_list()
    updated = next(p for p in products if p["product_id"] == product["product_id"])

    assert updated["stock_qty"] == 17  # 20 - 3


def test_create_sale_calculates_correct_total(db):
    product = pos_logic.add_product(
        barcode="TEST-0007",
        description="Total Test Product",
        selling_price=12.50,
        cost_price=6.00,
        stock_qty=10,
    )

    sale = pos_logic.create_sale([
        {"product_id": product["product_id"], "quantity": 4, "selling_price": 12.50},
    ])

    assert sale["total_amount"] == 50.00  # 4 x 12.50


def test_create_sale_rejects_insufficient_stock(db):
    product = pos_logic.add_product(
        barcode="TEST-0008",
        description="Low Stock Product",
        selling_price=10.00,
        cost_price=5.00,
        stock_qty=2,
    )

    with pytest.raises(ValueError):
        pos_logic.create_sale([
            {"product_id": product["product_id"], "quantity": 5, "selling_price": 10.00},
        ])


# ------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------

def _create_test_user(db, username, password, role):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
        (username, generate_password_hash(password), role),
    )


def test_login_with_correct_password_returns_role(db):
    _create_test_user(db, "pytest_cashier", "correct-password-123", "cashier")

    role = pos_logic.login("pytest_cashier", "correct-password-123")

    assert role == "cashier"


def test_login_with_wrong_password_returns_none(db):
    _create_test_user(db, "pytest_cashier2", "correct-password-123", "cashier")

    role = pos_logic.login("pytest_cashier2", "totally-wrong-password")

    assert role is None


def test_login_with_unknown_username_returns_none(db):
    role = pos_logic.login("this_user_does_not_exist", "anything")

    assert role is None
