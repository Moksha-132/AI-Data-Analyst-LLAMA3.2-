import streamlit as st
import os

# Path to the generated hero image (adjust if location changes)
IMAGE_PATH = os.path.join(os.getenv('USERPROFILE'), '.gemini', 'antigravity', 'brain', '2c0b803e-2d5d-47ab-aa53-50c88cfc35b2', 'home_hero_1767537700912.png')

def home_page():
    """Render the attractive home landing page."""
    st.title("AI Data Insight Generator (Offline Explainable Analytics)")
    st.subheader("Analyze Your Data Offline")
    # Display hero image if it exists
    if os.path.exists(IMAGE_PATH):
        st.image(IMAGE_PATH, use_column_width=True)
    else:
        st.info("Hero image not found.")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            st.session_state['navigate'] = "Login"
    with col2:
        if st.button("Sign Up"):
            st.session_state['navigate'] = "Sign Up"
    st.markdown(
        """
        <div style='text-align: center; margin-top: 2rem;'>
            <p>Empower your data decisions with offline AI-driven insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
