-- Power Physique Zone - PL/SQL Procedures for XAMPP MySQL
-- Copy and paste this entire file into phpMyAdmin SQL editor

-- ============================================================
-- 1. USER MANAGEMENT PROCEDURES
-- ============================================================

-- Create user registration procedure
DELIMITER //
CREATE PROCEDURE sp_register_user(
    IN p_username VARCHAR(50),
    IN p_email VARCHAR(100),
    IN p_password_hash VARCHAR(255),
    IN p_full_name VARCHAR(100),
    IN p_phone_number VARCHAR(15),
    IN p_address TEXT,
    OUT p_user_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error creating user';
    END;
    
    -- Check if username already exists
    IF EXISTS (SELECT 1 FROM Users WHERE username = p_username) THEN
        SET p_success = FALSE;
        SET p_message = 'Username already exists';
    -- Check if email already exists
    ELSEIF EXISTS (SELECT 1 FROM Users WHERE email = p_email) THEN
        SET p_success = FALSE;
        SET p_message = 'Email already exists';
    ELSE
        INSERT INTO Users (username, email, password_hash, full_name, phone_number, address, role, is_active)
        VALUES (p_username, p_email, p_password_hash, p_full_name, p_phone_number, p_address, 'Member', TRUE);
        
        SET p_user_id = LAST_INSERT_ID();
        SET p_success = TRUE;
        SET p_message = 'User registered successfully';
    END IF;
END //
DELIMITER ;

-- Authenticate user procedure
DELIMITER //
CREATE PROCEDURE sp_authenticate_user(
    IN p_username VARCHAR(50),
    IN p_password_hash VARCHAR(255),
    OUT p_user_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_user_id INT;
    
    SELECT user_id INTO v_user_id 
    FROM Users 
    WHERE username = p_username AND password_hash = p_password_hash AND is_active = TRUE;
    
    IF v_user_id IS NOT NULL THEN
        SET p_user_id = v_user_id;
        SET p_success = TRUE;
        SET p_message = 'Authentication successful';
    ELSE
        SET p_success = FALSE;
        SET p_message = 'Invalid username or password';
    END IF;
END //
DELIMITER ;

-- Get user profile procedure
DELIMITER //
CREATE PROCEDURE sp_get_user_profile(
    IN p_user_id INT
)
BEGIN
    SELECT user_id, username, email, full_name, phone_number, address, role, created_at, is_active
    FROM Users 
    WHERE user_id = p_user_id;
END //
DELIMITER ;

-- Update user profile procedure
DELIMITER //
CREATE PROCEDURE sp_update_user_profile(
    IN p_user_id INT,
    IN p_full_name VARCHAR(100),
    IN p_phone_number VARCHAR(15),
    IN p_address TEXT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error updating profile';
    END;
    
    UPDATE Users 
    SET full_name = p_full_name, phone_number = p_phone_number, address = p_address
    WHERE user_id = p_user_id;
    
    SET p_success = TRUE;
    SET p_message = 'Profile updated successfully';
END //
DELIMITER ;

-- ============================================================
-- 2. QUESTION & ANSWER PROCEDURES
-- ============================================================

-- Submit question procedure
DELIMITER //
CREATE PROCEDURE sp_submit_question(
    IN p_user_id INT,
    IN p_user_name VARCHAR(100),
    IN p_question_text TEXT,
    OUT p_question_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error submitting question';
    END;
    
    INSERT INTO User_Questions (user_id, user_name, question_text, is_answered)
    VALUES (p_user_id, p_user_name, p_question_text, FALSE);
    
    SET p_question_id = LAST_INSERT_ID();
    SET p_success = TRUE;
    SET p_message = 'Question submitted successfully';
END //
DELIMITER ;

-- Answer question procedure
DELIMITER //
CREATE PROCEDURE sp_answer_question(
    IN p_question_id INT,
    IN p_answer_text TEXT,
    IN p_admin_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error answering question';
    END;
    
    UPDATE User_Questions 
    SET answer_text = p_answer_text, is_answered = TRUE, answered_by_user_id = p_admin_id
    WHERE question_id = p_question_id;
    
    SET p_success = TRUE;
    SET p_message = 'Question answered successfully';
END //
DELIMITER ;

-- Get all questions procedure
DELIMITER //
CREATE PROCEDURE sp_get_all_questions()
BEGIN
    SELECT question_id, user_name, question_text, answer_text, is_answered, submitted_at
    FROM User_Questions
    ORDER BY submitted_at DESC;
END //
DELIMITER ;

-- Get unanswered questions procedure
DELIMITER //
CREATE PROCEDURE sp_get_unanswered_questions()
BEGIN
    SELECT question_id, user_name, question_text, submitted_at
    FROM User_Questions
    WHERE is_answered = FALSE
    ORDER BY submitted_at ASC;
END //
DELIMITER ;

-- ============================================================
-- 3. CONTACT & MESSAGE PROCEDURES
-- ============================================================

-- Submit contact message procedure
DELIMITER //
CREATE PROCEDURE sp_submit_contact_message(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_subject VARCHAR(255),
    IN p_message_text TEXT,
    OUT p_message_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error sending message';
    END;
    
    INSERT INTO Contact_Messages (name, email, subject, message_text, is_read)
    VALUES (p_name, p_email, p_subject, p_message_text, FALSE);
    
    SET p_message_id = LAST_INSERT_ID();
    SET p_success = TRUE;
    SET p_message = 'Message sent successfully';
END //
DELIMITER ;

-- Get all contact messages procedure
DELIMITER //
CREATE PROCEDURE sp_get_all_messages()
BEGIN
    SELECT message_id, name, email, subject, message_text, sent_at, is_read
    FROM Contact_Messages
    ORDER BY sent_at DESC;
END //
DELIMITER ;

-- Mark message as read procedure
DELIMITER //
CREATE PROCEDURE sp_mark_message_read(
    IN p_message_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error marking message';
    END;
    
    UPDATE Contact_Messages 
    SET is_read = TRUE
    WHERE message_id = p_message_id;
    
    SET p_success = TRUE;
    SET p_message = 'Message marked as read';
END //
DELIMITER ;

-- ============================================================
-- 4. SUBSCRIPTION PROCEDURES
-- ============================================================

-- Create subscription procedure
DELIMITER //
CREATE PROCEDURE sp_create_subscription(
    IN p_user_id INT,
    IN p_plan_id INT,
    IN p_start_date DATE,
    IN p_duration_months INT,
    OUT p_subscription_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_end_date DATE;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error creating subscription';
    END;
    
    -- Calculate end date
    SET v_end_date = DATE_ADD(p_start_date, INTERVAL p_duration_months MONTH);
    
    INSERT INTO User_Subscriptions (user_id, plan_id, start_date, end_date, is_active, auto_renewal)
    VALUES (p_user_id, p_plan_id, p_start_date, v_end_date, TRUE, TRUE);
    
    SET p_subscription_id = LAST_INSERT_ID();
    SET p_success = TRUE;
    SET p_message = 'Subscription created successfully';
END //
DELIMITER ;

-- Cancel subscription procedure
DELIMITER //
CREATE PROCEDURE sp_cancel_subscription(
    IN p_subscription_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error cancelling subscription';
    END;
    
    UPDATE User_Subscriptions 
    SET is_active = FALSE
    WHERE subscription_id = p_subscription_id;
    
    SET p_success = TRUE;
    SET p_message = 'Subscription cancelled';
END //
DELIMITER ;

-- Get active subscriptions procedure
DELIMITER //
CREATE PROCEDURE sp_get_active_subscriptions(
    IN p_user_id INT
)
BEGIN
    SELECT 
        s.subscription_id, 
        s.user_id, 
        m.plan_name, 
        m.price_usd,
        s.start_date, 
        s.end_date, 
        s.is_active
    FROM User_Subscriptions s
    JOIN Membership_Plans m ON s.plan_id = m.plan_id
    WHERE s.user_id = p_user_id AND s.is_active = TRUE;
END //
DELIMITER ;

-- ============================================================
-- 5. PRODUCT & ORDER PROCEDURES
-- ============================================================

-- Add product procedure
DELIMITER //
CREATE PROCEDURE sp_add_product(
    IN p_name VARCHAR(255),
    IN p_category VARCHAR(50),
    IN p_price DECIMAL(10,2),
    IN p_description TEXT,
    IN p_pack_size VARCHAR(50),
    IN p_stock_quantity INT,
    OUT p_product_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error adding product';
    END;
    
    INSERT INTO Products (name, category, price, description, pack_size, stock_quantity)
    VALUES (p_name, p_category, p_price, p_description, p_pack_size, p_stock_quantity);
    
    SET p_product_id = LAST_INSERT_ID();
    SET p_success = TRUE;
    SET p_message = 'Product added successfully';
END //
DELIMITER ;

-- Get products by category procedure
DELIMITER //
CREATE PROCEDURE sp_get_products_by_category(
    IN p_category VARCHAR(50)
)
BEGIN
    SELECT product_id, name, category, price, description, pack_size, stock_quantity
    FROM Products
    WHERE category = p_category
    ORDER BY created_at DESC;
END //
DELIMITER ;

-- Create order procedure
DELIMITER //
CREATE PROCEDURE sp_create_order(
    IN p_user_id INT,
    IN p_total_amount DECIMAL(10,2),
    IN p_delivery_address TEXT,
    OUT p_order_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error creating order';
    END;
    
    INSERT INTO User_Orders (user_id, order_date, total_amount, order_status, delivery_address)
    VALUES (p_user_id, CURDATE(), p_total_amount, 'Pending', p_delivery_address);
    
    SET p_order_id = LAST_INSERT_ID();
    SET p_success = TRUE;
    SET p_message = 'Order created successfully';
END //
DELIMITER ;

-- Add order item procedure
DELIMITER //
CREATE PROCEDURE sp_add_order_item(
    IN p_order_id INT,
    IN p_product_id INT,
    IN p_quantity INT,
    IN p_unit_price DECIMAL(10,2),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error adding order item';
    END;
    
    INSERT INTO Order_Items (order_id, product_id, quantity, unit_price)
    VALUES (p_order_id, p_product_id, p_quantity, p_unit_price);
    
    SET p_success = TRUE;
    SET p_message = 'Item added to order';
END //
DELIMITER ;

-- Update order status procedure
DELIMITER //
CREATE PROCEDURE sp_update_order_status(
    IN p_order_id INT,
    IN p_order_status VARCHAR(20),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error updating order';
    END;
    
    UPDATE User_Orders 
    SET order_status = p_order_status
    WHERE order_id = p_order_id;
    
    SET p_success = TRUE;
    SET p_message = 'Order status updated';
END //
DELIMITER ;

-- Get user orders procedure
DELIMITER //
CREATE PROCEDURE sp_get_user_orders(
    IN p_user_id INT
)
BEGIN
    SELECT order_id, order_date, total_amount, order_status, delivery_address
    FROM User_Orders
    WHERE user_id = p_user_id
    ORDER BY order_date DESC;
END //
DELIMITER ;

-- ============================================================
-- 6. REVIEW PROCEDURES
-- ============================================================

-- Add product review procedure
DELIMITER //
CREATE PROCEDURE sp_add_product_review(
    IN p_product_id INT,
    IN p_user_id INT,
    IN p_rating TINYINT,
    IN p_review_text TEXT,
    OUT p_review_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error adding review';
    END;
    
    IF p_rating < 1 OR p_rating > 5 THEN
        SET p_success = FALSE;
        SET p_message = 'Rating must be between 1 and 5';
    ELSE
        INSERT INTO Customer_Reviews (product_id, user_id, rating, review_text)
        VALUES (p_product_id, p_user_id, p_rating, p_review_text);
        
        SET p_review_id = LAST_INSERT_ID();
        SET p_success = TRUE;
        SET p_message = 'Review added successfully';
    END IF;
END //
DELIMITER ;

-- Get product reviews procedure
DELIMITER //
CREATE PROCEDURE sp_get_product_reviews(
    IN p_product_id INT
)
BEGIN
    SELECT review_id, user_id, rating, review_text, reviewed_at, helpful_count
    FROM Customer_Reviews
    WHERE product_id = p_product_id
    ORDER BY reviewed_at DESC;
END //
DELIMITER ;

-- ============================================================
-- 7. WORKOUT PROCEDURES
-- ============================================================

-- Add workout procedure
DELIMITER //
CREATE PROCEDURE sp_add_workout(
    IN p_name VARCHAR(100),
    IN p_category VARCHAR(50),
    IN p_description TEXT,
    IN p_difficulty_level VARCHAR(20),
    IN p_duration_minutes INT,
    OUT p_workout_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error adding workout';
    END;
    
    INSERT INTO Workouts (name, category, description, difficulty_level, duration_minutes)
    VALUES (p_name, p_category, p_description, p_difficulty_level, p_duration_minutes);
    
    SET p_workout_id = LAST_INSERT_ID();
    SET p_success = TRUE;
    SET p_message = 'Workout added successfully';
END //
DELIMITER ;

-- Get workouts by category procedure
DELIMITER //
CREATE PROCEDURE sp_get_workouts_by_category(
    IN p_category VARCHAR(50)
)
BEGIN
    SELECT workout_id, name, category, description, difficulty_level, duration_minutes, created_at
    FROM Workouts
    WHERE category = p_category
    ORDER BY difficulty_level ASC;
END //
DELIMITER ;

-- Get workout exercises procedure
DELIMITER //
CREATE PROCEDURE sp_get_workout_exercises(
    IN p_workout_id INT
)
BEGIN
    SELECT exercise_id, workout_id, name, sets, reps, description, rest_seconds
    FROM Exercises
    WHERE workout_id = p_workout_id
    ORDER BY exercise_id ASC;
END //
DELIMITER ;

-- ============================================================
-- 8. COMPETITION PROCEDURES
-- ============================================================

-- Create competition procedure
DELIMITER //
CREATE PROCEDURE sp_create_competition(
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_grand_prize DECIMAL(10,2),
    OUT p_competition_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error creating competition';
    END;
    
    INSERT INTO Competitions (name, description, start_date, end_date, grand_prize)
    VALUES (p_name, p_description, p_start_date, p_end_date, p_grand_prize);
    
    SET p_competition_id = LAST_INSERT_ID();
    SET p_success = TRUE;
    SET p_message = 'Competition created successfully';
END //
DELIMITER ;

-- Register for competition procedure
DELIMITER //
CREATE PROCEDURE sp_register_competition(
    IN p_competition_id INT,
    IN p_user_id INT,
    OUT p_participant_id INT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_success = FALSE;
        SET p_message = 'Error registering for competition';
    END;
    
    IF EXISTS (SELECT 1 FROM Competition_Participants 
               WHERE competition_id = p_competition_id AND user_id = p_user_id) THEN
        SET p_success = FALSE;
        SET p_message = 'Already registered for this competition';
    ELSE
        INSERT INTO Competition_Participants (competition_id, user_id, registration_date)
        VALUES (p_competition_id, p_user_id, CURDATE());
        
        SET p_participant_id = LAST_INSERT_ID();
        SET p_success = TRUE;
        SET p_message = 'Registered successfully';
    END IF;
END //
DELIMITER ;

-- Get competition leaderboard procedure
DELIMITER //
CREATE PROCEDURE sp_get_competition_leaderboard(
    IN p_competition_id INT
)
BEGIN
    SELECT 
        cp.participant_id,
        cp.rank,
        u.username,
        u.full_name,
        cp.score,
        cp.registration_date
    FROM Competition_Participants cp
    JOIN Users u ON cp.user_id = u.user_id
    WHERE cp.competition_id = p_competition_id
    ORDER BY cp.rank ASC;
END //
DELIMITER ;

-- ============================================================
-- 9. ADMIN DASHBOARD PROCEDURES
-- ============================================================

-- Get dashboard statistics procedure
DELIMITER //
CREATE PROCEDURE sp_get_dashboard_stats()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM Users) as total_users,
        (SELECT COUNT(*) FROM User_Questions) as total_questions,
        (SELECT COUNT(*) FROM User_Questions WHERE is_answered = FALSE) as unanswered_questions,
        (SELECT COUNT(*) FROM Contact_Messages WHERE is_read = FALSE) as unread_messages,
        (SELECT COUNT(*) FROM Products) as total_products,
        (SELECT COUNT(*) FROM User_Orders WHERE order_status = 'Pending') as pending_orders,
        (SELECT COUNT(*) FROM User_Subscriptions WHERE is_active = TRUE) as active_subscriptions;
END //
DELIMITER ;

-- Get recent activity procedure
DELIMITER //
CREATE PROCEDURE sp_get_recent_activity(
    IN p_limit INT
)
BEGIN
    SELECT 'Question' as activity_type, user_name as name, submitted_at as activity_date, question_text as details
    FROM User_Questions
    ORDER BY submitted_at DESC
    LIMIT p_limit;
END //
DELIMITER ;

-- Get sales report procedure
DELIMITER //
CREATE PROCEDURE sp_get_sales_report(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        DATE(order_date) as order_date,
        COUNT(*) as total_orders,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value
    FROM User_Orders
    WHERE order_date BETWEEN p_start_date AND p_end_date
    GROUP BY DATE(order_date)
    ORDER BY order_date DESC;
END //
DELIMITER ;

-- ============================================================
-- 10. UTILITY PROCEDURES
-- ============================================================

-- Get all locations procedure
DELIMITER //
CREATE PROCEDURE sp_get_all_locations()
BEGIN
    SELECT location_id, city, area, address, phone, created_at
    FROM Gym_Locations
    ORDER BY city ASC, area ASC;
END //
DELIMITER ;

-- Get location details procedure
DELIMITER //
CREATE PROCEDURE sp_get_location_details(
    IN p_location_id INT
)
BEGIN
    SELECT 
        gl.location_id,
        gl.city,
        gl.area,
        gl.address,
        gl.phone,
        COUNT(DISTINCT ge.equipment_id) as equipment_count
    FROM Gym_Locations gl
    LEFT JOIN Gym_Equipment ge ON gl.location_id = ge.location_id
    WHERE gl.location_id = p_location_id
    GROUP BY gl.location_id;
END //
DELIMITER ;

-- Search products procedure
DELIMITER //
CREATE PROCEDURE sp_search_products(
    IN p_search_term VARCHAR(255)
)
BEGIN
    SELECT product_id, name, category, price, description, pack_size, stock_quantity
    FROM Products
    WHERE name LIKE CONCAT('%', p_search_term, '%')
       OR description LIKE CONCAT('%', p_search_term, '%')
    ORDER BY created_at DESC;
END //
DELIMITER ;

-- ============================================================
-- 11. TRIGGERS FOR AUDIT & AUTO-UPDATE
-- ============================================================

-- Trigger: Update subscription status on end date
DELIMITER //
CREATE TRIGGER tr_update_expired_subscriptions
AFTER UPDATE ON User_Subscriptions
FOR EACH ROW
BEGIN
    IF NEW.end_date < CURDATE() AND NEW.is_active = TRUE THEN
        UPDATE User_Subscriptions
        SET is_active = FALSE
        WHERE subscription_id = NEW.subscription_id;
    END IF;
END //
DELIMITER ;

-- Trigger: Update product stock after order
DELIMITER //
CREATE TRIGGER tr_update_product_stock
AFTER INSERT ON Order_Items
FOR EACH ROW
BEGIN
    UPDATE Products
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END //
DELIMITER ;

-- ============================================================
-- USAGE EXAMPLES - Copy and run these to test procedures
-- ============================================================

/*

-- 1. Register a new user
CALL sp_register_user(
    'john_doe',
    'john@example.com',
    'hashed_password_123',
    'John Doe',
    '1234567890',
    '123 Fitness St',
    @user_id,
    @success,
    @message
);
SELECT @user_id, @success, @message;

-- 2. Authenticate user
CALL sp_authenticate_user(
    'john_doe',
    'hashed_password_123',
    @auth_user_id,
    @auth_success,
    @auth_message
);
SELECT @auth_user_id, @auth_success, @auth_message;

-- 3. Submit a question
CALL sp_submit_question(
    1,
    'John Doe',
    'How should I start a fitness routine?',
    @q_id,
    @q_success,
    @q_message
);
SELECT @q_id, @q_success, @q_message;

-- 4. Get all questions
CALL sp_get_all_questions();

-- 5. Answer a question
CALL sp_answer_question(
    1,
    'Start with basic exercises and gradually increase intensity',
    1,
    @ans_success,
    @ans_message
);

-- 6. Submit contact message
CALL sp_submit_contact_message(
    'Jane Smith',
    'jane@example.com',
    'Inquiry',
    'I want to know about your services',
    @msg_id,
    @msg_success,
    @msg_message
);

-- 7. Get dashboard stats
CALL sp_get_dashboard_stats();

-- 8. Create order
CALL sp_create_order(
    1,
    299.99,
    '123 Main St',
    @order_id,
    @order_success,
    @order_message
);

-- 9. Get user orders
CALL sp_get_user_orders(1);

-- 10. Search products
CALL sp_search_products('protein');

*/

-- ============================================================
-- END OF PL/SQL PROCEDURES
-- Ready to paste in XAMPP phpMyAdmin SQL Editor
-- ============================================================
