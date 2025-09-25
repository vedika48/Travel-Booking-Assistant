from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class TravelQuery(BaseModel):
    departure_location: str
    destination_location: str
    travel_dates: Dict[str, str]
    travel_mode: Optional[str] = None
    specific_area: Optional[str] = None

class ServiceSearch(BaseModel):
    departure: str
    destination: str
    date: Optional[str] = None
    checkin: Optional[str] = None
    checkout: Optional[str] = None
    area: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    session_key: str

class SessionCreate(BaseModel):
    user_id: str

class AgentSelect(BaseModel):
    agent_id: str
    query: str

class BookingRequest(BaseModel):
    service_id: str
    booking_data: Dict[str, Any]