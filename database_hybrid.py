"""
Database module supporting both SQLite and MySQL (XAMPP)
Automatically detects and uses the appropriate database
"""

import mysql.connector
from mysql.connector import Error
import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Database paths
DB_PATH = Path(__file__).parent.parent / "database" / "power_physique.db"
XAMPP_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'power_physique',
    'port': 3306
}


class Database:
    """Database class supporting both SQLite and MySQL"""
    
    def __init__(self, use_mysql=False, config=None):
        """
        Initialize database
        
        Args:
            use_mysql (bool): Use MySQL (XAMPP) or SQLite
            config (dict): Custom MySQL configuration
        """
        self.use_mysql = use_mysql
        self.config = config or XAMPP_CONFIG
        self.db_path = DB_PATH
        
        if use_mysql:
            self.init_mysql_db()
        else:
            self.init_sqlite_db()
    
    # ==================== MYSQL FUNCTIONS ====================
    
    def get_mysql_connection(self):
        """Get MySQL connection"""
        try:
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                port=self.config['port']
            )
            return conn
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def init_mysql_db(self):
        """Initialize MySQL database with schema"""
        try:
            conn = self.get_mysql_connection()
            if not conn:
                print("Failed to connect to MySQL")
                return
            
            cursor = conn.cursor()
            
            # Read schema file
            schema_path = Path(__file__).parent.parent / "database" / "schema_mysql.sql"
            
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    sql_script = f.read()
                    # Execute each statement
                    for statement in sql_script.split(';'):
                        if statement.strip():
                            try:
                                cursor.execute(statement)
                            except Error as e:
                                if "already exists" not in str(e):
                                    print(f"Error executing: {e}")
                conn.commit()
                print("✓ MySQL database initialized successfully")
            else:
                self._create_mysql_tables(conn)
            
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error initializing MySQL: {e}")
    
    def _create_mysql_tables(self, conn):
        """Create MySQL tables"""
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                phone_number VARCHAR(15),
                address TEXT,
                role VARCHAR(20) DEFAULT 'Member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_username (username),
                INDEX idx_email (email)
            )
        ''')
        
        # User_Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User_Questions (
                question_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                user_name VARCHAR(100) NOT NULL,
                question_text LONGTEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                answer_text LONGTEXT,
                answered_by_user_id INT,
                is_answered BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
                FOREIGN KEY (answered_by_user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_is_answered (is_answered)
            )
        ''')
        
        # Contact_Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Contact_Messages (
                message_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                subject VARCHAR(255),
                message_text LONGTEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT FALSE,
                INDEX idx_email (email),
                INDEX idx_sent_at (sent_at)
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                product_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                description LONGTEXT,
                pack_size VARCHAR(50),
                image_url VARCHAR(255),
                stock_quantity INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_category (category)
            )
        ''')
        
        # Gym_Locations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Gym_Locations (
                location_id INT PRIMARY KEY AUTO_INCREMENT,
                city VARCHAR(50) NOT NULL,
                area VARCHAR(100) NOT NULL UNIQUE,
                address TEXT,
                phone VARCHAR(15),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_city (city)
            )
        ''')
        
        conn.commit()
        print("✓ MySQL tables created successfully")
    
    # ==================== SQLITE FUNCTIONS ====================
    
    def get_sqlite_connection(self):
        """Get SQLite connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_sqlite_db(self):
        """Initialize SQLite database"""
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        
        if not schema_path.exists():
            print("Warning: Schema file not found")
            return
        
        with self.get_sqlite_connection() as conn:
            cursor = conn.cursor()
            with open(schema_path, 'r') as f:
                sql_script = f.read()
                cursor.executescript(sql_script)
            conn.commit()
            print("✓ SQLite database initialized successfully")
    
    # ==================== COMMON FUNCTIONS ====================
    
    def get_connection(self):
        """Get appropriate database connection"""
        if self.use_mysql:
            return self.get_mysql_connection()
        else:
            return self.get_sqlite_connection()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username: str, email: str, password: str,
                    full_name: str = "", phone: str = "", address: str = "") -> Dict:
        """Create a new user"""
        try:
            password_hash = self.hash_password(password)
            
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Users (username, email, password_hash, full_name,
                                     phone_number, address)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (username, email, password_hash, full_name, phone, address))
                conn.commit()
                user_id = cursor.lastrowid
                cursor.close()
                conn.close()
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Users (username, email, password_hash, full_name,
                                     phone_number, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, password_hash, full_name, phone, address))
                conn.commit()
                user_id = cursor.lastrowid
                conn.close()
            
            return {"success": True, "user_id": user_id, "message": "User created successfully"}
        
        except Exception as e:
            return {"success": False, "message": f"User creation failed: {str(e)}"}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        try:
            password_hash = self.hash_password(password)
            
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT user_id, username, email, full_name, role
                    FROM Users
                    WHERE username = %s AND password_hash = %s AND is_active = TRUE
                ''', (username, password_hash))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                return user
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, email, full_name, role FROM Users
                    WHERE username = ? AND password_hash = ? AND is_active = 1
                ''', (username, password_hash))
                user = cursor.fetchone()
                conn.close()
                return dict(user) if user else None
        
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT user_id, username, email, full_name, phone_number,
                           address, role, created_at FROM Users WHERE user_id = %s
                ''', (user_id,))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                return user
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, email, full_name, phone_number,
                           address, role, created_at FROM Users WHERE user_id = ?
                ''', (user_id,))
                user = cursor.fetchone()
                conn.close()
                return dict(user) if user else None
        
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    # ==================== QUESTION OPERATIONS ====================
    
    def add_question(self, user_name: str, question_text: str, user_id: Optional[int] = None) -> Dict:
        """Add a question"""
        try:
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO User_Questions (user_id, user_name, question_text)
                    VALUES (%s, %s, %s)
                ''', (user_id, user_name, question_text))
                conn.commit()
                question_id = cursor.lastrowid
                cursor.close()
                conn.close()
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO User_Questions (user_id, user_name, question_text)
                    VALUES (?, ?, ?)
                ''', (user_id, user_name, question_text))
                conn.commit()
                question_id = cursor.lastrowid
                conn.close()
            
            return {"success": True, "question_id": question_id, "message": "Question submitted successfully"}
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_all_questions(self) -> List[Dict]:
        """Get all questions"""
        try:
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT question_id, user_name, question_text, answer_text,
                           is_answered, submitted_at FROM User_Questions
                    ORDER BY submitted_at DESC
                ''')
                questions = cursor.fetchall()
                cursor.close()
                conn.close()
                return questions if questions else []
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT question_id, user_name, question_text, answer_text,
                           is_answered, submitted_at FROM User_Questions
                    ORDER BY submitted_at DESC
                ''')
                questions = cursor.fetchall()
                conn.close()
                return [dict(q) for q in questions] if questions else []
        
        except Exception as e:
            print(f"Error getting questions: {e}")
            return []
    
    def answer_question(self, question_id: int, answer_text: str, admin_id: int) -> Dict:
        """Answer a question"""
        try:
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE User_Questions
                    SET answer_text = %s, is_answered = TRUE, answered_by_user_id = %s
                    WHERE question_id = %s
                ''', (answer_text, admin_id, question_id))
                conn.commit()
                cursor.close()
                conn.close()
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE User_Questions
                    SET answer_text = ?, is_answered = 1, answered_by_user_id = ?
                    WHERE question_id = ?
                ''', (answer_text, admin_id, question_id))
                conn.commit()
                conn.close()
            
            return {"success": True, "message": "Answer added successfully"}
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    # ==================== CONTACT OPERATIONS ====================
    
    def add_contact_message(self, name: str, email: str, subject: str, message: str) -> Dict:
        """Add contact message"""
        try:
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Contact_Messages (name, email, subject, message_text)
                    VALUES (%s, %s, %s, %s)
                ''', (name, email, subject, message))
                conn.commit()
                message_id = cursor.lastrowid
                cursor.close()
                conn.close()
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Contact_Messages (name, email, subject, message_text)
                    VALUES (?, ?, ?, ?)
                ''', (name, email, subject, message))
                conn.commit()
                message_id = cursor.lastrowid
                conn.close()
            
            return {"success": True, "message_id": message_id, "message": "Message sent successfully"}
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_all_messages(self) -> List[Dict]:
        """Get all contact messages"""
        try:
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT message_id, name, email, subject, message_text,
                           sent_at, is_read FROM Contact_Messages
                    ORDER BY sent_at DESC
                ''')
                messages = cursor.fetchall()
                cursor.close()
                conn.close()
                return messages if messages else []
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT message_id, name, email, subject, message_text,
                           sent_at, is_read FROM Contact_Messages
                    ORDER BY sent_at DESC
                ''')
                messages = cursor.fetchall()
                conn.close()
                return [dict(m) for m in messages] if messages else []
        
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        try:
            if self.use_mysql:
                conn = self.get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute('SELECT COUNT(*) as count FROM Users')
                user_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM User_Questions')
                question_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM User_Questions WHERE is_answered = FALSE')
                unanswered = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM Contact_Messages')
                message_count = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM Products')
                product_count = cursor.fetchone()['count']
                
                cursor.close()
                conn.close()
            else:
                conn = self.get_sqlite_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) as count FROM Users')
                user_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) as count FROM User_Questions')
                question_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) as count FROM User_Questions WHERE is_answered = 0')
                unanswered = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) as count FROM Contact_Messages')
                message_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) as count FROM Products')
                product_count = cursor.fetchone()[0]
                
                conn.close()
            
            return {
                "total_users": user_count,
                "total_questions": question_count,
                "unanswered_questions": unanswered,
                "total_messages": message_count,
                "total_products": product_count
            }
        
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}


# Initialize with SQLite by default, set use_mysql=True to use MySQL
db = Database(use_mysql=False)

if __name__ == "__main__":
    print("Database module loaded successfully!")
    print(f"Using MySQL: {db.use_mysql}")
    stats = db.get_dashboard_stats()
    print(f"Database stats: {stats}")
