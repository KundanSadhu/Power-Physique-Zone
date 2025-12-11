"""
Flask App - Supporting both SQLite and MySQL (XAMPP)
Switch between databases by changing USE_MYSQL flag
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from pathlib import Path

# Import the hybrid database module
from database_hybrid import Database

# ==================== CONFIGURATION ====================
app = Flask(__name__)
CORS(app)

# Switch to True to use MySQL (XAMPP), False to use SQLite
USE_MYSQL = False

# Initialize database
db = Database(use_mysql=USE_MYSQL)

print(f"✓ Flask app initialized")
print(f"✓ Using {'MySQL (XAMPP)' if USE_MYSQL else 'SQLite'} database")


# ==================== HELPER FUNCTIONS ====================

def json_response(data, status_code=200):
    """Create JSON response"""
    return jsonify(data), status_code


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ('username', 'email', 'password')):
            return json_response({"success": False, "message": "Missing required fields"}, 400)
        
        result = db.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', ''),
            phone=data.get('phone', ''),
            address=data.get('address', '')
        )
        
        return json_response(result, 201 if result['success'] else 400)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return json_response({"success": False, "message": "Missing username or password"}, 400)
        
        user = db.authenticate_user(data['username'], data['password'])
        
        if user:
            return json_response({"success": True, "user": dict(user)}, 200)
        else:
            return json_response({"success": False, "message": "Invalid username or password"}, 401)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile"""
    try:
        user = db.get_user(user_id)
        
        if user:
            return json_response({"success": True, "user": dict(user)}, 200)
        else:
            return json_response({"success": False, "message": "User not found"}, 404)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


# ==================== QUESTION ROUTES ====================

@app.route('/api/questions', methods=['POST'])
def post_question():
    """Submit a question"""
    try:
        data = request.get_json()
        
        if not data.get('user_name') or not data.get('question_text'):
            return json_response({"success": False, "message": "Missing required fields"}, 400)
        
        result = db.add_question(
            user_name=data['user_name'],
            question_text=data['question_text'],
            user_id=data.get('user_id')
        )
        
        return json_response(result, 201 if result['success'] else 400)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Get all questions"""
    try:
        questions = db.get_all_questions()
        return json_response({
            "success": True,
            "questions": questions,
            "total": len(questions)
        }, 200)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


@app.route('/api/questions/<int:question_id>/answer', methods=['POST'])
def answer_question(question_id):
    """Answer a question (admin only)"""
    try:
        data = request.get_json()
        
        if not data.get('answer_text') or not data.get('admin_id'):
            return json_response({"success": False, "message": "Missing required fields"}, 400)
        
        result = db.answer_question(
            question_id=question_id,
            answer_text=data['answer_text'],
            admin_id=data['admin_id']
        )
        
        return json_response(result, 200 if result['success'] else 400)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


# ==================== CONTACT ROUTES ====================

@app.route('/api/contact', methods=['POST'])
def post_contact():
    """Submit contact message"""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ('name', 'email', 'message')):
            return json_response({"success": False, "message": "Missing required fields"}, 400)
        
        result = db.add_contact_message(
            name=data['name'],
            email=data['email'],
            subject=data.get('subject', ''),
            message=data['message']
        )
        
        return json_response(result, 201 if result['success'] else 400)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all contact messages (admin only)"""
    try:
        messages = db.get_all_messages()
        return json_response({
            "success": True,
            "messages": messages,
            "total": len(messages)
        }, 200)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        stats = db.get_dashboard_stats()
        return json_response({
            "success": True,
            "stats": stats
        }, 200)
    
    except Exception as e:
        return json_response({"success": False, "message": str(e)}, 500)


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        stats = db.get_dashboard_stats()
        return json_response({
            "success": True,
            "status": "healthy",
            "database": "MySQL (XAMPP)" if USE_MYSQL else "SQLite",
            "stats": stats
        }, 200)
    
    except Exception as e:
        return json_response({
            "success": False,
            "status": "unhealthy",
            "message": str(e)
        }, 500)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return json_response({"success": False, "message": "Endpoint not found"}, 404)


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return json_response({"success": False, "message": "Internal server error"}, 500)


# ==================== MAIN ====================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Power Physique Flask Server")
    print("=" * 60)
    print(f"Database: {'MySQL (XAMPP)' if USE_MYSQL else 'SQLite'}")
    print(f"Server: http://localhost:5000")
    print(f"CORS: Enabled")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='localhost', port=5000)
