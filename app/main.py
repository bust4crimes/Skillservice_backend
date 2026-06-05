import logging
import os
import json # ◄── Added to parse the cloud JSON secret
from contextlib import asynccontextmanager

import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Internal Modules
from .config import settings
from .database import init_db
from .routers import (
    app_settings,
    auth,
    bookings,
    chat,
    locations,
    notifications,
    posts,
    reviews,
)
from .routers import settings as user_settings_router

# --- Logging Configuration ---
log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s'
)
log_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.setLevel(settings.LOG_LEVEL)


# --- Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
        return response


# --- Application Lifespan (Startup & Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure static uploads directory exists
    os.makedirs("static/uploads", exist_ok=True)
    
    # Initialize MongoDB NoSQL Database
    await init_db(settings.MONGO_URI) 
    logger.info("Successfully connected to the MongoDB NoSQL Engine!")
    
    # --- FIREBASE CLOUD FIX ---
    # Try to load credentials from a cloud environment variable first
    firebase_cloud_json = os.environ.get("FIREBASE_JSON_SECRET")
    cred_path = settings.FIREBASE_CREDENTIALS_PATH

    if firebase_cloud_json:
        # We are in the cloud! Load the JSON string directly
        cred = credentials.Certificate(json.loads(firebase_cloud_json))
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin initialized via Cloud Environment Variable!")
    elif os.path.exists(cred_path):
        # We are on your local computer! Load the file
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK successfully initialized via local file!")
    else:
        logger.warning("Firebase credentials missing! Token validation will fail.")
        
    yield


# --- Application Initialization ---
app = FastAPI(
    title="SkillService API", 
    description="Teacher-Approved Master Social & Skills Development Ecosystem with Firebase Auth",
    lifespan=lifespan
)


# --- Middlewares ---
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ◄── Set to allow all origins so Flutter doesn't get blocked
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


# Include all endpoint routers
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(reviews.router)  
app.include_router(bookings.router)  
app.include_router(user_settings_router.router)  
app.include_router(chat.router)  
app.include_router(notifications.router) 
app.include_router(app_settings.router)
app.include_router(locations.router)  


# --- Root Endpoint ---
@app.get("/", tags=["Health Check"])
def root():
    return {"status": "Running", "database": "MongoDB NoSQL Engine Active"}