import streamlit as st
import pandas as pd
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import scipy.signal as signal
import requests
import base64

# 1. Page Config
st.set_page_config(page_title="Aura Global Research", layout="wide")

# Connection Info (Pulled from your Secrets)
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]  # Should be: mikewososouski/Aura-Whale-Decoder-042009
BRANCH = "main"

# 2. Security Wall
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Enter Research Password", type="password", key="password")
        st.button("Log In", on_click=lambda: st.session_state.update(
            {"password_correct": st.session_state.password == st.secrets["RESEARCH_PASS"]}))
        return False
    return st.session_state["password_correct"]

# 3. Permanent Save Function (Community Archive)
def save_to_github(uploaded_file):
    # This path targets the research_data folder you created
    url = f"https://api.github.com/repos/{REPO}/contents/research_data/{uploaded_file.name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Check if file exists to prevent overwriting
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return "⚠️ This recording is already in the archive."

    content = base64.b64encode(uploaded_file.getvalue()).decode()
    data = {
        "message": f"New Community Contribution: {uploaded_file.name}",
        "content": content,
        "branch": BRANCH
    }
    
    put_res = requests.put(url, json=data, headers=headers)
    if put_res.status_code == 201:
        return "✅ Success! Added to the Global Archive for all researchers."
    else:
        return f"❌ Sync failed: {put_res.json().get('message')}"

if check_password():
    st.title("🐋 Aura Community Research Archive")
    st.markdown("---")

    # 4. Global Contribution Section
    col_up, col_info = st.columns([1, 1])
    with col_up:
        st.subheader("⬆️ Contribute Data")
        uploaded_file = st.file_uploader("Upload audio to save permanently", type=["wav", "mp3"])
        if uploaded_file:
            if st.button("🚀 Sync to Global Database"):
                with st.spinner("Linking to the universal fabric..."):
                    msg = save_to_github(uploaded_file)
                    st.success(msg)

    with col_info:
        st.info("**Archive Protocol:**\n- Files are stored permanently in the GitHub repo.\n- Visible to anyone with access to this dashboard.\n- Please ensure high-quality audio for accurate click detection.")

    st.divider()

    # 5. Shared Library View (DEBUG VERSION)
    st.subheader("🌐 Shared Research Library")
    list_url = f"https://api.github.com/repos/{REPO}/contents/research_data"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Try to fetch the folder
    files_res = requests.get(list_url, headers=headers)
    
    if files_res.status_code == 200:
        file_list = [f['name'] for f in files_res.json() if f['name'].endswith(('.wav', '.mp3'))]
        
        if not file_list:
            st.warning("The 'research_data' folder exists, but it's empty!")
        else:
            selected_file = st.selectbox("Choose a file:", ["-- Select --"] + file_list)
            if selected_file != "-- Select --":
                raw_url = next(f['download_url'] for f in files_res.json() if f['name'] == selected_file)
                st.audio(raw_url)
    else:
        # This part will reveal the actual secret error
        st.error(f"⚠️ Connection Error: {files_res.status_code}")
        st.write(f"GitHub Message: {files_res.json().get('message')}")
        st.info(f"Checking Repo Path: {REPO}")
