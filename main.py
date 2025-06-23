import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from utils.dorker import scan_dork
from utils.ai_gen import generate_dorks_openai

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/scan")
async def websocket_scan(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        obj = json.loads(data)
        dorks = obj.get("dorks", [])
        results = []
        for result in await scan_dork(dorks):
            await websocket.send_text(json.dumps(result))
            results.append(result)
        await websocket.close()
    except WebSocketDisconnect:
        print("Client disconnected")

@app.websocket("/ws/generate_dorks")
async def websocket_generate_dorks(websocket: WebSocket):
    await websocket.accept()
    try:
        prompt = await websocket.receive_text()
        dorks = await generate_dorks_openai(prompt)
        await websocket.send_text(json.dumps(dorks))
        await websocket.close()
    except WebSocketDisconnect:
        print("Client disconnected")
