import pytest
from pony.orm import Database, db_session
from src.theThing.models.db import db


@pytest.fixture(scope="module", autouse=True)
def clear_db():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    yield
    db.drop_all_tables(with_all_data=True)
    db.create_tables()


@pytest.fixture(scope="session")
def test_db():
    yield db
