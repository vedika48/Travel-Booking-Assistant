import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# In-memory storage for sessions
sessions_db = {}
travel_states_db = {}

class SessionService:
    @staticmethod
    def create_session(user_id: str) -> Dict[str, Any]:
        session_key = str(uuid.uuid4())
        session = {
            'session_key': session_key,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        sessions_db[session_key] = session
        
        # Initialize travel state
        travel_state = {
            'user_query': '',
            'user_profile': None,
            'session_key': session_key,
            'conversation_history': [],
            'current_agent': 'general',
            'departure_location': None,
            'destination_location': None,
            'travel_mode': None,
            'travel_dates': None,
            'specific_area_pune': None,
            'flight_data': None,
            'hotel_data': None,
            'cab_data': None,
            'train_data': None,
            'bus_data': None,
            'selected_options': {},
            'final_itinerary': None,
            'booking_status': {},
            'communication_logs': [],
            'is_intracity': False,
            'guide_data': None
        }
        travel_states_db[session_key] = travel_state
        
        return session
    
    @staticmethod
    def get_session(session_key: str) -> Optional[Dict[str, Any]]:
        return sessions_db.get(session_key)
    
    @staticmethod
    def get_travel_state(session_key: str) -> Optional[Dict[str, Any]]:
        return travel_states_db.get(session_key)
    
    @staticmethod
    def update_travel_state(session_key: str, updates: Dict[str, Any]):
        if session_key in travel_states_db:
            travel_states_db[session_key].update(updates)
            return True
        return False