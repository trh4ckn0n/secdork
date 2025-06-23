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

        if not dorks:
            await websocket.send_text(json.dumps({"error": "Aucun dork fourni"}))
            return

        results = await dorker(dorks)

        # Envoie un message par dork avec ses résultats
        for dork, links in results.items():
            await websocket.send_text(json.dumps({
                "dork": dork,
                "results": links
            }))

    except WebSocketDisconnect:
        print("⚠️ Client déconnecté (scan)")
    except Exception as e:
        print(f"❌ Erreur pendant le scan : {e}")
        await websocket.send_text(json.dumps({
            "error": "Erreur lors du scan. Vérifie les dorks ou la connexion réseau."
        }))
    finally:
        await websocket.close()

@app.websocket("/ws/generate_dorks")
async def websocket_generate_dorks(websocket: WebSocket):
    await websocket.accept()
    try:
        prompt = await websocket.receive_text()
        dorks = await generate_dorks_openai(prompt)

        if not dorks:
            await websocket.send_text(json.dumps({"error": "Aucun dork généré"}))
        else:
            await websocket.send_text(json.dumps({
                "generated": dorks
            }))

    except WebSocketDisconnect:
        print("⚠️ Client déconnecté (generate)")
    except Exception as e:
        print(f"❌ Erreur génération : {e}")
        await websocket.send_text(json.dumps({
            "error": "Erreur pendant la génération des dorks."
        }))
    finally:
        await websocket.close()
