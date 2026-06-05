from fastapi import APIRouter, HTTPException
from typing import List
from .. import models, schemas

router = APIRouter(prefix="/notifications", tags=["In-App Notification Stream"])

# 🔔 GET ALL USER NOTIFICATIONS
@router.get("/user/{user_id}", response_model=List[schemas.NotificationResponse])
async def get_my_notifications(user_id: str):
    alerts = await models.Notification.find(
        models.Notification.user_id == user_id
    ).sort(-models.Notification.timestamp).to_list()
    return alerts

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