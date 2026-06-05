from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .. import models

router = APIRouter(prefix="/settings/app", tags=["App Settings"])

class AppSettingsUpdate(BaseModel):
    font_size: Optional[str] = None
    font_style: Optional[str] = None
    dark_mode: Optional[bool] = None
    language: Optional[str] = None

@router.put("/{user_id}")
async def update_app_settings(user_id: str, data: AppSettingsUpdate):
    user = await models.User.get(user_id)
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update logic (only updates if data is provided)
    if data.font_size: user.font_size = data.font_size
    if data.font_style: user.font_style = data.font_style
    if data.dark_mode is not None: user.dark_mode = data.dark_mode
    if data.language: user.language = data.language
    
    await user.save()
    return {"message": "App settings updated successfully"}

@router.put("/{user_id}/active-status")
async def toggle_active_status(user_id: str):
    user = await models.User.get(user_id)
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    
    user.active_status = not user.active_status
    await user.save()
    return {"active_status": user.active_status}

@router.put("/{user_id}/block/{target_user_id}")
async def toggle_block_user(user_id: str, target_user_id: str):
    user = await models.User.get(user_id)
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    
    if target_user_id not in user.blocked_user_ids:
        user.blocked_user_ids.append(target_user_id)
    else:
        user.blocked_user_ids.remove(target_user_id)
        
    await user.save()
    return {"message": "Block status updated"}