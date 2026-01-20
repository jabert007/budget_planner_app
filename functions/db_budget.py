import mysql.connector
import streamlit as st
from datetime import date

def get_connection():
    # Helper to get DB connection using existing secrets
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

def init_budget_db():
    """Create budget_goals and budget_expenses tables if not exist."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Budget Goals Table
        # Stores monthly income for a user
        cur.execute("""
            CREATE TABLE IF NOT EXISTS budget_goals (
                username VARCHAR(255) PRIMARY KEY,
                monthly_income DECIMAL(15, 2) NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Budget Expenses Table
        # Stores individual items
        cur.execute("""
            CREATE TABLE IF NOT EXISTS budget_expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL,
                item_name VARCHAR(255) NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                expense_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (username),
                INDEX (expense_date)
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"DB Init Error: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

# --- GOAL OPERATIONS ---

def set_user_goal(username, income):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Upsert: Insert or Update if exists
        cur.execute("""
            INSERT INTO budget_goals (username, monthly_income) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE monthly_income = %s
        """, (username, income, income))
        conn.commit()
        return True
    except Exception as e:
        print(f"Set Goal Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_user_goal(username):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT monthly_income FROM budget_goals WHERE username = %s", (username,))
        res = cur.fetchone()
        return res["monthly_income"] if res else 0
    except Exception as e:
        print(f"Get Goal Error: {e}")
        return 0
    finally:
        cur.close()
        conn.close()

def delete_user_goal(username):
    """Deletes goal AND all expenses (Reset)"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM budget_goals WHERE username = %s", (username,))
        cur.execute("DELETE FROM budget_expenses WHERE username = %s", (username,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Delete Goal Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# --- EXPENSE OPERATIONS ---

def add_expense(username, category, item, amount, date_obj):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO budget_expenses (username, category, item_name, amount, expense_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, category, item, amount, date_obj))
        conn.commit()
        return True
    except Exception as e:
        print(f"Add Expense Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def delete_expense(expense_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM budget_expenses WHERE id = %s", (expense_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Delete Expense Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_monthly_expenses(username, target_month_date):
    """
    Get all expenses for a specific month.
    target_month_date: A date object (we only use month/year)
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # Filter by MONTH() and YEAR()
        cur.execute("""
            SELECT id, category, item_name as item, amount, expense_date as date
            FROM budget_expenses 
            WHERE username = %s 
              AND MONTH(expense_date) = %s 
              AND YEAR(expense_date) = %s
            ORDER BY expense_date DESC, id DESC
        """, (username, target_month_date.month, target_month_date.year))
        return cur.fetchall()
    except Exception as e:
        print(f"Get Expenses Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_all_expenses_for_chart(username):
    """Get ALL expenses for the user to plot separate trends"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT category, item_name as item, amount, expense_date as date
            FROM budget_expenses 
            WHERE username = %s 
            ORDER BY expense_date ASC
        """, (username,))
        return cur.fetchall()
    except Exception as e:
        print(f"Chart Data Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()
