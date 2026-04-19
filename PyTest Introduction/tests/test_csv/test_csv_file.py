import pytest
import csv
from pathlib import Path


def read_csv():
    base_dir = Path(__file__).resolve().parents[2]
    file_path = base_dir / "src" / "data" / "data.csv"

    with open(file_path, newline="") as file:
        return list(csv.DictReader(file))


def test_file_not_empty():
    data = read_csv()
    assert len(data) > 0, "CSV file is empty"

@pytest.mark.validate_csv
def test_schema():
    data = read_csv()
    actual_columns = list(data[0].keys())

    expected_columns = ["id", "name", "age", "email", "is_active"]

    assert actual_columns == expected_columns, f"Schema mismatch: {actual_columns}"

@pytest.mark.validate_csv
@pytest.mark.skip(reason="Skipping age validation for now")
def test_age_range():
    data = read_csv()

    for row in data:
        age = int(row["age"])
        assert 0 <= age <= 100, f"Invalid age: {age}"


import re

@pytest.mark.validate_csv
def test_email_format():
    data = read_csv()

    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    for row in data:
        assert re.match(pattern, row["email"]), f"Invalid email: {row['email']}"

@pytest.mark.validate_csv
@pytest.mark.xfail(reason="Duplicates exist in data")
def test_no_duplicates():
    data = read_csv()

    seen = set()

    for row in data:
        row_tuple = tuple(row.items())

        assert row_tuple not in seen, "Duplicate row found"
        seen.add(row_tuple)


@pytest.mark.parametrize("id_val, expected", [
    ("1", "False"),
    ("2", "True")
])
def test_is_active(id_val, expected):
    data = read_csv()

    for row in data:
        if row["id"] == id_val:
            assert row["is_active"] == expected, f"Wrong is_active for id {id_val}"
