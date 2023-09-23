from fastapi import FastAPI
from settings import DATABASE_FILENAME
from models import db
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "La Cosa"}

db.bind(provider='sqlite', filename=DATABASE_FILENAME, create_db=True)
db.generate_mapping(create_tables=True)