import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import random
import os

# --- TIMEZONE IST (India Time) ---
def get_ist_time():
    return datetime.now() + timedelta(hours=5, minutes=30)

# --- GOOGLE SHEETS CONNECTION (SAFE) ---
def get_gspread_client():
    try:
        # Streamlit Secrets se data uthayega (Safe Method)
        creds_dict = st.secrets["gcp_service_account"]
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Google Connection Error: {e}")
        return None

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

# Logout function
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Page Config
if not st.session_state.get("logged_in", False):
    st.set_page_config(page_title="SPAY INDIA", layout="centered")
else:
    st.set_page_config(page_title="SPAY INDIA", layout="wide")

# ================= LOGIN STYLES =================
st.markdown("""
<style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none !important;}
    .stApp { background-color: #f5f7fb; }

    .title { font-size: 42px; font-weight: bold; color: #1a237e; text-align: center; }
    .subtitle { text-align: center; color: black; margin-bottom: 40px; }
    .input-label { font-weight: bold; margin-top: 10px; }

    /* Login Buttons Gradient */
    div.stButton > button {
        background: linear-gradient(90deg, #ff007a, #a020f0) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 60px !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    /* Dark Blue Color for NEXT and SUBMIT on Test Page */
    /* Hum CSS selector se second column ke buttons ko blue karenge */
    .stColumn:nth-child(2) div.stButton > button {
        background: #1a237e !important;
    }

    div.stButton > button:hover {
        opacity: 0.9 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if not st.session_state.get("logged_in", False) or st.session_state.user_logged != st.session_state.mobile:

    st.markdown('<div style="padding-top: 5rem;"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1.2,1])

    with col1:
        # Online GitHub Image Link
        img_url = "https://github.com/Amit-Jha97/spay-skill-test/blob/main/interview_boy.png?raw=true"
        st.image(img_url, width=320)

    with col2:
        st.markdown('<div class="title">SPAY INDIA</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Candidate Portal</div>', unsafe_allow_html=True)

        st.markdown('<div class="input-label">Mobile Number</div>', unsafe_allow_html=True)
        mobile = st.text_input("", placeholder="Mobile number", label_visibility="collapsed")

        st.markdown('<div class="input-label">Enter OTP</div>', unsafe_allow_html=True)
        otp_input = st.text_input("", placeholder="OTP", label_visibility="collapsed", type="password")

        if not st.session_state.otp_sent:
            clicked = st.button("SEND OTP", use_container_width=True)
        else:
            clicked = st.button("VERIFY OTP", use_container_width=True)

        msg = st.empty()

        if clicked:
            if not st.session_state.otp_sent:
                if mobile and len(mobile)==10 and mobile.isdigit():
                    otp = str(random.randint(100000,999999))
                    st.session_state.otp = otp
                    st.session_state.mobile = mobile
                    st.session_state.otp_sent = True
                    st.session_state.otp_time = get_ist_time()

                    client = get_gspread_client()
                    if client:
                        try:
                            sheet = client.open("Assessment_Results").get_worksheet(1)
                            sheet.append_row([get_ist_time().strftime("%Y-%m-%d %I:%M %p"), mobile, otp])
                            msg.success("✅ OTP Sent Successfully")
                            st.rerun()
                        except Exception as e:
                            msg.error(f"Sheet Error: {e}")
                else:
                    msg.error("❌ Invalid Mobile Number")
            else:
                if otp_input == st.session_state.otp:
                    st.session_state.logged_in = True
                    st.session_state.user_logged = st.session_state.mobile
                    st.rerun()
    st.stop()

# ================= TEST =================
# Auto Logout Check
if st.session_state.logged_in:
    now = get_ist_time()
    diff = (now - st.session_state.last_activity).total_seconds()
    if diff > 300: # 5 mins
        logout()
    else:
        st.session_state.last_activity = now

# Header
st.markdown("""
<div style="background:linear-gradient(to right, #1a237e, #4caf50, #fbc02d); padding:20px; border-radius:10px; color:white; text-align:center;">
    <h1 style="margin:0; font-size:42px;">SPAY INDIA</h1>
    <p style="margin:0; font-weight:bold;">SKILL ASSESSMENT TEST</p>
</div>
""", unsafe_allow_html=True)

# QUESTIONS POOL (50 total - add yours here)
questions = [
    {"q":"She ___ to the office every day.","options":["go","goes","going","gone"],"cor":"goes","cat":"English"},
    {"q":"Opposite of success?","options":["failure","win","achieve","progress"],"cor":"failure","cat":"English"},
    {"q":"25% of 200 = ?","options":["40","45","50","55"],"cor":"50","cat":"Math"},
    {"q":"15% of 200 = ?","options":["20","25","30","35"],"cor":"30","cat":"Math"},
] # Yahan apni puri list 25+25 ki bhar dena

# Random 20 Questions (10 Math + 10 English)
if "questions_set" not in st.session_state:
    eng = [q for q in questions if q["cat"]=="English"]
    math = [q for q in questions if q["cat"]=="Math"]
    
    st.session_state.questions_set = random.sample(eng, min(10, len(eng))) + random.sample(math, min(10, len(math)))
    random.shuffle(st.session_state.questions_set)
    st.session_state.answers = [""] * len(st.session_state.questions_set)
    st.session_state.current_q = 0

st.warning("⚠️ Warning: Refreshing the page will end your test and logout.")

# Form
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="input-label">Candidate Name</div>', unsafe_allow_html=True)
    name = st.text_input("", placeholder="Name", label_visibility="collapsed")
with col2:
    st.markdown('<div class="input-label">HR Name</div>', unsafe_allow_html=True)
    hr = st.text_input("", placeholder="HR Name", label_visibility="collapsed")
with col3:
    st.markdown('<div class="input-label">Interview Team</div>', unsafe_allow_html=True)
    team = st.text_input("", placeholder="Team", label_visibility="collapsed")

st.divider()

# Question Display
q_index = st.session_state.current_q
q = st.session_state.questions_set[q_index]

st.markdown(f"### QUESTION {q_index+1} / {len(st.session_state.questions_set)}")
st.markdown(f"<div style='color:#0d47a1; font-weight:bold; font-size:22px;'>{q['q']}</div>", unsafe_allow_html=True)

ans = st.radio("Select Answer:", q["options"], key=f"q_{q_index}")
st.session_state.answers[q_index] = ans

st.markdown("<br>", unsafe_allow_html=True)
b1, b2 = st.columns(2)

with b1:
    if q_index > 0:
        if st.button("← PREVIOUS", use_container_width=True):
            st.session_state.current_q -= 1
            st.rerun()

with b2:
    if q_index < len(st.session_state.questions_set) - 1:
        if st.button("NEXT →", use_container_width=True):
            st.session_state.last_activity = get_ist_time()
            st.session_state.current_q += 1
            st.rerun()
    else:
        if st.button("SUBMIT TEST", use_container_width=True):
            correct = sum(1 for i,q in enumerate(st.session_state.questions_set) if st.session_state.answers[i]==q["cor"])
            client = get_gspread_client()
            if client:
                try:
                    sheet = client.open("Assessment_Results").sheet1
                    sheet.append_row([
                        get_ist_time().strftime("%Y-%m-%d %I:%M %p"),
                        name, st.session_state.mobile, hr, team, f"{correct}/20"
                    ])
                    st.success("✅ Test Submitted Successfully")
                    st.balloons()
                    st.session_state.logged_in = False
                except Exception as e:
                    st.error(f"Error: {e}")
