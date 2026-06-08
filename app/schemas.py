from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ==========================================
# 🔐 AUTH & USER SCHEMAS 
# ==========================================
class UserRegisterRequest(BaseModel):
    id_token: str
    first_name: str
    last_name: str
    birthday: str
    location: str
    gender: str

class UserLoginVerifyRequest(BaseModel):
    id_token: str

class AddSkillRequest(BaseModel):
    skill_name: str

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: str
    first_name: str
    last_name: str
    location: str
    
    class Config:
        populate_by_name = True
        from_attributes = True

# ==========================================
# 📝 POST SCHEMAS 
# ==========================================
class PostCreate(BaseModel):
    title: str
    description: str
    type: str
    owner_id: str = ""

class CommentResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    comment_text: str
    timestamp: datetime

class PostResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: str
    type: str
    owner_id: str
    media_urls: List[str] = Field(default_factory=list)
    comments: List[CommentResponse] = Field(default_factory=list)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    timestamp: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True

# ==========================================
# 🔔 NOTIFICATION SCHEMAS
# ==========================================
class NotificationResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    sender_id: Optional[str] = None
    sender_name: str
    type: str
    message: str
    is_read: bool = False
    timestamp: datetime

    class Config:
        populate_by_name = True
        from_attributes = True

# ==========================================
# ⭐ REVIEW SCHEMAS 
# ==========================================
class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: str
    tag: str
    target_user_id: str

class ReviewResponse(BaseModel):
    id: str = Field(alias="_id")
    rating: float
    comment: str
    tag: Optional[str] = None
    target_user_id: str
    reviewer_id: str
    timestamp: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True

# ==========================================
# 📅 BOOKING SCHEMAS 
# ==========================================
class BookingCreate(BaseModel):
    post_id: str
    provider_id: str

class BookingResponse(BaseModel):
    id: str = Field(alias="_id")
    post_id: str
    client_id: str
    provider_id: str
    status: str = "Pending"

    class Config:
        populate_by_name = True
        from_attributes = True

# ==========================================
# 📊 PROFILE DASHBOARD SCHEMA 
# ==========================================
class SkillRatingResponse(BaseModel):
    reviewer_id: str
    rating: float
    comment: str

class SkillResponse(BaseModel):
    name: str
    average_rating: float
    total_ratings: int
    feedback: List[SkillRatingResponse] = Field(default_factory=list)

class UserProfileDashboard(BaseModel):
    id: str = Field(alias="_id")
    email: str
    first_name: str
    last_name: str
    location: str
    bio: str
    birthday: Optional[str] = None
    gender: str
    profile_picture: Optional[str] = None
    active_status: bool = True
    followers_count: int = 0
    following_count: int = 0
    average_overall_rating: float = 0.0
    total_reviews_count: int = 0
    skills_inventory: List[SkillResponse] = Field(default_factory=list)
    photo_gallery: List[str] = Field(default_factory=list)
    active_posts: List[PostResponse] = Field(default_factory=list)
    recently_deleted_posts: List[PostResponse] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        from_attributes = True