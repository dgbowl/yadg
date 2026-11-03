from pathlib import Path

import pytest


@pytest.fixture
def datadir(request) -> Path:
    """Get the read-only test data folder from a module."""
    return Path(request.module.__file__).with_suffix("")
