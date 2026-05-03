import pytest
import csv

def pytest_collection_modifyitems(session, config, items):
    for item in items:
        if not item.own_markers:
            item.add_marker(pytest.mark.unmarked)

@pytest.fixture(scope="session")
def read_csv(request):
    path_to_file = getattr(request, "param", "data.csv")
    with open(path_to_file, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
    return reader


@pytest.fixture(scope="session")
def validate_schema():
    def _validate(actual_schema, expected_schema):
        assert actual_schema == expected_schema, f"Schema mismatch: {actual_schema} != {expected_schema}"
    return _validate
