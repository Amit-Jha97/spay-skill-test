import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import random
import os
import pytz

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
    st.session_state.logged_in = False
    st.session_state.otp_sent = False
    st.session_state.user_logged = None
    st.rerun()

# Page Config
if not st.session_state.get("logged_in", False):
    st.set_page_config(page_title="SPAY INDIA", layout="centered")
else:
    st.set_page_config(page_title="SPAY INDIA", layout="wide")

# ---------------- GLOBAL CSS (Solid Blue Buttons & IST Header) ----------------
st.markdown("""
<style>
    header {visibility: hidden;}
    .stApp { background-color: #f5f7fb; }
    
    /* बटन स्टाइल - Solid Blue (No light color on hover) */
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
    div.stButton > button:hover, div.stButton > button:active {
        background-color: #1a237e !important;
        opacity: 1 !important;
        border: none !important;
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
    .input-label { font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN PAGE (Original Layout) =================
if not st.session_state.get("logged_in", False):
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        img_filename = "interview_boy.png" 
        if os.path.exists(img_filename):
            st.image(img_filename, width=320)

    with col2:
        st.markdown('<div style="font-size: 42px; font-weight: bold; color: #1a237e; text-align: center;">SPAY INDIA</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: black; margin-bottom: 40px;">Candidate Portal</div>', unsafe_allow_html=True)

        st.markdown('<div class="input-label">Mobile Number</div>', unsafe_allow_html=True)
        mobile_input = st.text_input("", placeholder="Write your mobile number", label_visibility="collapsed")

        st.markdown('<div class="input-label">Enter OTP</div>', unsafe_allow_html=True)
        otp_field = st.text_input("", placeholder="Enter OTP", label_visibility="collapsed", type="password")

        btn_label = "VERIFY OTP" if st.session_state.otp_sent else "SEND OTP"
        clicked = st.button(btn_label, use_container_width=True)

        msg = st.empty()

        if clicked:
            if not st.session_state.otp_sent:
                if mobile_input and len(mobile_input) == 10:
                    # Generate OTP
                    generated_otp = str(random.randint(100000, 999999))
                    st.session_state.otp = generated_otp
                    st.session_state.mobile = mobile_input
                    st.session_state.otp_sent = True
                    st.session_state.otp_time = get_ist_time()
                    
                    # Log OTP to Google Sheet
                    try:
                        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
                        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
                        client = gspread.authorize(creds)
                        sheet = client.open("Assessment_Results").get_worksheet(1)
                        sheet.append_row([get_ist_time().strftime("%Y-%m-%d %H:%M"), mobile_input, generated_otp])
                        msg.success(f"✅ OTP Sent Successfully! (Check Sheet)")
                        st.rerun()
                    except Exception as e:
                        msg.error(f"Sheet Error: {e}")
                else:
                    msg.error("❌ Invalid Mobile Number")
            else:
                if otp_field == st.session_state.otp:
                    st.session_state.logged_in = True
                    st.session_state.user_logged = st.session_state.mobile
                    st.rerun()
                else:
                    msg.error("❌ Wrong OTP")
    st.stop()

# ================= TEST PAGE (10 Math + 10 English) =================

# 1. Refresh Warning
st.markdown('<div class="warning-box">⚠️ Warning: Do not refresh this page. Your progress will be lost!</div>', unsafe_allow_html=True)

# 2. Questions Database
all_questions = [
    # MATH (Add your 50+ questions here)
    {"q":"25% of 200?","options":["40","50","60"],"cor":"50","cat":"Math"},
    {"q":"30% of 600?","options":["160","180","200"],"cor":"180","cat":"Math"},
    # ENGLISH (Add your 50+ questions here)
    {"q":"She ___ to office.","options":["go","goes","going"],"cor":"goes","cat":"English"},
    {"q":"Opposite of Success?","options":["Failure","Win","Progress"],"cor":"Failure","cat":"English"},
]

# 3. 10+10 Selection Logic
if "questions_set" not in st.session_state:
    maths = [q for q in all_questions if q["cat"] == "Math"]
    engs = [q for q in all_questions if q["cat"] == "English"]
    
    st.session_state.questions_set = random.sample(maths, min(10, len(maths))) + random.sample(engs, min(10, len(engs)))
    st.session_state.answers = [""] * len(st.session_state.questions_set)
    st.session_state.current_q = 0

# UI Header
st.markdown('<div class="header-container"><div class="header-title">SPAY INDIA</div><div class="header-subtitle">SKILL ASSESSMENT TEST</div></div>', unsafe_allow_html=True)

# Form
c1, c2 = st.columns(2)
with c1:
    name = st.text_input("Candidate Name")
    st.text_input("Mobile No", value=st.session_state.mobile, disabled=True)
with c2:
    hr = st.text_input("HR Name")
    team = st.text_input("Interview Team")

st.divider()

# Question Logic
curr = st.session_state.current_q
q = st.session_state.questions_set[curr]

st.markdown(f"### Question {curr+1} / {len(st.session_state.questions_set)} ({q['cat']})")
st.markdown(f"<div style='color:#1a237e; font-weight:bold; font-size:22px;'>{q['q']}</div>", unsafe_allow_html=True)

ans = st.radio("Choose:", q["options"], key=f"q_{curr}")
st.session_state.answers[curr] = ans

# Nav
col_n, col_s = st.columns(2)
with col_n:
    if curr < len(st.session_state.questions_set) - 1:
        if st.button("NEXT →", use_container_width=True):
            st.session_state.current_q += 1
            st.rerun()
with col_s:
    if st.button("SUBMIT TEST", use_container_width=True):
        score = sum(1 for i,ques in enumerate(st.session_state.questions_set) if st.session_state.answers[i]==ques["cor"])
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"])
            client = gspread.authorize(creds)
            sheet = client.open("Assessment_Results").sheet1
            sheet.append_row([get_ist_time().strftime("%Y-%m-%d %H:%M"), name, st.session_state.mobile, hr, team, f"{score}/20"])
            st.success("✅ Test Submitted!")
            st.balloons()
        except:
            st.error("Error saving results.")
