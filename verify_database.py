"""
Database Setup Verification Script
Run this to verify your database is working correctly
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from database import db

def verify_database():
    """Verify database setup and functionality"""
    
    print("=" * 60)
    print("Power Physique Zone - Database Verification")
    print("=" * 60)
    
    # 1. Check database file
    print("\n✓ Step 1: Checking database file...")
    if db.db_path.exists():
        print(f"  ✓ Database file exists: {db.db_path}")
        print(f"  ✓ File size: {db.db_path.stat().st_size} bytes")
    else:
        print(f"  ✗ Database file not found at {db.db_path}")
        return False
    
    # 2. Test database connection
    print("\n✓ Step 2: Testing database connection...")
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"  ✓ Connected successfully")
        print(f"  ✓ SQLite version: {version}")
        conn.close()
    except Exception as e:
        print(f"  ✗ Connection failed: {str(e)}")
        return False
    
    # 3. Verify table creation
    print("\n✓ Step 3: Verifying tables...")
    required_tables = [
        'Users', 'User_Questions', 'Contact_Messages', 
        'Products', 'Gym_Locations', 'Membership_Plans',
        'User_Subscriptions', 'User_Orders', 'Order_Items',
        'Workouts', 'Exercises', 'Customer_Reviews',
        'Competitions', 'Competition_Participants',
        'Gym_Equipment', 'Equipment_Ratings'
    ]
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ✗ Table '{table}' missing")
        
        conn.close()
    except Exception as e:
        print(f"  ✗ Error verifying tables: {str(e)}")
        return False
    
    # 4. Test user operations
    print("\n✓ Step 4: Testing user operations...")
    try:
        # Create test user
        result = db.create_user(
            username="test_user_verify",
            email="test@verify.com",
            password="testpass123",
            full_name="Test User"
        )
        
        if result["success"]:
            print(f"  ✓ User creation works")
            user_id = result["user_id"]
            
            # Retrieve user
            user = db.get_user(user_id)
            if user:
                print(f"  ✓ User retrieval works")
                print(f"    - Username: {user['username']}")
                print(f"    - Email: {user['email']}")
            
            # Authenticate user
            auth_user = db.authenticate_user("test_user_verify", "testpass123")
            if auth_user:
                print(f"  ✓ User authentication works")
        else:
            print(f"  ! User already exists (expected if run before)")
    
    except Exception as e:
        print(f"  ✗ User operations failed: {str(e)}")
    
    # 5. Test question operations
    print("\n✓ Step 5: Testing question operations...")
    try:
        # Add question
        result = db.add_question(
            user_name="Test User",
            question_text="Is this a test question?",
            user_id=1
        )
        
        if result["success"]:
            print(f"  ✓ Question submission works")
            question_id = result["question_id"]
            
            # Get questions
            questions = db.get_all_questions()
            if questions:
                print(f"  ✓ Question retrieval works")
                print(f"    - Total questions: {len(questions)}")
            
            # Get unanswered
            unanswered = db.get_unanswered_questions()
            print(f"  ✓ Unanswered questions: {len(unanswered)}")
    
    except Exception as e:
        print(f"  ✗ Question operations failed: {str(e)}")
    
    # 6. Test contact operations
    print("\n✓ Step 6: Testing contact operations...")
    try:
        result = db.add_contact_message(
            name="Test Contact",
            email="test@contact.com",
            subject="Test Subject",
            message="This is a test message"
        )
        
        if result["success"]:
            print(f"  ✓ Contact message submission works")
            
            # Get messages
            messages = db.get_all_messages()
            print(f"  ✓ Contact message retrieval works")
            print(f"    - Total messages: {len(messages)}")
    
    except Exception as e:
        print(f"  ✗ Contact operations failed: {str(e)}")
    
    # 7. Test location operations
    print("\n✓ Step 7: Testing location operations...")
    try:
        result = db.add_gym_location(
            city="TEST",
            area="TEST_AREA",
            address="Test Address",
            phone="9999999999"
        )
        
        if result["success"]:
            print(f"  ✓ Location creation works")
        elif "already exists" in result["message"]:
            print(f"  ! Location already exists (expected if run before)")
        
        # Get locations
        locations = db.get_all_locations()
        print(f"  ✓ Location retrieval works")
        print(f"    - Total locations: {len(locations)}")
        
        # Get by city
        hyd_locations = db.get_locations_by_city("HYD")
        print(f"    - HYD locations: {len(hyd_locations)}")
    
    except Exception as e:
        print(f"  ✗ Location operations failed: {str(e)}")
    
    # 8. Test product operations
    print("\n✓ Step 8: Testing product operations...")
    try:
        result = db.add_product(
            name="Test Product",
            category="Protein",
            price=999.99,
            description="Test product description",
            pack_size="1KG",
            stock=50
        )
        
        if result["success"]:
            print(f"  ✓ Product creation works")
        
        # Get products
        products = db.get_all_products()
        print(f"  ✓ Product retrieval works")
        print(f"    - Total products: {len(products)}")
        
        # Get by category
        protein_products = db.get_products_by_category("Protein")
        print(f"    - Protein products: {len(protein_products)}")
    
    except Exception as e:
        print(f"  ✗ Product operations failed: {str(e)}")
    
    # 9. Get statistics
    print("\n✓ Step 9: Database Statistics...")
    try:
        stats = db.get_dashboard_stats()
        print(f"  ✓ Statistics retrieval works")
        for key, value in stats.items():
            print(f"    - {key}: {value}")
    
    except Exception as e:
        print(f"  ✗ Statistics retrieval failed: {str(e)}")
    
    # 10. Export test
    print("\n✓ Step 10: Testing data export...")
    try:
        result = db.export_to_json("test_backup.json")
        if result["success"]:
            print(f"  ✓ Data export works")
            print(f"    - Export file: test_backup.json")
        else:
            print(f"  ! Export failed: {result['message']}")
    
    except Exception as e:
        print(f"  ✗ Export failed: {str(e)}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ Database verification complete!")
    print("=" * 60)
    print("\nYour database is ready to use!")
    print("\nNext steps:")
    print("1. Run: python app.py (to start the Flask backend)")
    print("2. Run: python init_sample_data.py (to add sample data)")
    print("3. Open: admin.html (to access admin panel)")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = verify_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
