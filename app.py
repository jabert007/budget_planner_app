import streamlit as st
from functions.dbfunctionlogin import register_user, login_user, init_users_db

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Login / Register", page_icon="🔐", layout="centered")

# Hide Streamlit default UI (hamburger menu, footer, search bar)
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ------------------- SESSION SETUP -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# ------------------- INIT DB -------------------
init_users_db()

# ------------------- CUSTOM PAGE STYLE -------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #74ABE2, #5563DE);
    }
    .stApp {
        background-color: transparent;
    }
    .card {
        background-color: white;
        padding: 2rem 1.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        width: 100%;
        max-width: 380px;
        margin: 2rem auto;
    }
    .title {
        text-align: center;
        font-size: 1.6rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    button[kind="primary"] {
        background: linear-gradient(to right, #667eea, #764ba2);
        color: white !important;
        border: none;
    }
    /* Mobile Friendly Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: white;
        padding: 5px;
        border-radius: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        flex-grow: 1;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------- INIT STATE -------------------
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# ------------------- LOGIN / REGISTER TOGGLE -------------------
# Use columns as custom tabs to allow programmatic switching
c1, c2 = st.columns(2)
with c1:
    if st.button("🔑 Login", use_container_width=True, type="primary" if st.session_state.auth_mode == "login" else "secondary"):
        st.session_state.auth_mode = "login"
        st.rerun()
with c2:
    if st.button("📝 Register", use_container_width=True, type="primary" if st.session_state.auth_mode == "register" else "secondary"):
        st.session_state.auth_mode = "register"
        st.rerun()

st.write("") # Spacer

# ------------------- FORMS -------------------

if st.session_state.auth_mode == "login":
    # --- LOGIN FORM ---
    st.markdown('<div class="title">Welcome Back 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Please sign in to continue</div>', unsafe_allow_html=True)

    # Check for success message from redirect
    if "reg_success" in st.session_state and st.session_state.reg_success:
        st.success("✅ Account created! You can now log in.")
        del st.session_state["reg_success"]

    # Country Code & Phone Split for LOGIN
    c_code, c_num = st.columns([1.5, 3.5])
    with c_code:
        l_country_code = st.selectbox("Code", ["+91", "+1", "+44", "+971", "+61", "+81", "+49", "+33"], index=0, key="l_code")
    with c_num:
        l_phone_num = st.text_input("Mobile No", placeholder="9876543210", key="l_phone")

    password_input = st.text_input("Password", placeholder="Enter your password", type="password", key="login_pass")
    
    st.write("")
    login_btn = st.button("Login", use_container_width=True, type="primary")

    if login_btn:
        if not l_phone_num or not password_input:
            st.error("Please enter mobile number and password.")
        else:
            full_login_phone = f"{l_country_code}{l_phone_num}"
            user = login_user(full_login_phone, password_input)
            if user:
                st.session_state.logged_in = True
                # Store EMAIL as the unique identifier for Database operations
                st.session_state.user_email = user["email"]
                # Store Name for UI Greeting
                st.session_state.username = user["email"].split("@")[0]
                
                st.toast("✅ Login successful!")
                st.switch_page("pages/2_Budget_Split.py")
            else:
                st.error("❌ Invalid mobile number or password.")


elif st.session_state.auth_mode == "register":
    # --- REGISTER FORM ---
    st.markdown('<div class="title">Create Account 🆕</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Join us and get started today</div>', unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=True):
        # Country Code & Phone Split
        c_code, c_num = st.columns([1.5, 3.5])
        with c_code:
            country_code = st.selectbox("Code", ["+91", "+1", "+44", "+971", "+61", "+81", "+49", "+33"], index=0)
        with c_num:
            phone_num = st.text_input("Mobile No", placeholder="9876543210")
        
        new_email = st.text_input("Email", placeholder="Enter your email address")
        new_pass = st.text_input("Password", placeholder="Create a password", type="password")
        
        st.write("")
        register_btn = st.form_submit_button("Register", use_container_width=True, type="primary")

        if register_btn:
            if not phone_num or not new_email or not new_pass:
                st.error("⚠️ All fields are required.")
            else:
                # Combine Code + Number
                full_phone = f"{country_code}{phone_num}"
                
                # Basic length logic check (optional, but good for DB constraints)
                # Allowing 20 chars now to be safe (e.g. spaces)
                if len(full_phone) > 20:
                     st.error(f"⚠️ Phone number is too long ({len(full_phone)} chars). Max 20.")
                else:
                    db_success = register_user(full_phone, new_email, new_pass)
                    if db_success:
                        # Success Logic: Switch mode and Rerun
                        st.session_state.auth_mode = "login"
                        st.session_state.reg_success = True
                        st.rerun()
                    else:
                        st.error("❌ Email or Phone already exists.")
