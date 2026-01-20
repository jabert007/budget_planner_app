import mysql.connector
import streamlit as st
# Assuming utils is in the root directory and app.py is run from root
from utils import hash_password, check_password


def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )


def init_users_db():
    """Create users table if not exists."""
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                phone VARCHAR(20) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (email),
                INDEX (phone)
            )
        """)
        
        # SELF-HEALING: Attempt to expand column if it exists but is too small (e.g. 15)
        try:
             cur.execute("ALTER TABLE users MODIFY COLUMN phone VARCHAR(20)")
             conn.commit()
        except:
             pass 

        # SELF-HEALING: Remove PIN column if it exists (Cleanup)
        try:
             cur.execute("ALTER TABLE users DROP COLUMN pin")
             conn.commit()
        except:
             pass 

        conn.commit()
    except Exception as e:
        print(f"DB Init Error: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()


# --- AUTH ---
# REMOVED PIN Argument
def register_user(phone, email, password):
    conn = None
    cur = None
    try:
        # --- DB Connection ---
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        # DEBUG: Print what we are trying to insert
        print(f"DEBUG: Attempting to register {email} / {phone}")

        # REMOVED PIN from INSERT
        cur.execute(
            "INSERT INTO users (phone, email, password_hash) VALUES (%s, %s, %s)",
            (phone, email, hash_password(password)),
        )
        conn.commit()
        
        # Verify if row count > 0
        if cur.rowcount > 0:
            print("DEBUG: Registration Successful, row committed.")
            return True
        else:
            print("DEBUG: Registration executed but no row added?")
            return False

    except mysql.connector.IntegrityError as e:
        print(f"DEBUG: Integrity Error (Duplicate?): {e}")
        return False

    except Exception as e:
        import traceback
        print(f"DEBUG: Error during registration: {e}")
        traceback.print_exc() # Print full stack trace for debugging
        return False

    finally:
        # --- Prevent connection leaks ---
        if cur:
            cur.close()
        if conn:
            conn.close()

# Updated LOGIN to use PHONE only
def login_user(phone, password):
    conn = None
    cur = None
    # --- DB Connection ---
    try :
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        # Check by PHONE Only
        cur.execute("SELECT * FROM users WHERE phone=%s", (phone,))
        user = cur.fetchone()
        
        if user:
            # Check Password Hash
            if check_password(user["password_hash"], password):
                return user
                
        return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

    finally:
        # --- Prevent connection leaks ---
        if cur:
            cur.close()
        if conn:
            conn.close()