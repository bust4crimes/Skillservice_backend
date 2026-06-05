from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import shutil
import os
import uuid
from .. import models

router = APIRouter(prefix="/chat", tags=["Real-Time Chat Engine"])

class ReactionRequest(BaseModel):
    user_id: str
    emoji: str

class BlockRequest(BaseModel):
    user_id: str        # The person executing the block action
    target_id: str      # The person being blocked

class ChatConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_private_message(self, data: dict, receiver_id: str):
        if receiver_id in self.active_connections:
            receiver_socket = self.active_connections[receiver_id]
            await receiver_socket.send_json(data)

manager = ChatConnectionManager()

# 📡 1. LIVE WEBSOCKET TUNNEL (With Built-In Block Security Safeguards)
@router.websocket("/ws/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            target_receiver_id = data.get("receiver_id")
            text_content = data.get("message")
            msg_type = data.get("msg_type", "text")
            media_url = data.get("media_url", None)

            if target_receiver_id:
                # 🛡️ SECURITY GUARD check: Did the recipient block this sender?
                recipient = await models.User.get(target_receiver_id)
                if recipient and user_id in recipient.blocked_user_ids:
                    # Silently reject message distribution or send back a system notice alert
                    await websocket.send_json({"type": "error", "message": "Message delivery failed. User restriction active."})
                    continue

                saved_msg = models.ChatMessage(
                    sender_id=user_id,
                    receiver_id=target_receiver_id,
                    message=text_content,
                    msg_type=msg_type,
                    media_url=media_url
                )
                await saved_msg.insert()

                payload = {
                    "id": str(saved_msg.id),
                    "sender_id": user_id,
                    "receiver_id": target_receiver_id,
                    "message": text_content,
                    "msg_type": msg_type,
                    "media_url": media_url,
                    "reactions": [],
                    "timestamp": str(saved_msg.timestamp)
                }
                await manager.send_private_message(payload, receiver_id=target_receiver_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"⚠️ Chat WebSocket error drop: {e}")
        manager.disconnect(user_id)

# 📁 2. CHAT MEDIA UPLOAD CONTROLLER (With Block Protection Loops)
@router.post("/upload-file")
async def upload_chat_file(
    sender_id: str = Form(...),
    receiver_id: str = Form(...),
    file: UploadFile = File(...)
):
    # 🛡️ SECURITY GUARD check: Ensure media transfers are blocked if user restrictions exist
    recipient = await models.User.get(receiver_id)
    if recipient and sender_id in recipient.blocked_user_ids:
        raise HTTPException(status_code=403, detail="Action prohibited. You are restricted from messaging this recipient.")

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension in [".jpg", ".jpeg", ".png"]:
        msg_type = "image"
    elif file_extension in [".mp3", ".m4a", ".wav", ".aac"]:
        msg_type = "audio"
    elif file_extension in [".mp4", ".mov", ".mkv"]:
        msg_type = "video"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format allocation.")

    unique_filename = f"chat_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join("static/uploads", unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save asset: {str(e)}")

    generated_url = f"http://127.0.0.1:8000/static/uploads/{unique_filename}"

    saved_msg = models.ChatMessage(
        sender_id=sender_id,
        receiver_id=receiver_id,
        msg_type=msg_type,
        media_url=generated_url
    )
    await saved_msg.insert()

    live_alert = {
        "id": str(saved_msg.id),
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": None,
        "msg_type": msg_type,
        "media_url": generated_url,
        "reactions": [],
        "timestamp": str(saved_msg.timestamp)
    }
    await manager.send_private_message(live_alert, receiver_id=receiver_id)
    return live_alert

# 📄 3. UNIFIED CHAT HISTORY LOGS
@router.get("/history/{user_a}/{user_b}")
async def get_chat_history(user_a: str, user_b: str):
    messages = await models.ChatMessage.find(
        ((models.ChatMessage.sender_id == user_a) & (models.ChatMessage.receiver_id == user_b)) |
        ((models.ChatMessage.sender_id == user_b) & (models.ChatMessage.receiver_id == user_a))
    ).sort(+models.ChatMessage.timestamp).to_list()

    return [
        {
            "id": str(m.id),
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "message": m.message,
            "msg_type": m.msg_type,
            "media_url": m.media_url,
            "reactions": [{"user_id": r.user_id, "emoji": r.emoji} for r in m.reactions],
            "timestamp": m.timestamp
        } for m in messages
    ]

# 🗑️ 4. DELETE / UNSEND MESSAGE ENDPOINT
@router.delete("/delete-message/{message_id}")
async def delete_chat_message(message_id: str, user_id: str):
    message = await models.ChatMessage.get(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")

    if message.sender_id != user_id:
        raise HTTPException(status_code=403, detail="Action denied. Ownership mismatch.")

    receiver_id = message.receiver_id
    await message.delete()

    live_delete_alert = {
        "type": "message_deleted",
        "message_id": message_id,
        "sender_id": user_id,
        "receiver_id": receiver_id
    }
    await manager.send_private_message(live_delete_alert, receiver_id=receiver_id)
    return {"status": "Success", "message": "Message successfully unsent."}

# ❤️ 5. EMOJI REACTION CONTROLLER
@router.put("/react/{message_id}")
async def add_or_remove_message_reaction(message_id: str, payload: ReactionRequest):
    message = await models.ChatMessage.get(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Target chat message instance not found.")

    existing_reaction_index = -1
    for i, r in enumerate(message.reactions):
        if r.user_id == payload.user_id:
            existing_reaction_index = i
            break

    if existing_reaction_index != -1:
        if message.reactions[existing_reaction_index].emoji == payload.emoji:
            message.reactions.pop(existing_reaction_index)
            action_taken = "removed"
        else:
            message.reactions[existing_reaction_index].emoji = payload.emoji
            action_taken = "updated"
    else:
        new_reaction = models.MessageReaction(user_id=payload.user_id, emoji=payload.emoji)
        message.reactions.append(new_reaction)
        action_taken = "added"

    await message.save()

    receiver_target = message.receiver_id if payload.user_id == message.sender_id else message.sender_id
    
    live_reaction_alert = {
        "type": "reaction_changed",
        "message_id": message_id,
        "action": action_taken,
        "user_id": payload.user_id,
        "emoji": payload.emoji,
        "current_reactions": [{"user_id": r.user_id, "emoji": r.emoji} for r in message.reactions]
    }
    await manager.send_private_message(live_reaction_alert, receiver_id=receiver_target)
    return {"status": "Success", "action": action_taken, "reactions": message.reactions}

# 🧼 6. CLEAR FULL CONVERSATION ENDPOINT
@router.delete("/clear-conversation")
async def clear_entire_conversation(user_a: str, user_b: str):
    messages_to_delete = await models.ChatMessage.find(
        ((models.ChatMessage.sender_id == user_a) & (models.ChatMessage.receiver_id == user_b)) |
        ((models.ChatMessage.sender_id == user_b) & (models.ChatMessage.receiver_id == user_a))
    ).to_list()

    if not messages_to_delete:
        return {"status": "Success", "message": "The chat conversation is already empty."}

    for message in messages_to_delete:
        await message.delete()

    live_clear_alert = {
        "type": "conversation_cleared",
        "cleared_by": user_a,
        "partner_id": user_b
    }
    await manager.send_private_message(live_clear_alert, receiver_id=user_b)
    return {"status": "Success", "message": f"Successfully deleted conversation thread."}

# 🚫 7. NEW BLOCK USER ENDPOINT - ADDED!
@router.post("/block-user")
async def block_user_profile(payload: BlockRequest):
    user = await models.User.get(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Your user profile was not found.")
        
    if payload.target_id == payload.user_id:
        raise HTTPException(status_code=400, detail="You cannot block your own user account profile.")

    if payload.target_id not in user.blocked_user_ids:
        user.blocked_user_ids.append(payload.target_id)
        await user.save()

    # Inform the target user's UI stream immediately so it updates their window to say "Blocked"
    live_block_alert = {
        "type": "user_blocked_you",
        "blocker_id": payload.user_id
    }
    await manager.send_private_message(live_block_alert, receiver_id=payload.target_id)

    return {"status": "Success", "message": "User has been successfully blocked.", "blocked_list": user.blocked_user_ids}

# 🔓 8. NEW UNBLOCK USER ENDPOINT - ADDED!
@router.post("/unblock-user")
async def unblock_user_profile(payload: BlockRequest):
    user = await models.User.get(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Your user profile was not found.")

    if payload.target_id in user.blocked_user_ids:
        user.blocked_user_ids.remove(payload.target_id)
        await user.save()

    live_unblock_alert = {
        "type": "user_unblocked_you",
        "unblocker_id": payload.user_id
    }
    await manager.send_private_message(live_unblock_alert, receiver_id=payload.target_id)

    return {"status": "Success", "message": "User has been successfully unblocked.", "blocked_list": user.blocked_user_ids}