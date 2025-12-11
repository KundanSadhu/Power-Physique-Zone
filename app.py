from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import db
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS to allow requests from frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})


@app.route("/")
def root() -> str:
    """Simple health-check endpoint."""
    return "Backend is running. Use the /api endpoints to interact with data."


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    stats = db.get_dashboard_stats()
    return jsonify({
        "status": "healthy",
        "message": "Backend is running",
        "stats": stats
    }), 200


# ========== QUESTION ENDPOINTS ==========

@app.route("/api/questions", methods=["GET"])
def get_questions():
    """Return the list of stored questions with answers."""
    try:
        questions = db.get_all_questions()
        return jsonify(questions), 200
    except Exception as e:
        logger.error(f"Error fetching questions: {str(e)}")
        return jsonify({"error": "Failed to fetch questions"}), 500


@app.route("/api/questions", methods=["POST"])
def submit_question():
    """Receive and save a new user question."""
    try:
        payload = request.get_json(silent=True) or {}

        username = (payload.get("username") or "").strip()
        question_text = (payload.get("question") or "").strip()

        if not username or not question_text:
            return jsonify({
                "message": "Both 'username' and 'question' are required fields.",
                "received": payload
            }), 400

        # Add question to database
        result = db.add_question(username, question_text)
        
        if result["success"]:
            return jsonify({
                "message": result["message"],
                "question_id": result["question_id"],
                "status": "pending"
            }), 201
        else:
            return jsonify({"message": result["message"]}), 500

    except Exception as e:
        logger.error(f"Error submitting question: {str(e)}")
        return jsonify({"error": "Failed to submit question"}), 500


@app.route("/api/questions/<int:question_id>", methods=["GET"])
def get_question(question_id):
    """Get a specific question"""
    try:
        questions = db.get_all_questions()
        question = next((q for q in questions if q['question_id'] == question_id), None)
        
        if question:
            return jsonify(question), 200
        else:
            return jsonify({"error": "Question not found"}), 404
    except Exception as e:
        logger.error(f"Error fetching question: {str(e)}")
        return jsonify({"error": "Failed to fetch question"}), 500


# ========== CONTACT ENDPOINTS ==========

@app.route("/api/contact", methods=["POST"])
def handle_contact():
    """Handle contact form submission."""
    try:
        payload = request.get_json(silent=True) or {}
        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip()
        subject = (payload.get("subject") or "").strip()
        message = (payload.get("message") or "").strip()

        if not (name and email and message):
            return jsonify({
                "message": "Fields 'name', 'email', and 'message' are required.",
                "received": payload
            }), 400

        # Add contact message to database
        result = db.add_contact_message(name, email, subject, message)
        
        if result["success"]:
            return jsonify({
                "message": result["message"],
                "message_id": result["message_id"]
            }), 200
        else:
            return jsonify({"message": result["message"]}), 500

    except Exception as e:
        logger.error(f"Error handling contact: {str(e)}")
        return jsonify({"error": "Failed to process contact message"}), 500


@app.route("/api/messages", methods=["GET"])
def get_messages():
    """Get all contact messages (admin only)"""
    try:
        messages = db.get_all_messages()
        return jsonify(messages), 200
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        return jsonify({"error": "Failed to fetch messages"}), 500


# ========== USER ENDPOINTS ==========

@app.route("/api/users/signup", methods=["POST"])
def signup():
    """Create a new user account"""
    try:
        payload = request.get_json(silent=True) or {}
        
        username = (payload.get("username") or "").strip()
        email = (payload.get("email") or "").strip()
        password = (payload.get("password") or "").strip()
        full_name = (payload.get("full_name") or "").strip()
        phone = (payload.get("phone") or "").strip()
        address = (payload.get("address") or "").strip()
        
        if not (username and email and password):
            return jsonify({
                "message": "username, email, and password are required"
            }), 400
        
        result = db.create_user(username, email, password, full_name, phone, address)
        
        if result["success"]:
            return jsonify({
                "message": result["message"],
                "user_id": result["user_id"]
            }), 201
        else:
            return jsonify({"message": result["message"]}), 400
    
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        return jsonify({"error": "Failed to create account"}), 500


@app.route("/api/users/login", methods=["POST"])
def login():
    """Authenticate user"""
    try:
        payload = request.get_json(silent=True) or {}
        
        username = (payload.get("username") or "").strip()
        password = (payload.get("password") or "").strip()
        
        if not (username and password):
            return jsonify({"message": "username and password are required"}), 400
        
        user = db.authenticate_user(username, password)
        
        if user:
            return jsonify({
                "message": "Login successful",
                "user": user
            }), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": "Login failed"}), 500


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get user by ID"""
    try:
        user = db.get_user(user_id)
        
        if user:
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
    
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        return jsonify({"error": "Failed to fetch user"}), 500


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Update user information"""
    try:
        payload = request.get_json(silent=True) or {}
        
        result = db.update_user(user_id, **payload)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({"error": "Failed to update user"}), 500


# ========== PRODUCT ENDPOINTS ==========

@app.route("/api/products", methods=["GET"])
def get_products():
    """Get all products"""
    try:
        category = request.args.get("category")
        
        if category:
            products = db.get_products_by_category(category)
        else:
            products = db.get_all_products()
        
        return jsonify(products), 200
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({"error": "Failed to fetch products"}), 500


# ========== GYM LOCATION ENDPOINTS ==========

@app.route("/api/locations", methods=["GET"])
def get_locations():
    """Get all gym locations"""
    try:
        city = request.args.get("city")
        
        if city:
            locations = db.get_locations_by_city(city)
        else:
            locations = db.get_all_locations()
        
        return jsonify(locations), 200
    except Exception as e:
        logger.error(f"Error fetching locations: {str(e)}")
        return jsonify({"error": "Failed to fetch locations"}), 500


# ========== ADMIN ENDPOINTS ==========

@app.route("/api/admin/stats", methods=["GET"])
def get_stats():
    """Get dashboard statistics (admin)"""
    try:
        stats = db.get_dashboard_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({"error": "Failed to fetch statistics"}), 500


@app.route("/api/admin/questions/unanswered", methods=["GET"])
def get_unanswered_questions():
    """Get unanswered questions (admin)"""
    try:
        questions = db.get_unanswered_questions()
        return jsonify(questions), 200
    except Exception as e:
        logger.error(f"Error fetching unanswered questions: {str(e)}")
        return jsonify({"error": "Failed to fetch unanswered questions"}), 500


@app.route("/api/admin/questions/<int:question_id>/answer", methods=["POST"])
def answer_question(question_id):
    """Answer a question (admin)"""
    try:
        payload = request.get_json(silent=True) or {}
        answer_text = (payload.get("answer") or "").strip()
        admin_id = payload.get("admin_id")
        
        if not (answer_text and admin_id):
            return jsonify({"message": "answer and admin_id are required"}), 400
        
        result = db.answer_question(question_id, answer_text, admin_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        return jsonify({"error": "Failed to answer question"}), 500


# ========== ORDER/CART ENDPOINTS ==========

@app.route("/api/orders", methods=["POST"])
def create_order():
    """Create a new order from cart"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_name', 'customer_email', 'customer_phone', 'delivery_address', 'items']
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": "Missing required fields"}), 400
        
        if not data['items']:
            return jsonify({"success": False, "message": "Order must contain items"}), 400
        
        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in data['items'])
        tax = subtotal * 0.1
        total = subtotal + tax
        
        # Store order data (simplified - in production use database)
        order = {
            "order_date": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_name": data['customer_name'],
            "customer_email": data['customer_email'],
            "customer_phone": data['customer_phone'],
            "delivery_address": data['delivery_address'],
            "payment_method": data.get('payment_method', 'Unknown'),
            "items": data['items'],
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "notes": data.get('notes', ''),
            "status": "Pending"
        }
        
        # In production, save to database:
        # db.create_order(order)
        
        logger.info(f"Order created: {data['customer_email']} - Total: ${total}")
        
        return jsonify({
            "success": True,
            "message": "Order placed successfully",
            "order": order
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return jsonify({"success": False, "message": "Failed to create order"}), 500


@app.route("/api/products", methods=["GET"])
def get_products():
    """Get all products by category"""
    try:
        category = request.args.get('category', 'all')
        
        products = [
            {
                "product_id": 1,
                "name": "Whey Protein Powder",
                "category": "Protein",
                "price": 49.99,
                "description": "Premium whey protein isolate for muscle building",
                "pack_size": "2.5 kg"
            },
            {
                "product_id": 2,
                "name": "Casein Protein",
                "category": "Protein",
                "price": 39.99,
                "description": "Slow-release casein protein for overnight recovery",
                "pack_size": "2 kg"
            },
            {
                "product_id": 3,
                "name": "Plant-Based Protein",
                "category": "Protein",
                "price": 44.99,
                "description": "Vegan protein blend with all essential amino acids",
                "pack_size": "1.5 kg"
            },
            {
                "product_id": 4,
                "name": "Chicken Breast Pack",
                "category": "FoodDiet",
                "price": 24.99,
                "description": "Lean protein rich chicken breast - fresh daily",
                "pack_size": "2 kg"
            },
            {
                "product_id": 5,
                "name": "Salmon Fillet",
                "category": "FoodDiet",
                "price": 34.99,
                "description": "Wild-caught salmon rich in Omega-3 fatty acids",
                "pack_size": "1.5 kg"
            },
            {
                "product_id": 6,
                "name": "Organic Quinoa",
                "category": "FoodDiet",
                "price": 19.99,
                "description": "Complete protein with all amino acids - organic",
                "pack_size": "1 kg"
            },
            {
                "product_id": 7,
                "name": "Muscle Building Plan",
                "category": "NutritionPlan",
                "price": 99.99,
                "description": "12-week customized meal plan for muscle growth",
                "pack_size": "Digital"
            },
            {
                "product_id": 8,
                "name": "Fat Loss Program",
                "category": "NutritionPlan",
                "price": 89.99,
                "description": "8-week fat loss meal plan with grocery list",
                "pack_size": "Digital"
            },
            {
                "product_id": 9,
                "name": "Maintenance Plan",
                "category": "NutritionPlan",
                "price": 79.99,
                "description": "Balanced meal plan for weight maintenance",
                "pack_size": "Digital"
            }
        ]
        
        if category != 'all':
            products = [p for p in products if p['category'] == category]
        
        return jsonify({
            "success": True,
            "products": products,
            "total": len(products)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({"success": False, "message": "Failed to fetch products"}), 500


if __name__ == "__main__":
    logger.info(f"Starting Power Physique Zone Backend")
    logger.info(f"Database initialized: {db.db_path}")
    app.run(host="0.0.0.0", port=5000, debug=True)