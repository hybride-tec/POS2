# server_api.py
from flask import Flask, request, jsonify
import pos_logic

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    role = pos_logic.login(username, password)
    if role:
        return jsonify({"role": role}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route("/products", methods=["GET"])
def get_products():
    products = pos_logic.get_products_list()
    return jsonify(products), 200


@app.route("/product", methods=["POST"])
def add_product():
    try:
        data = request.get_json(silent=True) or {}
    except Exception:
        data = {}

    barcode = data.get("barcode", "")
    description = data.get("description", "")
    selling_price = data.get("selling_price", 0)
    cost_price = data.get("cost_price", 0)

    try:
        product = pos_logic.add_product(
            barcode,
            description,
            selling_price,
            cost_price,
        )
        return jsonify({"status": "ok", "product": product}), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/product/<int:product_id>", methods=["PUT", "DELETE"])
def change_or_delete_product(product_id):
    if request.method == "DELETE":
        try:
            result = pos_logic.delete_product(product_id)
            return jsonify(result), 200
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except Exception as error:
            return jsonify({"error": f"Server error: {error}"}), 500

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
@app.route("/product/<int:product_id>/receive-stock", methods=["POST"])
def receive_stock(product_id):
    data = request.get_json(silent=True) or {}

    try:
        quantity_received = int(data.get("quantity_received", 0))
        product = pos_logic.receive_stock(product_id, quantity_received)

        return jsonify({
            "status": "ok",
            "message": "Stock received successfully.",
            "product": product,
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500

@app.route("/sale", methods=["POST"])
def create_sale():
    data = request.get_json(silent=True) or {}

    items = data.get("items", [])

    if not items:
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
def list_sales():
    try:
        sales = pos_logic.load_sales()

        # Convert dict to list and sort by sale_id descending (newest first)
        sales_list = sorted(
            sales.values(),
            key=lambda s: int(s.get("sale_id", 0)),
            reverse=True,
        )

        return jsonify(sales_list), 200

    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/sales/<int:sale_id>", methods=["GET"])
def get_sale(sale_id):
    try:
        sales = pos_logic.load_sales()

        if sale_id not in sales:
            return jsonify({"error": f"Sale {sale_id} not found."}), 404

        return jsonify(sales[sale_id]), 200

    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500
@app.route("/dashboard/today", methods=["GET"])
def dashboard_today():
    try:
        summary = pos_logic.get_today_sales_summary()
        return jsonify(summary), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/dashboard/month", methods=["GET"])
def dashboard_month():
    try:
        summary = pos_logic.get_month_sales_summary()
        return jsonify(summary), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/dashboard/product-stats", methods=["GET"])
def dashboard_product_stats():
    days = 30  # last 30 days
    try:
        stats = pos_logic.get_product_sales_stats(days=days)
        # Convert dict to list
        stats_list = sorted(
            stats.values(),
            key=lambda x: x["quantity_sold"],
            reverse=True,
        )
        return jsonify(stats_list), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500


@app.route("/dashboard/low-stock", methods=["GET"])
def dashboard_low_stock():
    threshold = 10
    try:
        low_stock = pos_logic.get_low_stock_products(threshold=threshold)
        return jsonify(low_stock), 200
    except Exception as error:
        return jsonify({"error": f"Server error: {error}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
