# config.py
import os

# Falls back to the known VM IP if no environment variable is set,
# so the app still runs out-of-the-box during development.
SERVER_URL = os.environ.get("POS_SERVER_URL", "http://192.168.149.131:5000")
