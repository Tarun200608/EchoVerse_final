import streamlit as st
from PyPDF2 import PdfReader
from transformers import pipeline
from gtts import gTTS
import base64
import os
import uuid
from streamlit_lottie import st_lottie
import json

# --------------- SETUP ----------------
st.set_page_config(page_title="EchoVerse", layout="centered")

# --------------- LOAD LOCAL LOTTIE ----------------
def load_local_lottie(path: str):
    with open(path, "r") as f:
        return json.load(f)

animation = load_local_lottie("assets/book.json")  # Change this to your file name
st_lottie(animation, speed=1, height=250, key="intro")

# --------------- TITLE ----------------
st.title("📖 EchoVerse – AI-Powered Audiobook Creator")

# --------------- SELECT MODES ----------------
rewrite_mode = st.selectbox("✍️ Select Rewrite Mode:", ["None", "Formal", "Casual", "Easy"])
summarize_mode = st.toggle("📝 Enable Summarization")
voice_choice = st.selectbox("🎙️ Select Voice:", ["Lisa (female)", "Michael (male)", "Allison (female)"])

# --------------- FILE UPLOAD / TEXT INPUT ----------------
uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
manual_text = st.text_area("💬 Or paste your text here:")

# --------------- FUNCTIONS ----------------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def rewrite_text(text, mode):
    if mode == "None":
        return text
    style_map = {
        "Formal": "Rewrite the text in a formal tone.",
        "Casual": "Rewrite the text in a casual tone.",
        "Easy": "Rewrite the text to be easy to understand.",
    }
    prompt = style_map[mode] + "\n\n" + text
    pipe = pipeline("text2text-generation", model="google/flan-t5-base")
    result = pipe(prompt, max_new_tokens=500)
    return result[0]["generated_text"]

def summarize_text(text):
    pipe = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    summary = pipe(text, max_length=150, min_length=40, do_sample=False)
    return summary[0]["summary_text"]

def generate_audio(text, voice_name):
    tts = gTTS(text=text, lang="en", tld="com")
    filename = f"audio_{uuid.uuid4().hex}.mp3"
    tts.save(filename)
    return filename

def get_download_link(file_path):
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{file_path}">📥 Download Audio</a>'
    return href

# --------------- PROCESS ----------------
if st.button("▶️ Process"):
    if uploaded_file:
        original_text = extract_text_from_pdf(uploaded_file)
    elif manual_text.strip():
        original_text = manual_text.strip()
    else:
        st.warning("Please upload a PDF or enter text.")
        st.stop()

    st.subheader("📝 Original Text")
    st.write(original_text)

    final_text = original_text

    if summarize_mode:
        st.info("Summarizing text...")
        final_text = summarize_text(final_text)

    if rewrite_mode != "None":
        st.info(f"Rewriting text in {rewrite_mode} tone...")
        final_text = rewrite_text(final_text, rewrite_mode)

    st.subheader("✍️ Final Text")
    st.write(final_text)

    # AUDIO
    voice_label = voice_choice.split()[0]
    st.success(f"Generating audio with voice: {voice_label}")
    audio_file = generate_audio(final_text, voice_label)

    st.audio(audio_file, format="audio/mp3")
    st.markdown(get_download_link(audio_file), unsafe_allow_html=True)

# --------------- FOOTER ----------------
st.markdown("---")
st.caption("Made with ❤️ for the GenAI Hackathon – EchoVerse by Team Tarun")
