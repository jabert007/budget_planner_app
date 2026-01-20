import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from functions.db_budget import (
    init_budget_db, get_user_goal, set_user_goal, delete_user_goal,
    add_expense, get_monthly_expenses, delete_expense, get_all_expenses_for_chart
)
from languages import TRANSLATIONS

# ----------------- PAGE CONFIG -----------------
# Initial Sidebar State can be collapsed
st.set_page_config(page_title="Penny Wise - Budget", page_icon="images/logo.png", layout="wide", initial_sidebar_state="collapsed")

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

/* HIDE SIDEBAR COMPLETELY */
[data-testid="stSidebar"] {display: none;}
[data-testid="stSidebarNav"] {display: none;}

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

# Helper
if "language" not in st.session_state:
    st.session_state.language = "English"

def txt(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

# Keys
user_id = st.session_state.get("user_email", st.session_state.get("username"))
display_name = st.session_state.get("username", "User")

# --- INITIALIZE DATABASE ---
init_budget_db()

# ================== MAIN NAVIGATION HEADER ==================
# No more sidebar. Everything is at the top.
# Layout: [Logo + Title] [Spacer] [Month Select] [Lang] [Logout]

head_cols = st.columns([1, 4, 2, 2, 1])

with head_cols[0]:
    st.image("images/logo.png", width=60)
with head_cols[1]:
    st.markdown(f"### {display_name}")

# Prepare Month Options
current_date = date.today()
month_options = []
start_date = current_date.replace(day=1) - timedelta(days=365)
for i in range(24):
    d = (start_date + timedelta(days=i*31)).replace(day=1)
    month_options.append(d)
month_options.sort()
try:
    default_idx = month_options.index(current_date.replace(day=1))
except:
    default_idx = 0

with head_cols[2]:
    # Month Selector in Header
    selected_month_date = st.selectbox(
        "", 
        options=month_options, 
        format_func=lambda x: x.strftime("%B %Y"),
        index=default_idx,
        label_visibility="collapsed",
        key="month_select_top"
    )

with head_cols[3]:
    # Language switch in Header
    sel_lang = st.selectbox("", ["English", "Tamil", "Malayalam"], key="lang_select_top", label_visibility="collapsed", index=["English", "Tamil", "Malayalam"].index(st.session_state.language))
    if sel_lang != st.session_state.language:
        st.session_state.language = sel_lang
        st.rerun()

with head_cols[4]:
    st.write("") # Spacer
    if st.button("🚪", help=txt("logout"), type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_email = None
        st.switch_page("app.py")

st.markdown("---")

# ----------------- MAIN LOGIC: CHECK GOAL (DB) -----------------
total_income = get_user_goal(user_id)

if total_income == 0:
    st.markdown(f"""
    <div class='create-card'>
        <h2>{txt('set_goal_title')}</h2>
        <p style='color: #666;'>{txt('set_goal_msg')}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.write("") 
        income = st.number_input(txt("enter_income"), min_value=0, step=1000)
        
        st.write("")
        if st.button(txt("set_goal_btn"), type="primary"):
            if income > 0:
                if set_user_goal(user_id, income):
                    st.toast("Redirecting...", icon="🚀")
                    st.rerun()
                else:
                    st.error("Error saving goal.")
    st.stop()

# ================= SHOW BUDGET SPLIT UI =================

# ----------------- FETCH DATA (DB) -----------------
categories = ["Needs", "Wants", "Culture", "Unexpected", "Others"]
cat_icons = {"Needs": "🏠", "Wants": "🎬", "Culture": "🌍", "Unexpected": "🚑", "Others": "📦"}
# Translate Category Labels for Display
cat_labels = {k: txt("categories")[k] for k in categories}

expenses = get_monthly_expenses(user_id, selected_month_date)
current_monthly_allocated = sum(e["amount"] for e in expenses)
monthly_balance = float(total_income) - float(current_monthly_allocated)

# ----------------- HEADER SUMMARY -----------------
c_head, c_del = st.columns([5, 1])
with c_head:
    st.markdown(f"""
    <div class="summary-box">
        <h2>{txt('budget_for')} {selected_month_date.strftime("%B %Y")}</h2>
        <div class="amount">₹{total_income:,}</div>
    </div>
    """, unsafe_allow_html=True)
with c_del:
    st.write("") 
    st.write("")
    if st.button(txt("reset"), help=txt("reset_help"), type="secondary"):
        if delete_user_goal(user_id):
            st.session_state.clear()
            st.session_state.logged_in = True
            st.switch_page("app.py")
        else:
            st.error("Failed to delete.")

# ----------------- TABS INTERFACE -----------------
# Use Translated Labels in Tabs
tabs = st.tabs([f"{cat_icons[c]} {cat_labels[c]}" for c in categories])

for i, category in enumerate(categories):
    with tabs[i]:
        with st.form(f"add_form_{category}", clear_on_submit=True):
            st.caption(f"{txt('add_item')} {selected_month_date.strftime('%B %Y')}")
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                new_item = st.text_input(txt("item_name"))
            with c2:
                if selected_month_date.month == date.today().month and selected_month_date.year == date.today().year:
                    def_date = date.today()
                else:
                    def_date = selected_month_date
                new_date = st.date_input(txt("date"), value=def_date)
            with c3:
                new_amount = st.number_input(txt("amount"), min_value=0, step=100)
            with c4:
                st.write("") 
                st.write("") 
                submitted = st.form_submit_button(txt("add_btn"), type="primary", use_container_width=True)
            
            if submitted:
                if not new_item:
                    st.toast("⚠️ Name required")
                elif new_amount <= 0:
                    st.toast("⚠️ Amount > 0")
                else:
                    if add_expense(user_id, category, new_item, new_amount, new_date):
                        st.rerun()
                    else:
                        st.error("DB Error")

        # --- LIST VIEW ---
        cat_expenses = [e for e in expenses if e["category"] == category]
        
        if not cat_expenses:
            st.info(f"---")
        else:
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
                         if st.button("🗑️", key=f"del_{exp['id']}"):
                             if delete_expense(exp["id"]):
                                 st.rerun()

# ----------------- FOOTER STATS -----------------
st.markdown("---")
st.markdown(f"""
<div class="stats-container">
    <div class="stat-item">
        <div class="stat-label">{txt('allocated')} ({selected_month_date.strftime("%b")})</div>
        <div class="stat-val" style="color: #ef4444;">₹{current_monthly_allocated:,}</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">{txt('remaining')} ({selected_month_date.strftime("%b")})</div>
        <div class="stat-val" style="color: #10b981;">₹{monthly_balance:,}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- CHART -----------------
st.markdown("---")
st.markdown(f"### {txt('monthly_trends')}")

all_data = get_all_expenses_for_chart(user_id)
if all_data:
    df = pd.DataFrame(all_data)
    df['date'] = pd.to_datetime(df['date'])
    df['Month'] = df['date'].dt.strftime('%Y-%m')
    df['Amount'] = df['amount'].astype(float)
    
    monthly_data = df.groupby(["Month", "category"])["Amount"].sum().reset_index()
    monthly_data.columns = ["Month", "Category", "Amount"]
    
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
