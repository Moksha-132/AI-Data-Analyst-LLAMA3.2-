import streamlit as st
import sqlite3
from passlib.hash import bcrypt
from .db import get_connection


def create_user(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    password_hash = bcrypt.hash(password)
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # Username already exists
        success = False
    finally:
        conn.close()
    return success


def signup_page():
    st.title("📝 Sign Up")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    password_confirm = st.text_input("Confirm password", type="password")
    if st.button("Sign Up"):
        if not username or not password:
            st.error("Username and password cannot be empty.")
        elif password != password_confirm:
            st.error("Passwords do not match.")
        else:
            if create_user(username, password):
                st.success("Account created successfully. You can now log in.")
                st.experimental_rerun()
            else:
                st.error("Username already taken. Please choose another.")
