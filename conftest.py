# conftest.py
"""
Shared pytest setup.

The key idea: every test runs inside one real database transaction that is
rolled back at the end, so nothing a test does -- adding a product, creating
a sale, inserting a user -- ever actually stays in the database. Your real
products and sales data are never touched by running the tests.
"""

import pytest
import pos_logic


class _NonClosingConnection:
    """
    Wraps a real database connection so that pos_logic.py's normal
    conn.commit() / conn.close() calls don't actually commit or close
    anything during a test. Only the fixture itself (below) ever commits
    or closes the real connection -- and it always rolls back instead.
    """

    def __init__(self, real_conn):
        self._real = real_conn

    def cursor(self, *args, **kwargs):
        return self._real.cursor(*args, **kwargs)

    def commit(self):
        pass  # intentionally does nothing during tests

    def rollback(self):
        self._real.rollback()

    def close(self):
        pass  # intentionally does nothing; the fixture closes the real connection


@pytest.fixture
def db(monkeypatch):
    """
    Use this fixture in any test that needs the database.
    Everything the test does is automatically undone afterward.
    """
    real_conn = pos_logic.get_connection()
    wrapper = _NonClosingConnection(real_conn)

    # Every function in pos_logic.py calls get_connection() -- patch that
    # one name so all of them transparently use our wrapped connection.
    monkeypatch.setattr(pos_logic, "get_connection", lambda: wrapper)

    yield real_conn

    real_conn.rollback()
    real_conn.close()
