import os
from functools import wraps
from flask import Flask, jsonify, request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import pos_logic

app = Flask(__name__)

# Used to sign and verify login tokens. In production this should be a long,
# random value kept secret in .env -- it falls back to a dev-only default so
# the app still runs if it's missing, but that fallback must never be used
# for a real deployment.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")
serializer = URLSafeTimedSerializer(SECRET_KEY)

TOKEN_MAX_AGE_SECONDS = 8 * 60 * 60  # 8 hours


def generate_token(username: str, role: str) -> str:
    return serializer.dumps({"username": username, "role": role})


def verify_token(token: str):
    """Return {'username':..., 'role':...} if valid, else None."""
    try:
        return serializer.loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None


def require_auth(role=None):
    """
    Decorator for routes that need a valid token.
    If `role` is given (e.g. "admin"), the token's role must match it too.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid Authorization header."}), 401

            token = auth_header[len("Bearer "):]
            payload = verify_token(token)
            if payload is None:
                return jsonify({"error": "Invalid or expired token. Please log in again."}), 401

            if role is not None and payload.get("role") != role:
                return jsonify({"error": "You don't have permission to do that."}), 403

            request.user = payload  # available inside the route if needed
            return f(*args, **kwargs)
        return wrapped
    return decorator


@app.get("/health")
def health():
    return {"status": "ok"}, 200


@app.route('/')
def index():
    return {
        "status": "online",
        "message": "Inventory API is running",
        "endpoints": ["/products", "/login", "/sale", "/dashboard/today"]
    }


# ------------------------------------------------------------
# LOGIN (no auth required -- this is how you GET a token)
# ------------------------------------------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "")
    password = data.get("password", "")

    role = pos_logic.login(username, password)

    if role:
        token = generate_token(username, role)
        return jsonify({"role": role, "token": token}), 200

    return jsonify({"error": "Invalid username or password"}), 401


# ------------------------------------------------------------
# PRODUCTS
# ------------------------------------------------------------

@app.route("/products", methods=["GET"])
@require_auth()  # any logged-in user (admin or cashier) can view products
def get_products():
    try:
        products = pos_logic.get_products_list()
        return jsonify(products), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/product", methods=["POST"])
@require_auth(role="admin")
def add_product():
    data = request.get_json(silent=True) or {}

    barcode = data.get("barcode", "")
    description = data.get("description", "")
    selling_price = data.get("selling_price", 0)
    cost_price = data.get("cost_price", 0)
    stock_qty = data.get("stock_qty", 0)

    try:
        product = pos_logic.add_product(
            barcode=barcode,
            description=description,
            selling_price=selling_price,
            cost_price=cost_price,
            stock_qty=stock_qty,
        )
        return jsonify({"status": "ok", "product": product}), 201
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/product/<int:product_id>", methods=["PUT"])
@require_auth(role="admin")
def update_product(product_id):
    data = request.get_json(silent=True) or {}

    try:
        product = pos_logic.update_product(
            product_id=product_id,
            barcode=data.get("barcode"),
            description=data.get("description"),
            selling_price=data.get("selling_price"),
            cost_price=data.get("cost_price"),
            stock_qty=data.get("stock_qty"),
        )
        return jsonify({"status": "ok", "product": product}), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/product/<int:product_id>", methods=["DELETE"])
@require_auth(role="admin")
def delete_product(product_id):
    try:
        result = pos_logic.delete_product(product_id)
        return jsonify(result), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


# ------------------------------------------------------------
# RECEIVE STOCK
# ------------------------------------------------------------

@app.route("/product/<int:product_id>/receive-stock", methods=["POST"])
@require_auth(role="admin")
def receive_stock(product_id):
    data = request.get_json(silent=True) or {}

    try:
        quantity_received = int(data.get("quantity_received", 0))
        product = pos_logic.receive_stock(
            product_id=product_id,
            quantity_received=quantity_received,
        )
        return jsonify({
            "status": "ok",
            "message": "Stock received successfully.",
            "product": product,
        }), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


# ------------------------------------------------------------
# SALES / CHECKOUT
# ------------------------------------------------------------

@app.route("/sale", methods=["POST"])
@require_auth()  # admin or cashier can record a sale
def create_sale():
    data = request.get_json(silent=True) or {}

    items = data.get("items", [])

    if not isinstance(items, list) or not items:
        return jsonify({"error": "No items in the sale."}), 400

    try:
        sale = pos_logic.create_sale(items)
        return jsonify({
            "status": "ok",
            "message": "Sale created successfully.",
            "sale": sale,
        }), 201
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/sales", methods=["GET"])
@require_auth(role="admin")
def list_sales():
    try:
        sales = pos_logic.load_sales()
        sales_list = sorted(
            sales.values(),
            key=lambda sale: int(sale.get("sale_id", 0)),
            reverse=True,
        )
        return jsonify(sales_list), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/sales/<int:sale_id>", methods=["GET"])
@require_auth(role="admin")
def get_sale(sale_id):
    try:
        sales = pos_logic.load_sales()
        sale = sales.get(str(sale_id)) or sales.get(sale_id)
        if sale is None:
            return jsonify({"error": f"Sale {sale_id} not found."}), 404
        return jsonify(sale), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


# ------------------------------------------------------------
# MANAGER DASHBOARD
# ------------------------------------------------------------

@app.route("/dashboard/today", methods=["GET"])
@require_auth(role="admin")
def dashboard_today():
    try:
        summary = pos_logic.get_today_sales_summary()
        return jsonify(summary), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/dashboard/month", methods=["GET"])
@require_auth(role="admin")
def dashboard_month():
    try:
        summary = pos_logic.get_month_sales_summary()
        return jsonify(summary), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/dashboard/product-stats", methods=["GET"])
@require_auth(role="admin")
def dashboard_product_stats():
    try:
        days_text = request.args.get("days", "30")
        days = int(days_text)
        if days <= 0:
            days = 30

        stats = pos_logic.get_product_sales_stats(days=days)
        stats_list = sorted(
            stats.values(),
            key=lambda item: item.get("quantity_sold", 0),
            reverse=True,
        )
        return jsonify(stats_list), 200
    except ValueError:
        return jsonify({"error": "days must be a whole number."}), 400
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/dashboard/low-stock", methods=["GET"])
@require_auth(role="admin")
def dashboard_low_stock():
    try:
        threshold_text = request.args.get("threshold", "10")
        threshold = int(threshold_text)
        if threshold < 0:
            threshold = 10

        low_stock = pos_logic.get_low_stock_products(threshold=threshold)
        return jsonify(low_stock), 200
    except ValueError:
        return jsonify({"error": "threshold must be a whole number."}), 400
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


# ------------------------------------------------------------
# START SERVER
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
