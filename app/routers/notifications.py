from fastapi import APIRouter, HTTPException
from typing import List
from .. import models, schemas

router = APIRouter(prefix="/notifications", tags=["In-App Notification Stream"])

def _notif_to_dict(n: models.Notification) -> dict:
    return {
        "id": str(n.id),
        "user_id": n.user_id,
        "sender_id": n.sender_id,
        "sender_name": n.sender_name,
        "type": n.type,
        "message": n.message,
        "is_read": n.is_read,
        "timestamp": n.timestamp.isoformat() if n.timestamp else None,
    }

# 🔔 GET ALL USER NOTIFICATIONS
@router.get("/user/{user_id}", response_model=List[schemas.NotificationResponse])
async def get_my_notifications(user_id: str):
    alerts = await models.Notification.find(
        models.Notification.user_id == user_id
    ).to_list()
    alerts.sort(key=lambda n: n.timestamp, reverse=True)
    return [_notif_to_dict(n) for n in alerts]

# 🧼 MARK ALL AS READ
@router.put("/mark-read/{user_id}")
async def mark_notifications_as_read(user_id: str):
    unread_alerts = await models.Notification.find(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).to_list()
    
    for alert in unread_alerts:
        alert.is_read = True
        await alert.save()
        
    return {"status": "Success", "message": f"Marked {len(unread_alerts)} alerts as read."}