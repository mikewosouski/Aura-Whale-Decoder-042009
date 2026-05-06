import streamlit as st
import pandas as pd
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import scipy.signal as signal

# Set up the page
st.set_page_config(page_title="Aura Research Database", layout="wide")

# Initialize the Research Memory (Session State)
if "research_history" not in st.session_state:
    st.session_state.research_history = {} # Stores {Filename: {y: data, sr: rate, events: count}}

# 1. Security Logic
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Enter Research Password", type="password", key="password")
        st.button("Log In", on_click=lambda: st.session_state.update(
            {"password_correct": st.session_state.password == st.secrets["RESEARCH_PASS"]}))
        return False
    return st.session_state["password_correct"]

if check_password():
    st.title("🐋 Aura Whale Research Database")

    # 2. Upload Section
    with st.expander("⬆️ Upload New Data", expanded=True):
        uploaded_files = st.file_uploader("Drop new audio files here", type=["wav", "mp3"], accept_multiple_files=True)
        
        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.research_history:
                    with st.spinner(f"Decoding {file.name}..."):
                        y, sr = librosa.load(file, sr=None)
                        peaks, _ = signal.find_peaks(y, height=np.mean(y) + (np.std(y) * 2))
                        
                        # Save everything into memory
                        st.session_state.research_history[file.name] = {
                            "y": y,
                            "sr": sr,
                            "events": len(peaks),
                            "duration": round(librosa.get_duration(y=y, sr=sr), 2),
                            "file_obj": file
                        }
            st.success("All files processed and added to history!")

    # 3. The History Table (The "Master Sheet")
    if st.session_state.research_history:
        st.subheader("📊 Research Results Log")
        
        # Create a clean table from our memory
        history_data = [
            {"File Name": name, "Events": data["events"], "Length (s)": data["duration"]}
            for name, data in st.session_state.research_history.items()
        ]
        st.table(pd.DataFrame(history_data))

        # 4. VIEW PREVIOUS TESTS (The Back-and-Forth Section)
        st.divider()
        st.subheader("🔍 Detailed Archive View")
        
        # Dropdown to pick ANY file we've ever uploaded in this session
        selected_file = st.selectbox(
            "Select a file from your history to view its graphs:", 
            options=list(st.session_state.research_history.keys())
        )

        if selected_file:
            data = st.session_state.research_history[selected_file]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Analysis for:** {selected_file}")
                fig, ax = plt.subplots()
                librosa.display.waveshow(data["y"], sr=data["sr"], ax=ax)
                st.pyplot(fig)
            
            with col2:
                st.write(f"**Detected Events:** {data['events']}")
                fig, ax = plt.subplots()
                D = librosa.amplitude_to_db(np.abs(librosa.stft(data["y"])), ref=np.max)
                librosa.display.specshow(D, sr=data["sr"], x_axis='time', y_axis='hz', ax=ax)
                st.pyplot(fig)

            st.audio(data["file_obj"])
    else:
        st.info("No data in history. Please upload a file to begin.")

else:
    st.warning("Please enter the password to access the research tools.")

