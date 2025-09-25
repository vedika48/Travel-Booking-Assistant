import os
import json
import requests
from urllib.parse import quote_plus
from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict

# Groq API import
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError as e:
    print(f"Groq dependencies missing: {e}")
    GROQ_AVAILABLE = False

# Tavily imports
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

class TravelState(TypedDict):
    user_query: str
    user_profile: Optional[Dict]
    session_key: str
    conversation_history: List[Dict]
    current_agent: str
    departure_location: Optional[str]
    destination_location: Optional[str]
    travel_mode: Optional[str]
    travel_dates: Optional[Dict]
    specific_area_pune: Optional[str]
    flight_data: Optional[Dict]
    hotel_data: Optional[Dict]
    cab_data: Optional[Dict]
    train_data: Optional[Dict]
    bus_data: Optional[Dict]
    selected_options: Dict[str, Any]
    final_itinerary: Optional[Dict]
    booking_status: Dict
    communication_logs: List[Dict]
    is_intracity: bool
    guide_data: Optional[Dict]

class LocationService:
    @staticmethod
    def geocode_location(address: str) -> Optional[Dict]:
        if not address: return None
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={quote_plus(address)}&format=json&addressdetails=1"
            headers = {'User-Agent': 'TravelBot/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]
            return None
        except Exception as e:
            print(f"Geocoding failed for '{address}': {e}")
            return None

    @staticmethod
    def create_map(center_lat=20.5937, center_lon=78.9629, zoom=4):
        import folium
        return folium.Map(location=[center_lat, center_lon], zoom_start=zoom)

class DeepLinkGenerator:
    IATA_CODES = {'pune': 'PNQ', 'mumbai': 'BOM', 'delhi': 'DEL', 'bengaluru': 'BLR', 'chennai': 'MAA', 'kolkata': 'CCU', 'hyderabad': 'HYD', 'goa': 'GOI'}
    STATION_CODES = {'pune': 'PUNE', 'mumbai': 'CSTM', 'delhi': 'NDLS', 'bengaluru': 'SBC', 'chennai': 'MAS', 'kolkata': 'HWH', 'hyderabad': 'SC'}
    LOCAL_BUS_SITES = {'pune': ('PMPML', 'https://www.pmpml.org/'), 'mumbai': ('BEST', 'https://www.bestundertaking.com/'), 'delhi': ('DTC', 'http://www.dtc.nic.in/'), 'bengaluru': ('BMTC', 'https://mybmtc.karnataka.gov.in/')}

    @staticmethod
    def for_local_buses(city: str) -> Dict[str, str]:
        city_lower = city.lower().split(',')[0].strip()
        if city_lower in DeepLinkGenerator.LOCAL_BUS_SITES:
            name, url = DeepLinkGenerator.LOCAL_BUS_SITES[city_lower]
            return {name: url}
        return {}

    @staticmethod
    def for_flights(dep_city: str, dest_city: str, date: datetime) -> Dict[str, str]:
        dep_code = DeepLinkGenerator.IATA_CODES.get(dep_city.lower(), dep_city)
        dest_code = DeepLinkGenerator.IATA_CODES.get(dest_city.lower(), dest_city)
        date_str = date.strftime("%y%m%d")
        links = {"MakeMyTrip": f"https://www.makemytrip.com/flight/search?itinerary={dep_code}-{dest_code}-{date_str}", "Goibibo": f"https://www.goibibo.com/flights/air-{dep_code}-{dest_code}-1-0-0-E-D/"}
        return links

    @staticmethod
    def for_hotels(city: str, checkin: datetime, checkout: datetime) -> Dict[str, str]:
        city_q = quote_plus(city)
        checkin_str = checkin.strftime("%Y-%m-%d")
        checkout_str = checkout.strftime("%Y-%m-%d")
        links = {"Booking.com": f"https://www.booking.com/searchresults.html?ss={city_q}&checkin={checkin_str}&checkout={checkout_str}", "Agoda": f"https://www.agoda.com/search?city={city_q}&checkIn={checkin_str}&checkOut={checkout_str}"}
        return links

    @staticmethod
    def for_intercity_cabs(dep_coords: Dict, dest_coords: Dict, dep_city: str, dest_city: str) -> Dict[str, str]:
        links = {}
        if dep_coords and dest_coords:
            links["Uber"] = (
                f"https://m.uber.com/ul/?action=setPickup&pickup[latitude]={dep_coords['lat']}&pickup[longitude]={dep_coords['lon']}"
                f"&dropoff[latitude]={dest_coords['lat']}&dropoff[longitude]={dest_coords['lon']}"
            )
            links["Ola (Mobile)"] = (
                f"ola://app/launch?pickup_lat={dep_coords['lat']}&pickup_lng={dep_coords['lon']}"
                f"&drop_lat={dest_coords['lat']}&drop_lng={dest_coords['lon']}&category=outstation"
            )
        return links

    @staticmethod
    def for_trains(dep_city: str, dest_city: str, date: datetime) -> Dict[str, str]:
        dep_code = DeepLinkGenerator.STATION_CODES.get(dep_city.lower(), dep_city)
        dest_code = DeepLinkGenerator.STATION_CODES.get(dest_city.lower(), dest_city)
        date_str = date.strftime("%d-%m-%Y")
        links = {"RailYatri": f"https://www.railyatri.in/train-ticket/from-{dep_code}/to-{dest_code}?date={date_str}"}
        return links

    @staticmethod
    def for_buses(dep_city: str, dest_city: str, date: datetime) -> Dict[str, str]:
        date_str = date.strftime("%Y-%m-%d")
        links = {"redBus": f"https://www.redbus.in/search?fromCityName={dep_city.title()}&toCityName={dest_city.title()}&src={quote_plus(dep_city)}&dst={quote_plus(dest_city)}&onward={date_str}"}
        return links

class GroqLLM:
    def __init__(self, api_key: str, model_name: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model_name = model_name
        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            self.client = None
            
    def invoke(self, prompt: str) -> str:
        if not self.client:
            return "Groq API not available. Please check your API key."
        try:
            chat_completion = self.client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=self.model_name)
            response = chat_completion.choices[0].message.content
            return response if response else "Sorry, I couldn't generate a proper response."
        except Exception as e:
            print(f"Groq API Error: {e}")
            return f"Error generating response: {e}"

class EnhancedSearchTools:
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.setup_search_tools()
        self.setup_llm()
    
    def setup_llm(self):
        if self.groq_api_key and GROQ_AVAILABLE:
            self.llm = GroqLLM(self.groq_api_key)
        else:
            self.llm = None
    
    def setup_search_tools(self):
        try:
            if LANGCHAIN_AVAILABLE:
                self.duckduckgo_search = DuckDuckGoSearchRun()
            else:
                self.duckduckgo_search = None
            if self.tavily_api_key and TAVILY_AVAILABLE:
                self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
            else:
                self.tavily_client = None
        except Exception as e:
            print(f"Error setting up search tools: {e}")
            self.duckduckgo_search = None
            self.tavily_client = None

    def search_web(self, query: str, search_type: str = "general") -> str:
        results = []
        if self.tavily_client:
            try:
                tavily_results = self.tavily_client.search(query, max_results=3)
                for result in tavily_results.get('results', []):
                    results.append({'title': result.get('title', ''), 'content': result.get('content', ''), 'url': result.get('url', ''), 'source': 'Tavily'})
            except Exception as e:
                print(f"Tavily search failed: {e}")
        if self.serper_api_key and len(results) < 3:
            try:
                results.extend(self.serper_search(query))
            except Exception as e:
                print(f"Serper search failed: {e}")
        if self.duckduckgo_search and len(results) < 2:
            try:
                ddg_result = self.duckduckgo_search.run(query)
                results.append({'title': query, 'content': ddg_result, 'url': '', 'source': 'DuckDuckGo'})
            except Exception as e:
                print(f"DuckDuckGo search failed: {e}")
        if results:
            return "\n\n".join([f"Source: {r['source']}\nTitle: {r['title']}\nContent: {r['content'][:500]}..." for r in results])
        else:
            return f"No search results found for: {query}."

    def serper_search(self, query: str) -> List[Dict]:
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({"q": query, "num": 5, "gl": "in", "hl": "en"})
            headers = {'X-API-KEY': self.serper_api_key, 'Content-Type': 'application/json'}
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [{'title': i.get('title', ''), 'content': i.get('snippet', ''), 'url': i.get('link', ''), 'source': 'Google (Serper)'} for i in data.get('organic', [])[:3]]
        except Exception as e:
            print(f"Serper API error: {e}")
            return []

    def _execute_search(self, query: str, instruction: str) -> Dict:
        search_results = self.search_web(query)
        processed_data = "AI processing not available."
        if self.llm and self.llm.client:
            try:
                processed_data = self.process_search_with_llm(search_results, instruction)
            except Exception as e:
                processed_data = f"AI processing error: {e}"
        return {"search_results": search_results, "processed_data": processed_data, "search_query": query, "timestamp": datetime.now().isoformat()}
        
    def search_flights(self, departure: str, destination: str, date: str = None) -> Dict:
        query = f"flights from {departure} to {destination} on {date or 'today'} prices booking airlines"
        instruction = f"Extract flight info from {departure} to {destination}, including airlines, prices, and booking links."
        return self._execute_search(query, instruction)
    
    def search_hotels(self, city: str, area: str = None, checkin: str = None, checkout: str = None) -> Dict:
        location = f"{area}, {city}" if area else city
        date_info = f"check-in {checkin} check-out {checkout}" if checkin and checkout else ""
        query = f"hotels in {location} booking prices ratings {date_info}"
        instruction = f"Extract hotel info for {location}, including names, ratings, prices, and booking links."
        return self._execute_search(query, instruction)

    def search_intercity_cab(self, departure: str, destination: str, date: str = None) -> Dict:
        query = f"intercity cab from {departure} to {destination} on {date or 'today'} one way price booking"
        instruction = f"Extract intercity cab options from {departure} to {destination}, including providers (Ola, Uber, local), car types, and estimated fares."
        return self._execute_search(query, instruction)

    def search_trains(self, departure: str, destination: str, date: str = None) -> Dict:
        query = f"trains from {departure} to {destination} on {date or 'today'} IRCTC seat availability classes price"
        instruction = f"Extract train information from {departure} to {destination}, including train names/numbers, travel classes (AC, Sleeper), and approximate ticket prices."
        return self._execute_search(query, instruction)

    def search_buses(self, departure: str, destination: str, date: str = None) -> Dict:
        query = f"bus from {departure} to {destination} on {date or 'today'} redbus abhibus price AC sleeper"
        instruction = f"Extract bus travel options from {departure} to {destination}, including bus operators, types (AC, Sleeper, Seater), and ticket prices."
        return self._execute_search(query, instruction)

    def process_search_with_llm(self, search_results: str, instruction: str) -> str:
        if not self.llm or not self.llm.client:
            return "AI processing not available."
        try:
            prompt = f"""
            Task: Extract CONCISE, ACTIONABLE information from the search results below.
            Instructions:
            - Focus on specific prices (in INR), names (hotels, airlines, etc.), and booking websites.
            - {instruction}
            - Format the output clearly using markdown lists.
            - Keep the summary under 150 words. Be practical.
            Search Results:
            {search_results[:2000]}
            Summary:
            """
            return self.llm.invoke(prompt)
        except Exception as e:
            return f"Processing error: {e}."

    def get_travel_guide(self, city: str) -> Dict:
        print(f"Creating guide for {city}...")
        
        yt_query = f"YouTube videos for tourists in {city} attractions and food"
        search_results = ""
        if self.tavily_client:
            try:
                tavily_response = self.tavily_client.search(yt_query, search_depth="advanced", max_results=5)
                search_results = "\n".join([f"URL: {r['url']} Content: {r['content']}" for r in tavily_response.get('results', [])])
            except Exception:
                search_results = self.search_web(yt_query)
        else:
            search_results = self.search_web(yt_query)

        yt_instruction = f"""
        From the provided search results, extract up to 3 real, valid YouTube video URLs for a tourist visiting {city}.
        - The URL MUST start with 'https://www.youtube.com/watch?v='.
        - Do NOT invent or create any URLs.
        - If you cannot find any valid YouTube URLs in the results, respond with ONLY the text 'No valid videos found.'
        - Format the valid links you find as a markdown list: '- [Title](URL)'
        """
        youtube_links_md = self.process_search_with_llm(search_results, yt_instruction)
        google_earth_link = f"https://earth.google.com/web/search/{quote_plus(city)}"
        
        return {"youtube_links_md": youtube_links_md, "google_earth_link": google_earth_link, "city": city}

    def generate_intelligent_itinerary(self, travel_state: TravelState) -> Dict:
        departure_str = travel_state.get('departure_location', '')
        destination_str = travel_state.get('destination_location', 'Your Destination')
        user_profile = travel_state.get('user_profile', {})
        travel_dates = travel_state.get('travel_dates', {})

        duration_in_days = 1
        if travel_dates and travel_dates.get('return') and travel_dates.get('departure'):
            try:
                start_date = datetime.fromisoformat(travel_dates['departure'])
                end_date = datetime.fromisoformat(travel_dates['return'])
                duration_in_days = (end_date - start_date).days + 1
                if duration_in_days <= 0:
                    duration_in_days = 1
            except (ValueError, TypeError):
                duration_in_days = 3

        departure_details = LocationService.geocode_location(departure_str)
        destination_details = LocationService.geocode_location(destination_str)
        
        is_intracity = False
        if departure_details and destination_details:
            dep_city = departure_details.get('address', {}).get('city') or departure_details.get('address', {}).get('county')
            dest_city = destination_details.get('address', {}).get('city') or destination_details.get('address', {}).get('county')
            if dep_city and dest_city and dep_city.lower() == dest_city.lower():
                is_intracity = True
        
        itinerary_prompt = ""
        display_duration = f"{duration_in_days} Day(s)"

        if is_intracity:
            display_duration = "Local Outing"
            itinerary_prompt = f"""
            Create a plan for a local, one-day outing. The user wants to explore the area around "{destination_str}".
            Instructions: Suggest 3-4 interesting local places. Create a simple schedule. Include suggestions for local transport and estimated costs.
            """
        else:
            itinerary_prompt = f"""
            Create a practical {duration_in_days}-day travel itinerary for {destination_str.title()}.
            - The itinerary should span exactly {duration_in_days} days.
            - For each day, suggest 2-4 main activities with timings.
            - Include approximate costs in local currency and suggestions for transport.
            - Provide a total estimated budget summary for the trip (excluding flights/hotels).
            Keep the response concise and well-formatted.
            """
        
        try:
            if self.llm and self.llm.client:
                itinerary_content = self.llm.invoke(itinerary_prompt)
            else:
                itinerary_content = "Itinerary generation is currently unavailable."
            
            return {
                "traveler": user_profile.get('name', 'Traveler'),
                "destination": destination_str.title(),
                "duration": display_duration,
                "itinerary": itinerary_content,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"error": str(e)}

class IntelligentChatBot:
    def __init__(self, search_tools: EnhancedSearchTools):
        self.search_tools = search_tools
    
    def get_response(self, user_message: str, travel_state: TravelState) -> str:
        try:
            context = self._build_context(travel_state)
            enhanced_prompt = f"You are a helpful travel assistant. Current travel context: {context}. User Message: {user_message}. Provide a helpful, conversational response. If you need current information like prices or availability, I will provide it."
            
            if self._needs_search(user_message):
                search_results = self.search_tools.search_web(user_message)
                enhanced_prompt += f"\n\nCurrent Information from Web Search:\n{search_results[:1000]}"
            
            if self.search_tools.llm and self.search_tools.llm.client:
                return self.search_tools.llm.invoke(enhanced_prompt)
            else:
                return f"I can provide general advice about '{user_message}'. For specific, live data, my AI core is currently offline."
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request. Error: {e}."
    
    def _build_context(self, travel_state: TravelState) -> str:
        parts = []
        if travel_state.get('destination_location'): parts.append(f"Destination: {travel_state['destination_location']}")
        if travel_state.get('departure_location'): parts.append(f"Departure: {travel_state['departure_location']}")
        if travel_state.get('travel_dates'): parts.append(f"Dates: {travel_state['travel_dates']}")
        return "; ".join(parts) or "No specific travel context"
    
    def _needs_search(self, message: str) -> bool:
        return any(k in message.lower() for k in ['current', 'latest', 'today', 'price', 'cost', 'booking', 'available', 'weather', 'flights', 'hotels', 'trains', 'bus', 'cab'])