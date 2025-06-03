import streamlit as st

# Home page
st.title("Reef Check Slate Analyser")

# Add a coral reef image
st.image("https://www.andbeyond.com/wp-content/uploads/sites/5/5-surprising-facts-about-coral-reefs.jpg", caption="Coral Reefs")

if not st.experimental_user.is_logged_in:
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
else:
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
        st.stop()