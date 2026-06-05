from fastapi import APIRouter, HTTPException, status, Query
from firebase_admin import auth as firebase_auth
from datetime import datetime, timedelta, timezone
from .. import models, schemas

router = APIRouter(prefix="/auth", tags=["Authentication & Profiles"])

def verify_firebase_token(id_token: str, enforce_verification: bool = True) -> dict:
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        if enforce_verification and not decoded_token.get("email_verified"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email address not verified. Please check your inbox."
            )
        return decoded_token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired Firebase ID Token: {str(e)}"
        )

@router.post("/register")
async def register_user(payload: schemas.UserRegisterRequest):
    decoded_token = verify_firebase_token(payload.id_token, enforce_verification=False)
    firebase_uid = decoded_token["uid"]
    verified_email = decoded_token["email"]

    existing_user = await models.User.get(firebase_uid)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered.")
    
    google_avatar = decoded_token.get("picture", None)

    # Save user with created_at (auto-generated in model)
    new_user = models.User(
        id=firebase_uid, 
        email=verified_email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        birthday=payload.birthday,
        location=payload.location,
        gender=payload.gender,
        bio="", 
        profile_picture=google_avatar,
        is_verified=False
    )
    await new_user.insert()
    return {"status": "Success", "user_id": firebase_uid}

@router.post("/login-verify")
async def login_and_verify_user(payload: schemas.UserLoginVerifyRequest, login_location: str = "Unknown Location"):
    decoded_token = verify_firebase_token(payload.id_token, enforce_verification=True)
    firebase_uid = decoded_token["uid"]

    user = await models.User.get(firebase_uid)
    if not user:
        return {"status": "Onboarding Required", "uid": firebase_uid}
    
    user.is_verified = True
    user.active_status = True
    await user.save()

    # Create notification
    await models.Notification(
        user_id=firebase_uid,
        sender_name="Firebase Guard",
        type="new_login",
        message=f"Verified login from {login_location}."
    ).insert()
    
    return {"status": "Authenticated", "user_id": firebase_uid}

@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    user = await models.User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

# 🧹 Maintenance Route: Cleanup unverified zombies
@router.delete("/cleanup-zombies")
async def cleanup_unverified_users(admin_secret: str = Query(...)):
    # Simple security check - replace with env var in production
    if admin_secret != "super-secret-key":
        raise HTTPException(status_code=403, detail="Unauthorized")

    threshold_date = datetime.now(timezone.utc) - timedelta(hours=48)
    
    zombies = await models.User.find(
        models.User.is_verified == False,
        models.User.created_at < threshold_date
    ).to_list()
    
    deleted_count = 0
    for user in zombies:
        await user.delete()
        deleted_count += 1
        
    return {"status": "Success", "deleted_count": deleted_count}