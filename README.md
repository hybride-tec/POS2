# POS System

A full-stack Point of Sale (POS) system built with Python. It combines a **Tkinter desktop client** for cashiers and managers with a **Flask REST API** backend, self-hosted on an Ubuntu Server VM.

> This is a personal portfolio project, built to practice full-stack Python development, client-server architecture, and basic Linux/VM administration.

## Screenshots

![Login screen/Lending screen..](Imgs/LENDING%20SCREEN.png)
![Main Menu....................](Imgs/MAIN%20MENU.png)
![Cashier window...............](Imgs/CASHIER%20WINDOW.png)
![Cashier checkout.............](Imgs/CHECK%20OUT.png)
![View current stock...........](Imgs/CURRENT%20STOCK.png)
![Receive stock................](Imgs/RECEIVE%20STOCK.png)
![Add new product..............](Imgs/ADD%20NEW%20PRODUCT.png)
![Manager dashboard............](Imgs/MANAGER%20DASHBOARD.png)


## Features

- **Role-based login** — admin and cashier accounts see different screens. Cashiers are routed straight to the checkout window; admins get full management access.
- **Cashier checkout** — product search, editable cart, cash/card payment, automatic change calculation, and a printable-style receipt popup.
- **Product management** — add, view, edit, and delete products (barcode, description, cost price, selling price, stock quantity).
- **Stock receiving** — add received stock to existing products and see live quantity updates.
- **Sales history** — browse past sales with date-range filtering, view line-item detail per sale, and export filtered sales to CSV.
- **Manager dashboard** — today's and this month's sales totals, profit against cost, fast-moving and slow-moving products (last 30 days), and a low-stock alert list.
- **Secure authentication** — passwords are hashed server-side (`werkzeug.security`), never stored or compared in plaintext.
- **Configurable server address** — the client's server URL is read from an environment variable with a sane default, instead of being hardcoded.

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop client | Python, Tkinter |
| Backend API | Python, Flask |
| Data storage | PostgreSQL |
| Authentication | `werkzeug.security` password hashing |
| Hosting | Self-hosted on Ubuntu Server (VMware VM) |
| Version control | Git / GitHub |

## Architecture

```
┌─────────────────────┐         HTTP / JSON          ┌──────────────────────┐
│   Tkinter Client     │ ────────────────────────────▶│     Flask API          │
│   (pos_gui.py +      │◀──────────────────────────── │   (server_api.py)     │
│    modules)          │                               │                      │
└─────────────────────┘                               └──────────┬───────────┘
                                                                   │
                                                                   ▼
                                                        ┌──────────────────────┐
                                                        │   pos_logic.py        │
                                                        │ (business logic +     │
                                                        │  auth)                │
                                                        └──────────┬───────────┘
                                                                   │
                                                                   ▼
                                                        ┌──────────────────────┐
                                                        │  data/products.csv    │
                                                        │  sales.json           │
                                                        └──────────────────────┘
```

The client and server are deliberately separated: the Tkinter app never touches data directly, it only talks to the Flask API over HTTP. This means multiple checkout terminals could run against the same server, and the backend could be swapped to a different database later without touching the UI code.

## Project Structure

```
.
├── pos_gui.py          # Client entry point: login screen, admin menu, role routing
├── config.py           # Client configuration (server URL)
├── products.py         # Add / view / edit product windows
├── stock.py            # Receive stock window
├── cashier.py          # Cashier checkout, payment, and receipt windows
├── sales.py            # View sales, date filtering, CSV export
├── manager.py          # Manager login and dashboard
├── server_api.py       # Flask API routes
├── pos_logic.py        # Business logic, data access, authentication
├── data/
│   └── products.csv    # Product data store
├── .env.example         # Template for required environment variables
└── requirements.txt     # Python dependencies
```

## Getting Started

### Prerequisites
- Python 3.10+
- `pip`

### 1. Clone the repository
```bash
git clone https://github.com/hybride-tec/POS2.git
cd POS2
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy the example file and fill in your own values:
```bash
cp .env.example .env
```
Edit `.env`:
```
ADMIN_PASSWORD=choose_a_strong_password
CASHIER1_PASSWORD=choose_a_strong_password
```

### 4. Set up the database
Install PostgreSQL, then create the database and a user:
```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql
```
Inside psql:
```sql
CREATE DATABASE pos_db;
CREATE USER pos_user WITH PASSWORD 'choose_a_password';
GRANT ALL PRIVILEGES ON DATABASE pos_db TO pos_user;
\c pos_db
GRANT ALL ON SCHEMA public TO pos_user;
\q
```
Add the matching `DB_*` values to your `.env`, then run the setup script once to create the tables and migrate any existing data:
```bash
python3 init_db.py

### 5. Run the desktop client
On the same machine or a different one on the network:
```bash
python pos_gui.py
```
By default, the client points at a preset server address in `config.py`. To point it at a different server without editing code, set an environment variable before launching:
```bash
# Windows (PowerShell)
$env:POS_SERVER_URL = "http://your-server-ip:5000"
python pos_gui.py

# Linux / macOS
export POS_SERVER_URL="http://your-server-ip:5000"
python pos_gui.py
```

### 6. Log in
- **Admin:** username `admin`, password whatever you set as `ADMIN_PASSWORD`
- **Cashier:** username `cashier1`, password whatever you set as `CASHIER1_PASSWORD`

## What I Learned Building This

- Structuring a client-server application so the UI and business logic stay independent
- Debugging real-world issues: a misplaced `app.run()` that silently broke most of the API's routes, Windows/Unix line-ending mismatches causing subtle indentation bugs, and a missing `.env` loader that made password changes silently ineffective
- Replacing hardcoded credentials with server-side, hashed authentication
- Refactoring a single 2,000+ line file into focused, maintainable modules
- Managing a Python application across two machines (Ubuntu server, Windows client) with Git

## Possible Future Improvements

- Move from CSV/JSON storage to a proper database (SQLite or PostgreSQL)
- Add automated tests for cart totals, stock deduction, and authentication
- Containerize the Flask API with Docker for easier deployment
- Add a proper cashier-facing menu instead of routing straight to the checkout window
- Implement the still-placeholder features (reprint receipt, sales report, stock quantity lookup)

## License

See [LICENSE](LICENSE) for details.
