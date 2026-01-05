import streamlit as st
import sqlite3
from passlib.hash import bcrypt
from .db import get_connection


def verify_user(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        stored_hash = row[0]
        return bcrypt.verify(password, stored_hash)
    return False


def login_page():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not username or not password:
            st.error("Please provide both username and password.")
        elif verify_user(username, password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.success(f"Logged in as {username}")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials. Please try again.")
