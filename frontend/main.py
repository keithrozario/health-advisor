import streamlit as st
import boto3
import random
import time

from util import get_answers

s3 = boto3.client('s3')

st.title("HealthCare.AI")
# uploaded_file = st.file_uploader("Upload your Medical Report")

# if uploaded_file is not None:
#     s3.upload_fileobj(uploaded_file, 'uploaded-documents-unicorn-gym-16122024', 'uploaded')
#     st.success("File uploaded successfully!")

# Streamed response emulator
def response_generator(prompt: str):
    response=get_answers(prompt)
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
        response, source_doc = response_generator(prompt)
        full_response = f"{response}\n\n{source_doc}"
        response = st.write(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
