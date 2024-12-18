import streamlit as st
import boto3
import uuid

from util import get_agent_response

st.title("HealthCare.AI")

# Set Unique Session ID
session_id = uuid.uuid4().__str__()

# Streamed response emulator
def response_generator(prompt: str):
    response=get_agent_response(prompt, session_id)
    return response

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = get_agent_response(prompt, session_id)
        st.write(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
