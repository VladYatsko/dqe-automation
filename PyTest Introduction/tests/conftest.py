import pytest
import pandas as pd


def pytest_collection_modifyitems(config, items):
    for item in items:
        if not item.own_markers:
            item.add_marker(pytest.mark.unmarked)
