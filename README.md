# SkillService Backend
Social media API for sideline jobs built with FastAPI.

## MVC Structure
- **Models**: SQLAlchemy tables in `app/models.py`
- **Views**: Pydantic schemas in `app/schemas.py`
- **Controllers**: API logic in `app/routers/`

## Features
- FastAPI backend with automatic Swagger docs at `/docs`
- SQLite database connection through SQLAlchemy
- Full CRUD for users, posts, and reviews
- Pydantic request/response validation
- Error handling for missing records, invalid ownership, and invalid review users

## Setup
1. `python -m venv venv`
2. `.\venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --reload`

Server URL: `http://127.0.0.1:8000`

Swagger UI: `http://127.0.0.1:8000/docs`

## Test Script
With the server running, open a second terminal and run:

```powershell
python test_script.py
```

The script creates, reads, updates, and deletes users, posts, and reviews to verify the endpoints.
