from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone

# --- Sub-models ---
class MessageReaction(BaseModel):
    user_id: str
    emoji: str

class SkillRating(BaseModel):
    reviewer_id: str
    rating: float
    comment: str

class UserSkill(BaseModel):
    name: str
    ratings: List[SkillRating] = Field(default_factory=list)

class PostComment(BaseModel):
    id: str = Field(default_factory=lambda: str(datetime.now(timezone.utc).timestamp()))
    user_id: str
    user_name: str
    comment_text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Documents ---
class User(Document):
    id: Optional[str] = Field(default=None, alias="_id")  # FIX: Changed type to str to support Firebase UIDs
    email: Indexed(str, unique=True)
    first_name: str
    last_name: str
    birthday: str
    location: str
    gender: str
    bio: str = ""
    profile_picture: Optional[str] = None
    is_verified: bool = False
    active_status: bool = True
    following_ids: List[str] = Field(default_factory=list)
    follower_ids: List[str] = Field(default_factory=list)
    blocked_user_ids: List[str] = Field(default_factory=list)
    skills: List[UserSkill] = Field(default_factory=list)
    font_size: str = "medium"
    font_style: str = "default"
    dark_mode: bool = False
    language: str = "en"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # FIX: Added field for maintenance route support

    class Settings: 
        name = "users"

class Post(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    title: Indexed(str)
    description: str
    type: str
    owner_id: str
    media_urls: List[str] = Field(default_factory=list)
    comments: List[PostComment] = Field(default_factory=list)
    is_archived: bool = False
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings: 
        name = "posts"

class Review(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    rating: float
    comment: str
    tag: str
    target_user_id: str
    reviewer_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings: 
        name = "reviews"

class Booking(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    post_id: str
    client_id: str
    provider_id: str
    status: str = "Pending"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings: 
        name = "bookings"

class Notification(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    user_id: str
    sender_id: Optional[str] = None
    sender_name: str
    type: str
    message: str
    is_read: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings: 
        name = "notifications"

class ChatMessage(Document):
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    sender_id: Indexed(str)
    receiver_id: Indexed(str)
    message: Optional[str] = None
    msg_type: str = "text"
    media_url: Optional[str] = None
    reactions: List[MessageReaction] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings: 
        name = "chat_messages"