from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from routes.stocks import fetch_stock_data
import asyncio
from colorama import Back, Style

router = APIRouter()


connected_clients = {}

# WebSocket for real-time stock updates
@router.websocket("/ws/stocks/{user_id}")
async def stock_updates(websocket: WebSocket, user_id: str):
    print(Back.GREEN + f"WebSocket connected => User ID: {user_id}" + Style.RESET_ALL)
    await websocket.accept()
    connected_clients[user_id] = websocket
    try:
        while True:
            stock_data = await fetch_stock_data()
            print(Back.BLUE + f"Sending message => User ID: {user_id}" + Style.RESET_ALL)
            print(stock_data)
            await websocket.send_json(stock_data)
            await asyncio.sleep(60)  # Send updates every second
    except WebSocketDisconnect:
        print(Back.RED + f"WebSocket disconnected => User ID: {user_id}" + Style.RESET_ALL)
        connected_clients.pop(user_id, None)