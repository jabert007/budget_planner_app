import streamlit as st
from functions.dbfunctionlogin import register_user, login_user, init_users_db
from languages import TRANSLATIONS # Import Translations

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Penny Wise", page_icon="images/logo.png", layout="centered")

# Hide Streamlit default UI
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ------------------- SESSION SETUP -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "language" not in st.session_state:
    st.session_state.language = "English"

# ------------------- INIT DB -------------------
init_users_db()

# ------------------- CUSTOM PAGE STYLE -------------------
# ------------------- CUSTOM PAGE STYLE -------------------
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #74ABE2, #5563DE);
    }
    .stApp {
        background-color: transparent;
    }
    .login-card {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin-top: 20px;
    }
    .title {
        text-align: left; /* Changed to Left */
        font-size: 1.6rem;
        font-weight: 700;
        color: #333 !important; /* Force Dark Color */
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: left;
        color: #666 !important;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    /* Force Input Text Colors for Dark Mode Compatibility inside the White Card */
    input {
        color: #333 !important;
    }
    button[kind="primary"] {
        background: linear-gradient(to right, #667eea, #764ba2);
        color: white !important;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------- LANGUAGE SELECTOR -------------------
lang_cols = st.columns([8, 2])
with lang_cols[1]:
    sel_lang = st.selectbox("", ["English", "Tamil", "Malayalam"], key="lang_select", label_visibility="collapsed")
    st.session_state.language = sel_lang

# Helper to get text
def txt(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

st.write("")

# ------------------- LOGIN / REGISTER TOGGLE -------------------
c1, c2 = st.columns(2)
with c1:
    if st.button(f"🔑 {txt('login')}", use_container_width=True, type="primary" if st.session_state.auth_mode == "login" else "secondary"):
        st.session_state.auth_mode = "login"
        st.rerun()
with c2:
    if st.button(f"📝 {txt('register')}", use_container_width=True, type="primary" if st.session_state.auth_mode == "register" else "secondary"):
        st.session_state.auth_mode = "register"
        st.rerun()

# ------------------- MAIN CARD CONTAINER -------------------
st.markdown('<div class="login-card">', unsafe_allow_html=True)

if st.session_state.auth_mode == "login":
    # --- HEADER: Title Left, Logo Right ---
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown(f'<div class="title">{txt("welcome")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="subtitle">{txt("signin_msg")}</div>', unsafe_allow_html=True)
    with h2:
        st.image("images/logo.png", width=70)

    if "reg_success" in st.session_state and st.session_state.reg_success:
        st.success(txt("reg_success"))
        del st.session_state["reg_success"]

    # --- LOGIN FORM ---
    # Country Code & Phone Split for LOGIN
    c_code, c_num = st.columns([1.5, 3.5])
    with c_code:
        l_country_code = st.selectbox(txt("code"), ["+91", "+1", "+44", "+971", "+61", "+81", "+49", "+33"], index=0, key="l_code")
    with c_num:
        l_phone_num = st.text_input(txt("mobile"), placeholder="9876543210", key="l_phone")

    password_input = st.text_input(txt("password"), type="password", key="login_pass")
    
    st.write("")
    login_btn = st.button(txt("login"), use_container_width=True, type="primary")

    if login_btn:
        if not l_phone_num or not password_input:
            st.error(txt("req_fields"))
        else:
            # Sanitize
            clean_num = l_phone_num.strip()
            if clean_num.startswith(l_country_code):
                clean_num = clean_num[len(l_country_code):]
                
            full_login_phone = f"{l_country_code}{clean_num}"
            user = login_user(full_login_phone, password_input)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = user["email"]
                st.session_state.username = user["email"].split("@")[0]
                
                st.toast(txt("login_success"))
                st.switch_page("pages/2_Budget_Split.py")
            else:
                st.error(txt("invalid_login"))


elif st.session_state.auth_mode == "register":
    # --- HEADER: Title Left, Logo Right ---
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown(f'<div class="title">{txt("create_account")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="subtitle">{txt("join_msg")}</div>', unsafe_allow_html=True)
    with h2:
        st.image("images/logo.png", width=70)

    with st.form("register_form", clear_on_submit=True):
        c_code, c_num = st.columns([1.5, 3.5])
        with c_code:
            country_code = st.selectbox(txt("code"), ["+91", "+1", "+44", "+971", "+61", "+81", "+49", "+33"], index=0)
        with c_num:
            phone_num = st.text_input(txt("mobile"), placeholder="9876543210")
        
        new_email = st.text_input(txt("email"))
        new_pass = st.text_input(txt("password"), type="password")
        
        st.write("")
        register_btn = st.form_submit_button(txt("register"), use_container_width=True, type="primary")

        if register_btn:
            if not phone_num or not new_email or not new_pass:
                st.error(txt("req_fields"))
            else:
                clean_num = phone_num.strip()
                if clean_num.startswith(country_code):
                    clean_num = clean_num[len(country_code):]

                full_phone = f"{country_code}{clean_num}"
                if len(full_phone) > 20:
                     st.error(txt("phone_long"))
                else:
                    db_success = register_user(full_phone, new_email, new_pass)
                    if db_success:
                        st.session_state.auth_mode = "login"
                        st.session_state.reg_success = True
                        st.rerun()
                    else:
                        st.error(txt("exists_error"))

st.markdown('</div>', unsafe_allow_html=True) # Close Login Card
