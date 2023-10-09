from fastapi import FastAPI
from src.settings import DATABASE_FILENAME
from src.theThing.models.db import db
from src.theThing.games import endpoints as games_endpoints
from fastapi.middleware.cors import CORSMiddleware
from src.theThing.players.websocket_handler import router as players_router
import socketio

app = FastAPI()
app.include_router(games_endpoints.router)
app.include_router(players_router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "La Cosa"}


sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
socketio_app = socketio.ASGIApp(sio, app, socketio_path='/sockets')


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.on('message')
async def chat_message(sid, data):
    print("message ", data, "hola")
    await sio.emit('response', 'hola mundo')


@sio.on('join')
async def join(sid, data):
    print("join ", data)
    await sio.emit('response', 'te uniste'+data, room=sid)
@sio.event
def disconnect(sid):
    print('disconnect ', sid)


db.bind(provider="sqlite", filename=DATABASE_FILENAME, create_db=True)
db.generate_mapping(create_tables=True)
