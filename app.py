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
if "submitted" not in st.session_state:
    st.session_state.submitted = False

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

# ---------------- GLOBAL CSS (Adaptive Theme & Blue Radio Buttons) ----------------
st.markdown("""
<style>
    header {visibility: hidden;}

    /* 1. Page ke sabse upar ka extra space hatane ke liye */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
    }

    /* 2. Image aur Login Box ko thoda aur upar push karne ke liye */
    [data-testid="stVerticalBlock"] {
        gap: 0rem;
    }

    /* 3. Header hidden rakhein (Jo aapne pehle bhi kiya tha) */
    header {visibility: hidden;}
    
    /* Input box text adjustment: Adapt to Streamlit Theme */
    div[data-baseweb="input"] input {
        color: inherit !important; /* Automatic: Black in light, White in dark */
    }

    /* Placeholder color to keep it readable */
    div[data-baseweb="input"] input::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
    }

    /* Solid Blue Buttons */
    div.stButton > button {
        background-color: #1a237e !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        height: 40px !important;
        border: none !important;
    }

    /* Radio Button (Options) Styling */
    /* Text color for options */
    div[data-testid="stMarkdownContainer"] p {
        color: inherit;
    }

    /* Blue highlight for selected radio circle */
    div[role="radiogroup"] label div[data-testid="stMarker"] {
        background-color: #1a237e !important;
        border-color: #1a237e !important;
    }

    /* Header styling */
    .header-container {
        width: 100%; margin-top: 30px; height: 100px;
        background: linear-gradient(to right, #1a237e, #4caf50, #fbc02d);
        display: flex; justify-content: center; align-items: center;
        color: white; border-radius: 10px; flex-direction: column;
        margin-bottom: 20px;
    }
    .header-title { font-size: 42px; font-weight: bold; color: white; }
    .header-subtitle { font-size: 15px; font-weight: bold; color: white; }

    .warning-box {
        padding: 10px; background-color: #fff3cd; color: #856404;
        border-radius: 5px; text-align: center; font-weight: bold; margin-bottom: 10px;
    }
    
    .input-label { font-weight: bold; margin-top: 10px; color: inherit; }

    /* Login Page Title specifically for Blue color */
    .login-brand {
        font-size: 42px; font-weight: bold; color: #1a237e; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN PAGE (Original Layout) =================
if not st.session_state.get("logged_in", False):
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        img_filename = "interview_boy.png" 
        if os.path.exists(img_filename):
            st.image(img_filename, width=300)

    with col2:
        st.markdown('<div class="login-brand">SPAY INDIA</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; font-weight: 600; margin-bottom: 40px;">Candidate Portal</div>', unsafe_allow_html=True)
    # ... baki ka code
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
    # ================= MATH QUESTIONS (20) =================
    {"q":"25% of 200 = ?","options":["40","50","60","70"],"cor":"50","cat":"Math"},
    {"q":"15% of 500 = ?","options":["65","70","75","80"],"cor":"75","cat":"Math"},
    {"q":"30% of 900 = ?","options":["250","270","290","310"],"cor":"270","cat":"Math"},
    {"q":"Calculate: 12 * 8 + 4","options":["96","100","104","108"],"cor":"100","cat":"Math"},
    {"q":"Square root of 144?","options":["10","11","12","13"],"cor":"12","cat":"Math"},
    {"q":"Solve: (50 + 50) / 2","options":["25","50","75","100"],"cor":"50","cat":"Math"},
    {"q":"What is 1/4 of 1000?","options":["200","250","300","350"],"cor":"250","cat":"Math"},
    {"q":"If a pen costs 15, what is the cost of 12 pens?","options":["160","170","180","190"],"cor":"180","cat":"Math"},
    {"q":"20% of what number is 40?","options":["150","180","200","250"],"cor":"200","cat":"Math"},
    {"q":"Solve: 150 - (25 * 4)","options":["50","75","100","125"],"cor":"50","cat":"Math"},
    {"q":"What is the average of 10, 20, and 30?","options":["15","20","25","30"],"cor":"20","cat":"Math"},
    {"q":"450 / 9 = ?","options":["40","45","50","55"],"cor":"50","cat":"Math"},
    {"q":"If x + 15 = 40, find x.","options":["20","25","30","35"],"cor":"25","cat":"Math"},
    {"q":"7 * 9 = ?","options":["56","63","72","81"],"cor":"63","cat":"Math"},
    {"q":"Convert 0.75 into percentage.","options":["7.5%","75%","0.75%","750%"],"cor":"75%","cat":"Math"},
    {"q":"Which is greater: 0.5 or 0.05?","options":["0.5","0.05","Both equal","None"],"cor":"0.5","cat":"Math"},
    {"q":"How many minutes are there in 2.5 hours?","options":["120","140","150","160"],"cor":"150","cat":"Math"},
    {"q":"10% of 1500 = ?","options":["100","150","200","250"],"cor":"150","cat":"Math"},
    {"q":"(8 + 2) * (5 - 3) = ?","options":["10","15","20","25"],"cor":"20","cat":"Math"},
    {"q":"Next number in series: 2, 4, 8, 16, ?","options":["20","24","32","36"],"cor":"32","cat":"Math"},

    # ================= ENGLISH QUESTIONS (20) =================
    {"q":"She ___ to the office every day.","options":["go","goes","going","gone"],"cor":"goes","cat":"English"},
    {"q":"Choose the opposite of 'Success'.","options":["Victory","Failure","Growth","Progress"],"cor":"Failure","cat":"English"},
    {"q":"Which one is a synonym of 'Fast'?","options":["Slow","Quick","Delay","Lazy"],"cor":"Quick","cat":"English"},
    {"q":"He is ___ honest man.","options":["a","an","the","no article"],"cor":"an","cat":"English"},
    {"q":"Identify the correctly spelled word.","options":["Recieve","Receive","Recive","Receve"],"cor":"Receive","cat":"English"},
    {"q":"Plural of 'Child' is ___","options":["Childs","Children","Childrens","Childes"],"cor":"Children","cat":"English"},
    {"q":"They ___ playing cricket yesterday.","options":["was","were","is","am"],"cor":"were","cat":"English"},
    {"q":"Opposite of 'Difficult' is ___","options":["Hard","Easy","Simple","Soft"],"cor":"Easy","cat":"English"},
    {"q":"I ___ finished my work.","options":["has","have","is","am"],"cor":"have","cat":"English"},
    {"q":"Look! The bus ___","options":["come","coming","is coming","comes"],"cor":"is coming","cat":"English"},
    {"q":"Choose the correct preposition: He is fond ___ music.","options":["of","off","to","with"],"cor":"of","cat":"English"},
    {"q":"Which is a noun?","options":["Beautiful","Run","London","Quickly"],"cor":"London","cat":"English"},
    {"q":"Antonym of 'Brave' is ___","options":["Strong","Coward","Hero","Fearless"],"cor":"Coward","cat":"English"},
    {"q":"Past tense of 'Eat' is ___","options":["Eated","Eating","Ate","Eaten"],"cor":"Ate","cat":"English"},
    {"q":"I have been waiting here ___ two hours.","options":["since","for","from","at"],"cor":"for","cat":"English"},
    {"q":"Identify the adjective.","options":["Speak","Blue","Slowly","Happiness"],"cor":"Blue","cat":"English"},
    {"q":"'To cry wolf' means?","options":["To kill a wolf","To give a false alarm","To be brave","To shout"],"cor":"To give a false alarm","cat":"English"},
    {"q":"Which sentence is correct?","options":["He don't like tea.","He doesn't likes tea.","He doesn't like tea.","He not like tea."],"cor":"He doesn't like tea.","cat":"English"},
    {"q":"Synonym of 'Large' is ___","options":["Small","Huge","Tiny","Thin"],"cor":"Huge","cat":"English"},
    {"q":"The cat is sitting ___ the table.","options":["in","under","between","over"],"cor":"under","cat":"English"}
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

# Validation: Check if all details are filled
if not name or not hr or not team:
    st.warning("⚠️ Please fill in all details (Name, HR Name, Team) before starting the test!")
    st.stop()
# ================= QUESTION LOGIC (Fully Adaptive) =================
curr = st.session_state.current_q
q = st.session_state.questions_set[curr]

# 1. Question Number: Thoda upar (-35px) aur Gray color mein
st.markdown(f"""
    <div style='font-size: 14px; color: gray; margin-top: -35px; margin-bottom: 2px;'>
        Question {curr+1} / {len(st.session_state.questions_set)} ({q['cat']})
    </div>
    """, unsafe_allow_html=True)

# 2. Main Question: 
# Dark Mode mein 'White' aur Light Mode mein 'Blue' dikhane ke liye niche wala CSS:
st.markdown(f"""
    <style>
        /* Light Mode (Default) */
        .adaptive-question {{
            color: #1a237e; 
            font-weight: bold; 
            font-size: 26px; 
            line-height: 1.2;
        }}
        
        /* Dark Mode Detection */
        @media (prefers-color-scheme: dark) {{
            .adaptive-question {{
                color: #FFFFFF !important;
            }}
        }}
    </style>
    <div class="adaptive-question">
        {q['q']}
    </div>
    """, unsafe_allow_html=True)

# 3. Radio Buttons (Options)
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
ans = st.radio("Options:", q["options"], key=f"q_{curr}", label_visibility="collapsed")
st.session_state.answers[curr] = ans = ans

# Nav
col_n, col_s = st.columns(2)
with col_n:
    if curr < len(st.session_state.questions_set) - 1:
        if st.button("NEXT →", use_container_width=True):
            st.session_state.current_q += 1
            st.rerun()
with col_s:
    if st.button("SUBMIT TEST", use_container_width=True, disabled=st.session_state.get("submitted", False)):
        if not st.session_state.get("submitted", False):
            st.session_state.submitted = True
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
