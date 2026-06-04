"""Pytest configuration.

Point the app at an in-memory database before it is imported so the app
lifespan does not create a stray SQLite file during the test run. Individual
tests still override the DB dependency with their own temporary database.
"""

import os

os.environ.setdefault("NSM_DATABASE_URL", "sqlite:///:memory:")
