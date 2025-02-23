import streamlit as st
import sys
import requests
import time

from loguru import logger


st.set_page_config(
    page_title="Survey Analysis Agent",
    page_icon="📊",
)

st.markdown(
    """
    <h1 style='text-align: center;'>Survey Analysis Agent</h1>
    <p style='text-align: center;'>This agent will provide answers based on documents from ConocoPhillips, the AIM Presentation 2023 and the Proxy Statement 2024.</p>
    """,
    unsafe_allow_html=True
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if query := st.chat_input("Enter your query here"):
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Send query to backend
    response = requests.post("http://localhost:8000/survey", json={"query": query})
    response = response.json()
    
    # add emoji in spinner
    with st.spinner(""):
        time.sleep(2)    
        st.chat_message("ai").markdown(response['answer'])
        st.session_state.messages.append({"role": "assistant", "content": response['answer']})
        
    


