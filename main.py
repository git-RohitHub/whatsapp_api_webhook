import uvicorn 
from fastapi import FastAPI, Request,Query,Response
from fastapi.responses import JSONResponse
import requests
import os

app = FastAPI()

PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

WHATSAPP_URL = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"



@app.get("/webhook")
def verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED")
        return JSONResponse(status_code=200, content=int(hub_challenge))
    else:
        return JSONResponse(status_code=403, content="Verification failed")

# 🔹 Step 2: receive messages (POST)
@app.post("/webhook")
async def receive_message(request: Request):
    print(request)
    data = await request.json()
    print("INCOMING:", data)

    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = msg["from"]
        text = msg["text"]["body"]

        reply = f"You said: {text}"
        send_message(sender, reply)

    except Exception as e:
        print("No message found", e)

    return {"status": "ok"}


# 🔹 Step 3: send message
def send_message(to: str, text: str):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": "+919759279921",
        "type": "text",
        "text": {
            "body": text
        }
    }

    r = requests.post(WHATSAPP_URL, json=payload, headers=headers)
    print("SENT:", r.json())

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        reload=True
    )
