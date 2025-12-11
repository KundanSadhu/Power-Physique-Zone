-- Power Physique Zone Database Schema
-- Complete database for gym management system

-- 1. Users Table (For login and authentication)
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    phone_number VARCHAR(15),
    address TEXT,
    role VARCHAR(20) DEFAULT 'Member', -- 'Member', 'Admin', 'Co-Founder'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- 2. Membership Plans Table
CREATE TABLE IF NOT EXISTS Membership_Plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name VARCHAR(50) NOT NULL UNIQUE, -- 'Bronze', 'Silver', 'Gold'
    price_usd DECIMAL(10, 2) NOT NULL,
    billing_cycle VARCHAR(20) DEFAULT 'Monthly', -- 'Monthly', 'Annual'
    description TEXT,
    features TEXT, -- JSON format for plan features
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. User Subscriptions Table
CREATE TABLE IF NOT EXISTS User_Subscriptions (
    subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT 1,
    auto_renewal BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES Membership_Plans(plan_id)
);

-- 4. Products Table (Nutrition/Food Diet items)
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'Protein', 'FoodDiet', 'Equipment'
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    pack_size VARCHAR(50),
    image_url VARCHAR(255),
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Gym Locations Table
CREATE TABLE IF NOT EXISTS Gym_Locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city VARCHAR(50) NOT NULL,
    area VARCHAR(100) NOT NULL UNIQUE,
    address TEXT,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. User Questions Table (Q&A section)
CREATE TABLE IF NOT EXISTS User_Questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    user_name VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answer_text TEXT,
    answered_by_user_id INTEGER,
    is_answered BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (answered_by_user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

-- 7. Contact Messages Table
CREATE TABLE IF NOT EXISTS Contact_Messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    subject VARCHAR(255),
    message_text TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0
);

-- 8. Customer Reviews Table
CREATE TABLE IF NOT EXISTS Customer_Reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    rating TINYINT NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    helpful_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
);

-- 9. Workouts Table
CREATE TABLE IF NOT EXISTS Workouts (
    workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'Muscle Building', 'Fat Loss', 'Strength', 'Cardio', etc.
    description TEXT,
    difficulty_level VARCHAR(20), -- 'Beginner', 'Intermediate', 'Advanced'
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Exercises Table
CREATE TABLE IF NOT EXISTS Exercises (
    exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER,
    name VARCHAR(100) NOT NULL,
    sets INTEGER,
    reps INTEGER,
    description TEXT,
    rest_seconds INTEGER,
    FOREIGN KEY (workout_id) REFERENCES Workouts(workout_id) ON DELETE CASCADE
);

-- 11. User Orders Table (for purchasing products)
CREATE TABLE IF NOT EXISTS User_Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_status VARCHAR(20) DEFAULT 'Pending', -- 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'
    delivery_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 12. Order Items Table
CREATE TABLE IF NOT EXISTS Order_Items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES User_Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE RESTRICT
);

-- 13. Competitions Table
CREATE TABLE IF NOT EXISTS Competitions (
    competition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    grand_prize DECIMAL(10, 2),
    runner_up_1_prize DECIMAL(10, 2),
    runner_up_2_prize DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Competition Participants Table
CREATE TABLE IF NOT EXISTS Competition_Participants (
    participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    registration_date DATE NOT NULL,
    score DECIMAL(10, 2),
    rank INTEGER,
    FOREIGN KEY (competition_id) REFERENCES Competitions(competition_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE(competition_id, user_id)
);

-- 15. Gym Equipment Table
CREATE TABLE IF NOT EXISTS Gym_Equipment (
    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    location_id INTEGER,
    purchase_date DATE,
    maintenance_date DATE,
    condition VARCHAR(20) DEFAULT 'Good', -- 'Good', 'Fair', 'Poor'
    FOREIGN KEY (location_id) REFERENCES Gym_Locations(location_id) ON DELETE SET NULL
);

-- 16. Equipment Ratings Table
CREATE TABLE IF NOT EXISTS Equipment_Ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    user_id INTEGER,
    rating TINYINT NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES Gym_Equipment(equipment_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_username ON Users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON Users(email);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON User_Subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_is_active ON User_Subscriptions(is_active);
CREATE INDEX IF NOT EXISTS idx_questions_user_id ON User_Questions(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON Customer_Reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON Customer_Reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON User_Orders(user_id);
CREATE INDEX IF NOT EXISTS idx_competitions_user_id ON Competition_Participants(user_id);
