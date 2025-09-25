from fastapi import APIRouter, HTTPException
from app.services.travel_service import SessionService
from app.models.travel import SessionCreate, TravelQuery, ItineraryRequest, TravelGuideRequest
from app.services.search_service import EnhancedSearchTools

router = APIRouter()
search_tools = EnhancedSearchTools()

@router.post("/sessions/create")
async def create_session(session_data: SessionCreate):
    try:
        session = SessionService.create_session(session_data.user_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

@router.get("/sessions/current/{session_key}")
async def get_current_session(session_key: str):
    try:
        session = SessionService.get_session(session_key)
        if session:
            return session
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.post("/itinerary/generate")
async def generate_itinerary(itinerary_request: ItineraryRequest):
    try:
        travel_state = {
            'departure_location': itinerary_request.departure_location,
            'destination_location': itinerary_request.destination_location,
            'travel_dates': itinerary_request.travel_dates,
            'user_profile': itinerary_request.user_profile or {}
        }
        
        itinerary = search_tools.generate_intelligent_itinerary(travel_state)
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Itinerary generation failed: {str(e)}")

@router.post("/guide")
async def get_travel_guide(guide_request: TravelGuideRequest):
    try:
        guide_data = search_tools.get_travel_guide(guide_request.destination)
        return guide_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get travel guide: {str(e)}")

@router.get("/map")
async def generate_map(lat: float = 20.5937, lon: float = 78.9629, zoom: int = 4):
    try:
        from app.services.search_service import LocationService
        map_data = LocationService.create_map(lat, lon, zoom)
        return {"map_base64": map_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Map generation failed: {str(e)}")