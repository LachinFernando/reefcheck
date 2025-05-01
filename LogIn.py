import pandas as pd
import streamlit as st

from reef_check import reef_analyser


IMAGE_ADDRESS = "https://www.andbeyond.com/wp-content/uploads/sites/5/5-surprising-facts-about-coral-reefs.jpg"

# web app
st.title("Reef Check Slate Analyser")

st.image(IMAGE_ADDRESS, caption = "Coral Reefs")

if not st.experimental_user.is_logged_in:
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
else:
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
        st.stop()
    # call the application
    reef_analyser()