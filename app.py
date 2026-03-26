import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import random
import os

# --- TIMEZONE HELPER (IST) ---
def get_ist_time():
    # Streamlit server UTC use karta hai, India ke liye 5:30 ghante add karne honge
    return datetime.now() + timedelta(hours=5, minutes=30)

# --- GOOGLE SHEETS CONNECTION (SAFE) ---
def get_gspread_client():
    try:
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

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Page Config
if not st.session_state.get("logged_in", False):
    st.set_page_config(page_title="SPAY INDIA", layout="centered")
else:
    st.set_page_config(page_title="SPAY INDIA", layout="wide")

# ================= GLOBAL STYLES (Hide UI & Fix Buttons) =================
st.markdown("""
<style>
    /* Hide Streamlit Header, Footer and Deploy Button */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    
    /* Global Background */
    .stApp { background-color: #f5f7fb; }

    /* Button Styling & Hover Fix */
    div.stButton > button {
        background: linear-gradient(90deg, #ff007a, #a020f0) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 60px !important;
        font-weight: bold !important;
        border: none !important;
        transition: none !important;
    }
    
    div.stButton > button:hover {
        opacity: 1 !important; /* Dimming effect hata diya */
        background: linear-gradient(90deg, #ff007a, #a020f0) !important;
        color: white !important;
        border: none !important;
    }

    .title { font-size: 42px; font-weight: bold; color: #1a237e; text-align: center; }
    .subtitle { text-align: center; color: black; margin-bottom: 40px; }
    .input-label { font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN PAGE =================
if not st.session_state.get("logged_in", False) or st.session_state.user_logged != st.session_state.mobile:

    st.markdown('<div style="padding-top: 2rem;"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1.2,1])

    with col1:
        img_url = "https://github.com/Amit-Jha97/spay-skill-test/blob/main/interview_boy.png?raw=true"
        st.image(img_url, width=320)

    with col2:
        st.markdown('<div class="title">SPAY INDIA</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Candidate Portal</div>', unsafe_allow_html=True)

        st.markdown('<div class="input-label">Mobile Number</div>', unsafe_allow_html=True)
        mobile = st.text_input("", placeholder="Write your mobile number", label_visibility="collapsed")

        st.markdown('<div class="input-label">Enter OTP</div>', unsafe_allow_html=True)
        otp_input = st.text_input("", placeholder="Enter OTP", label_visibility="collapsed", type="password")

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
                    if (get_ist_time() - st.session_state.otp_time).total_seconds() > 600:
                        msg.error("⏰ OTP Expired")
                    else:
                        st.session_state.last_activity = get_ist_time()
                        st.session_state.logged_in = True
                        st.session_state.user_logged = st.session_state.mobile
                        st.rerun()
                else:
                    msg.error("❌ Wrong OTP")
    st.stop()

# ================= TEST PAGE =================

# Auto Logout Check (5 Minutes)
if st.session_state.logged_in:
    now = get_ist_time()
    diff = (now - st.session_state.last_activity).total_seconds()
    if diff > 300:
        logout()
        st.rerun()
    else:
        st.session_state.last_activity = now

st.markdown("""
<style>
.header-container {
    width: 100%; margin-top: 10px; height: 110px;
    background: linear-gradient(to right, #1a237e, #4caf50, #fbc02d);
    display: flex; justify-content: center; align-items: center;
    color: white; border-radius: 10px; flex-direction: column;
}
.header-title { font-size: 42px; font-weight: bold; }
.header-subtitle { font-size: 15px; font-weight: bold; }
</style>

<div class="header-container">
    <div class="header-title">SPAY INDIA</div>
    <div class="header-subtitle">SKILL ASSESSMENT TEST</div>
</div>
""", unsafe_allow_html=True)

# QUESTIONS
questions = [
    {"q":"She ___ to the office every day.","options":["go","goes","going","gone"],"cor":"goes","cat":"English"},
    {"q":"Opposite of success?","options":["failure","win","achieve","progress"],"cor":"failure","cat":"English"},
    {"q":"Synonym of fast?","options":["slow","quick","delay","lazy"],"cor":"quick","cat":"English"},
    {"q":"He speaks English ___ than his brother.","options":["good","better","best","well"],"cor":"better","cat":"English"},
    {"q":"25% of 200 = ?","options":["40","45","50","55"],"cor":"50","cat":"Math"},
    {"q":"15% of 200 = ?","options":["20","25","30","35"],"cor":"30","cat":"Math"},
    {"q":"30% of 600 = ?","options":["160","180","200","220"],"cor":"180","cat":"Math"},
    {"q":"20% of 500 = ?","options":["80","90","100","110"],"cor":"100","cat":"Math"},
]

if "questions_set" not in st.session_state or st.session_state.get("questions_user") != st.session_state.mobile:
    st.session_state.questions_set = random.sample(questions, len(questions))
    st.session_state.answers = [""] * len(st.session_state.questions_set)
    st.session_state.current_q = 0
    st.session_state.questions_user = st.session_state.mobile

# FORM
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="input-label">Candidate Name</div>', unsafe_allow_html=True)
    name = st.text_input("", placeholder="Enter your name", label_visibility="collapsed")
    mobile_field = st.text_input("**Mobile No**", value=st.session_state.mobile)
with col2:
    st.markdown('<div class="input-label">HR Name</div>', unsafe_allow_html=True)
    hr = st.text_input("", placeholder="Enter HR name", label_visibility="collapsed")
    st.markdown('<div class="input-label">Interview Team</div>', unsafe_allow_html=True)
    team = st.text_input("", placeholder="Enter team name", label_visibility="collapsed")

st.divider()

# DISPLAY
q_index = st.session_state.current_q
q = st.session_state.questions_set[q_index]

st.markdown(f"### QUESTION {q_index+1} / {len(st.session_state.questions_set)}")
st.markdown(f"<div style='color:#0d47a1; font-weight:bold; font-size:22px;'>{q['q']}</div>", unsafe_allow_html=True)

ans = st.radio("", q["options"], key=f"q_{q_index}")
st.session_state.answers[q_index] = ans

col_n1, col_n2 = st.columns(2)
with col_n1:
    if st.button("NEXT →", use_container_width=True):
        st.session_state.last_activity = get_ist_time()
        if q_index < len(st.session_state.questions_set)-1:
            st.session_state.current_q += 1
            st.rerun()

with col_n2:
    if st.button("SUBMIT TEST", use_container_width=True):
        st.session_state.last_activity = get_ist_time()
        correct = sum(1 for i,q in enumerate(st.session_state.questions_set) if st.session_state.answers[i]==q["cor"])
        
        client = get_gspread_client()
        if client:
            try:
                sheet = client.open("Assessment_Results").sheet1
                sheet.append_row([
                    get_ist_time().strftime("%Y-%m-%d %I:%M %p"),
                    name, mobile_field, hr, team,
                    f"{correct}/{len(st.session_state.questions_set)}"
                ])
                st.success("✅ Test Submitted Successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Error saving results: {e}")
