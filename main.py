from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from auth import verify_token, create_access_token
from websocket_manager import ConnectionManager
from utils import sanitize_message

app = FastAPI()
manager = ConnectionManager()


origins = ["https://my-frontend-domain.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        username = verify_token(token)
        await manager.connect(username, websocket)
        while True:
            data = await websocket.receive_text()
            clean_msg = sanitize_message(data)
            await manager.broadcast(clean_msg, sender=username)
    except WebSocketDisconnect:
        manager.disconnect(username)
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
