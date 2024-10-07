import easyocr
import cv2
import streamlit as st
import time
import os
from datetime import datetime
import numpy as np
from PIL import Image

st.set_page_config(
    page_title="Text Reader",
    page_icon="📷", 
    layout="centered",
    initial_sidebar_state="expanded"
)

def image_to_text(image_path):
    # Initialize the EasyOCR reader
    reader = easyocr.Reader(['en'])
    
    # Perform OCR on the image
    result = reader.readtext(image_path, detail=0)
    
    # Join the result text into a single string
    text = ' '.join(result)
    
    return text

from gtts import gTTS
from playsound import playsound

def text_to_speech(text, audio_file_path):
    # Convert text to speech
    tts = gTTS(text=text, lang='en')
    
    # Save the speech to a file
    tts.save(audio_file_path)
    
    # Play the audio in the background without opening a file system window
    playsound(audio_file_path)

# Create directories for storing images and audio
os.makedirs('captured_images', exist_ok=True)
os.makedirs('captions', exist_ok=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page", ("Home", "History"))

if page == "Home":
    # Image Captioning
    st.subheader("Upload to get real-time Text")
    uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        
        st.image(img, caption="Uploaded Image", use_column_width=True)

        # Save the uploaded image temporarily
        image_path = f"captured_images/temp_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(image_path)

        try:
            # Extract text from the uploaded image using OCR
            extracted_text = image_to_text(image_path)
            st.write("Extracted Text:", extracted_text)

            # Generate audio from the extracted text
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_file_path = f"captions/caption_{timestamp}.mp3"
            text_to_speech(extracted_text, audio_file_path)

            #st.success("Audio generated and saved successfully.")
            # Audio is saved but not played or displayed in the Home page

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload an image file.")

elif page == "History":
    st.title("Audio History")

    # List audio files in the 'captions' folder
    captions_folder = 'captions'
    audio_files = [f for f in os.listdir(captions_folder) if f.endswith('.mp3')]
    audio_files.sort(key=lambda x: os.path.getmtime(os.path.join(captions_folder, x)), reverse=True)  # Sort by modification time

    # Display audio files with play buttons and timestamps
    st.write("Generated Audio Files:")
    if audio_files:
        for audio_file in audio_files:
            audio_path = os.path.join(captions_folder, audio_file)
            # Get the modification time and format it
            mod_time = os.path.getmtime(audio_path)
            timestamp = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

            # Create two columns: one for audio, one for timestamp
            col1, col2 = st.columns([3, 1])  # Create two columns

            with col1:
                st.audio(audio_path, format="audio/mp3")  # Display audio player
            
            with col2:
                st.write(timestamp)  # Display the timestamp
    else:
        st.write("No audio files available in history.")
