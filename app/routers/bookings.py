from fastapi import APIRouter, HTTPException, status
from typing import List
from .. import models, schemas

router = APIRouter(prefix="/bookings", tags=["Bookings & Schedule Engine"])

@router.post("/create/{client_id}", response_model=schemas.BookingResponse)
async def create_booking(client_id: str, booking_data: schemas.BookingCreate):
    client = await models.User.get(client_id)
    post = await models.Post.get(booking_data.post_id)
    provider = await models.User.get(booking_data.provider_id)
    
    if not client or not post or not provider:
        raise HTTPException(status_code=404, detail="Required entities not found.")

    if client_id == booking_data.provider_id:
        raise HTTPException(status_code=400, detail="Cannot book yourself.")

    new_booking = models.Booking(
        post_id=booking_data.post_id,
        client_id=client_id,
        provider_id=booking_data.provider_id,
        status="Pending"
    )
    await new_booking.insert()

    # 🔥 Blueprint: Trigger Notification for Provider
    await models.Notification(
        user_id=booking_data.provider_id,
        sender_id=client_id,
        sender_name=f"{client.first_name} {client.last_name}",
        type="Booking",
        message=f"{client.first_name} applied to your post: {post.title}"
    ).insert()

    return schemas.BookingResponse(
        id=str(new_booking.id),
        post_id=new_booking.post_id,
        client_id=new_booking.client_id,
        provider_id=new_booking.provider_id,
        status=new_booking.status
    )

@router.put("/status/{booking_id}")
async def update_booking_status(booking_id: str, provider_id: str, new_status: str):
    if new_status not in ["Accepted", "Rejected", "Completed"]:
        raise HTTPException(status_code=400, detail="Invalid status.")

    booking = await models.Booking.get(booking_id)
    if not booking or booking.provider_id != provider_id:
        raise HTTPException(status_code=403, detail="Unauthorized or not found.")

    booking.status = new_status
    await booking.save()

    # 🔥 Blueprint: Trigger Notification for Client regarding status update
    provider = await models.User.get(provider_id)
    await models.Notification(
        user_id=booking.client_id,
        sender_id=provider_id,
        sender_name=f"{provider.first_name} {provider.last_name}",
        type="StatusUpdate",
        message=f"Your booking status is now: {new_status}"
    ).insert()

    return {"message": f"Updated to '{new_status}'."}