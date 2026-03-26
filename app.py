import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import random
import os
import pytz # requirements.txt में pytz जरूर लिखें

# --- TIMEZONE SETUP ---
def get_ist_time():
    return datetime.now(pytz.timezone('Asia/Kolkata'))

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "otp" not in st.session_state:
    st.session_state.otp = ""
if "mobile" not in st.session_state:
    st.session_state.mobile = ""
if "otp_time" not in st.session_state:
    st.session_state.otp_time = None
if "user_logged" not in st.session_state:
    st.session_state.user_logged = None
if "last_activity" not in st.session_state:
    st.session_state.last_activity = get_ist_time()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Page Config
if not st.session_state.get("logged_in", False):
    st.set_page_config(page_title="SPAY INDIA", layout="centered")
else:
    st.set_page_config(page_title="SPAY INDIA", layout="wide")

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
    header {visibility: hidden;}
    .stApp { background-color: #f5f7fb; }
    
    /* बटन स्टाइल (Solid Blue) */
    div.stButton > button {
        background-color: #1a237e !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        height: 50px !important;
        border: none !important;
        opacity: 1 !important;
        transition: none !important;
    }
    div.stButton > button:hover {
        background-color: #1a237e !important;
        opacity: 1 !important;
    }
    .header-container {
        width: 100%; margin-top: 10px; height: 110px;
        background: linear-gradient(to right, #1a237e, #4caf50, #fbc02d);
        display: flex; justify-content: center; align-items: center;
        color: white; border-radius: 10px; flex-direction: column;
    }
    .warning-box {
        padding: 10px; background-color: #fff3cd; color: #856404;
        border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN PAGE =================
if not st.session_state.logged_in:
    col1, col2 = st.columns([1.2,1])
    with col1:
        img_filename = "interview_boy.png" 
        if os.path.exists(img_filename):
            st.image(img_filename, width=320)
    with col2:
        st.markdown('<h1 style="color: #1a237e; text-align: center;">SPAY INDIA</h1>', unsafe_allow_html=True)
        mobile = st.text_input("Mobile Number", placeholder="10 Digit Number")
        otp_input = st.text_input("Enter OTP", type="password")
        
        btn_text = "VERIFY OTP" if st.session_state.otp_sent else "SEND OTP"
        if st.button(btn_text, use_container_width=True):
            if not st.session_state.otp_sent:
                if len(mobile) == 10:
                    st.session_state.otp = str(random.randint(100000, 999999))
                    st.session_state.mobile = mobile
                    st.session_state.otp_sent = True
                    st.session_state.otp_time = get_ist_time()
                    st.success(f"OTP Sent! (Check Sheet or Logs)")
                    # Google Sheet Log for OTP (Optional)
                    st.rerun()
            else:
                if otp_input == st.session_state.otp:
                    st.session_state.logged_in = True
                    st.session_state.user_logged = st.session_state.mobile
                    st.rerun()
    st.stop()

# ================= TEST PAGE =================

# 1. Refresh Warning
st.markdown('<div class="warning-box">⚠️ Warning: Do not refresh this page. Your progress will be lost!</div>', unsafe_allow_html=True)

# 2. Questions Database (यहाँ आप 50 या ज्यादा सवाल जोड़ सकते हैं)
all_questions = [
    # MATH (Category: Math)
    {"q":"25% of 200?","options":["40","50","60"],"cor":"50","cat":"Math"},
    {"q":"15% of 300?","options":["45","50","55"],"cor":"45","cat":"Math"},
    {"q":"10 * 10?","options":["100","200","10"],"cor":"100","cat":"Math"},
    # ... यहाँ और Math के सवाल जोड़ें
    
    # ENGLISH (Category: English)
    {"q":"She ___ happy.","options":["is","are","am"],"cor":"is","cat":"English"},
    {"q":"Opposite of Hot?","options":["Cold","Warm","Sun"],"cor":"Cold","cat":"English"},
    {"q":"Synonym of Big?","options":["Small","Large","Tiny"],"cor":"Large","cat":"English"},
    # ... यहाँ और English के सवाल जोड़ें
]

# 3. 10 Math + 10 English Logic
if "questions_set" not in st.session_state:
    math_qs = [q for q in all_questions if q["cat"] == "Math"]
    eng_qs = [q for q in all_questions if q["cat"] == "English"]
    
    # रैंडम सिलेक्शन (10 Math, फिर 10 English)
    selected_math = random.sample(math_qs, min(10, len(math_qs)))
    selected_eng = random.sample(eng_qs, min(10, len(eng_qs)))
    
    st.session_state.questions_set = selected_math + selected_eng
    st.session_state.answers = [""] * len(st.session_state.questions_set)
    st.session_state.current_q = 0

# UI Header
st.markdown('<div class="header-container"><div class="header-title">SPAY INDIA</div></div>', unsafe_allow_html=True)

# Candidate Details
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
with col2:
    hr_name = st.text_input("HR Name")

st.divider()

# Display Question
curr = st.session_state.current_q
q_data = st.session_state.questions_set[curr]

st.subheader(f"Question {curr + 1} of {len(st.session_state.questions_set)} ({q_data['cat']})")
st.write(f"### {q_data['q']}")

ans = st.radio("Select Answer:", q_data["options"], key=f"ans_{curr}")
st.session_state.answers[curr] = ans

# Navigation
c1, c2 = st.columns(2)
with c1:
    if curr < len(st.session_state.questions_set) - 1:
        if st.button("NEXT →", use_container_width=True):
            st.session_state.current_q += 1
            st.rerun()

with c2:
    if st.button("SUBMIT TEST", use_container_width=True):
        # Result Calculation
        score = sum(1 for i, q in enumerate(st.session_state.questions_set) if st.session_state.answers[i] == q["cor"])
        
        # Google Sheet Entry
        try:
            scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
            client = gspread.authorize(creds)
            sheet = client.open("Assessment_Results").sheet1
            
            sheet.append_row([
                get_ist_time().strftime("%Y-%m-%d %H:%M:%S"),
                name, st.session_state.mobile, hr_name, 
                f"{score}/{len(st.session_state.questions_set)}"
            ])
            st.success("✅ Submitted!")
            st.balloons()
            st.stop()
        except Exception as e:
            st.error(f"Sheet Error: {e}")
