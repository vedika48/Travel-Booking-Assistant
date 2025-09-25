from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.travel import ChatMessage
from app.services.search_service import EnhancedSearchTools, IntelligentChatBot
from app.services.travel_service import SessionService

router = APIRouter()
search_tools = EnhancedSearchTools()
chat_bot = IntelligentChatBot(search_tools)

@router.post("/message")
async def send_message(chat_data: ChatMessage):
    try:
        # Get current travel state
        travel_state = SessionService.get_travel_state(chat_data.session_key)
        if not travel_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get response from chatbot
        response = chat_bot.get_response(chat_data.message, travel_state)
        
        # Update conversation history
        SessionService.update_travel_state(chat_data.session_key, {
            'conversation_history': travel_state.get('conversation_history', []) + [
                {'role': 'user', 'content': chat_data.message},
                {'role': 'assistant', 'content': response}
            ]
        })
        
        return {
            "response": response,
            "session_key": chat_data.session_key,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")