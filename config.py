"""
Database configuration for XAMPP MySQL connection
Configure your MySQL database connection here
"""

import os

# XAMPP MySQL Configuration
XAMPP_CONFIG = {
    'host': 'localhost',           # XAMPP MySQL host
    'user': 'root',                # Default XAMPP MySQL user
    'password': '',                # Default XAMPP MySQL password (empty)
    'database': 'power_physique',  # Your database name
    'port': 3306                   # Default MySQL port
}

# SQLAlchemy Database URI for Flask
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{XAMPP_CONFIG['user']}:{XAMPP_CONFIG['password']}"
    f"@{XAMPP_CONFIG['host']}:{XAMPP_CONFIG['port']}/{XAMPP_CONFIG['database']}"
)

# Alternative configuration (if using mysql-connector)
ALTERNATIVE_URI = (
    f"mysql+mysqlconnector://{XAMPP_CONFIG['user']}:{XAMPP_CONFIG['password']}"
    f"@{XAMPP_CONFIG['host']}:{XAMPP_CONFIG['port']}/{XAMPP_CONFIG['database']}"
)

print("Database Configuration loaded from config.py")
print(f"Database: {XAMPP_CONFIG['database']}")
print(f"Host: {XAMPP_CONFIG['host']}:{XAMPP_CONFIG['port']}")
