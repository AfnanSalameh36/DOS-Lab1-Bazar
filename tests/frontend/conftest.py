import importlib.util
from pathlib import Path

import pytest

FRONTEND_APP = Path(__file__).resolve().parents[2] / "frontend" / "app.py"


@pytest.fixture
def frontend_app():
    """Load frontend/app.py as a module and return it."""
    spec = importlib.util.spec_from_file_location(
        "frontend_app", FRONTEND_APP
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config["TESTING"] = True
    return module