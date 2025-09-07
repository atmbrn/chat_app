from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from auth import create_access_token, authenticate_user, verify_token
from websocket_manager import ConnectionManager
from utils import sanitize_message

app = FastAPI(title="JWT Chat")

manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
async def me(token: str):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"username": username}

@app.get("/users")
async def get_users(token: str):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"active_users": manager.get_active_users()}

@app.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket, token: str):
    username = verify_token(token)
    if not username:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await manager.connect(username, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            clean_msg = sanitize_message(data)
            await manager.broadcast(clean_msg, sender=username)
    except WebSocketDisconnect:
        manager.disconnect(username)
