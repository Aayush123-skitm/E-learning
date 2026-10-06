import csv
import smtplib
from email.message import EmailMessage
import random
import re
import os
import subprocess
import time
import wave

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

from db import con, cursor

# =====================================================================
# BASIC SETUP
# =====================================================================
st.set_page_config(page_title="Smart E-Learning & Quiz System", page_icon="🎓", layout="wide")

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
mai_folder = os.path.join(BASE_FOLDER, "study_material")

load_dotenv()

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# =====================================================================
# CSS / UI THEME
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.6rem; padding-bottom: 4rem; max-width: 1200px; }

/* ---------- HERO ---------- */
.hero {
    position: relative; overflow: hidden;
    background: linear-gradient(120deg, #4338ca 0%, #7c3aed 45%, #db2777 100%);
    background-size: 200% 200%; animation: heroShift 12s ease infinite;
    padding: 34px 40px; border-radius: 24px; color: #fff; margin-bottom: 26px;
    box-shadow: 0 18px 45px -12px rgba(124,58,237,.55);
}
.hero::before, .hero::after {
    content: ""; position: absolute; border-radius: 50%; background: rgba(255,255,255,.10);
}
.hero::before { width: 260px; height: 260px; right: -60px; top: -90px; }
.hero::after  { width: 160px; height: 160px; right: 140px; bottom: -80px; background: rgba(255,255,255,.07); }
.hero h1 { margin: 0; font-size: 2.1rem; font-weight: 800; color: #fff; letter-spacing: -.5px; position: relative; z-index: 1; }
.hero p  { margin: 8px 0 0 0; opacity: .92; font-size: 1.02rem; position: relative; z-index: 1; }
@keyframes heroShift { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }

/* ---------- CHIPS ---------- */
.chips { display: flex; flex-wrap: wrap; gap: 10px; margin: -6px 0 22px 0; }
.chip {
    padding: 8px 16px; border-radius: 999px; font-size: .85rem; font-weight: 600;
    background: rgba(124,58,237,.12); color: #7c3aed; border: 1px solid rgba(124,58,237,.30);
}

/* ---------- CARDS ---------- */
.card {
    background: var(--secondary-background-color, rgba(128,128,160,.08));
    border: 1px solid rgba(128,128,160,.22); border-left: 5px solid #7c3aed;
    border-radius: 16px; padding: 18px 22px; margin-bottom: 14px;
    box-shadow: 0 6px 18px -8px rgba(0,0,0,.25); transition: transform .15s ease, box-shadow .15s ease;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 12px 26px -10px rgba(124,58,237,.45); }
.card h4 { margin: 0 0 6px 0; font-weight: 700; }
.qcard {
    background: linear-gradient(135deg, rgba(79,70,229,.14), rgba(219,39,119,.09));
    border: 1px solid rgba(124,58,237,.40); border-radius: 18px; padding: 22px 26px; margin-bottom: 14px;
    font-size: 1.05rem; line-height: 1.6; box-shadow: 0 8px 22px -12px rgba(124,58,237,.5);
}
.badge { display:inline-block; padding: 3px 12px; border-radius: 999px; font-size:.75rem; font-weight:700; letter-spacing:.3px; }
.b-ok   { background:#16a34a22; color:#16a34a; border:1px solid #16a34a66; }
.b-bad  { background:#dc262622; color:#dc2626; border:1px solid #dc262666; }
.b-skip { background:#f59e0b22; color:#d97706; border:1px solid #f59e0b66; }

/* ---------- BUTTONS ---------- */
div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
    border-radius: 12px; font-weight: 600; padding: .6rem 1.4rem; border: 0; color: #fff;
    background: linear-gradient(135deg, #4f46e5, #7c3aed 60%, #c026d3);
    box-shadow: 0 6px 16px -6px rgba(124,58,237,.6); transition: all .15s ease;
}
div.stButton > button:hover, div.stDownloadButton > button:hover, div.stFormSubmitButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 12px 24px -8px rgba(124,58,237,.75); color: #fff; border: 0;
}
div.stButton > button:active, div.stFormSubmitButton > button:active { transform: translateY(0); }

/* ---------- INPUTS ---------- */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    border-radius: 12px !important; border: 1.5px solid rgba(128,128,160,.35) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: #7c3aed !important; box-shadow: 0 0 0 3px rgba(124,58,237,.20) !important;
}
div[data-baseweb="select"] > div { border-radius: 12px !important; }
[data-testid="stForm"] {
    border: 1px solid rgba(128,128,160,.25); border-radius: 18px; padding: 22px 24px;
    background: var(--secondary-background-color, rgba(128,128,160,.06));
}

/* ---------- QUIZ OPTIONS (main area radio as option cards) ---------- */
.main div[role="radiogroup"] { gap: 10px; }
.main div[role="radiogroup"] > label {
    border: 1.5px solid rgba(128,128,160,.35); border-radius: 14px; padding: 12px 16px;
    background: var(--secondary-background-color, rgba(128,128,160,.06)); transition: all .15s ease; width: 100%;
}
.main div[role="radiogroup"] > label:hover { border-color: #7c3aed; transform: translateX(3px); }
.main div[role="radiogroup"] > label:has(input:checked) {
    border-color: #7c3aed; background: rgba(124,58,237,.14); box-shadow: 0 0 0 2px rgba(124,58,237,.25);
}

/* ---------- METRICS / TABS / PROGRESS ---------- */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(79,70,229,.10), rgba(219,39,119,.06));
    border: 1px solid rgba(124,58,237,.30); padding: 14px 18px; border-radius: 16px;
}
[data-testid="stMetricValue"] { font-weight: 800; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    font-weight: 600; border-radius: 12px 12px 0 0; padding: 10px 20px;
}
.stTabs [aria-selected="true"] { color: #7c3aed !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #7c3aed !important; height: 3px; }
.stProgress > div > div > div > div { background: linear-gradient(90deg, #4f46e5, #db2777); }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid rgba(128,128,160,.25); }
[data-testid="stAlert"] { border-radius: 14px; }

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #312e81 60%, #4c1d95 100%); }
[data-testid="stSidebar"] * { color: #e0e7ff !important; }
.brand { font-size: 1.35rem; font-weight: 800; padding: 6px 4px 2px 4px; color: #fff !important; }
.brand span { display: block; font-size: .75rem; font-weight: 500; opacity: .75; margin-top: 2px; }
.welcome {
    background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.18);
    border-radius: 14px; padding: 10px 14px; margin: 10px 0 16px 0; font-weight: 600;
}
[data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 14px; border-radius: 12px; width: 100%; transition: all .15s ease; border: 1px solid transparent;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: rgba(255,255,255,.10); }
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, rgba(124,58,237,.85), rgba(219,39,119,.70));
    border: 1px solid rgba(255,255,255,.25); box-shadow: 0 6px 16px -6px rgba(0,0,0,.5);
}
</style>
""", unsafe_allow_html=True)


def hero(title, subtitle=""):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def card(html):
    st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)


# =====================================================================
# SESSION STATE
# =====================================================================
def init_state():
    defaults = {
        "student": None,      # login row of student
        "nm": None,           # typed name used for queries
        "admin": None,        # admin name
        "reg": {"stage": "email"},
        "fp": {"stage": "check"},
        "quiz": None,
        "code": None,
        "hr": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# =====================================================================
# HELPERS (same logic as original)
# =====================================================================
OTP_CHARACTERS = "ABCDEFGHI123tuvrs4567890#@"


def generate_otp():
    return ''.join(random.choices(OTP_CHARACTERS, k=random.randint(4, 6)))


def smtp_send(msg):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()


def send_otp_email(to_email, subject, body_text):
    sender_email = os.getenv("SENDER_EMAIL")
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body_text)
    try:
        smtp_send(msg)
        return True, None
    except Exception as e:
        return False, e


def registration_otp_body(otp):
    return f"""
Hello Learners 👋,

Welcome to Smart E-Learning!

Your One-Time Password (OTP) for registration is:

OTP: {otp}

This OTP is valid for 2 minutes.
Please do not share this OTP with anyone.

If you did not request this registration, please ignore this email.

Best Regards,
Smart E-Learning Team
College Learning & Quiz Platform
"""


def details_otp_body(otp):
    return f"""
Hello Learner 👋,

Welcome to Smart E-Learning!

Your OTP to view your account details is:

OTP: {otp}

This OTP is valid for 2 minutes.
Please do not share this OTP with anyone.

If you did not request this, please ignore this email.

Best Regards,
Smart E-Learning Team
College Learning & Quiz Platform
"""


def send_certificate_email(student_email, certificate_file):
    sender_email = os.getenv("SENDER_EMAIL")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = student_email
    msg["Subject"] = "Smart E-Learning | Course Certificate"

    msg.set_content("""
Hello Learner 👋,

Congratulations! 🎉

Your course certificate is attached with this email.

Thank you for learning with Smart E-Learning.

Best Regards,
Smart E-Learning Team
""")

    with open(certificate_file, "rb") as f:
        certificate_data = f.read()

    msg.add_attachment(
        certificate_data,
        maintype="application",
        subtype="pdf",
        filename="Smart_E-Learning_Certificate.pdf"
    )

    try:
        smtp_send(msg)
        return True, "Certificate sent successfully to your email."
    except Exception as e:
        return False, f"Certificate sending failed: {e}"


def email_score(em):
    score = 0
    if re.search(r"@", em):
        score += 1
    if re.search(r"^[^@\s]+@", em):
        score += 1
    if re.search(r"@[^@\s]+\.com$", em):
        score += 1
    if " " not in em:
        score += 1
    return score


def password_score(sp):
    score = 0
    if len(sp) >= 8:
        score += 1
    if re.search(r"[a-z]", sp):
        score += 1
    if re.search(r'[A-Z]', sp):
        score += 1
    if re.search(r'[0-9]', sp):
        score += 1
    return score


def ask_ai(prompt, model):
    response = openrouter_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def logout():
    st.session_state.student = None
    st.session_state.nm = None
    st.session_state.admin = None
    st.session_state.quiz = None
    st.session_state.code = None
    st.session_state.hr = {}
    st.session_state.reg = {"stage": "email"}
    st.session_state.fp = {"stage": "check"}


# =====================================================================
# STUDENT : REGISTER
# =====================================================================
def student_register():
    reg = st.session_state.reg
    st.subheader("📝 Create your account")

    if reg["stage"] == "email":
        with st.form("reg_email"):
            name = st.text_input("ENTER YOUR FULL NAME")
            em = st.text_input("ENTER YOUR EMAIL")
            go = st.form_submit_button("Send OTP 📧")
        if go:
            sql = "SELECT student_id FROM students WHERE name = %s"
            cursor.execute(sql, (name,))
            existing_student = cursor.fetchone()
            if existing_student:
                st.warning("YOU ARE ALREADY REGISTERED! Please login instead.")
            elif email_score(em) < 4:
                st.error("Invalid Email.")
            else:
                otp = generate_otp()
                otp_time = time.time()
                ok, err = send_otp_email(em, "Smart E-Learning | Email Verification OTP",
                                         registration_otp_body(otp))
                if ok:
                    st.session_state.reg = {"stage": "otp", "name": name, "em": em,
                                            "otp": otp, "otp_time": otp_time}
                    st.rerun()
                else:
                    st.error(f"OTP sending failed: {err}")

    elif reg["stage"] == "otp":
        st.success("OTP sent successfully to your email.")
        with st.form("reg_otp"):
            user_otp = st.text_input("ENTER OTP")
            c1, c2 = st.columns(2)
            verify = c1.form_submit_button("Verify OTP ✅")
            resend = c2.form_submit_button("Change Email / Resend 🔁")
        if resend:
            st.session_state.reg = {"stage": "email"}
            st.rerun()
        if verify:
            current_time = time.time()
            if current_time - reg["otp_time"] > 120:
                st.error("OTP EXPIRED. Please request a new OTP.")
            elif user_otp == reg["otp"]:
                reg["stage"] = "details"
                st.rerun()
            else:
                st.error("WRONG OTP. Please try again.")

    elif reg["stage"] == "details":
        st.success("EMAIL VERIFIED SUCCESSFULLY.")
        with st.form("reg_details"):
            sp = st.text_input("SET PASSWORD", type="password",
                               help="Min 8 chars, with lowercase, uppercase and number")
            pn = st.number_input("ROLL NUMBER (eg.01 aur 02 , not abcd01)", min_value=0, step=1)
            cn = st.text_input("ENTER YOUR COLLEGE NAME")
            cr = st.text_input("COURSE NAME")
            br = st.text_input("BRANCH NAME")
            st.markdown("**SECURITY QUESTIONS**")
            fi = st.text_input("WHAT IS YOUR DOB (EG.01NOVEMBER2005)")
            go = st.form_submit_button("REGISTER 🚀")
        if go:
            if password_score(sp) < 4:
                st.error("weak")
            else:
                sql = """
                insert into students
                (Name, Email, set_pss, ph_no, clg_name, course, branch, secu_ans)
                values (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                data = (reg["name"], reg["em"], sp, int(pn), cn, cr, br, fi)
                cursor.execute(sql, data)
                con.commit()
                st.session_state.reg = {"stage": "email"}
                st.success("REGISTER SUCCESSFULL. Ab Login tab se login kariye.")
                st.balloons()


# =====================================================================
# STUDENT : LOGIN + FORGOT PASSWORD
# =====================================================================
def student_login():
    st.subheader("🔐 Student Login")
    with st.form("login_form"):
        nm = st.text_input("ENTER YOUR NAME")
        ps = st.text_input("ENTER YOUR PASSWORD", type="password")
        go = st.form_submit_button("LOGIN")
    if go:
        sql = """
        select * from students
        where name = %s AND set_pss = %s
        """
        cursor.execute(sql, (nm, ps))
        ec = cursor.fetchone()
        if ec:
            st.session_state.student = ec
            st.session_state.nm = nm
            st.rerun()
        else:
            st.error("NOT REGISTER.")


def student_forgot():
    fp = st.session_state.fp
    st.subheader("🔑 Lost your password?")

    if fp["stage"] == "check":
        st.info("SECURITY QUESTIONS")
        with st.form("fp_check"):
            nm = st.text_input("ENTER YOUR NAME")
            p = st.text_input("WHAT IS YOUR DOB")
            go = st.form_submit_button("Verify")
        if go:
            sql = """
            SELECT * FROM students
            WHERE Name = %s AND secu_ans = %s
            """
            cursor.execute(sql, (nm, p))
            result = cursor.fetchone()
            if result:
                st.session_state.fp = {"stage": "send", "nm": nm}
                st.rerun()
            else:
                st.error("WRONG NAME OR SECURITY ANSWER.")

    elif fp["stage"] == "send":
        st.success("Security answer correct. Password change karne ke liye OTP bhejna hoga.")
        if st.button("CHANGE PASSWORD (Send OTP to registered email)"):
            sql = """
            SELECT student_id, Name, Email, set_pss, ph_no,
                clg_name, course, branch
            FROM students
            WHERE Name = %s
            """
            cursor.execute(sql, (fp["nm"],))
            ec = cursor.fetchall()
            if ec:
                row = ec[0]
                em = row[2]
                otp = generate_otp()
                otp_time = time.time()
                ok, err = send_otp_email(em, "Smart E-Learning | Details Verification OTP",
                                         details_otp_body(otp))
                if ok:
                    st.session_state.fp = {"stage": "otp", "nm": fp["nm"], "otp": otp, "otp_time": otp_time}
                    st.rerun()
                else:
                    st.error(f"OTP sending failed: {err}")
            else:
                st.error("STUDENT DETAILS NOT FOUND.")

    elif fp["stage"] == "otp":
        st.success("OTP sent successfully to your registered email.")
        with st.form("fp_otp"):
            user_otp = st.text_input("ENTER OTP")
            go = st.form_submit_button("Verify OTP")
        if go:
            current_time = time.time()
            if current_time - fp["otp_time"] > 120:
                st.error("OTP EXPIRED. Please try again.")
                st.session_state.fp = {"stage": "check"}
            elif user_otp == fp["otp"]:
                fp["stage"] = "newpass"
                st.rerun()
            else:
                st.error("WRONG OTP. DETAILS CANNOT BE SHOWN.")

    elif fp["stage"] == "newpass":
        st.success("EMAIL VERIFIED SUCCESSFULLY.")
        st.markdown("### CHANGE PASSWORD")
        with st.form("fp_new"):
            new_password = st.text_input("ENTER NEW PASSWORD", type="password")
            confirm_password = st.text_input("CONFIRM NEW PASSWORD", type="password")
            go = st.form_submit_button("Update Password")
        if go:
            if new_password == confirm_password:
                if len(new_password) < 6:
                    st.error("PASSWORD MUST BE AT LEAST 6 CHARACTERS.")
                else:
                    sql = """
                    UPDATE students
                    SET set_pss = %s
                    WHERE Name = %s
                    """
                    cursor.execute(sql, (new_password, fp["nm"]))
                    con.commit()
                    st.session_state.fp = {"stage": "check"}
                    st.success("PASSWORD CHANGED SUCCESSFULLY. PLEASE LOGIN WITH YOUR NEW PASSWORD.")
            else:
                st.error("PASSWORDS DO NOT MATCH.")


# =====================================================================
# STUDENT PAGES
# =====================================================================
def page_detail():
    hero("👤 Your Detail", "Aapki profile ki saari jaankari")
    sql = """
    select student_id, Name, Email, set_pss, ph_no, clg_name, course, branch from students
    where name = %s
    """
    cursor.execute(sql, (st.session_state.nm,))
    ec = cursor.fetchall()
    for row in ec:
        c1, c2 = st.columns(2)
        with c1:
            card(f"<h4>🆔 Id</h4>{row[0]}")
            card(f"<h4>📧 Email</h4>{row[2]}")
            card(f"<h4>🔢 Roll Number</h4>{row[4]}")
            card(f"<h4>🎓 Course</h4>{row[6]}")
        with c2:
            card(f"<h4>🙋 Name</h4>{row[1]}")
            card(f"<h4>🔑 Password</h4>{row[3]}")
            card(f"<h4>🏫 College</h4>{row[5]}")
            card(f"<h4>🌿 Branch</h4>{row[7]}")


def page_result():
    hero("📊 Your Result", "Aapke saare quiz results")
    sql = """
    select result_id, name, subject, tq, score, percentage, status, medium, st_0f_certi from result
    where name = %s
    """
    cursor.execute(sql, (st.session_state.nm,))
    ec = cursor.fetchall()
    if ec:
        df = pd.DataFrame(ec, columns=["Result Id", "Name", "Subject", "Total Question", "Score",
                                       "Percentage", "Status", "Medium", "Status Of Certificate"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Quizzes", len(df))
        c2.metric("Best Percentage", f"{pd.to_numeric(df['Percentage'], errors='coerce').max():.1f}%")
        c3.metric("Passed", int((df["Status"] == "PASS").sum()))
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Abhi tak koi result nahi hai.")


def page_courses():
    hero("📚 Course List", "Available subjects")
    courses = ["Python", "Java", "C", "CPP", "HTML", "DBMS", "Aptitude",
               "Machine Learning", "Natural Language Processing"]
    cols = st.columns(3)
    for i, c in enumerate(courses):
        with cols[i % 3]:
            card(f"<h4>{i + 1}. {c}</h4>")


def page_certificates():
    hero("🏅 Your Certificates", "Download karein apne certificates")
    sid = st.session_state.student[0]
    sql = """
    SELECT certi_id, subject, score, status, certi_file
    FROM certificate
    WHERE student_id = %s
    """
    cursor.execute(sql, (sid,))
    certificates = cursor.fetchall()
    if certificates:
        df = pd.DataFrame([r[:4] for r in certificates],
                          columns=["Certificate ID", "Subject", "Score", "Status"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        cert_choice = st.selectbox("Enter Certificate ID to open", [r[0] for r in certificates])
        if st.button("Open Certificate 📄"):
            cursor.execute("""
            SELECT certi_file
            FROM certificate
            WHERE certi_id = %s AND student_id = %s
            """, (cert_choice, sid))
            cert = cursor.fetchone()
            if cert:
                pdf_path = cert[0]
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button("⬇️ Download / Open Certificate", f.read(),
                                           file_name=os.path.basename(pdf_path), mime="application/pdf")
                    try:
                        img = Image.open(pdf_path)
                        st.image(img, use_container_width=True)
                    except Exception:
                        pass
                else:
                    st.error("Certificate file not found.")
            else:
                st.error("Invalid Certificate ID.")
    else:
        st.info("You don't have any certificate.")


def page_learn():
    hero("🎥 Learn using Videos & PDFs", "Study material subject-wise")
    if os.path.isdir(mai_folder):
        subs = sorted([d for d in os.listdir(mai_folder) if os.path.isdir(os.path.join(mai_folder, d))])
    else:
        subs = []
    if subs:
        sub = st.selectbox("subject", subs)
    else:
        sub = st.text_input("subject")
    sub = sub.lower().strip().strip("'\"")

    fol = os.path.join(mai_folder, sub)
    cs = st.radio("Choice", ["Video", "PDF"], horizontal=True)

    if not sub:
        return

    if cs == "PDF":
        pdf = os.path.join(fol, f"{sub}_Basic_Notes.pdf")
        st.caption(f"Checking: {pdf}")
        if os.path.exists(pdf):
            with open(pdf, "rb") as f:
                st.download_button("⬇️ Open / Download PDF", f.read(),
                                   file_name=os.path.basename(pdf), mime="application/pdf")
        else:
            st.error("File not found!")
            st.write("Expected file:", pdf)
    else:
        videos = []
        if os.path.isdir(fol):
            for file in os.listdir(fol):
                if file.endswith(".mp4"):
                    videos.append(file)
        if len(videos) == 0:
            st.warning(f"No videos available for {sub}")
        else:
            gf = st.selectbox("Which video", videos)
            path = os.path.join(fol, gf)
            st.caption(f"Checking: {path}")
            if os.path.exists(path):
                st.video(path)
            else:
                st.error("File not found!")


# ---------------------------------------------------------------------
# QUIZ
# ---------------------------------------------------------------------
QUIZ_SUBJECTS = {
    "Python": "python", "Java": "java", "C": "c", "CPP": "cpp", "HTML": "html",
    "DBMS": "dbms", "Aptitude": "aptitude", "Machine Learning": "ml",
    "Natural Language Processing": "nlp",
}


def quiz_new(sub):
    qu = []
    with open(os.path.join(BASE_FOLDER, f"{sub}.csv"), "r", encoding="utf-8-sig", newline="") as f:
        read = csv.DictReader(f)
        for row in read:
            qu.append(row)
    qq = random.sample(qu, 5)
    st.session_state.quiz = {
        "sub": sub, "qq": qq, "idx": 0, "score": 0, "correct": 0, "wrong": 0, "skipped": 0,
        "history": [], "start": time.time(), "limit": 600, "finished": False,
        "processed": False, "feedback": None, "time_over": False, "msgs": [],
        "solutions": {}, "tt": 0, "percentage": 0,
    }


def quiz_record(qz, q, ans):
    """ans: 'a'/'b'/'c'/'d' or 'skip'"""
    base = {"question": q["qus"], "op_a": q["op_a"], "op_b": q["op_b"],
            "op_c": q["op_c"], "op_d": q["op_d"], "correct_answer": q["correct_ans"]}
    if ans == "skip":
        qz["feedback"] = ("warning", "Question Skipped! No marks deducted.")
        qz["skipped"] += 1
        qz["history"].append({**base, "user_answer": "SKIPPED", "status": "SKIPPED"})
        qz["idx"] += 1
        return

    USER_ANS = "op_" + ans
    if USER_ANS == q["correct_ans"]:
        qz["feedback"] = ("success", "Your Answer Is Correct")
        qz["score"] += 1
        qz["correct"] += 1
        status = "CORRECT"
    else:
        qz["feedback"] = ("error", f"Your Answer Is Incorrect — Correct Answer Is {q['correct_ans']}")
        qz["score"] -= 0.25
        qz["wrong"] += 1
        status = "WRONG"
    qz["history"].append({**base, "user_answer": USER_ANS, "status": status})
    qz["idx"] += 1


def quiz_finalize(qz):
    """Result save + certificate generation (same logic as original)."""
    sub = qz["sub"]
    sid = st.session_state.student[0]
    name = st.session_state.student[1]
    me = "EASY"
    qq = qz["qq"]
    score = qz["score"]
    msgs = []

    percentage = (score / len(qq)) * 100
    qz["percentage"] = percentage

    if percentage >= 45:
        ST = "PASS"
        msgs.append(("success", "YOU ARE PASS"))
        tt = qz["tt"]
        cert = "Genrated"

        sql = """
        INSERT INTO result
        (student_id, subject, tq, score, percentage,
        time_taken, status, medium, name, st_0f_certi)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (sid, sub, len(qq), score, percentage, tt, ST, me, name, cert)
        cursor.execute(sql, data)
        con.commit()
        msgs.append(("info", "Result Saved."))
        nss = name
        QUIZ = sub

        sql = """
        SELECT certi_id, certi_file
        FROM certificate
        WHERE student_id = %s AND subject = %s
        """
        cursor.execute(sql, (sid, sub))
        existing_certificate = cursor.fetchone()
        if existing_certificate:
            msgs.append(("warning", f"CERTIFICATE ALREADY GENERATED! You already have a certificate for {sub}"))
        else:
            try:
                base_folder = os.path.dirname(os.path.abspath(__file__))
                certificate_folder = os.path.join(base_folder, "certificates")
                os.makedirs(certificate_folder, exist_ok=True)

                cerpy_path = os.path.join(BASE_FOLDER, "cerpy.png")
                cerp = Image.open(cerpy_path)
                draw = ImageDraw.Draw(cerp)
                font_path = os.path.join(BASE_FOLDER, "Boldonse-Regular.ttf")
                font = ImageFont.truetype(font_path, 38)

                # NAME CENTER
                bbox = draw.textbbox((0, 0), nss, font=font)
                name_width = bbox[2] - bbox[0]
                name_x = (cerp.width - name_width) // 2
                draw.text((name_x, 644), nss, fill="black", font=font)

                # COURSE CENTER
                bbox = draw.textbbox((0, 0), QUIZ, font=font)
                course_width = bbox[2] - bbox[0]
                course_x = (cerp.width - course_width) // 2
                draw.text((course_x, 873), QUIZ, fill="black", font=font)

                pdf_path = os.path.join(certificate_folder, f"{nss}_{QUIZ}.pdf")
                cerp.convert("RGB").save(pdf_path)
                msgs.append(("success", f"CERTIFICATE GENRATOR FOR THE {nss}"))

                sql = """
                INSERT INTO certificate
                (student_id, subject, score, status, certi_file)
                VALUES (%s, %s, %s, %s, %s)
                """
                data = (sid, sub, score, ST, pdf_path)
                cursor.execute(sql, data)
                con.commit()
                msgs.append(("info", "Certificate details saved in database."))

                student_email = st.session_state.student[2]
                ok, text = send_certificate_email(student_email, pdf_path)
                msgs.append(("success" if ok else "error", text))
            except Exception as e:
                msgs.append(("error", f"Certificate generation failed: {e}"))
    else:
        msgs.append(("error", "YOU ARE NOT ELIGIBLE FOR CERTIFICATE."))

    qz["msgs"] = msgs
    qz["processed"] = True


def page_quiz():
    hero("📝 Give Quiz", "Minus marking • 5 random questions")

    qz = st.session_state.quiz

    # ---------------- SELECT SUBJECT ----------------
    if qz is None:
        st.markdown("### ===== SELECT SUBJECT =====")
        label = st.selectbox("ENTER YOUR SUBJECT", list(QUIZ_SUBJECTS.keys()))
        card("<h4>⚠️ INSTRUCTION</h4>1. Minus Marking<br>2. Time gives Only 15 Minutes")
        if st.button("START QUIZ ▶️"):
            sub_key = QUIZ_SUBJECTS[label]
            try:
                quiz_new(sub_key)
                st.rerun()
            except FileNotFoundError:
                st.error(f"Question file nahi mili: {sub_key}.csv (app.py wale folder me rakhiye).")
            except ValueError:
                st.error(f"{sub_key}.csv me kam se kam 5 questions hone chahiye.")
            except KeyError as e:
                st.error(f"{sub_key}.csv me ye column missing hai: {e}. Columns: qus, op_a, op_b, op_c, op_d, correct_ans")
        return

    # ---------------- RUNNING ----------------
    if not qz["finished"]:
        use_time = time.time() - qz["start"]
        remaining = qz["limit"] - use_time

        if qz["idx"] >= len(qz["qq"]) or use_time >= qz["limit"]:
            if qz["idx"] < len(qz["qq"]) and use_time >= qz["limit"]:
                qz["time_over"] = True
            qz["finished"] = True
            qz["tt"] = int(time.time() - qz["start"])
            st.rerun()

        c1, c2, c3 = st.columns(3)
        c1.metric("Question", f"{qz['idx'] + 1} / {len(qz['qq'])}")
        c2.metric("Score", qz["score"])
        c3.metric("⏱ Time Left", f"{int(remaining // 60)}:{int(remaining % 60):02d}")
        st.progress(qz["idx"] / len(qz["qq"]))

        if qz["feedback"]:
            kind, text = qz["feedback"]
            getattr(st, kind)(text)

        q = qz["qq"][qz["idx"]]
        st.markdown(f'<div class="qcard"><b>Q.</b> {q["qus"]}</div>', unsafe_allow_html=True)

        opts = {"a": q["op_a"], "b": q["op_b"], "c": q["op_c"], "d": q["op_d"]}
        ans = st.radio("ENTER YOUR ANSWER (A/B/C/D)", list(opts.keys()),
                       format_func=lambda k: f"{k.upper()}.  {opts[k]}",
                       index=None, key=f"ans_{qz['idx']}")
        st.caption("If you do not know the answer, press SKIP.")

        b1, b2, _ = st.columns([1, 1, 4])
        if b1.button("Submit ✅"):
            if ans is None:
                st.warning("Option select kariye ya SKIP dabaiye.")
            else:
                quiz_record(qz, q, ans)
                st.rerun()
        if b2.button("SKIP ⏭️"):
            quiz_record(qz, q, "skip")
            st.rerun()
        return

    # ---------------- RESULT ----------------
    if not qz["processed"]:
        quiz_finalize(qz)

    if qz["time_over"]:
        st.warning("TIME OVER!")
    if qz["feedback"]:
        kind, text = qz["feedback"]
        getattr(st, kind)(text)

    st.markdown("## 🏁 RESULT")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("TOTAL QUESTIONS", len(qz["qq"]))
    c2.metric("CORRECT ANSWERS", qz["correct"])
    c3.metric("WRONG ANSWERS", qz["wrong"])
    c4.metric("SKIPPED", qz["skipped"])
    c5.metric("YOUR SCORE", f"{qz['score']} / {len(qz['qq'])}")
    st.metric("PERCENTAGE", f"{qz['percentage']}")

    for kind, text in qz["msgs"]:
        getattr(st, kind)(text)

    st.markdown("---")
    view = st.toggle("Do you want to view your questions?")
    if view:
        model = "meta-llama/llama-3.2-3b-instruct" if qz["sub"] == "python" else "openrouter/free"
        for i, item in enumerate(qz["history"], start=1):
            badge = {"CORRECT": "b-ok", "WRONG": "b-bad", "SKIPPED": "b-skip"}[item["status"]]
            st.markdown(
                f'<div class="qcard"><b>QUESTION {i}</b> &nbsp; '
                f'<span class="badge {badge}">{item["status"]}</span><br><br>{item["question"]}<br><br>'
                f'A. {item["op_a"]}<br>B. {item["op_b"]}<br>C. {item["op_c"]}<br>D. {item["op_d"]}<br><br>'
                f'<b>Your Answer :</b> {item["user_answer"]}<br>'
                f'<b>Correct Answer :</b> {item["correct_answer"]}</div>',
                unsafe_allow_html=True)

            if st.button("💡 Full solution", key=f"sol_{i}"):
                try:
                    correct_option = item["correct_answer"]
                    if correct_option == "op_a":
                        correct_text = item["op_a"]
                    elif correct_option == "op_b":
                        correct_text = item["op_b"]
                    elif correct_option == "op_c":
                        correct_text = item["op_c"]
                    else:
                        correct_text = item["op_d"]

                    subj_name = {v: k for k, v in QUIZ_SUBJECTS.items()}.get(qz["sub"], qz["sub"])
                    prompt = f"""
Give a very short and simple solution for this {subj_name} quiz question.

Question:
{item["question"]}

Correct Answer:
{correct_text}

Rules:
- Explain in only 2 to 4 short lines.
- Use very simple English.
- If useful, give a tiny {subj_name} example.
- Do not add headings.
- Do not make the explanation lengthy.
"""
                    with st.spinner("Generating solution..."):
                        qz["solutions"][i] = ask_ai(prompt, model)
                except Exception as e:
                    qz["solutions"][i] = f"Solution could not be generated: {e}"
            if i in qz["solutions"]:
                st.info("**SOLUTION:**\n\n" + qz["solutions"][i])

    if st.button("🔁 Give another quiz"):
        st.session_state.quiz = None
        st.rerun()


def page_announcements():
    hero("📢 Announcements", "Latest updates")
    cursor.execute("select * from announce")
    ac = cursor.fetchall()
    if ac:
        for row in ac:
            card(f"<h4>{row[1]}</h4>{row[2]}<br><small>ID: {row[0]} &nbsp;|&nbsp; Date: {row[3]} "
                 f"&nbsp;|&nbsp; Status: {row[4]}</small>")
    else:
        st.info("No announcements.")


def page_feedback():
    hero("💬 Feedback", "Aapki raay humare liye important hai")
    with st.form("fb_form"):
        mes = st.text_area("ENTER YOUR FEEDBACK")
        go = st.form_submit_button("Submit Feedback")
    if go:
        sql = """
        insert into feedback
        (student_id, Name, msg)
        values (%s, %s, %s)
        """
        data = (st.session_state.student[0], st.session_state.student[1], mes)
        cursor.execute(sql, data)
        con.commit()
        st.success("THANKYOU FOR FEEDBACK")


# ---------------------------------------------------------------------
# HR INTERVIEW PRACTICE
# ---------------------------------------------------------------------
HR_QUESTIONS = [
    "Tell me about yourself",
    "What are your strengths?",
    "What are your weaknesses?",
    "Why should we hire you?",
    "Why do you want to join our company?",
    "Where do you see yourself in 5 years?",
    "How do you handle pressure?",
    "Are you comfortable working in a team?",
    "What are your career goals?",
    "Do you have any questions for us?",
]


def hr_prompt(selected_question):
    return f"""
You are an HR interview coach who is preparing a college student
for a real HR interview.

Interview Question:
{selected_question}

Your job is to explain HOW the student should answer this specific
question and then provide a natural SAMPLE ANSWER.

IMPORTANT:
The answer must be according to the selected question.
Do not use the same answer structure for every question.

Use EXACTLY these sections:

============================================================
HOW TO ANSWER
============================================================

Give 4 to 6 useful points according to the question.

For every point:
- Explain what the candidate should say.
- Keep the explanation short.
- Give practical speaking advice.
- Use simple English.

The structure should change according to the question.

Examples:

For "Tell me about yourself":
1. Start with your name
2. Education / current status
3. Skills and interests
4. Project / experience if applicable
5. Career goal
6. Natural ending

For "What are your strengths?":
1. Choose 2-3 genuine strengths
2. Briefly explain each strength
3. Give a small example
4. Connect strengths with the job
5. End naturally

For "What are your weaknesses?":
1. Choose one genuine but manageable weakness
2. Briefly explain it
3. Explain its effect
4. Explain how you are improving it
5. End positively

For "Why should we hire you?":
1. Mention relevant skills
2. Give a project/learning example
3. Explain what you can contribute
4. Show willingness to learn
5. End confidently

For "Why do you want to join our company?":
1. Explain what interests you about the company/role
2. Connect it with your career interest
3. Explain what you want to learn
4. Explain why the role is relevant
5. End naturally

For "Where do you see yourself in 5 years?":
1. Explain professional direction
2. Mention skills you want to develop
3. Mention realistic growth
4. Show willingness to learn and take responsibility
5. End positively

For "How do you handle pressure?":
1. Explain your approach
2. Explain how you prioritize tasks
3. Explain how you remain calm and focused
4. Give a small example if applicable
5. Explain what you learned

For "Are you comfortable working in a team?":
1. Say whether you are comfortable
2. Explain communication with teammates
3. Mention your role in teamwork
4. Give a small example if applicable
5. Explain what you learned

For "What are your career goals?":
1. Mention short-term goal
2. Mention skills you want to improve
3. Mention long-term direction
4. Explain how the job can help you grow
5. End naturally

For "Do you have any questions for us?":
1. Ask about the role
2. Ask about learning/responsibilities
3. Ask about team/work environment
4. Avoid obvious questions
5. End politely

============================================================
IMPORTANT POINTS
============================================================

Give 4 to 6 short practical points.

- Speak naturally.
- Do not memorize word-by-word.
- Stay focused on the question.
- Use simple English.
- Avoid difficult vocabulary.
- Avoid corporate language.
- Do not give unnecessary personal information.
- Keep the answer around 45-60 seconds when appropriate.
- Be honest and realistic.

============================================================
SAMPLE ANSWER
============================================================

Write a natural spoken answer that a college student or fresher
could actually say in a real interview.

IMPORTANT:

The SAMPLE ANSWER must directly answer:
"{selected_question}"

Do not use the "Tell me about yourself" structure for other questions.

Only add name, education, project or career goal when relevant.

Use short and natural sentences.

The answer should sound like a real student speaking.

Do not make it textbook-like.

Do not make it corporate speech.

Do not use these phrases:
"add value to the organization"
"professional journey"
"dynamic environment"
"leverage my skills"
"contribute to the growth of the organization"

Do not invent personal information.

Do not invent college, degree, company, internship, project
or experience.

If personal information is unavailable, use a simple generic
example or explain what the student should mention.

Do not make a fresher sound like an experienced professional.

The answer should be realistic and easy to speak.

IMPORTANT LANGUAGE RULE:

HOW TO ANSWER:
→ Give explanation in Hinglish.

IMPORTANT POINTS:
→ Give explanation in Hinglish.

SAMPLE ANSWER:
→ Give the actual answer in simple natural English.

============================================================
FINAL CHECK
============================================================

Before answering, check:

1. Is HOW TO ANSWER specific to the selected question?
2. Does SAMPLE ANSWER directly answer the selected question?
3. Is the answer natural and easy to speak?
4. Was no personal information invented?
5. Was difficult/corporate language avoided?
6. Was a different structure used according to the question?

Do not add any extra sections.
"""


def hr_eval_prompt(selected_question, candidate_answer):
    return f"""
You are an experienced HR interviewer.

Interview Question:
{selected_question}

Candidate's Answer:
{candidate_answer}

Evaluate the candidate's answer as a real HR interviewer.

IMPORTANT:
Do not judge only grammar.

Evaluate:

1. Relevance
2. Completeness
3. Clarity
4. Natural speaking
5. Confidence of content
6. Whether the answer actually answers the question
7. Whether the answer is suitable for a college student/fresher

Use EXACTLY these sections:

============================================================
WHAT WAS GOOD
============================================================

Give 2-4 specific positive points.

============================================================
WHAT CAN BE IMPROVED
============================================================

Give 2-4 practical improvement points.

============================================================
BETTER WAY TO ANSWER
============================================================

Give a short improved version of the candidate's answer.

Keep the candidate's original meaning.
Do not invent personal information.

============================================================
SCORE
============================================================

Give a score out of 10.

Also give one short reason for the score.

IMPORTANT:

A simple but relevant and natural answer can get a good score.

A fluent answer that does not answer the question should get
a lower score.

Do not give a high score only because the English is grammatically
correct.

Keep the feedback useful for a college student.
Use simple language.
"""


def hr_mock_interview(hr):
    selected_question = hr["question"]
    hr["answer"] = None
    hr["feedback"] = None
    hr["error"] = None
    hr["info"] = None

    st.info("Get ready... You will have 5 seconds to prepare.")
    time.sleep(5)

    try:
        import sounddevice as sd

        duration = 60
        sample_rate = 16000

        st.success("🎤 SPEAK NOW — You have maximum 60 seconds. Recording started...")
        bar = st.progress(0)

        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16'
        )
        for sec in range(duration):
            time.sleep(1)
            bar.progress((sec + 1) / duration, text=f"Recording... {sec + 1}s / {duration}s")
        sd.wait()
        bar.empty()

        st.write("Recording finished.")

        audio_file = "hr_answer.wav"

        with wave.open(audio_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())

        # SPEECH TO TEXT
        with st.spinner("Converting your voice into text..."):
            import speech_recognition as sr

            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)

            try:
                candidate_answer = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                candidate_answer = ""
            except sr.RequestError as e:
                hr["info"] = f"Speech recognition service error: {e}"
                candidate_answer = ""

        # CHECK ANSWER
        if candidate_answer.strip() == "":
            hr["answer"] = ""
        else:
            hr["answer"] = candidate_answer
            try:
                with st.spinner("AI is evaluating your answer..."):
                    hr["feedback"] = ask_ai(hr_eval_prompt(selected_question, candidate_answer),
                                            "meta-llama/llama-3.2-3b-instruct")
            except Exception as e:
                hr["error"] = f"OPENROUTER ERROR: {e}"

        try:
            os.remove(audio_file)
        except Exception:
            pass

    except Exception as e:
        hr["error"] = (f"VOICE RECORDING ERROR: {e}\n\nCheck:\n1. Microphone permission\n"
                       f"2. sounddevice installation\n3. Microphone connection")


def page_interview():
    hero("🎤 HR Interview Practice", "AI guidance + voice mock interview")
    hr = st.session_state.hr

    selected_question = st.selectbox("Select question", HR_QUESTIONS)

    if st.button("Get HR Guidance 🤖"):
        hr.clear()
        hr["question"] = selected_question
        try:
            with st.spinner("AI guidance generate ho rahi hai..."):
                hr["guidance"] = ask_ai(hr_prompt(selected_question), "meta-llama/llama-3.2-3b-instruct")
        except Exception as e:
            hr["guidance_error"] = str(e)
        st.rerun()

    if hr.get("question"):
        st.markdown(f"### QUESTION\n**{hr['question']}**")
        if hr.get("guidance_error"):
            st.error(f"OPENROUTER ERROR\n\n{hr['guidance_error']}")
        if hr.get("guidance"):
            st.markdown("### HR GUIDANCE")
            st.markdown(hr["guidance"])

        st.markdown("---")
        st.markdown("### MOCK INTERVIEW")
        if st.button("Do you want to attempt this question? 🎙️ Start"):
            hr_mock_interview(hr)

        if hr.get("info"):
            st.warning(hr["info"])
        if hr.get("answer") == "":
            st.warning("COULD NOT UNDERSTAND — Your voice could not be converted into text. Please try again.")
        elif hr.get("answer"):
            st.markdown("### YOUR ANSWER")
            st.write(hr["answer"])
        if hr.get("feedback"):
            st.markdown("### AI INTERVIEW FEEDBACK")
            st.markdown(hr["feedback"])
        if hr.get("error"):
            st.error(hr["error"])


# ---------------------------------------------------------------------
# CODING PRACTICE
# ---------------------------------------------------------------------
CODING_FILES = {
    "Python": ("python_coding_questions.csv", "PYTHON"),
    "C": ("c_code.csv", "C"),
    "Java": ("java_code.csv", "JAVA"),
    "C++": ("cpp_code.csv", "CPP"),
}


def coding_load(lang):
    fname, _ = CODING_FILES[lang]
    qu = []
    with open(os.path.join(BASE_FOLDER, fname), "r", encoding="utf-8-sig", newline="") as f:
        read = csv.DictReader(f)
        for row in read:
            qu.append(row)
    st.session_state.code = {"lang": lang, "qu": qu, "q": None, "output": None,
                             "review": None, "n": 0, "done": False, "msg": None}
    coding_next()


def coding_next():
    cd = st.session_state.code
    cd["output"] = None
    cd["review"] = None
    cd["msg"] = None
    cd["n"] += 1
    if cd["qu"]:
        q = random.choice(cd["qu"])
        cd["qu"].remove(q)
        cd["q"] = q
    else:
        cd["q"] = None
        cd["done"] = True


def coding_run(cd, code):
    q = cd["q"]
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            output = result.stdout
            cd["output"] = ("ok", output if output else "(No output)")
        else:
            output = result.stderr
            cd["output"] = ("err", output)
    except subprocess.TimeoutExpired:
        output = "Program execution timed out."
        cd["output"] = ("err", output)
    except Exception as e:
        output = str(e)
        cd["output"] = ("err", f"Execution Error: {e}")

    evaluation_prompt = f"""
You are an AI code reviewer for a student coding practice system.

Language: Python

Question:
{q["question"]}

Example:
{q["example"]}

Student Code:
{code}

Program Output:
{output}

Review ONLY the student's code.

IMPORTANT RULES:
- Do NOT write another solution.
- Do NOT provide corrected code.
- Do NOT provide alternative code.
- Do NOT give a long explanation.
- Do NOT assume errors that are not present.
- If the code is correct, clearly say it is correct.
- Keep the review short and simple.

Use exactly this format:

Logic:
[1-2 short lines]

Error:
[Write "No error" if there is no error.]

Improvement:
[1 short line]

Score:
[X/10]
"""
    try:
        cd["review"] = ask_ai(evaluation_prompt, "meta-llama/llama-3.2-3b-instruct")
    except Exception as e:
        cd["review"] = f"AI Review Error: {e}"


def page_coding():
    hero("💻 Online Coding Practice & AI Code Reviewer", "Code likhiye, run kariye, AI se review lijiye")
    cd = st.session_state.code

    if cd is None:
        st.markdown("### SELECT PROGRAMMING LANGUAGE")
        lang = st.selectbox("Enter your choice", list(CODING_FILES.keys()))
        if st.button("Start Practice ▶️"):
            try:
                coding_load(lang)
                st.rerun()
            except Exception as e:
                st.error(f"Questions load nahi hue: {e}")
        return

    title = CODING_FILES[cd["lang"]][1]

    if cd["done"]:
        st.success(f"You have completed all {cd['lang']} questions!")
        if st.button("Exit Coding Practice"):
            st.session_state.code = None
            st.rerun()
        return

    q = cd["q"]
    st.markdown(f"### {title} CODING PRACTICE")
    st.markdown(f'<div class="qcard"><b>Q.</b> {q["question"]}<br><br><b>e.g.</b> {q["example"]}</div>',
                unsafe_allow_html=True)

    code = st.text_area("Write your code below.", height=260, key=f"code_{cd['n']}",
                        placeholder="# apna code yahan likhiye")

    if st.button("▶️ RUN CODE & AI REVIEW"):
        if not code.strip():
            cd["msg"] = "No code entered."
            cd["output"] = None
            cd["review"] = None
        else:
            cd["msg"] = None
            with st.spinner("RUNNING CODE..."):
                coding_run(cd, code)

    if cd["msg"]:
        st.warning(cd["msg"])
    if cd["output"]:
        kind, text = cd["output"]
        if kind == "ok":
            st.markdown("#### OUTPUT:")
            st.code(text)
        else:
            st.markdown("#### CODE ERROR:")
            st.code(text)
    if cd["review"]:
        st.markdown("#### 🤖 AI CODE REVIEW")
        st.info(cd["review"])

    st.markdown("---")
    st.markdown("#### WHAT DO YOU WANT TO DO?")
    c1, c2, _ = st.columns([1, 1, 3])
    if c1.button("1. Next Question ➡️"):
        coding_next()
        st.rerun()
    if c2.button("2. Exit Coding Practice"):
        st.session_state.code = None
        st.rerun()


# =====================================================================
# ADMIN
# =====================================================================
def admin_login():
    st.subheader("🛡️ Admin Login")
    with st.form("admin_login"):
        nv = st.text_input("ENTER YOUR NAME")
        pss = st.text_input("ENTER YOUR PASSWORD", type="password")
        go = st.form_submit_button("LOGIN")
    if go:
        sql = """
        SELECT * FROM Admin
        WHERE Name = %s AND set_pss = %s
        """
        cursor.execute(sql, (nv, pss))
        result = cursor.fetchone()
        if result:
            st.session_state.admin = nv
            st.rerun()
        else:
            st.error("INVALID.")


def admin_forgot():
    st.subheader("🔑 Lost your password?")
    st.info("SECURITY QUESTIONS")
    with st.form("admin_fp"):
        nv = st.text_input("ENTER YOUR NAME")
        p = st.text_input("WHAT IS YOUR SECURITY ANSWER")
        go = st.form_submit_button("Check Details")
    if go:
        sql = """
        SELECT * FROM Admin
        WHERE Name = %s AND secu_ans = %s
        """
        cursor.execute(sql, (nv, p))
        result = cursor.fetchone()
        if result:
            sql = """
            select Name, Email, set_pss from admin
            where name = %s
            """
            cursor.execute(sql, (nv,))
            ec = cursor.fetchall()
            st.markdown("### YOUR DETAIL IS")
            for row in ec:
                card(f"<b>Name</b> : {row[0]}<br><b>Email</b> : {row[1]}<br><b>Password</b> : {row[2]}")
        else:
            st.error("WRONG NAME OR SECURITY ANSWER.")


def admin_students():
    hero("👥 Student Records", "Saare registered students")
    cursor.execute("select * from students")
    ec = cursor.fetchall()

    def g(row, i):
        return row[i] if i < len(row) else ""

    df = pd.DataFrame([{
        "Student Id": g(r, 0), "Name": g(r, 1), "Email": g(r, 2), "Password": g(r, 3),
        "Roll Number": g(r, 4), "College Name": g(r, 5), "Course": g(r, 6),
        "Security Answer": g(r, 7), "Subject": g(r, 8), "Branch": g(r, 10),
    } for r in ec])
    st.metric("Total Students", len(df))
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("### 🗑️ Delete Student")
    student_id = st.number_input("Enter Student ID to delete", min_value=0, step=1)
    if st.button("Delete Student"):
        cursor.execute("DELETE FROM students WHERE student_id = %s", (int(student_id),))
        con.commit()
        if cursor.rowcount > 0:
            st.success("Student Deleted Successfully!")
        else:
            st.error("Student ID Not Found!")


def admin_results():
    hero("📈 Students Result Record", "Saare students ke results")
    cursor.execute("select * from result")
    ec = cursor.fetchall()
    df = pd.DataFrame([{
        "Result ID": r[0], "Student ID": r[1], "Name": r[9], "Subject": r[2],
        "Total Questions": r[3], "Score": r[4], "Percentage": r[5],
        "Time Taken": r[6], "Status": r[7], "Medium": r[8],
    } for r in ec])
    st.metric("Total Results", len(df))
    st.dataframe(df, use_container_width=True, hide_index=True)


def admin_add_announcement():
    hero("➕ Add Announcement", "Students ke liye nayi announcement")
    with st.form("add_ann"):
        title = st.text_input("ENTER ANNOUNCEMENT TITLE")
        message = st.text_area("ENTER ANNOUNCEMENT MESSAGE")
        date = st.text_input("ENTER ANNOUNCEMENT DATE")
        go = st.form_submit_button("Add Announcement")
    if go:
        sql = """
        insert into announce
        (title, message, announce_date)
        values(%s, %s, %s)
        """
        cursor.execute(sql, (title, message, date))
        con.commit()
        st.success("ANNOUNCEMENT ADDED SUCCESSFULLY.")


def admin_view_announcement():
    hero("📢 View Announcement", "Manage announcements")
    cursor.execute("select * from announce")
    ac = cursor.fetchall()
    if ac:
        for row in ac:
            card(f"<h4>{row[1]}</h4>{row[2]}<br><small>Announcement ID: {row[0]} &nbsp;|&nbsp; "
                 f"Date: {row[3]} &nbsp;|&nbsp; Status: {row[4]}</small>")

        ch = st.radio("Action", ["DELETE ANNOUNCEMENT", "INACTIVE ANNOUNCEMENT",
                                 "ACTIVE ANNOUNCEMENT"], horizontal=True)
        ann_id = st.number_input("ENTER ANNOUNCEMENT ID", min_value=0, step=1)
        if st.button("Apply"):
            ann_id = int(ann_id)
            if ch == "DELETE ANNOUNCEMENT":
                cursor.execute("DELETE FROM announce where ann_id = %s", (ann_id,))
                con.commit()
                if cursor.rowcount > 0:
                    st.success("DELETED SUCCESSFULLY.")
                else:
                    st.error("ID NOT FOUND !!!")
            elif ch == "INACTIVE ANNOUNCEMENT":
                cursor.execute("update announce SET status = 'INACTIVE' where ann_id =%s", (ann_id,))
                con.commit()
                if cursor.rowcount > 0:
                    st.success("ANNOUNCEMENT IS INACTIVE.")
                else:
                    st.error("ID NOT FOUND")
            else:
                cursor.execute("update announce SET status = 'ACTIVE' where ann_id =%s", (ann_id,))
                con.commit()
                if cursor.rowcount > 0:
                    st.success("ANNOUNCEMENT IS ACTIVE.")
                else:
                    st.error("ID NOT FOUND")
    else:
        st.info("NO ANNOUCEMENTS.")


def admin_feedback():
    hero("💬 All Feedback", "Students ka feedback")
    cursor.execute("select * from feedback")
    z = cursor.fetchall()
    if z:
        for row in z:
            card(f"<h4>{row[2]}</h4>{row[3]}<br><small>Feedback ID: {row[0]} &nbsp;|&nbsp; "
                 f"Student ID: {row[1]}</small>")
    else:
        st.info("Abhi koi feedback nahi hai.")


# =====================================================================
# MAIN ROUTER
# =====================================================================
STUDENT_MENU = {
    "1. 👤 Your Detail": page_detail,
    "2. 📊 Check Result": page_result,
    "3. 📚 Course List": page_courses,
    "4. 🏅 Check Certificate": page_certificates,
    "5. 🎥 Learn (Videos & PDFs)": page_learn,
    "6. 📝 Give Quiz": page_quiz,
    "7. 📢 Announcements": page_announcements,
    "8. 💬 Feedback": page_feedback,
    "9. 🎤 Interview Practice": page_interview,
    "10. 💻 Coding Practice": page_coding,
    "11. 🚪 Exit": None,
}

ADMIN_MENU = {
    "1. 👥 Check Student Data": admin_students,
    "2. 📈 Check Results": admin_results,
    "3. ➕ Add Announcement": admin_add_announcement,
    "4. 📢 View Announcement": admin_view_announcement,
    "5. 💬 Show all feedback": admin_feedback,
    "6. 🚪 Exit": None,
}


def main():
    # ---------------- STUDENT LOGGED IN ----------------
    if st.session_state.student is not None:
        with st.sidebar:
            st.markdown('<div class="brand">🎓 Smart E-Learning<span>Learn • Quiz • Get Certified</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="welcome">👋 Welcome, {st.session_state.student[1]}</div>', unsafe_allow_html=True)
            choice = st.radio("Menu", list(STUDENT_MENU.keys()), label_visibility="collapsed")
        if STUDENT_MENU[choice] is None:
            logout()
            st.rerun()
        STUDENT_MENU[choice]()
        return

    # ---------------- ADMIN LOGGED IN ----------------
    if st.session_state.admin is not None:
        with st.sidebar:
            st.markdown('<div class="brand">🛡️ Admin Panel<span>Smart E-Learning</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="welcome">👋 Welcome, {st.session_state.admin}</div>', unsafe_allow_html=True)
            choice = st.radio("Menu", list(ADMIN_MENU.keys()), label_visibility="collapsed")
        if ADMIN_MENU[choice] is None:
            st.info("Exiting Admin Panel...")
            logout()
            st.rerun()
        ADMIN_MENU[choice]()
        return

    # ---------------- NOT LOGGED IN ----------------
    with st.sidebar:
        st.markdown('<div class="brand">🎓 Smart E-Learning<span>Learn • Quiz • Get Certified</span></div>', unsafe_allow_html=True)
        role = st.radio("Login as", ["STUDENT", "ADMIN"])

    hero("🎓 SMART E-LEARNING & QUIZ SYSTEM",
         "Learn • Practice • Quiz • Get Certified")
    st.markdown(
        '<div class="chips"><span class="chip">📚 Video & PDF Notes</span>'
        '<span class="chip">📝 Timed Quizzes</span><span class="chip">🏅 Instant Certificates</span>'
        '<span class="chip">🎤 HR Interview Practice</span><span class="chip">💻 AI Code Review</span></div>',
        unsafe_allow_html=True)

    if role == "STUDENT":
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "🔑 Forgot Password"])
        with tab1:
            student_login()
        with tab2:
            student_register()
        with tab3:
            student_forgot()
    else:
        tab1, tab2 = st.tabs(["🔐 Login", "🔑 Forgot Password"])
        with tab1:
            admin_login()
        with tab2:
            admin_forgot()


main()