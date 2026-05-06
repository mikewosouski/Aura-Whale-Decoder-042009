import streamlit as st
import pandas as pd
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import scipy.signal as signal
import requests
import base64

# 1. Page Configuration
st.set_page_config(page_title="Aura Global Research", layout="wide")

# Connection Info (Pulled from your Secrets)
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"] 
BRANCH = "main"

# 2. Security Wall
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Enter Research Password", type="password", key="password")
        st.button("Log In", on_click=lambda: st.session_state.update(
            {"password_correct": st.session_state.password == st.secrets["RESEARCH_PASS"]}))
        return False
    return st.session_state["password_correct"]

# 3. Permanent Save Function
def save_to_github(uploaded_file):
    url = f"https://api.github.com/repos/{REPO}/contents/research_data/{uploaded_file.name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Check if file exists
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
        return "✅ Success! Added to the Global Archive."
    else:
        return f"❌ Sync failed: {put_res.json().get('message')}"

if check_password():
    st.title("🐋 Aura Community Research Archive")
    st.markdown("---")

    # 4. Upload Section
    col_up, col_info = st.columns([1, 1])
    with col_up:
        st.subheader("⬆️ Contribute Data")
        uploaded_file = st.file_uploader("Upload audio (WAV/MP3)", type=["wav", "mp3"])
        if uploaded_file:
            if st.button("🚀 Sync to Global Database"):
                with st.spinner("Linking to the universal fabric..."):
                    msg = save_to_github(uploaded_file)
                    st.success(msg)

    with col_info:
        st.info("**Archive Protocol:**\n- Files store permanently in GitHub.\n- Viewable by the research collective.")

    st.divider()

    # 5. Shared Library & Visualization
    st.subheader("🌐 Shared Research Library")
    list_url = f"https://api.github.com/repos/{REPO}/contents/research_data"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    files_res = requests.get(list_url, headers=headers)
    
    if files_res.status_code == 200:
        file_list = [f['name'] for f in files_res.json() if f['name'].endswith(('.wav', '.mp3'))]
        
        if not file_list:
            st.warning("Archive is currently empty.")
        else:
            selected_file = st.selectbox("Select a file for frequency analysis:", ["-- Choose a File --"] + file_list)

            if selected_file != "-- Choose a File --":
                raw_url = next(f['download_url'] for f in files_res.json() if f['name'] == selected_file)
                
                with st.spinner("Decoding shared frequencies..."):
                    # Download and load audio
                    y, sr = librosa.load(raw_url, sr=None)
                    
                    # Math for Click Detection (Standard Deviation analysis)
                    peaks, _ = signal.find_peaks(y, height=np.mean(y) + (np.std(y) * 2))

                    # Display Graphs
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**Acoustic Waveform**")
                        fig, ax = plt.subplots()
                        librosa.display.waveshow(y, sr=sr, ax=ax, color="#4F8BFF")
                        st.pyplot(fig)
                        
                    with c2:
                        st.write("**Frequency Spectrogram**")
                        fig, ax = plt.subplots()
                        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
                        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', ax=ax)
                        st.pyplot(fig)
                    
                    st.metric("Detected Acoustic Events", len(peaks))
                    st.audio(raw_url)
    else:
        st.error("Database connection issue. Check your folder permissions.")

else:
    st.warning("Access Restricted. Please log in to view the fabric of the ocean")
