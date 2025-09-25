from flask import Blueprint, request, jsonify
from app.services.travel_service import SessionService
from app.services.search_service import EnhancedSearchTools

travel_bp = Blueprint('travel', __name__)
search_tools = EnhancedSearchTools()

@travel_bp.route('/sessions/create', methods=['POST'])
def create_session():
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'user_id is required'}), 400
            
        session = SessionService.create_session(data['user_id'])
        return jsonify(session), 201
    except Exception as e:
        return jsonify({'error': f'Session creation failed: {str(e)}'}), 500

@travel_bp.route('/sessions/current/<session_key>', methods=['GET'])
def get_current_session(session_key):
    try:
        session = SessionService.get_session(session_key)
        if session:
            return jsonify(session)
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to get session: {str(e)}'}), 500

@travel_bp.route('/itinerary/generate', methods=['POST'])
def generate_itinerary():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        travel_state = {
            'departure_location': data.get('departure_location'),
            'destination_location': data.get('destination_location'),
            'travel_dates': data.get('travel_dates'),
            'user_profile': data.get('user_profile') or {}
        }
        
        itinerary = search_tools.generate_intelligent_itinerary(travel_state)
        return jsonify(itinerary)
    except Exception as e:
        return jsonify({'error': f'Itinerary generation failed: {str(e)}'}), 500

@travel_bp.route('/guide', methods=['POST'])
def get_travel_guide():
    try:
        data = request.get_json()
        if not data or 'destination' not in data:
            return jsonify({'error': 'destination is required'}), 400
            
        guide_data = search_tools.get_travel_guide(data['destination'])
        return jsonify(guide_data)
    except Exception as e:
        return jsonify({'error': f'Failed to get travel guide: {str(e)}'}), 500

@travel_bp.route('/map', methods=['GET'])
def generate_map():
    try:
        lat = request.args.get('lat', 20.5937, type=float)
        lon = request.args.get('lon', 78.9629, type=float)
        zoom = request.args.get('zoom', 4, type=int)
        
        from app.services.search_service import LocationService
        map_data = LocationService.create_map(lat, lon, zoom)
        return jsonify({'map_base64': map_data})
    except Exception as e:
        return jsonify({'error': f'Map generation failed: {str(e)}'}), 500