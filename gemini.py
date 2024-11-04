import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from yt_get_transcript import get_transcript_from_url
from yt_download_audio import download_youtube_audio

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))

def get_model(system_instruction):
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_instruction
    )

# Initialize models with different system instructions
with open('summarise.md', 'r') as f:
    summary_instructions = f.read()
summary_model = get_model(summary_instructions)

with open('write_post.md', 'r') as f:
    post_instructions = f.read()
post_model = get_model(post_instructions)

with open('write_essay.md', 'r') as f:
    essay_instructions = f.read()
essay_model = get_model(essay_instructions)

def generate_flash(prompt, model):
    try:
        # Generate content using Gemini
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        return None

# Streamlit UI
st.title("Content Remixer Pro")
st.write("Repurpose content with ease using Gemini AI")
# Input selection menu
input_type = option_menu(
    menu_title=None,
    options=["Upload Files", "Add URL", "Enter Text"],
    icons=["cloud-upload", "link", "file-text"],
    default_index=0,
    orientation="horizontal"
)

# Handle different input types
if input_type == "Upload Files":
    files = st.file_uploader("Upload PDF, EPUB or TXT files:", ["pdf", "epub", "txt"], accept_multiple_files=True)
    user_input = None
    if files:
        # Process uploaded files here
        pass

elif input_type == "Add URL":
    url = st.text_input("Enter YouTube or podcast URL:")
    user_input = None
    if url:
        # Process URL if it's a YouTube link
        if 'youtube.com' in url or 'youtu.be' in url:
            transcript = get_transcript_from_url(url)
            if transcript != 'Invalid YouTube URL':
                if transcript == 'Transcripts are disabled for this video.':
                    # Get audio and convert to text using Gemini
                    with st.spinner("Transcripts disabled. Converting audio to text..."):
                        uploaded_file, safety_settings = download_youtube_audio(url)
                        if uploaded_file:
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = model.generate_content(
                                ["Generate a transcript of this audio.", uploaded_file],
                                safety_settings=safety_settings
                            )
                            
                            # Check if response has candidates before accessing text
                            if response.candidates:
                                user_input = response.text
                            else:
                                st.error("No valid response generated. Please try again.")
                        else:
                            st.error("Could not process audio. Please try again.")
                else:
                    user_input = transcript
            else:
                st.error("Could not process YouTube URL. Please check the URL and try again.")
        else:
            st.warning("Currently only YouTube URLs are supported.")

else:  # Enter Text
    user_input = st.text_area("Enter your text here:", height=200)

# Dropdown for selecting operation
operation = st.selectbox(
    "Choose operation",
    ["Generate Summary", "Write Post", "Write Essay", "Custom Prompt"]
)

# Custom prompt input if selected
custom_prompt = ""
if operation == "Custom Prompt":
    custom_prompt = st.text_area("Enter your custom system prompt:", height=100)

# Single button for all operations
if st.button("Start"):
    if user_input:
        if operation == "Generate Summary":
            with st.spinner("Generating summary..."):
                result = generate_flash(user_input, summary_model)
                if result:
                    st.write("### Summary:")
                    st.write(result)
                else:
                    st.error("Failed to generate summary. Please try again.")
        elif operation == "Write Post":
            with st.spinner("Writing post..."):
                result = generate_flash(user_input, post_model)
                if result:
                    st.write("### Viral Post:")
                    st.write(result)
                else:
                    st.error("Failed to generate post. Please try again.")
        elif operation == "Custom Prompt":
            if custom_prompt:
                with st.spinner("Generating response..."):
                    custom_model = get_model(custom_prompt)
                    result = generate_flash(user_input, custom_model)
                    if result:
                        st.write("### Response:")
                        st.write(result)
                    else:
                        st.error("Failed to generate response. Please try again.")
            else:
                st.warning("Please enter a custom prompt first.")
        else:  # Write Essay
            with st.spinner("Writing essay..."):
                result = generate_flash(user_input, essay_model)
                if result:
                    st.write("### Essay:")
                    st.write(result)
                else:
                    st.error("Failed to generate essay. Please try again.")
    else:
        st.warning("Please enter some text first.")
