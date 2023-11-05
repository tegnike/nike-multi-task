import streamlit as st
import requests
from urllib.parse import quote

st.title("Text to Speech Converter")

mode = st.radio("Choose a mode", ["Text to Speech", "Sort JSON", "Process JSON"])

if mode == "Text to Speech":
    uploaded_file = st.file_uploader("Upload your text file", type=["txt"])

    type_options = ["google", "elevenlabs", "voicevox"]
    selected_type = st.selectbox("Choose a type:", type_options)

    if uploaded_file:
        if st.button("Upload"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            data = {"type": selected_type}

            response = requests.post("http://fastapi:8000/upload/", files=files, data=data)

            if response.status_code == 200:
                filename = response.json()["filename"]
                encoded_filename = quote(filename)  # ファイル名をURLエンコード
                download_link = f"http://localhost:8020/download/?filename={encoded_filename}"
                st.write(f"[Download the WAV file]({download_link})")
            elif "application/json" in response.headers.get("Content-Type", ""):
                st.error(response.json()["detail"])
            else:
                st.error(f"{response.status_code} error occurred.")
elif mode == "Sort JSON":
    uploaded_json = st.file_uploader("Upload your JSON file", type=["json"])
    if uploaded_json:
        if st.button("Sort and Save"):
            files = {"file": (uploaded_json.name, uploaded_json.getvalue())}
            response = requests.post("http://fastapi:8000/json_sort/", files=files)

            if response.status_code == 200:
                filename = response.json()["filename"]
                encoded_filename = quote(filename)  # ファイル名をURLエンコード
                download_link = f"http://localhost:8020/download/?filename={encoded_filename}"
                st.write(f"[Download the sorted JSON file]({download_link})")
            elif "application/json" in response.headers.get("Content-Type", ""):
                st.error(response.json()["detail"])
            else:
                st.error(f"{response.status_code} error occurred.")

else:
    json_file = st.file_uploader("Upload your JSON file", type=["json"])

    if json_file:
        if st.button("Process JSON"):
            files = {"file": (json_file.name, json_file.getvalue())}
            response = requests.post("http://fastapi:8000/process-json/", files=files)

            if response.status_code == 200:
                filename = response.json()["filename"]
                encoded_filename = quote(filename)
                download_link = f"http://localhost:8020/download/?filename={encoded_filename}"
                st.write(f"[Download the Processed JSON file]({download_link})")
            elif "application/json" in response.headers.get("Content-Type", ""):
                st.error(response.json()["detail"])
            else:
                st.error(f"{response.status_code} error occurred.")