# Point of Sale (POS) System

A desktop Point of Sale (POS) application built with Python and Tkinter, deployed on a headless Ubuntu Server environment hosted on 
the VMWARE, using virtual display forwarding.

---

## 📸 Overview & Key Features

* **Desktop GUI on Headless Host:** Runs a Tkinter desktop user interface on an Ubuntu Server host via virtual display rendering (`Xvfb`).
* **Landing Admin Menu:** It has the following Cashier, View sales Add new products, View current stock, Edit products, Receive stock and Reprint receipt(not implemented yet).
* **Cashier Operations:** Checkout interface for managing transactions, cart items, totals calculation and receipt display.
* **View sales:** Show the sales that were done with Product ID, Timestamp and the total with date ranges e. form 01-09-2026 to 20-09-26.
* **Add new Products:** Add new products to the server, Barcode, Description (Name), QTY, Sell and Cost price and automatically update the inventory.
* **View Current products:** View product Names, quantity, Selling price, Cost,Id
* **Edit Products:** Change the product details, Name , Cost, Selling
* **Manager Dashboard :** Tracks real time sales it also categories sales by months, gives profit against cost, shows fast and slowing products and give low stock alert
* **Database Backend:** Secure storage for transaction logs, product catalog, product and system users login details.

---

## 🏗️ System Architecture

+-------------------------------------------------------+
|                    Ubuntu Server                      |
|                                                       |
|  Windows / PowerShell                                 |
|   └── Tkinter POS GUI                                 |
|                                                       |
|   Ubuntu server                                       |
|   └── Flask API: pos_api.py                           |
|   └── POS business logic: pos_logic.py                |
|   └── Data storage                                    |
+------------------------------------------------------+
| Display Stream over LAN                               |
v                                                       |
+-------------------------------------------------------+
|                   Client Terminal                     |
|            (Cashier Monitor / ADMIN)                  |
+-------------------------------------------------------+


---

## 🛠️ Tech Stack

* **Programming Language:** Python 3.x
* **GUI Framework:** Tkinter
* **Operating System:** Ubuntu Server
* **Display Server & Management:** The Ubuntu server runs the Flask API, POS business logic, and data storage in
headless mode, without a desktop environment or graphical display server. The
Tkinter GUI runs on a separate Windows client machine and communicates with the
Ubuntu Flask API over the local network using HTTP requests.

---

## 🚀 Setup & Installation

### 1. Install Dependencies on Ubuntu Server
Ensure Python, Tkinter:

udo apt update
sudo apt install -y python3 python3-venv python3-pip curl.
