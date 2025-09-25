from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    
    # CORS middleware
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "allow_headers": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })
    
    # Register blueprints
    from app.api.travel import travel_bp
    from app.api.chat import chat_bp
    from app.api.services import services_bp
    
    app.register_blueprint(travel_bp, url_prefix='/api/travel')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({"message": "Travel Assistant API is running"})
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "travel-assistant-api"})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

app = create_app()