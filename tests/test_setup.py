import pytest
from pony.orm import Database, db_session
from src.theThing.models.db import db

db.bind(provider="sqlite", filename="test_database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)


@pytest.fixture(scope="session")
def test_db():
    yield db
