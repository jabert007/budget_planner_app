-- ==========================================
-- Budget Planner App Schema
-- Database: MySQL
-- ==========================================

-- 1. Users Table
-- Stores user credentials. Login is via Phone.
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (email),
    INDEX (phone)
);

-- 2. Budget Goals Table
-- Stores the monthly income for each user.
-- Use 'email' as the stable identifier from the 'users' table.
CREATE TABLE IF NOT EXISTS budget_goals (
    username VARCHAR(255) PRIMARY KEY, -- This stores user_email
    monthly_income DECIMAL(15, 2) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Budget Expenses Table
-- Stores individual cost items associated with a user.
CREATE TABLE IF NOT EXISTS budget_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL, -- This stores user_email
    category VARCHAR(50) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    expense_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (username),
    INDEX (expense_date)
);
