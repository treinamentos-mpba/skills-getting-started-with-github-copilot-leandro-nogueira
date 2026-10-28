from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as backend


@pytest.fixture
def activity_data(monkeypatch):
    data = deepcopy(backend.activities)
    monkeypatch.setattr(backend, "activities", data)
    return data


@pytest.fixture
def client(activity_data):
    with TestClient(backend.app) as test_client:
        yield test_client
