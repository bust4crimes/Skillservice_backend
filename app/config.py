from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB Connection
    MONGO_URI: str = "mongodb://localhost:27017" # Default for local development

    # Firebase Admin SDK Credentials
    FIREBASE_CREDENTIALS_PATH: str = "firebase_credentials.json" # Path to your Firebase service account key

    # CORS Origins
    # In production, replace "*" with your specific frontend domain(s), e.g., ["https://your-frontend.com"]
    CORS_ORIGINS: list[str] = ["*"] 

    # Secret Key for various security features (e.g., JWT, CSRF protection if implemented)
    # Generate a strong secret key for production: openssl rand -hex 32
    SECRET_KEY: str = "supersecretkey" # CHANGE THIS IN PRODUCTION!

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env" # Loads environment variables from a .env file

settings = Settings()
