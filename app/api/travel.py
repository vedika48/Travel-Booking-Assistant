from fastapi import APIRouter, HTTPException
from app.services.travel_service import SessionService
from app.models.travel import SessionCreate, TravelQuery
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
async def generate_itinerary(travel_query: TravelQuery):
    try:
        # Convert to travel state format
        travel_state = {
            'departure_location': travel_query.departure_location,
            'destination_location': travel_query.destination_location,
            'travel_dates': travel_query.travel_dates,
            'travel_mode': travel_query.travel_mode,
            'user_profile': None
        }
        
        itinerary = search_tools.generate_intelligent_itinerary(travel_state)
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Itinerary generation failed: {str(e)}")

@router.get("/guide/{destination}")
async def get_travel_guide(destination: str):
    try:
        guide_data = search_tools.get_travel_guide(destination)
        return guide_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get travel guide: {str(e)}")