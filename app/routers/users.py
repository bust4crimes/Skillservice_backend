from fastapi import APIRouter, HTTPException
from .. import models, schemas

router = APIRouter(prefix="/users", tags=["Profile & Dashboard"])

@router.get("/{user_id}/dashboard", response_model=schemas.UserProfileDashboard)
async def get_dashboard(user_id: str):
    user = await models.User.get(user_id)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    
    return schemas.UserProfileDashboard(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        location=user.location,
        bio=user.bio,
        gender=user.gender,
        followers_count=len(user.follower_ids),
        following_count=len(user.following_ids),
        skills_inventory=[],
        active_posts=[]
    )

@router.post("/{user_id}/follow/{target_id}")
async def follow_user(user_id: str, target_id: str):
    user = await models.User.get(user_id)
    target = await models.User.get(target_id)
    if not user or not target: raise HTTPException(status_code=404, detail="User not found")
    
    if target_id not in user.following_ids:
        user.following_ids.append(target_id)
        target.follower_ids.append(user_id)
        await user.save()
        await target.save()
    return {"message": "Followed"}