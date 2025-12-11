"""
Database module for Power Physique Zone
Handles all database operations with SQLite
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os

# Get the database path
DB_PATH = Path(__file__).parent.parent / "database" / "power_physique.db"


class Database:
    """Main database class for Power Physique Zone"""
    
    def __init__(self, db_path: Path = DB_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        
        if not schema_path.exists():
            print(f"Warning: Schema file not found at {schema_path}")
            self._create_default_schema()
            return
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            with open(schema_path, 'r') as f:
                sql_script = f.read()
                cursor.executescript(sql_script)
            conn.commit()
    
    def _create_default_schema(self):
        """Create default schema if SQL file not found"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    full_name VARCHAR(100),
                    phone_number VARCHAR(15),
                    address TEXT,
                    role VARCHAR(20) DEFAULT 'Member',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # User Questions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS User_Questions (
                    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name VARCHAR(100) NOT NULL,
                    question_text TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    answer_text TEXT,
                    answered_by_user_id INTEGER,
                    is_answered BOOLEAN DEFAULT 0
                )
            ''')
            
            # Contact Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Contact_Messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    subject VARCHAR(255),
                    message_text TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    # ========== USER OPERATIONS ==========
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, 
                    full_name: str = "", phone: str = "", address: str = "") -> Dict:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                password_hash = self.hash_password(password)
                
                cursor.execute('''
                    INSERT INTO Users (username, email, password_hash, full_name, 
                                     phone_number, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, password_hash, full_name, phone, address))
                
                conn.commit()
                return {
                    "success": True,
                    "user_id": cursor.lastrowid,
                    "message": "User created successfully"
                }
        except sqlite3.IntegrityError as e:
            return {"success": False, "message": f"User creation failed: {str(e)}"}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user by username and password"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT user_id, username, email, full_name, role FROM Users
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, email, full_name, phone_number, 
                       address, role, created_at FROM Users WHERE user_id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def update_user(self, user_id: int, **kwargs) -> Dict:
        """Update user information"""
        allowed_fields = ['full_name', 'phone_number', 'address', 'email']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return {"success": False, "message": "No valid fields to update"}
        
        set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [user_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE Users SET {set_clause} WHERE user_id = ?', values)
            conn.commit()
            return {"success": True, "message": "User updated successfully"}
    
    # ========== QUESTION OPERATIONS ==========
    
    def add_question(self, user_name: str, question_text: str, user_id: Optional[int] = None) -> Dict:
        """Add a new user question"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO User_Questions (user_id, user_name, question_text)
                    VALUES (?, ?, ?)
                ''', (user_id, user_name, question_text))
                
                conn.commit()
                return {
                    "success": True,
                    "question_id": cursor.lastrowid,
                    "message": "Question submitted successfully"
                }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_all_questions(self) -> List[Dict]:
        """Get all questions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT question_id, user_name, question_text, answer_text, 
                       is_answered, submitted_at FROM User_Questions
                ORDER BY submitted_at DESC
            ''')
            
            questions = cursor.fetchall()
            return [dict(q) for q in questions]
    
    def get_unanswered_questions(self) -> List[Dict]:
        """Get unanswered questions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT question_id, user_name, question_text, submitted_at 
                FROM User_Questions WHERE is_answered = 0
                ORDER BY submitted_at ASC
            ''')
            
            questions = cursor.fetchall()
            return [dict(q) for q in questions]
    
    def answer_question(self, question_id: int, answer_text: str, admin_id: int) -> Dict:
        """Answer a question"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE User_Questions 
                    SET answer_text = ?, is_answered = 1, answered_by_user_id = ?
                    WHERE question_id = ?
                ''', (answer_text, admin_id, question_id))
                
                conn.commit()
                return {"success": True, "message": "Answer added successfully"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    # ========== CONTACT MESSAGE OPERATIONS ==========
    
    def add_contact_message(self, name: str, email: str, subject: str, 
                           message: str) -> Dict:
        """Add a contact message"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Contact_Messages (name, email, subject, message_text)
                    VALUES (?, ?, ?, ?)
                ''', (name, email, subject, message))
                
                conn.commit()
                return {
                    "success": True,
                    "message_id": cursor.lastrowid,
                    "message": "Message sent successfully"
                }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_all_messages(self) -> List[Dict]:
        """Get all contact messages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT message_id, name, email, subject, message_text, 
                       sent_at, is_read FROM Contact_Messages
                ORDER BY sent_at DESC
            ''')
            
            messages = cursor.fetchall()
            return [dict(m) for m in messages]
    
    def mark_message_as_read(self, message_id: int) -> Dict:
        """Mark message as read"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE Contact_Messages SET is_read = 1 WHERE message_id = ?
                ''', (message_id,))
                
                conn.commit()
                return {"success": True, "message": "Message marked as read"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    # ========== PRODUCT OPERATIONS ==========
    
    def add_product(self, name: str, category: str, price: float, 
                   description: str = "", pack_size: str = "", 
                   image_url: str = "", stock: int = 0) -> Dict:
        """Add a new product"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Products (name, category, price, description, 
                                        pack_size, image_url, stock_quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, category, price, description, pack_size, image_url, stock))
                
                conn.commit()
                return {
                    "success": True,
                    "product_id": cursor.lastrowid,
                    "message": "Product added successfully"
                }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get products by category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT product_id, name, category, price, description, 
                       pack_size, image_url, stock_quantity FROM Products
                WHERE category = ? AND stock_quantity > 0
                ORDER BY name ASC
            ''', (category,))
            
            products = cursor.fetchall()
            return [dict(p) for p in products]
    
    def get_all_products(self) -> List[Dict]:
        """Get all products"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT product_id, name, category, price, description, 
                       pack_size, image_url, stock_quantity FROM Products
                ORDER BY category, name
            ''')
            
            products = cursor.fetchall()
            return [dict(p) for p in products]
    
    # ========== GYM LOCATION OPERATIONS ==========
    
    def add_gym_location(self, city: str, area: str, address: str = "", 
                        phone: str = "") -> Dict:
        """Add a gym location"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Gym_Locations (city, area, address, phone)
                    VALUES (?, ?, ?, ?)
                ''', (city, area, address, phone))
                
                conn.commit()
                return {
                    "success": True,
                    "location_id": cursor.lastrowid,
                    "message": "Location added successfully"
                }
        except sqlite3.IntegrityError:
            return {"success": False, "message": "Location already exists"}
    
    def get_all_locations(self) -> List[Dict]:
        """Get all gym locations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT location_id, city, area, address, phone FROM Gym_Locations
                ORDER BY city, area
            ''')
            
            locations = cursor.fetchall()
            return [dict(l) for l in locations]
    
    def get_locations_by_city(self, city: str) -> List[Dict]:
        """Get locations by city"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT location_id, city, area, address, phone FROM Gym_Locations
                WHERE city = ? ORDER BY area
            ''', (city,))
            
            locations = cursor.fetchall()
            return [dict(l) for l in locations]
    
    # ========== STATISTICS ==========
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get user count
            cursor.execute('SELECT COUNT(*) as count FROM Users')
            user_count = cursor.fetchone()['count']
            
            # Get total questions
            cursor.execute('SELECT COUNT(*) as count FROM User_Questions')
            question_count = cursor.fetchone()['count']
            
            # Get unanswered questions
            cursor.execute('SELECT COUNT(*) as count FROM User_Questions WHERE is_answered = 0')
            unanswered = cursor.fetchone()['count']
            
            # Get contact messages
            cursor.execute('SELECT COUNT(*) as count FROM Contact_Messages')
            message_count = cursor.fetchone()['count']
            
            # Get product count
            cursor.execute('SELECT COUNT(*) as count FROM Products')
            product_count = cursor.fetchone()['count']
            
            return {
                "total_users": user_count,
                "total_questions": question_count,
                "unanswered_questions": unanswered,
                "total_messages": message_count,
                "total_products": product_count
            }
    
    # ========== EXPORT OPERATIONS ==========
    
    def export_to_json(self, output_file: str = "backup.json") -> Dict:
        """Export all data to JSON for backup"""
        try:
            data = {
                "questions": self.get_all_questions(),
                "messages": self.get_all_messages(),
                "products": self.get_all_products(),
                "locations": self.get_all_locations(),
                "stats": self.get_dashboard_stats(),
                "exported_at": datetime.now().isoformat()
            }
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=4, default=str)
            
            return {"success": True, "message": f"Data exported to {output_file}"}
        except Exception as e:
            return {"success": False, "message": f"Export failed: {str(e)}"}


# Initialize database instance
db = Database()


if __name__ == "__main__":
    # Test database operations
    print("Database initialized successfully!")
    print(f"Database path: {DB_PATH}")
    
    # Print statistics
    stats = db.get_dashboard_stats()
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
