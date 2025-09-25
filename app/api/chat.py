from flask import Blueprint, request, jsonify
from app.services.search_service import EnhancedSearchTools, IntelligentChatBot
from app.services.travel_service import SessionService
from datetime import datetime

chat_bp = Blueprint('chat', __name__)
search_tools = EnhancedSearchTools()
chat_bot = IntelligentChatBot(search_tools)

@chat_bp.route('/message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        message = data.get('message')
        session_key = data.get('session_key')
        
        if not message or not session_key:
            return jsonify({'error': 'message and session_key are required'}), 400
        
        # Get current travel state
        travel_state = SessionService.get_travel_state(session_key)
        if not travel_state:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get response from chatbot
        response = chat_bot.get_response(message, travel_state)
        
        # Update conversation history
        SessionService.update_travel_state(session_key, {
            'conversation_history': travel_state.get('conversation_history', []) + [
                {'role': 'user', 'content': message},
                {'role': 'assistant', 'content': response}
            ]
        })
        
        return jsonify({
            "response": response,
            "session_key": session_key,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500