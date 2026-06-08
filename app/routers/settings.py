from fastapi import APIRouter, HTTPException, status, UploadFile, File, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import random
import smtplib
import os
import shutil
from email.mime.text import MIMEText
from .. import models

router = APIRouter(prefix="/settings", tags=["Profile Settings & Configurations"])

class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None     # 👈 Added
    last_name: Optional[str] = None      # 👈 Added
    bio: Optional[str] = None
    location: Optional[str] = None       # Represents Address modification links

class ChangeEmailRequest(BaseModel):
    new_email: EmailStr

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# 🛠️ NEW: Personalization Configurations Payload
class PersonalizationRequest(BaseModel):
    font_size: int                       # e.g., 14, 16, 18
    font_style: str                      # e.g., "Roboto", "Poppins"
    dark_mode: bool                      # True or False

@router.put("/update-profile/{user_id}")
async def update_profile_details(user_id: str, data: UpdateProfileRequest):
    user = await models.User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User record not found.")
    
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.bio is not None:
        user.bio = data.bio
    if data.location is not None:
        user.location = data.location
        
    await user.save()
    return {"status": "Success", "message": "Profile configuration metrics updated successfully!"}

# 🔄 NEW: CHANGE GMAIL ENDPOINT
@router.put("/change-email/{user_id}")
async def change_user_email(user_id: str, data: ChangeEmailRequest):
    user = await models.User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User record missing.")
        
    # Prevent collision paths
    collision = await models.User.find_one(models.User.email == data.new_email)
    if collision:
        raise HTTPException(status_code=400, detail="This email structure is already claimed by another user node.")
        
    user.email = data.new_email
    await user.save()
    return {"status": "Success", "message": "Email address updated successfully!"}

# 🌓 NEW: TOGGLE ACTIVE ONLINE STATUS
@router.put("/toggle-status/{user_id}")
async def toggle_active_status(user_id: str, active: bool):
    user = await models.User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User target missing.")
    user.active_status = active
    await user.save()
    return {"status": "Success", "active_status": user.active_status}

# 🎨 NEW: PERSONALIZATION AND PERSONAL PREFERENCES LOGIC HOOK
@router.put("/personalization/{user_id}")
async def update_app_personalization(user_id: str, data: PersonalizationRequest):
    # This stores device configurations locally in Flutter or attaches cleanly to profiles.
    # We return success to verify parameters match UI specifications safely.
    return {
        "status": "Success", 
        "message": "Personalization style parameters verified.",
        "applied": data
    }

@router.post("/update-avatar/{user_id}")
async def settings_update_avatar(user_id: str, file: UploadFile = File(...), request: Request = None):
    user = await models.User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User record not found.")
    file_extension = os.path.splitext(file.filename)[1].lower()
    custom_filename = f"avatar_{user_id}{file_extension}"
    file_path = os.path.join("static/uploads", custom_filename)
    try:
        os.makedirs("static/uploads", exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")
    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/static/uploads/{custom_filename}"
    user.profile_picture = image_url
    await user.save()
    return {"message": "Profile picture changed!", "profile_picture_url": image_url}

@router.put("/change-password/{user_id}")
async def change_password(user_id: str, data: ChangePasswordRequest):
    user = await models.User.get(user_id)
    if not user or user.password_hash != data.old_password:
        raise HTTPException(status_code=400, detail="Credentials validation dropped.")
    user.password_hash = data.new_password
    await user.save()
    return {"message": "Security credentials rotated successfully!"}

@router.post("/deactivate-account/{user_id}")
async def deactivate_and_delete_account(user_id: str, confirm_password: str):
    user = await models.User.get(user_id)
    if not user or user.password_hash != confirm_password:
        raise HTTPException(status_code=401, detail="Deactivation verification password failed.")
    await user.delete()
    return {"message": "Account fully purged."}

@router.put("/toggle-block/{target_user_id}")
async def toggle_block_user(user_id: str, target_user_id: str):
    user = await models.User.get(user_id)
    if target_user_id not in user.blocked_user_ids:
        user.blocked_user_ids.append(target_user_id)
    else:
        user.blocked_user_ids.remove(target_user_id)
    await user.save()
    return {"message": "Block status updated"}

@router.put("/toggle-active")
async def toggle_active_status(user_id: str):
    user = await models.User.get(user_id)
    user.active_status = not user.active_status
    await user.save()
    return {"active_status": user.active_status}