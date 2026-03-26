import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import random

# --- TIMEZONE IST ---
def get_ist_time():
    return datetime.now() + timedelta(hours=5, minutes=30)

# --- GOOGLE SHEETS CONNECTION ---
def get_gspread_client():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Google Connection Error: {e}")
        return None

# ---------------- QUESTIONS POOL ----------------
math_pool = [
    {"q":"25% of 200 = ?","options":["40","50","60","70"],"cor":"50","cat":"Math"},
    {"q":"Square root of 144?","options":["10","12","14","16"],"cor":"12","cat":"Math"},
] * 13 

english_pool = [
    {"q":"She ___ to the office every day.","options":["go","goes","going","gone"],"cor":"goes","cat":"English"},
    {"q":"Opposite of success?","options":["failure","win","achieve","progress"],"cor":"failure","cat":"English"},
] * 13

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "last_activity" not in st.session_state:
    st.session_state.last_activity = get_ist_time()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ================= GLOBAL STYLES =================
st.markdown("""
<style>
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    .stApp { background-color: #f5f7fb; }
    
    /* Default Button (Previous ke liye Gradient) */
    div.stButton > button {
        background: linear-gradient(90deg, #ff007a, #a020f0) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 55px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100% !important;
    }

    /* Next aur Submit Button ko Dark Blue karne ke liye */
    /* Hum 'div' ke nth-child ka use karenge ya text search */
    /* Streamlit mein button identify karne ka best tarika niche wala CSS hai */
    
    div.stButton > button:active, div.stButton > button:focus {
        border: none !important;
        box-shadow: none !important;
    }

    /* Specific Blue Color for NEXT and SUBMIT */
    /* Note: Ye CSS tab kaam karega jab NEXT/SUBMIT buttons col2 mein honge */
    .stColumn:nth-child(2) div.stButton > button {
        background-color: #1a237e !important;
        background-image: none !important; /* Gradient hatane ke liye */
    }

    div.stButton > button:hover {
        opacity: 0.9 !important;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .input-label { font-weight: bold; margin-top: 10px; color: #1a237e; }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN PAGE =================
if not st.session_state.logged_in:
    st.set_page_config(page_title="SPAY INDIA", layout="centered")
    col1, col2 = st.columns([1.2,1])
    with col1:
        st.image("https://github.com/Amit-Jha97/spay-skill-test/blob/main/interview_boy.png?raw=true", width=320)
    with col2:
        st.markdown("<h1 style='color:#1a237e; text-align:center;'>SPAY INDIA</h1>", unsafe_allow_html=True)
        mobile = st.text_input("Mobile Number", placeholder="10 Digit Number")
        otp_input = st.text_input("Enter OTP", type="password", placeholder="Enter OTP")
        
        if not st.session_state.otp_sent:
            if st.button("SEND OTP", key="send_otp"):
                if len(mobile) == 10 and mobile.isdigit():
                    st.session_state.otp = str(random.randint(100000, 999999))
                    st.session_state.mobile = mobile
                    st.session_state.otp_sent = True
                    st.success(f"✅ OTP Sent (Test: {st.session_state.otp})")
                    st.rerun()
        else:
            if st.button("VERIFY OTP", key="verify_otp"):
                if otp_input == st.session_state.otp:
                    st.session_state.logged_in = True
                    st.rerun()
    st.stop()

# ================= TEST PAGE =================
st.set_page_config(page_title="SPAY INDIA", layout="wide")

if "questions_set" not in st.session_state:
    sel_math = random.sample(math_pool, 10)
    sel_eng = random.sample(english_pool, 10)
    st.session_state.questions_set = sel_math + sel_eng
    random.shuffle(st.session_state.questions_set)
    st.session_state.answers = [""] * 20
    st.session_state.current_q = 0

if (get_ist_time() - st.session_state.last_activity).total_seconds() > 300:
    logout()

st.markdown("""
<div style="background:linear-gradient(to right, #1a237e, #4caf50, #fbc02d); padding:20px; border-radius:10px; color:white; text-align:center;">
    <h1 style="margin:0;">SPAY INDIA</h1>
    <p style="margin:0; font-weight:bold;">SKILL ASSESSMENT TEST</p>
</div>
""", unsafe_allow_html=True)

# Form Details
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.markdown('<div class="input-label">Candidate Name</div>', unsafe_allow_html=True)
    c_name = st.text_input("", placeholder="Enter Name", label_visibility="collapsed")
with col_f2:
    st.markdown('<div class="input-label">HR Name</div>', unsafe_allow_html=True)
    h_name = st.text_input("", placeholder="Enter HR Name", label_visibility="collapsed")
with col_f3:
    st.markdown('<div class="input-label">Interview Team</div>', unsafe_allow_html=True)
    t_name = st.text_input("", placeholder="Enter Team Name", label_visibility="collapsed")

st.divider()

# Question Display
q_idx = st.session_state.current_q
q_data = st.session_state.questions_set[q_idx]

st.markdown(f"### Question {q_idx + 1} / 20")
st.markdown(f"<div style='color:#0d47a1; font-weight:bold; font-size:22px;'>{q_data['q']}</div>", unsafe_allow_html=True)

ans = st.radio("Choose Option:", q_data["options"], key=f"ans_{q_idx}")
st.session_state.answers[q_idx] = ans

st.markdown("<br>", unsafe_allow_html=True)

# Navigation Buttons
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if q_idx > 0:
        if st.button("← PREVIOUS"):
            st.session_state.current_q -= 1
            st.rerun()

with col_btn2:
    if q_idx < 19:
        if st.button("NEXT →"):
            st.session_state.last_activity = get_ist_time()
            st.session_state.current_q += 1
            st.rerun()
    else:
        if st.button("SUBMIT TEST"):
            score = sum(1 for i, q in enumerate(st.session_state.questions_set) if st.session_state.answers[i] == q["cor"])
            client = get_gspread_client()
            if client:
                try:
                    sheet = client.open("Assessment_Results").sheet1
                    sheet.append_row([
                        get_ist_time().strftime("%Y-%m-%d %I:%M %p"),
                        c_name, st.session_state.mobile, h_name, t_name, f"{score}/20"
                    ])
                    st.success(f"✅ Submitted! Score: {score}/20")
                    st.balloons()
                    st.session_state.logged_in = False
                except Exception as e:
                    st.error(f"Error: {e}")
