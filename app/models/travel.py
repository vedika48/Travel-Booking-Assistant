# Since Flask doesn't have built-in validation like Pydantic,
# you can use plain Python classes or add validation libraries

class SessionCreate:
    def __init__(self, user_id: str):
        self.user_id = user_id

class TravelQuery:
    def __init__(self, query: str, session_key: str):
        self.query = query
        self.session_key = session_key

class ItineraryRequest:
    def __init__(self, departure_location: str, destination_location: str, 
                 travel_dates: dict, user_profile: dict = None):
        self.departure_location = departure_location
        self.destination_location = destination_location
        self.travel_dates = travel_dates
        self.user_profile = user_profile or {}

class TravelGuideRequest:
    def __init__(self, destination: str):
        self.destination = destination

class ServiceSearch:
    def __init__(self, departure: str = None, destination: str = None, 
                 date: str = None, checkin: str = None, checkout: str = None):
        self.departure = departure
        self.destination = destination
        self.date = date
        self.checkin = checkin
        self.checkout = checkout

class ChatMessage:
    def __init__(self, message: str, session_key: str):
        self.message = message
        self.session_key = session_key