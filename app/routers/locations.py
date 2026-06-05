import httpx
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/locations", tags=["Locations"])

# It is highly recommended to use an environment variable for security
# If you prefer to hardcode, replace the string below:
API_KEY = "AIzaSyAYaMYVhJHui-LUuEaQFOc8hFk3-G2bMQo"

@router.get("/search")
async def search_places(query: str):
    """
    Fetches location suggestions using the new Google Places API.
    """
    if not query or len(query) < 3:
        return []

    url = "https://places.googleapis.com/v1/places:autocomplete"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY
    }
    
    # Removed 'maxResultCount' to resolve the 400 error
    payload = {
        "input": query
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            
            # If it fails, we print the error to help you debug
            if response.status_code != 200:
                print(f"Google API Error Response: {response.text}")
                response.raise_for_status()
            
            data = response.json()
            suggestions = data.get("suggestions", [])
            return [s["placePrediction"]["text"]["text"] for s in suggestions]
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to fetch locations: {str(e)}"
            )