# pos_logic.py

def get_user_role(choice: str) -> str:
    """
    Given a choice string '1' or '2', return the role name.
    '1' -> 'admin'
    '2' -> 'cashier'
    Any other value -> 'unknown'
    """
    if choice == "1":
        return "admin"
    elif choice == "2":
        return "cashier"
    else:
        return "unknown"

# Simple in-memory "database" of users
# Format: username -> {"password": "...", "role": "..."}
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "cashier1": {"password": "cash123", "role": "cashier"},
}

def login(username: str, password: str) -> str | None:
    """
    If username/password match a user in USERS, return the role.
    Otherwise, return None.
    """
    user = USERS.get(username)
    if user is None:
        return None
    if user["password"] == password:
        return user["role"]
    return None

def add_product(name, category, cost_price, selling_price, stock_qty):
    """
    Add a new product to products.csv.
    - name: product name / description
    - category: optional, we'll use "General" if not provided
    - cost_price, selling_price: floats
    - stock_qty: initial stock (int)
    Returns the created product dict.
    """
    products = load_products()
    new_id = max(products.keys(), default=0) + 1
    product = {
        "product_id": new_id,
        "name": name,
        "category": "General",  # we can extend later
        "cost_price": float(cost_price),
        "selling_price": float(selling_price),
        "stock_qty": int(stock_qty),
    }
    products[new_id] = product
    save_products(products)
    return product
def load_products():
    products = {}

    if not os.path.exists(PRODUCTS_FILE):
        return products

    with open(PRODUCTS_FILE, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row["product_id"] = int(row["product_id"])
            row["cost_price"] = float(row["cost_price"])
            row["selling_price"] = float(row["selling_price"])
            row["stock_qty"] = int(row["stock_qty"])
            products[row["product_id"]] = row


def get_products_list():
    """
    Return all products as a list of dicts (not keyed by ID).
    Useful for sending to GUI as JSON.
    """
    products = load_products()
    return list(products.values())
