"""
Sample data initialization for Power Physique Zone
Run this script to populate the database with sample data
"""

from database import db
from datetime import datetime, timedelta

def init_sample_data():
    """Initialize database with sample data"""
    
    print("🚀 Initializing Power Physique Zone Database with Sample Data...\n")
    
    # 1. Create sample users
    print("📝 Creating sample users...")
    users = [
        {
            "username": "jeevan_founder",
            "email": "jeevan@powerphysique.com",
            "password": "admin123",
            "full_name": "Jeevan (Co-Founder)",
            "phone": "9876543210",
            "address": "Hyderabad, India"
        },
        {
            "username": "karthik_founder",
            "email": "karthik@powerphysique.com",
            "password": "admin123",
            "full_name": "Karthik (Co-Founder)",
            "phone": "9876543211",
            "address": "Hyderabad, India"
        },
        {
            "username": "manikanta_founder",
            "email": "manikanta@powerphysique.com",
            "password": "admin123",
            "full_name": "Manikanta (Co-Founder)",
            "phone": "9876543212",
            "address": "Hyderabad, India"
        },
        {
            "username": "john_member",
            "email": "john@example.com",
            "password": "user123",
            "full_name": "John Doe",
            "phone": "9999999999",
            "address": "Amerpet, Hyderabad"
        },
        {
            "username": "jane_member",
            "email": "jane@example.com",
            "password": "user123",
            "full_name": "Jane Smith",
            "phone": "8888888888",
            "address": "Gachibowli, Hyderabad"
        }
    ]
    
    user_ids = []
    for user in users:
        result = db.create_user(**user)
        if result["success"]:
            user_ids.append(result["user_id"])
            print(f"  ✓ Created user: {user['username']}")
    
    # 2. Create sample gym locations
    print("\n📍 Creating gym locations...")
    locations = [
        {"city": "HYD", "area": "AMERPET", "address": "123 Fort St, Amerpet", "phone": "040-23456789"},
        {"city": "HYD", "area": "KUKATPALLY", "address": "456 Main St, Kukatpally", "phone": "040-23456790"},
        {"city": "HYD", "area": "GACHIBOWLI", "address": "789 Tech Park, Gachibowli", "phone": "040-23456791"},
        {"city": "WARANGAL", "area": "HUNTER ROAD", "address": "321 Hunter St, Warangal", "phone": "0870-2456789"},
        {"city": "WARANGAL", "area": "ERRAGATA GUTA", "address": "654 Guta St, Warangal", "phone": "0870-2456790"},
        {"city": "KHAMMAM", "area": "TANK BUND", "address": "111 Tank St, Khammam", "phone": "0870-3456789"},
        {"city": "KHAMMAM", "area": "NTR CIRCLE", "address": "222 NTR Cir, Khammam", "phone": "0870-3456790"},
        {"city": "NALGONDA", "area": "SRINDAR NAGAR", "address": "333 Srindar St, Nalgonda", "phone": "08631-456789"},
        {"city": "MAHABADAD", "area": "SUBADARI", "address": "444 Subadari St, Mahabadad", "phone": "8761-456789"},
    ]
    
    for location in locations:
        result = db.add_gym_location(**location)
        if result["success"]:
            print(f"  ✓ Created location: {location['city']} - {location['area']}")
    
    # 3. Create sample products
    print("\n🛍️  Creating sample products...")
    products = [
        # Protein products
        {
            "name": "Pista Badam 24g Protein Powder - 1KG",
            "category": "Protein",
            "price": 1118.00,
            "description": "Pure pista badam protein with natural flavor",
            "pack_size": "1KG",
            "image_url": "https://storage.googleapis.com/a1aa/image/QPRMqXbeSI02CqtcJMRso2bo3PYa2UM3im11mOvpOSDKbetTA.jpg",
            "stock": 50
        },
        {
            "name": "Unflavoured 30g Whey Protein Isolate - 1KG",
            "category": "Protein",
            "price": 3371.00,
            "description": "Pure whey protein isolate at 90% concentration",
            "pack_size": "1KG",
            "image_url": "https://storage.googleapis.com/a1aa/image/OR8qFK43v9KtMB0XvO7ca9COSj6JJM53L4JwMSwD55mlNf2JA.jpg",
            "stock": 45
        },
        {
            "name": "Cold Coffee 24g Protein Powder - 1KG",
            "category": "Protein",
            "price": 3110.00,
            "description": "Real coffee flavor with protein boost",
            "pack_size": "1KG",
            "image_url": "https://storage.googleapis.com/a1aa/image/KfwfxpSZuciPfITLRrOl2bIOL5fiODIKkUiOFRR26cKOZz3OB.jpg",
            "stock": 40
        },
        {
            "name": "Light Cocoa 24g Protein Powder - 1KG",
            "category": "Protein",
            "price": 3110.00,
            "description": "Lightly flavored with real cocoa powder",
            "pack_size": "1KG",
            "image_url": "https://storage.googleapis.com/a1aa/image/HrNArfOu9jXICSsRVEy30HOY3W3ZmZ8Xkz5H7wSOqCRGbetTA.jpg",
            "stock": 35
        },
        # Food Diet products
        {
            "name": "Chicken Breast - Premium",
            "category": "FoodDiet",
            "price": 299.00,
            "description": "150-200 gms chicken breast 1 to 1.5 hours before workout",
            "pack_size": "500g",
            "image_url": "https://storage.googleapis.com/a1aa/image/bgqe4ezHkzttFk7xvuVhD2juiRbnGG7ChxpZNVxgAaLCe5bnA.jpg",
            "stock": 100
        },
        {
            "name": "Brown Rice - Organic",
            "category": "FoodDiet",
            "price": 89.00,
            "description": "150 gms brown rice - great source of carbohydrates",
            "pack_size": "1KG",
            "image_url": "https://storage.googleapis.com/a1aa/image/vsxj2HlISTrUDpz05nCMxybiDGPWWZQT63kJOh2LJFFgPf2JA.jpg",
            "stock": 80
        },
        {
            "name": "Greek Yogurt - Plain",
            "category": "FoodDiet",
            "price": 120.00,
            "description": "Pure greek yogurt for post-workout recovery",
            "pack_size": "500g",
            "image_url": "https://storage.googleapis.com/a1aa/image/LDsSvHc1JnLHBVM8x13i4TLeJTq6enFIK6JZ82DIUxL998tTA.jpg",
            "stock": 60
        },
        {
            "name": "Eggs - Free Range",
            "category": "FoodDiet",
            "price": 149.00,
            "description": "Fresh free range eggs for daily protein",
            "pack_size": "6 pieces",
            "image_url": "https://storage.googleapis.com/a1aa/image/beCj3jBrp31cc6fpE2MSie6HONZOmBsTo8oWH70CceEp3z3OB.jpg",
            "stock": 150
        },
        # Equipment
        {
            "name": "Dumbbells Set - 20kg",
            "category": "Equipment",
            "price": 2499.00,
            "description": "Complete dumbbell set with stand",
            "pack_size": "20kg set",
            "image_url": "https://www.altrafit.co.uk/cdn/shop/files/altrafit-urethane-studio-dumbell.jpg",
            "stock": 25
        },
        {
            "name": "Yoga Mat - Premium",
            "category": "Equipment",
            "price": 1299.00,
            "description": "High-quality non-slip yoga mat",
            "pack_size": "6mm thickness",
            "image_url": "https://c4.wallpaperflare.com/wallpaper/82/384/903/pose-elongation-yoga-exercises-wallpaper-preview.jpg",
            "stock": 40
        }
    ]
    
    for product in products:
        result = db.add_product(**product)
        if result["success"]:
            print(f"  ✓ Created product: {product['name']}")
    
    # 4. Create sample questions
    print("\n❓ Creating sample questions...")
    sample_questions = [
        {
            "user_name": "John Doe",
            "question_text": "What is the best workout routine for beginners?",
            "user_id": user_ids[3] if len(user_ids) > 3 else None
        },
        {
            "user_name": "Jane Smith",
            "question_text": "How much protein should I take daily?",
            "user_id": user_ids[4] if len(user_ids) > 4 else None
        },
        {
            "user_name": "Anonymous User",
            "question_text": "What supplements are recommended for muscle gain?",
            "user_id": None
        },
        {
            "user_name": "John Doe",
            "question_text": "How long should rest days be?",
            "user_id": user_ids[3] if len(user_ids) > 3 else None
        }
    ]
    
    for question in sample_questions:
        result = db.add_question(**question)
        if result["success"]:
            print(f"  ✓ Created question: {question['question_text'][:50]}...")
    
    # 5. Create sample contact messages
    print("\n✉️  Creating sample contact messages...")
    sample_messages = [
        {
            "name": "Rajesh Kumar",
            "email": "rajesh@example.com",
            "subject": "Membership Inquiry",
            "message": "I'm interested in joining the gym. Can you provide more information about your plans?"
        },
        {
            "name": "Priya Sharma",
            "email": "priya@example.com",
            "subject": "Personal Training",
            "message": "I would like to know about personal training options at your Gachibowli branch."
        },
        {
            "name": "Amit Patel",
            "email": "amit@example.com",
            "subject": "Group Classes",
            "message": "Are there any yoga or Zumba classes available?"
        }
    ]
    
    for message in sample_messages:
        result = db.add_contact_message(**message)
        if result["success"]:
            print(f"  ✓ Created message from: {message['name']}")
    
    # 6. Print statistics
    print("\n📊 Database Statistics:")
    stats = db.get_dashboard_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Sample data initialization complete!")
    print("\n🎉 Your database is ready to use!")


if __name__ == "__main__":
    try:
        init_sample_data()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
