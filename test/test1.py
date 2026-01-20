import streamlit as st
import mysql.connector
from db_config import get_connection
from utils import hash_password, check_password
import json
from datetime import date
import matplotlib.pyplot as plt

st.set_page_config(page_title="Budget Planner", layout="wide")

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None

# --- DB Connection ---
conn = get_connection()
cur = conn.cursor(dictionary=True)

# --- AUTH ---
def register_user(phone, email, password, pin):
    try:
        cur.execute("INSERT INTO users (phone, email, password_hash, pin) VALUES (%s,%s,%s,%s)",
                    (phone, email, hash_password(password), pin))
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False

def login_user(identifier, password_or_pin):
    cur.execute("SELECT * FROM users WHERE phone=%s OR email=%s", (identifier, identifier))
    user = cur.fetchone()
    if user and (check_password(user["password_hash"], password_or_pin) or user["pin"] == password_or_pin):
        return user
    return None

# --- APP ---
menu = ["Login", "Register"]
if not st.session_state.logged_in:
    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "Register":
        st.subheader("Register")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        pin = st.text_input("PIN", type="password")
        if st.button("Register"):
            if register_user(phone, email, password, pin):
                st.success("Registered successfully! Login now.")
            else:
                st.error("Phone or email already exists!")

    elif choice == "Login":
        st.subheader("Login")
        identifier = st.text_input("Phone or Email")
        password_or_pin = st.text_input("Password or PIN", type="password")
        if st.button("Login"):
            user = login_user(identifier, password_or_pin)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.username = user["email"]
                st.success(f"Logged in as {user['email']}")
            else:
                st.error("Invalid credentials")

else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

    st.header(f"Welcome, {st.session_state.username}")

    # --- Goal Input ---
    st.subheader("Set Goal")
    cur.execute("SELECT * FROM goals WHERE user_id=%s", (st.session_state.user_id,))
    goal = cur.fetchone()
    monthly_saving = st.number_input("Monthly Saving", value=5000)
    yearly_goal = st.number_input("End of Year Goal", value=60000)
    if st.button("Save Goal"):
        if goal:
            cur.execute("UPDATE goals SET monthly_saving=%s, yearly_goal=%s WHERE user_id=%s",
                        (monthly_saving, yearly_goal, st.session_state.user_id))
        else:
            cur.execute("INSERT INTO goals (user_id, monthly_saving, yearly_goal) VALUES (%s,%s,%s)",
                        (st.session_state.user_id, monthly_saving, yearly_goal))
        conn.commit()
        st.success("Goal saved!")

    # --- Budget Allocation ---
    st.subheader("Budget Allocation")
    needs = st.number_input("Needs", value=20000)
    wants = st.number_input("Wants", value=10000)
    culture = st.number_input("Culture", value=10000)
    unexpected = st.number_input("Unexpected", value=10000)
    if st.button("Save Budget Allocation"):
        month = date.today().strftime("%Y-%m")
        cur.execute("INSERT INTO budget_allocation (user_id, month, needs, wants, culture, unexpected) VALUES (%s,%s,%s,%s,%s,%s)                     ON DUPLICATE KEY UPDATE needs=%s,wants=%s,culture=%s,unexpected=%s",
                    (st.session_state.user_id, month, json.dumps(needs), json.dumps(wants), json.dumps(culture), json.dumps(unexpected),
                     json.dumps(needs), json.dumps(wants), json.dumps(culture), json.dumps(unexpected)))
        conn.commit()
        st.success("Budget Allocation Saved")

    # --- Daily Expenses ---
    st.subheader("Add Daily Expense")
    categories = ["needs", "wants", "culture", "unexpected"]
    cat = st.selectbox("Category", categories)
    subcat = st.text_input("Subcategory")
    amount = st.number_input("Amount", min_value=0.0, step=100.0)
    if st.button("Add Expense"):
        cur.execute("INSERT INTO daily_expenses (user_id,date,category,subcategory,amount) VALUES (%s,%s,%s,%s,%s)",
                    (st.session_state.user_id, date.today(), cat, subcat, amount))
        conn.commit()
        st.success("Expense Added")

    # --- Monthly Summary ---
    st.subheader("Monthly Summary")
    cur.execute("SELECT category,SUM(amount) as total FROM daily_expenses WHERE user_id=%s AND MONTH(date)=MONTH(CURDATE()) GROUP BY category",
                (st.session_state.user_id,))
    data = cur.fetchall()
    if data:
        categories = [d["category"] for d in data]
        totals = [float(d["total"]) for d in data]
        fig, ax = plt.subplots()
        ax.bar(categories, totals, color=["#4CAF50","#2196F3","#FFC107","#F44336"])
        st.pyplot(fig)
        total_expense = sum(totals)
        st.info(f"Total Expenses This Month: ₹{total_expense}")
