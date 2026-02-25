import requests
import streamlit as st

from uuid import uuid4

st.set_page_config(
    page_title="Prestashop Shopping Assistant",
    layout="centered",
)


st.markdown("# Prestashop Shopping Assistant 🤖🛒", unsafe_allow_html=True)

if user_query := st.chat_input("Ask something"):
    st.chat_message("user").markdown(user_query)

    response = requests.post(
        "http://localhost:8000/invoke",
        json={
            "message": user_query,
            "session_id": str(uuid4()),
            "user_id": "Lorenzo"
        }
    ).json()

    with st.chat_message("assistant"):
        st.write(response.get("response"))