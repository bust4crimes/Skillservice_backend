from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import User, Post, Review, Booking, Notification, ChatMessage
from .config import settings

async def init_db(mongo_uri: str):
    """
    Initializes the Beanie ODM with the provided MongoDB URI.
    """
    client = AsyncIOMotorClient(mongo_uri)
    await init_beanie(
        database=client["skillservice_db"],
        document_models=[
            User, 
            Post, 
            Review, 
            Booking, 
            Notification, 
            ChatMessage
        ]
    )