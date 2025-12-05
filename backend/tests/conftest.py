"""Pytest configuration for VitalSigns tests."""
import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async backend."""
    return "asyncio"
