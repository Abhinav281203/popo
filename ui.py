import streamlit as st
import requests
import time
import pandas as pd
import json
from streamlit_autorefresh import st_autorefresh

URL ="http://localhost:8000"

import requests
import streamlit as st

def upload_pdfs(files, email, num_questions):
    file_payload = [
        ("files", (file.name, file.getvalue(), file.type))
        for file in files
    ]

    try:
        response = requests.post(
            f"{URL}/upload", 
            files=file_payload,
            data={
                'email': email,
                'num_questions': num_questions
            }
        )

        if response.status_code != 200:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None

        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None


def get_task_status(task_id):
    try:
        response = requests.get(f"{URL}/status/{task_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "Error while getting task status"}
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

def main():
    st.title("PDF Question Generator")
    
    # Sidebar for configuration
    st.sidebar.header("Processing Configuration")
    email = st.sidebar.text_input("Your Email")
    num_questions = st.sidebar.number_input("Number of Questions", min_value=1, max_value=20, value=5)
    
    # File uploader
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if st.button("Process PDFs") and uploaded_files and email:
        with st.spinner('Uploading and Processing PDFs...'):
            task_results = upload_pdfs(uploaded_files, email, num_questions)

            if "files_metadata" not in st.session_state:
                st.session_state.files_metadata = task_results["process_metadata"]
                st.rerun()


    if "files_metadata" in st.session_state:
        count = st_autorefresh(interval=3000, limit=None, key="auto-refresh")
        st.write("Task Status:")
        for file_metadata in st.session_state.files_metadata:
            task_id = file_metadata["task_id"]
            status = get_task_status(task_id)
            st.write(f"PDF Name: {file_metadata["filename"]}")
            st.write(f"Status: {status["status"]}")
            


if __name__ == "__main__":
    main()