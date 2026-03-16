import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from PIL import Image
import os
import openai

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Royal Cambridge School",
    page_icon="logo.png",
    layout="wide"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
.stApp{
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color:white;
}

h1,h2,h3,h4{
    text-align:center;
}

.stButton>button{
    background:#FFD700;
    color:black;
    border-radius:10px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("school.db", check_same_thread=False)
c = conn.cursor()

# Users table
c.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
password TEXT,
role TEXT
)""")

# Notices table
c.execute("""CREATE TABLE IF NOT EXISTS notices(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
message TEXT,
date TEXT
)""")

conn.commit()

# ---------------- HEADER ----------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=120)
except:
    st.warning("Logo not found")

st.markdown("""
<h1>Royal Cambridge School</h1>
<h4>Ari Syedan, Islamabad</h4>
""", unsafe_allow_html=True)

st.info("Welcome to the Royal Cambridge School Smart Portal 🤖")

# ---------------- SIDEBAR MENU ----------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["Home","Login","Signup","AI Tutor","Homework","Notices","Timetable","Attendance","Gallery","Contact"]
)

# ---------------- HOME ----------------
if menu == "Home":
    st.title("School Smart Portal")
    st.write("""
This portal helps students, parents and teachers stay connected.

Features:
• AI Study Assistant  
• Homework updates  
• School notices  
• Attendance tracking  
• Timetable  
• School gallery
""")

# ---------------- SIGNUP ----------------
elif menu == "Signup":
    st.subheader("Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role",["Student","Parent","Teacher"])

    if st.button("Signup"):
        if name and email and password:
            c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
            (name,email,password,role))
            conn.commit()
            st.success("Account created successfully!")
        else:
            st.warning("Please fill all fields.")

# ---------------- LOGIN ----------------
elif menu == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password",type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE email=? AND password=?",(email,password))
        user = c.fetchone()
        if user:
            st.success("Login successful!")
            st.write("Welcome:", user[1])
            st.write("Role:", user[4])
        else:
            st.error("Invalid credentials")

# ---------------- AI TUTOR ----------------
elif menu == "AI Tutor":
    st.subheader("AI Study Assistant")
    question = st.text_input("Ask a study question")

    if st.button("Ask AI"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                openai.api_key = st.secrets["openai"]["api_key"]

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role":"user","content":question}]
                )
                answer = response.choices[0].message.content
                st.success(answer)
            except Exception as e:
                st.error(f"AI service not available. Check API key. ({e})")

# ---------------- HOMEWORK ----------------
elif menu == "Homework":
    st.subheader("Homework Section")
    uploaded_file = st.file_uploader("Upload Homework")
    if uploaded_file:
        with open(os.path.join("uploads", uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Homework uploaded successfully")

# ---------------- NOTICES ----------------
elif menu == "Notices":
    st.subheader("School Notices")
    title = st.text_input("Notice Title")
    message = st.text_area("Notice Message")

    if st.button("Post Notice"):
        if title and message:
            c.execute("INSERT INTO notices(title,message,date) VALUES(?,?,?)",
            (title,message,str(datetime.now())))
            conn.commit()
            st.success("Notice Posted")
        else:
            st.warning("Please fill title and message.")

    st.markdown("---")
    st.subheader("All Notices")
    c.execute("SELECT title,message,date FROM notices ORDER BY id DESC")
    notices = c.fetchall()
    for n in notices:
        st.warning("📢 " + n[0])
        st.write(n[1])
        st.caption(n[2])

# ---------------- TIMETABLE ----------------
elif menu == "Timetable":
    st.subheader("School Timetable")
    data = {
        "Day":["Monday","Tuesday","Wednesday","Thursday","Friday"],
        "Period 1":["Math","English","Science","Math","Computer"],
        "Period 2":["Urdu","Math","English","Science","Math"],
        "Period 3":["Science","Urdu","Math","English","Islamiat"]
    }
    st.table(data)

# ---------------- ATTENDANCE ----------------
elif menu == "Attendance":
    st.subheader("Attendance Chart")
    data = pd.DataFrame({
        "Month":["Jan","Feb","Mar","Apr","May"],
        "Attendance":[90,85,92,88,95]
    })
    st.line_chart(data.set_index("Month"))

# ---------------- GALLERY ----------------
elif menu == "Gallery":
    st.subheader("School Gallery")
    cols = st.columns(3)
    images = ["school1.jpg","school2.jpg","school3.jpg"]
    for col,img in zip(cols,images):
        try:
            col.image(img)
        except:
            col.warning(f"{img} not found")

# ---------------- CONTACT ----------------
elif menu == "Contact":
    st.subheader("Contact Royal Cambridge School")
    st.write("📍 Ari Syedan, Islamabad")
    st.write("📞 +92-300-XXXXXXX")
    st.write("✉ royalcambridge@gmail.com")
