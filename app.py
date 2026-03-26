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
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Google Connection Error: {e}")
        return None

# ---------------- 50 QUESTIONS POOL (25 MATH + 25 ENGLISH) ----------------
# NOTE: In lists mein aap apne baki ke sawal add kar sakte hain
math_pool = [
    {"q":"25% of 200 = ?","options":["40","50","60","70"],"cor":"50","cat":"Math"},
    {"q":"15% of 200 = ?","options":["20","25","30","35"],"cor":"30","cat":"Math"},
    {"q":"30% of 600 = ?","options":["160","180","200","220"],"cor":"180","cat":"Math"},
    {"q":"20% of 500 = ?","options":["80","90","100","110"],"cor":"100","cat":"Math"},
    {"q":"Square root of 144?","options":["10","12","14","16"],"cor":"12","cat":"Math"},
] * 5  # Ye sirf demo ke liye 25 sawal banane ke liye hai

english_pool = [
    {"q":"She ___ to the office every day.","options":["go","goes","going","gone"],"cor":"goes","cat":"English"},
    {"q":"Opposite of success?","options":["failure","win","achieve","progress"],"cor":"failure","cat":"English"},
    {"q":"Synonym of fast?","options":["slow","quick","delay","lazy"],"cor":"quick","cat":"English"},
    {"q":"He speaks English ___ than his brother.","options":["good","better","best","well"],"cor":"better","cat":"English"},
    {"q":"I ___ my homework yesterday.","options":["do","did","done","doing"],"cor":"did","cat":"English"},
] * 5 # Ye sirf demo ke liye 25 sawal banane ke liye hai

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "mobile" not in st.session_state:
    st.session_state.mobile = ""
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
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    .stApp { background-color: #f5f7fb; }
    div.stButton > button {
        background: linear-gradient(90deg, #ff007a, #a020f0) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 60px !important;
        font-weight: bold !important;
        border: none !important;
    }
    div.stButton > button:hover {
        opacity: 1 !important;
        background: linear-gradient(90deg, #ff007a, #a020f0) !important;
    }
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
            if st.button("SEND OTP", use_container_width=True):
                if len(mobile) == 10 and mobile.isdigit():
                    st.session_state.otp = str(random.randint(100000, 999999))
                    st.session_state.mobile = mobile
                    st.session_state.otp_sent = True
                    st.session_state.otp_time = get_ist_time()
                    st.success(f"✅ OTP Sent (Demo: {st.session_state.otp})")
                    st.rerun()
                else:
                    st.error("❌ Invalid Mobile")
        else:
            if st.button("VERIFY OTP", use_container_width=True):
                if otp_input == st.session_state.otp:
                    st.session_state.logged_in = True
                    st.session_state.user_logged = st.session_state.mobile
                    st.rerun()
                else:
                    st.error("❌ Wrong OTP")
    st.stop()

# ================= TEST PAGE (If logged in) =================
st.set_page_config(page_title="SPAY INDIA", layout="wide")

# Select 20 Random Questions once
if "questions_set" not in st.session_state:
    sel_math = random.sample(math_pool, 10)
    sel_eng = random.sample(english_pool, 10)
    final_list = sel_math + sel_eng
    random.shuffle(final_list)
    st.session_state.questions_set = final_list
    st.session_state.answers = [""] * 20
    st.session_state.current_q = 0

# Auto Logout Check
now = get_ist_time()
if (now - st.session_state.last_activity).total_seconds() > 300:
    logout()

st.markdown("""
<div style="background:linear-gradient(to right, #1a237e, #4caf50, #fbc02d); padding:20px; border-radius:10px; color:white; text-align:center;">
    <h1 style="margin:0;">SPAY INDIA</h1>
    <p style="margin:0; font-weight:bold;">SKILL ASSESSMENT TEST</p>
</div>
""", unsafe_allow_html=True)

st.warning("⚠️ Do NOT refresh this page. Progress will be lost.")

# Form
col_f1, col_f2 = st.columns(2)
with col_f1:
    candidate_name = st.text_input("Candidate Name", placeholder="Enter Name")
    st.write(f"**Mobile:** {st.session_state.mobile}")
with col_f2:
    hr_name = st.text_input("HR Name", placeholder="Enter HR Name")
    team_name = st.text_input("Interview Team", placeholder="Enter Team Name")

st.divider()

# Question Display
q_idx = st.session_state.current_q
q_data = st.session_state.questions_set[q_idx]

st.markdown(f"### Question {q_idx + 1} / 20")
st.markdown(f"<div style='color:#0d47a1; font-weight:bold; font-size:22px;'>{q_data['q']}</div>", unsafe_allow_html=True)

ans = st.radio("Choose Option:", q_data["options"], key=f"ans_{q_idx}")
st.session_state.answers[q_idx] = ans

st.markdown("<br>", unsafe_allow_html=True)
c_prev, c_next = st.columns(2)

with c_prev:
    if q_idx > 0:
        if st.button("← PREVIOUS", use_container_width=True):
            st.session_state.current_q -= 1
            st.rerun()

with c_next:
    if q_idx < 19:
        if st.button("NEXT →", use_container_width=True):
            st.session_state.last_activity = get_ist_time()
            st.session_state.current_q += 1
            st.rerun()
    else:
        if st.button("SUBMIT TEST", use_container_width=True):
            correct = sum(1 for i, q in enumerate(st.session_state.questions_set) if st.session_state.answers[i] == q["cor"])
            client = get_gspread_client()
            if client:
                try:
                    sheet = client.open("Assessment_Results").sheet1
                    sheet.append_row([
                        get_ist_time().strftime("%Y-%m-%d %I:%M %p"),
                        candidate_name, st.session_state.mobile, hr_name, team_name,
                        f"{correct}/20"
                    ])
                    st.success("✅ Submitted Successfully!")
                    st.balloons()
                    st.session_state.logged_in = False # Logout
                except Exception as e:
                    st.error(f"Error saving: {e}")
