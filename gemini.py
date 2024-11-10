import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from yt_get_transcript import get_transcript_from_url
from yt_download_audio import download_youtube_audio
from styling import local_css

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))

def get_model(system_instruction):
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_instruction,
        generation_config=genai.types.GenerationConfig(
            temperature=0
        )
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

with open('write_notes.md', 'r') as f:
    notes_instructions = f.read()
notes_model = get_model(notes_instructions)

with open('get_quotes.md', 'r') as f:
    quotes_instructions = f.read()
quotes_model = get_model(quotes_instructions)

def generate_flash(prompt, model):
    try:
        # Generate content using Gemini with temperature=0
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="Vectra", page_icon=":gear:")
local_css('style/style.css')

st.markdown('<h1 style="text-align: center; padding-left: 30px;">✧ Vectra ✧</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="padding-top: 1px; padding-left: 30px; color: #808080; font-size: 25px; text-align: center;">read • write • faster</h3>', unsafe_allow_html=True)

# Add this near the top of your file, after the st.markdown header statements
st.markdown("""
    <style>
        .stSpinner > div {
            text-align: center;
            align-items: center;
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

st.write("Pick a source:")
# Input selection menu
input_type = option_menu(
    menu_title=None,
    # options=["Upload Files", "Add URL", "Enter Text"],
    # icons=["cloud-upload", "link", "file-text"],
    options=["URL", "Text"],
    icons=["link", "file-text"],
    default_index=0,
    orientation="horizontal"
)

if input_type == "URL":
    url = st.text_input("Enter YouTube or podcast URL:")
    user_input = None
    if url:
        # Clear cache if URL changes
        if 'last_url' not in st.session_state or st.session_state.last_url != url:
            st.session_state.cached_transcripts = {}
            st.session_state.last_url = url
            
        if 'cached_transcripts' not in st.session_state:
            st.session_state.cached_transcripts = {}
            
        if 'youtube.com' in url or 'youtu.be' in url:
            if url in st.session_state.cached_transcripts:
                user_input = st.session_state.cached_transcripts[url]
            else:
                result = get_transcript_from_url(url)
                print (result)
                if result.success and result.content:
                    user_input = result.content
                    st.session_state.cached_transcripts[url] = result.content
                else:
                    if result.error_type == "DISABLED":
                        st.info("Transcript is disabled. Will transcribe audio first when you click Start.")
                        user_input = {"type": "audio", "url": url}
                    else:
                        st.info("Transcript not available. Will transcribe audio first when you click Start.")
                        user_input = {"type": "audio", "url": url}
        else:
            st.warning("Currently only YouTube URLs are supported.")

else:  # Enter Text
    user_input = st.text_area("Enter your text here:", height=200)

# Dropdown for selecting operation
operation = st.selectbox(
    "Choose operation:",
    [
        "Summarise Content",
        "Write Post",
        "Write Essay",
        "Write Notes",
        "Get Quotes",
        "CUSTOM PROMPT"
    ]
)

# Custom prompt input if selected
custom_prompt = ""
if operation == "CUSTOM PROMPT":
    custom_prompt = st.text_area("Enter your custom prompt:", height=100)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    start_button = st.button(
        "Start",
        icon=None,
        use_container_width=True
    )

if start_button:
    if user_input:
        # Handle audio processing if needed
        if isinstance(user_input, dict) and user_input["type"] == "audio":
            original_url = user_input["url"]  # Store the URL before processing
            # Check if we already have this URL's transcript cached
            if original_url in st.session_state.cached_transcripts:
                user_input = st.session_state.cached_transcripts[original_url]
                st.info("Using cached transcript")
            else:
                st.write("")
                with st.spinner("Converting audio to text. Please be patient..."):
                    uploaded_file, safety_settings = download_youtube_audio(original_url)
                    if uploaded_file:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(
                            ["Generate a transcript of this audio.", uploaded_file],
                            safety_settings=safety_settings,
                            generation_config=genai.types.GenerationConfig(
                                temperature=0
                            )
                        )
                        
                        if response.candidates:
                            user_input = response.text
                            # Cache the transcript using the original URL
                            st.session_state.cached_transcripts[original_url] = user_input
                        else:
                            st.error("No valid response generated. Please refresh browser and try again.")
                            user_input = None
                    else:
                        st.error("Could not process audio. Please refresh browser and try again.")
                        user_input = None

        if user_input:  # Continue only if we have valid input
            if operation == "Summarise Content":
                st.write("")
                with st.spinner("Generating summary..."):
                    result = generate_flash(user_input, summary_model)
                    if result:
                        st.write("---")
                        st.markdown('<h3 style="padding-top: 1px; padding-left: 30px; color: #808080; font-size: 25px; text-align: center;">Summary:</h3>', unsafe_allow_html=True)
                        st.write(result)
                    else:
                        st.error("Failed to generate summary. Please refresh browser and try again.")
            elif operation == "Write Post":
                st.write("")
                with st.spinner("Writing post..."):
                    result = generate_flash(user_input, post_model)
                    if result:
                        st.write("---")
                        st.markdown('<h3 style="padding-top: 1px; padding-left: 30px; color: #808080; font-size: 25px; text-align: center;">Post:</h3>', unsafe_allow_html=True)
                        st.write(result)
                    else:
                        st.error("Failed to generate post. Please refresh browser and try again.")
            elif operation == "Write Essay":
                st.write("")
                with st.spinner("Writing essay..."):
                    result = generate_flash(user_input, essay_model)
                    if result:
                        st.write("---")
                        st.markdown('<h3 style="padding-top: 1px; padding-left: 30px; color: #808080; font-size: 25px; text-align: center;">Essay:</h3>', unsafe_allow_html=True)
                        st.write(result)
                    else:
                        st.error("Failed to generate essay. Please refresh browser and try again.")
            elif operation == "Write Notes":
                st.write("")
                with st.spinner("Writing notes..."):
                    result = generate_flash(user_input, notes_model)
                    if result:
                        st.write("---")
                        st.markdown('<h3 style="padding-top: 1px; padding-left: 30px; color: #808080; font-size: 25px; text-align: center;">Notes:</h3>', unsafe_allow_html=True)
                        st.write(result)
                    else:
                        st.error("Failed to generate notes. Please refresh browser and try again.")
            elif operation == "Get Quotes":
                st.write("")
                with st.spinner("Extracting quotes..."):
                    result = generate_flash(user_input, quotes_model)
                    if result:
                        st.write("---")
                        st.markdown('<h3 style="padding-top: 1px; padding-left: 30px; color: #808080; font-size: 25px; text-align: center;">Quotes:</h3>', unsafe_allow_html=True)
                        st.write(result)
                    else:
                        st.error("Failed to extract quotes. Please refresh browser and try again.")
            elif operation == "CUSTOM PROMPT":
                if custom_prompt:
                    st.write("")
                    with st.spinner("Generating response..."):
                        custom_model = get_model(custom_prompt)
                        result = generate_flash(user_input, custom_model)
                        if result:
                            st.write("---")
                            st.markdown('<h3 style="padding-top: 1px; padding-left: 30px; color: #808080; font-size: 25px; text-align: center;">Response:</h3>', unsafe_allow_html=True)
                            st.write(result)
                        else:
                            st.error("Failed to generate response. Please refresh browser and try again.")
                else:
                    st.warning("Please enter a custom prompt first.")
    else:
        st.warning("Please enter some text first.")
