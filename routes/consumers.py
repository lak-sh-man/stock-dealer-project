from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from routes.stocks import fetch_stock_data
import asyncio
from colorama import Back, Style

router = APIRouter()


connected_clients = {}

# WebSocket for real-time stock updates
@router.websocket("/ws/stocks/{user_id}")
async def stock_updates(websocket: WebSocket, user_id: str):
    
    await websocket.accept()
    connected_clients[user_id] = websocket
    print(Back.GREEN + f"WebSocket connected => User ID: {user_id} | connected_clients: {list(connected_clients.keys())}" + Style.RESET_ALL)
    try:
        while True:
            stock_data = await fetch_stock_data()
            if websocket.client_state != WebSocketState.CONNECTED:
                break  # Ensure we're not sending data to a closed connection
            
            await websocket.send_json(stock_data[0:2])
            print(Back.BLUE + f"Sent message to {user_id}" + Style.RESET_ALL)
            await asyncio.sleep(60)  
            
    except WebSocketDisconnect:
        await websocket.close()
        connected_clients.pop(user_id, None)
        print(Back.MAGENTA + f"Exception, so disconnecting => User ID: {user_id} | connected_clients: {connected_clients}" + Style.RESET_ALL)
        
    finally:
        # Ensure the WebSocket is removed and closed properly
        connected_clients.pop(user_id, None)
        try:
            await websocket.close()
        except Exception:
            pass

        print(Back.RED + f"WebSocket disconnected => User ID: {user_id} | Remaining Clients: {list(connected_clients.keys())}" + Style.RESET_ALL)
