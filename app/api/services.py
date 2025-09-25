from flask import Blueprint, request, jsonify
from app.services.search_service import EnhancedSearchTools

services_bp = Blueprint('services', __name__)
search_tools = EnhancedSearchTools()

@services_bp.route('/flights/search', methods=['POST'])
def search_flights():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        results = search_tools.search_flights(
            data.get('departure'),
            data.get('destination'),
            data.get('date')
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'Flight search failed: {str(e)}'}), 500

@services_bp.route('/hotels/search', methods=['POST'])
def search_hotels():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        results = search_tools.search_hotels(
            data.get('destination'),
            data.get('checkin'),
            data.get('checkout')
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'Hotel search failed: {str(e)}'}), 500

@services_bp.route('/transport/search', methods=['POST'])
def search_transportation():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        results = {}
        
        # Search trains
        train_results = search_tools.search_trains(
            data.get('departure'),
            data.get('destination'),
            data.get('date')
        )
        results['trains'] = train_results
        
        # Search buses
        bus_results = search_tools.search_buses(
            data.get('departure'),
            data.get('destination'),
            data.get('date')
        )
        results['buses'] = bus_results
        
        # Search cabs
        cab_results = search_tools.search_intercity_cab(
            data.get('departure'),
            data.get('destination'),
            data.get('date')
        )
        results['cabs'] = cab_results
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'Transport search failed: {str(e)}'}), 500

@services_bp.route('/cabs/local', methods=['POST'])
def search_local_cabs():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        results = search_tools.search_local_cab(
            data.get('departure'),
            data.get('destination')
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'Local cab search failed: {str(e)}'}), 500