from fastapi import FastAPI
from settings import DATABASE_FILENAME
from models.db import db
from games import endpoints as games_endpoints


app = FastAPI()
app.include_router(games_endpoints.router)


@app.get("/")
async def root():
    return {"message": "La Cosa"}

db.bind(provider='sqlite', filename=DATABASE_FILENAME, create_db=True)
db.generate_mapping(create_tables=True)
