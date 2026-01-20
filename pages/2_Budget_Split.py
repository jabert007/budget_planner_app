import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
# Import DB functions
from functions.db_budget import (
    init_budget_db, get_user_goal, set_user_goal, delete_user_goal,
    add_expense, get_monthly_expenses, delete_expense, get_all_expenses_for_chart
)

# ----------------- LOAD BOOTSTRAP & CUSTOM CSS -----------------
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
body {
    background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    font-family: 'Inter', sans-serif;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.main-card, .create-card {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    margin: 20px auto;
    max-width: 800px;
}
.create-card {
    max-width: 500px;
    text-align: center;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"] {
    height: 45px;
    white-space: nowrap;
    background-color: #fff;
    border-radius: 8px;
    color: #4a5568;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    padding: 0 16px;
    font-weight: 600;
    border: 1px solid #e2e8f0;
}
.stTabs [aria-selected="true"] {
    background-color: #5563DE !important;
    color: white !important;
    border-color: #5563DE !important;
}
.item-row {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 8px;
    font-size: 0.95rem;
}
.item-name { font-weight: 600; color: #334155; }
.item-date { font-size: 0.8rem; color: #64748b; }
.item-amount { font-weight: 700; color: #1e293b; }
.summary-box {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    position: relative;
}
.summary-box h2 {
    font-size: 1.2rem;
    margin: 0;
    font-weight: 600;
    opacity: 0.9;
}
.summary-box .amount {
    font-size: 2rem;
    font-weight: 700;
    margin: 5px 0 0 0;
}
.delete-btn {
    position: absolute;
    top: 15px;
    right: 15px;
}
.stats-container {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}
.stat-item {
    text-align: center;
    width: 48%;
    background: #f1f5f9;
    padding: 10px;
    border-radius: 10px;
}
.stat-label { font-size: 0.8rem; color: #64748b; font-weight: 600; }
.stat-val { font-size: 1.1rem; color: #1e293b; font-weight: 700; }
.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ----------------- LOGIN CHECK -----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please log in first.")
    st.stop()

# Use user_email for DATABASE keys (Unique)
user_id = st.session_state.get("user_email", st.session_state.get("username"))
# Use username for DISPLAY (Friendly)
display_name = st.session_state.get("username", "User")

# --- INITIALIZE DATABASE ---
init_budget_db()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title(f"👤 {display_name}")
    if st.button("Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_email = None
        st.switch_page("app.py")

# ----------------- MAIN LOGIC: CHECK GOAL (DB) -----------------
# Get monthly income from DB
total_income = get_user_goal(user_id)

if total_income == 0:
    # ================= SHOW CREATE GOAL UI =================
    st.markdown("""
    <div class='create-card'>
        <h2>🎯 Create New Goal</h2>
        <p style='color: #666;'>Let's set up your monthly budget plan.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.write("") # Spacer
        income = st.number_input("💰 Enter your monthly income (₹):", min_value=0, step=1000, help="Total income you want to allocate")
        
        st.write("")
        if st.button("Set Goal & Start Planning", type="primary"):
            if income > 0:
                if set_user_goal(user_id, income):
                    st.toast("Goal created! Redirecting...", icon="🚀")
                    st.rerun()
                else:
                    st.error("Error saving goal to database.")
            else:
                st.error("Please enter a valid income amount.")
    
    st.stop() # Stop execution here if no goal exists

# ================= SHOW BUDGET SPLIT UI =================

# ----------------- MONTH SELECTOR -----------------
current_date = date.today()
month_options = []
start_date = current_date.replace(day=1) - timedelta(days=365) # Approx 1 year back

for i in range(24): # 2 years window
    d = (start_date + timedelta(days=i*31)).replace(day=1)
    month_options.append(d)

month_options.sort()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Select Month")
current_month_start = current_date.replace(day=1)
try:
    default_idx = month_options.index(current_month_start)
except ValueError:
    default_idx = 0

selected_month_date = st.sidebar.selectbox(
    "Planning for:", 
    options=month_options, 
    format_func=lambda x: x.strftime("%B %Y"),
    index=default_idx
)

# ----------------- FETCH DATA (DB) -----------------
categories = ["Needs", "Wants", "Culture", "Unexpected", "Others"]
cat_icons = {"Needs": "🏠", "Wants": "🎬", "Culture": "🌍", "Unexpected": "🚑", "Others": "📦"}

# Get expenses for selected month
expenses = get_monthly_expenses(user_id, selected_month_date)
# Calculate totals
current_monthly_allocated = sum(e["amount"] for e in expenses)
monthly_balance = float(total_income) - float(current_monthly_allocated)

# ----------------- HEADER SUMMARY & DELETE -----------------
c_head, c_del = st.columns([5, 1])
with c_head:
    st.markdown(f"""
    <div class="summary-box">
        <h2>Budget for {selected_month_date.strftime("%B %Y")}</h2>
        <div class="amount">₹{total_income:,}</div>
    </div>
    """, unsafe_allow_html=True)
with c_del:
    st.write("") # Spacer
    st.write("")
    if st.button("🗑️ Reset", help="Delete this goal and start over", type="secondary"):
        if delete_user_goal(user_id):
            st.session_state.clear()
            st.session_state.logged_in = True
            # Restore session logic after clear (tricky part of streamlit clear)
            # Actually, better to just clear budget data and rerun
            # But logic here requests full reset.
            st.switch_page("app.py") # Force re-login or just reload
        else:
            st.error("Failed to delete goal.")


# ----------------- TABS INTERFACE (MANAGE) -----------------
tabs = st.tabs([f"{cat_icons[c]} {c}" for c in categories])

for i, category in enumerate(categories):
    with tabs[i]:
        # --- ADD FORM ---
        with st.form(f"add_form_{category}", clear_on_submit=True):
            st.caption(f"Add expense to {selected_month_date.strftime('%B %Y')}")
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                new_item = st.text_input("Item Name", placeholder="e.g. Lunch")
            with c2:
                # Default date = selected month's first day or today
                if selected_month_date.month == date.today().month and selected_month_date.year == date.today().year:
                    def_date = date.today()
                else:
                    def_date = selected_month_date
                
                new_date = st.date_input("Date", value=def_date)
            with c3:
                new_msg = f"Max: ₹{monthly_balance:,}"
                new_amount = st.number_input("Amount", min_value=0, step=100, help=new_msg)
            with c4:
                st.write("") # Align button
                st.write("") 
                submitted = st.form_submit_button("➕ Add", type="primary", use_container_width=True)
            
            if submitted:
                if new_date.month != selected_month_date.month or new_date.year != selected_month_date.year:
                    st.toast(f"⚠️ Note: Item added to {new_date.strftime('%B')}, outside current view.")

                if not new_item:
                    st.toast("⚠️ Item name is required")
                elif new_amount <= 0:
                    st.toast("⚠️ Amount must be greater than 0")
                elif new_amount > monthly_balance and (new_date.month == selected_month_date.month):
                    st.toast("⚠️ Amount exceeds remaining budget!")
                else:
                    # DB Insert
                    if add_expense(user_id, category, new_item, new_amount, new_date):
                        st.rerun()
                    else:
                        st.error("Database Error: Could not add item.")

        # --- LIST VIEW (READ ONLY + DELETE) ---
        st.markdown(f"#### 📝 {category} List ({selected_month_date.strftime('%B')})")
        
        # Filter in-memory from the monthly fetch
        cat_expenses = [e for e in expenses if e["category"] == category]
        
        if not cat_expenses:
            st.info(f"No items for {category}.")
        else:
            to_remove_id = None
            for exp in cat_expenses:
                with st.container():
                    c_info, c_del_btn = st.columns([6, 1])
                    with c_info:
                        st.markdown(f"""
                        <div class="item-row">
                            <span class="item-name">{exp['item']}</span> • 
                            <span class="item-date">{exp['date']}</span>
                            <div style="float: right;" class="item-amount">₹{exp['amount']:,}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_del_btn:
                         if st.button("🗑️", key=f"del_{exp['id']}", help="Delete Item"):
                             to_remove_id = exp["id"]
            
            # Remove logic
            if to_remove_id is not None:
                if delete_expense(to_remove_id):
                    st.rerun()
                else:
                    st.error("Failed to delete item.")

# ----------------- FOOTER STATS -----------------
st.markdown("---")
st.markdown(f"""
<div class="stats-container">
    <div class="stat-item">
        <div class="stat-label">Allocated ({selected_month_date.strftime("%b")})</div>
        <div class="stat-val" style="color: #ef4444;">₹{current_monthly_allocated:,}</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">Remaining ({selected_month_date.strftime("%b")})</div>
        <div class="stat-val" style="color: #10b981;">₹{monthly_balance:,}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ----------------- ANALYSIS CHART SECTION (DB) -----------------
st.markdown("---")
st.markdown("### 📊 Monthly Trends")

all_data = get_all_expenses_for_chart(user_id)

if all_data:
    df = pd.DataFrame(all_data)
    # Ensure Date type
    df['date'] = pd.to_datetime(df['date'])
    df['Month'] = df['date'].dt.strftime('%Y-%m')
    df['Amount'] = df['amount'].astype(float) # Ensure float
    
    # Group
    monthly_data = df.groupby(["Month", "category"])["Amount"].sum().reset_index()
    monthly_data.columns = ["Month", "Category", "Amount"] # Fix case for Altair
    
    chart = {
        "mark": "bar",
        "encoding": {
            "x": {"field": "Month", "type": "ordinal", "axis": {"labelAngle": 0}},
            "y": {"field": "Amount", "type": "quantitative"},
            "color": {"field": "Category", "type": "nominal"},
            "tooltip": ["Month", "Category", "Amount"]
        },
    }
    st.vega_lite_chart(monthly_data, chart, use_container_width=True)
else:
    st.info("Add items to see spending visualization.")
