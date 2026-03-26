import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import random
import os

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
    st.session_state.last_activity = datetime.now()

# Logout Function
def logout():
    st.session_state.logged_in = False
    st.session_state.otp_sent = False
    st.session_state.questions_set = None
    st.session_state.questions_user = None
    st.session_state.answers = []
    st.session_state.current_q = 0
    st.session_state.user_logged = None

# Page Config
if not st.session_state.get("logged_in", False):
    st.set_page_config(page_title="SPAY INDIA", layout="centered")
else:
    st.set_page_config(page_title="SPAY INDIA", layout="wide")

# ---------------- GLOBAL CSS (FOR BOTH PAGES) ----------------
st.markdown("""
<style>
    header {visibility: hidden;}
    .stApp { background-color: #f5f7fb; }
    
    /* बटन की बेस स्टाइल (Solid Blue) */
    div.stButton > button {
        background-color: #1a237e !important;   /* गहरा नीला */
        color: white !important;                /* सफेद टेक्स्ट */
        font-weight: bold !important;
        border-radius: 8px !important;
        height: 50px !important;
        border: none !important;
        opacity: 1 !important;                  /* धुंधला होने से रोकेगा */
        transition: none !important;            /* एनीमेशन बंद */
    }

    /* माउस ले जाने (Hover) और क्लिक करने पर बदलाव नहीं होगा */
    div.stButton > button:hover, 
    div.stButton > button:active, 
    div.stButton > button:focus {
        background-color: #1a237e !important;
        color: white !important;
        opacity: 1 !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    .header-container {
        width: 100%; margin-top: 10px; height: 110px;
        background: linear-gradient(to right, #1a237e, #4caf50, #fbc02d);
        display: flex; justify-content: center; align-items: center;
        color: white; border-radius: 10px; flex-direction: column;
    }
    .header-title { font-size: 42px; font-weight: bold; }
    .header-subtitle { font-size: 15px; font-weight: bold; }
    .input-label { font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN PAGE =================
if not st.session_state.get("logged_in", False) or st.session_state.user_logged != st.session_state.mobile:
    
    col1, col2 = st.columns([1.2,1])

    with col1:
        # GitHub पर इमेज लोड करने के लिए सिर्फ फाइल का नाम दें
        img_filename = "interview_boy.png" 
        if os.path.exists(img_filename):
            st.image(img_filename, width=320)
        else:
            st.info("Logo Placeholder (Upload image to GitHub)")

    with col2:
        st.markdown('<div style="font-size: 42px; font-weight: bold; color: #1a237e; text-align: center;">SPAY INDIA</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: black; margin-bottom: 40px;">Candidate Portal</div>', unsafe_allow_html=True)

        st.markdown('<div class="input-label">Mobile Number</div>', unsafe_allow_html=True)
        mobile = st.text_input("", placeholder="Write your mobile number", label_visibility="collapsed", key="login_mobile")

        st.markdown('<div class="input-label">Enter OTP</div>', unsafe_allow_html=True)
        otp_input = st.text_input("", placeholder="Enter OTP", label_visibility="collapsed", key="login_otp")

        btn_text = "VERIFY OTP" if st.session_state.otp_sent else "SEND OTP"
        clicked = st.button(btn_text, use_container_width=True)

        msg = st.empty()

        if clicked:
            if not st.session_state.otp_sent:
                if mobile and len(mobile)==10 and mobile.isdigit():
                    otp = str(random.randint(100000,999999))
                    st.session_state.otp = otp
                    st.session_state.mobile = mobile
                    st.session_state.otp_sent = True
                    st.session_state.otp_time = datetime.now()
                    
                    # Google Sheets Connect
                    try:
                        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
                        # GitHub/Streamlit Cloud के लिए Secrets इस्तेमाल करें
                        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
                        client = gspread.authorize(creds)
                        sheet = client.open("Assessment_Results").get_worksheet(1)
                        sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), mobile, otp])
                        msg.success(f"✅ OTP Sent (For testing: {otp})")
                        st.rerun()
                    except Exception as e:
                        msg.error(f"Sheet Error: {e}")
                else:
                    msg.error("❌ Invalid Mobile Number")
            else:
                if otp_input == st.session_state.otp:
                    if (datetime.now() - st.session_state.otp_time).total_seconds() > 600:
                        msg.error("⏰ OTP Expired")
                    else:
                        st.session_state.last_activity = datetime.now()
                        st.session_state.logged_in = True
                        st.session_state.user_logged = st.session_state.mobile
                        st.rerun()
                else:
                    msg.error("❌ Wrong OTP")
    st.stop()

# ================= TEST PAGE (AFTER LOGIN) =================

# Auto Logout Check
now = datetime.now()
if (now - st.session_state.last_activity).total_seconds() > 300:
    logout()
    st.rerun()
else:
    st.session_state.last_activity = now

st.markdown("""
<div class="header-container">
    <div class="header-title">SPAY INDIA</div>
    <div class="header-subtitle">SKILL ASSESSMENT TEST</div>
</div>
""", unsafe_allow_html=True)

# Questions Logic
questions = [
    {"q":"She ___ to the office every day.","options":["go","goes","going","gone"],"cor":"goes","cat":"English"},
    {"q":"Opposite of success?","options":["failure","win","achieve","progress"],"cor":"failure","cat":"English"},
    {"q":"25% of 200 = ?","options":["40","45","50","55"],"cor":"50","cat":"Math"},
    {"q":"20% of 500 = ?","options":["80","90","100","110"],"cor":"100","cat":"Math"},
]

if "questions_set" not in st.session_state or st.session_state.get("questions_user") != st.session_state.mobile:
    st.session_state.questions_set = random.sample(questions, min(10, len(questions)))
    st.session_state.answers = [""] * len(st.session_state.questions_set)
    st.session_state.current_q = 0
    st.session_state.questions_user = st.session_state.mobile

# User Form
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Candidate Name", placeholder="Enter your name")
    mobile_field = st.text_input("Mobile No", value=st.session_state.mobile, disabled=True)
with col2:
    hr = st.text_input("HR Name", placeholder="Enter HR name")
    team = st.text_input("Interview Team", placeholder="Enter team name")

st.divider()

# Question Display
q_index = st.session_state.current_q
q = st.session_state.questions_set[q_index]

st.markdown(f"### QUESTION {q_index+1} / {len(st.session_state.questions_set)}")
st.markdown(f"<div style='color:#0d47a1; font-weight:bold; font-size:22px;'>{q['q']}</div>", unsafe_allow_html=True)

ans = st.radio("Choose Option:", q["options"], key=f"q_{q_index}")
st.session_state.answers[q_index] = ans

col_next, col_submit = st.columns(2)

with col_next:
    if q_index < len(st.session_state.questions_set)-1:
        if st.button("NEXT →", use_container_width=True):
            st.session_state.current_q += 1
            st.session_state.last_activity = datetime.now()
            st.rerun()

with col_submit:
    if st.button("SUBMIT TEST", use_container_width=True):
        correct = sum(1 for i,ques in enumerate(st.session_state.questions_set) if st.session_state.answers[i]==ques["cor"])
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"])
            client = gspread.authorize(creds)
            sheet = client.open("Assessment_Results").sheet1
            sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), name, mobile_field, hr, team, f"{correct}/{len(st.session_state.questions_set)}"])
            st.success("✅ Test Submitted Successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
