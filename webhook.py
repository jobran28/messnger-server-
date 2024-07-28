from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from db import ensure_page_recorded, ensure_chat_recorded, store_message, get_last_messages
from ai_model import get_openai_response, prepare_openai_messages
import json
import requests

router = APIRouter()

VERIFY_TOKEN = "myverfiftoken"
FB_ACCESS_TOKEN = "EAALfBwWVNikBOws6A7XAqsbOoemryHsfBPx2p8QruAyVbn5fC9bQHqkqQhJrHOr8xxP4pKuYMAvbXnrgPBnPKaf68bXHZCTGCGW8ZBhizECA3lYCa6sCTksTRqYNQbOZCqvT88ZA5ZBFC4QfGQwn3o5eXBcBRJDqCP6MttgNVHGBjtBx3ZBWFBEMyYi3Nz5bQwSwZDZD"

@router.get("/webhook")
async def verify_token(
    hub_mode: str = Query(alias="hub.mode"),
    hub_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    if hub_token == VERIFY_TOKEN and hub_mode == "subscribe":
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    for entry in payload.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            user_id = messaging_event["sender"]["id"]
            page_id = messaging_event["recipient"]["id"]
            message_text = messaging_event["message"].get("text", "")

            ensure_page_recorded(page_id)
            chat_id = ensure_chat_recorded(page_id, user_id)

            store_message(chat_id, message_text, "user")
            last_messages = get_last_messages(chat_id)
            openai_messages = prepare_openai_messages(last_messages)
            ai_response = get_openai_response(openai_messages)

            store_message(chat_id, ai_response, "bot")
            send_message(FB_ACCESS_TOKEN, user_id, ai_response)

    return {"status": "received"}

def send_message(access_token, recipient_id, message_text):
    url = f"https://graph.facebook.com/v20.0/me/messages?access_token={access_token}"
    headers = {"Content-Type": "application/json"}
    message_data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, headers=headers, data=json.dumps(message_data))
    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message: {response.status_code}")
        print(response.text)
