import importlib.util
import sys
from pathlib import Path

import pytest

ORDER_DIR = Path(__file__).resolve().parents[2] / "order"


@pytest.fixture
def order_app(tmp_path, monkeypatch):
    """Load order/app.py with a temporary database."""
    # Make "from database import ..." point to order/database.py
    monkeypatch.syspath_prepend(str(ORDER_DIR))
    sys.modules.pop("database", None)
    import database

    # Use a temp DB so the real orders.db is never touched
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "orders.db")

    spec = importlib.util.spec_from_file_location(
        "order_app", ORDER_DIR / "app.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config["TESTING"] = True

    yield module

    sys.modules.pop("database", None)