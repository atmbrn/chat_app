from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def send_personal_message(self, message: str, username: str):
        ws = self.active_connections.get(username)
        if ws:
            await ws.send_text(message)

    async def broadcast(self, message: str, sender: str):
        for user, connection in self.active_connections.items():
            if user != sender:
                await connection.send_text(f"{sender}: {message}")
