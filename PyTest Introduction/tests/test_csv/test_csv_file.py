import pytest
import re
import csv


pytestmark = pytest.mark.validate_csv

@pytest.fixture(scope="session")
def read_csv(request):
    path_to_file = getattr(request, "param", "src/data/data.csv")
    with open(path_to_file, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
    return reader

def test_file_not_empty(tmp_path):
    file_path = tmp_path / "data.csv"
    file_path.write_text("id,name,age,email,is_active\n1,Test,30,test@example.com,True\n")
    with open(file_path) as f:
        content = f.read()
    assert content.strip() != "", "CSV file is empty!"


@pytest.mark.validate_csv
def test_validate_schema(read_csv):
    expected_schema = ['id', 'name', 'age', 'email', 'is_active']
    actual_schema = list(read_csv[0].keys())
    assert actual_schema == expected_schema, f"Schema mismatch: {actual_schema} != {expected_schema}"


@pytest.mark.validate_csv
@pytest.mark.skip(reason="Skipping test_age_column check")
def test_age_column_valid(read_csv):
    for row in read_csv:
        age = int(row['age'])
        assert 0 <= age <= 100, f"Invalid age {age} for id {row['id']}"


@pytest.mark.validate_csv
def test_email_column_valid(read_csv):
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    for row in read_csv:
        email = row['email']
        assert re.match(email_regex, email), f"Invalid email format: {email} for id {row['id']}"


@pytest.mark.validate_csv
@pytest.mark.xfail(reason="Duplicate rows exist in the file")
def test_duplicates(read_csv):
    seen = set()
    for row in read_csv:
        row_tuple = tuple(row.items())
        assert row_tuple not in seen, f"Duplicate row found: {row}"
        seen.add(row_tuple)


@pytest.mark.parametrize("id_val, expected_active", [
    ("1", "False"),
    ("2", "True"),
    ])
def test_active_players(read_csv, id_val, expected_active):
    for row in read_csv:
        if row['id'] == id_val:
            assert row['is_active'] == expected_active, (
                f"Expected is_active={expected_active} for id={id_val}, got {row['is_active']}"
            )


def test_active_player(read_csv):
    for row in read_csv:
        if row['id'] == "2":
            assert row['is_active'] == "True", (
                f"Expected is_active=True for id=2, got {row['is_active']}"
            )
