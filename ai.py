import streamlit as st
from googletrans import Translator, LANGUAGES
import gtts
from io import BytesIO
from pydub import AudioSegment
import speech_recognition as sr

# Inject CSS for styling and animation
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #1E2A38, #FF4B4B);
        animation: gradientBG 10s ease infinite;
        background-size: 400% 400%;
        color: #FAFAFA;
        font-family: 'Arial', sans-serif;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;} 
    }
    .stApp {
        color: #FAFAFA;
        font-family: 'Arial', sans-serif;
    }
    .stTextArea, .stSelectbox {
        font-size: 1.1em;
    }
    .stButton > button {
        background-color: #FF4B4B;
        color: white;
        border: None;
        border-radius: 8px;
        padding: 8px 16px;
        transition: transform 0.3s, box-shadow 0.3s;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
    }
    .stButton > button:hover {
        background-color: #E33E3E;
        transform: scale(1.1);
        box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.3);
    }
    .stTitle {
        color: #FF4B4B;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
    }
    .audio-player {
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .audio-player:hover {
        background-color: #FF4B4B;
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Set up the translator
translator = Translator()

# Streamlit App
st.title("SMF Translater AI")
st.write("**Effortlessly translate text or voice input into any language of your choice! Enjoy a seamless experience with our visually captivating app.**")

# Input Section
st.sidebar.header("🔧 Settings")
input_mode = st.sidebar.radio("Select input mode:", ("Text", "Voice"))

if input_mode == "Text":
    st.subheader("📝 Enter Text for Translation")
    input_text = st.text_area("Type or paste your text below:", height=150)
elif input_mode == "Voice":
    st.subheader("🎙️ Upload Your Audio File")
    uploaded_audio = st.file_uploader("Upload an audio file (in WAV format):", type=["wav"])
    if uploaded_audio:
        # Convert audio to text
        audio = AudioSegment.from_file(uploaded_audio, format="wav")
        recognizer = sr.Recognizer()
        with BytesIO() as audio_buffer:
            audio.export(audio_buffer, format="wav")
            audio_buffer.seek(0)
            with sr.AudioFile(audio_buffer) as source:
                audio_data = recognizer.record(source)
                try:
                    input_text = recognizer.recognize_google(audio_data)
                    st.success(f"**Recognized Text:** {input_text}")
                except sr.UnknownValueError:
                    st.error("Could not understand the audio.")
                    input_text = ""
                except sr.RequestError as e:
                    st.error(f"Speech Recognition error: {e}")
                    input_text = ""
    else:
        input_text = ""

# Ensure input_text is never None
if input_text is None:
    input_text = ""

# Select the source language
st.sidebar.subheader("🌐 Language Options")
source_language = st.sidebar.selectbox(
    "Source Language:",
    ["Auto Detect"] + list(LANGUAGES.values()),
    index=0
)

# Select the target language
target_language = st.sidebar.selectbox(
    "Target Language:",
    list(LANGUAGES.values()),
    index=list(LANGUAGES.values()).index("english")
)

# Translate button
if st.button("🌟 Translate"):
    if input_text.strip():  # Ensure input_text is not empty
        try:
            # Convert language names to codes
            source_code = (list(LANGUAGES.keys())[list(LANGUAGES.values()).index(source_language)]
                           if source_language != "Auto Detect" else "auto")
            target_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(target_language)]

            # Perform the translation
            translation = translator.translate(input_text, src=source_code, dest=target_code)
            
            # Error handling for empty translation
            if not translation.text:
                raise ValueError("Translation output is empty. Check the input or selected languages.")
            
            # Display translated text
            st.subheader("🔄 Translated Text:")
            st.write(f"**{translation.text}**")

            # Generate voice output
            tts = gtts.gTTS(translation.text, lang=target_code)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # Display the audio player
            st.subheader("🔊 Play Translated Audio")
            st.audio(audio_buffer, format="audio/mp3")  # Removed the 'key' argument

            # Animated download button
            st.markdown(
                """
                <style>
                .download-button {
                    text-align: center;
                    padding: 10px 20px;
                    background-color: #FF4B4B;
                    color: white;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .download-button:hover {
                    background-color: #E33E3E;
                    transform: scale(1.1);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }
                </style>
                <div class="download-button" onclick="document.getElementById('download_audio').click();">
                    💾 Download Translated Audio
                </div>
                <a id="download_audio" href="data:audio/mp3;base64,{}" download="translated_audio.mp3" style="display:none;"></a>
                """.format(audio_buffer.getvalue().encode("base64")),
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"An error occurred during translation: {e}")
            if 'googletrans' in str(e):
                st.warning("Please ensure you're using 'googletrans==4.0.0-rc1'.")
    else:
        st.warning("Please enter text or upload audio to translate.")

# Display supported languages
with st.expander("🌍 Supported Languages"):
    st.write(LANGUAGES)
