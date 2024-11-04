import os
from groq import Groq
from dotenv import load_dotenv
import yt_dlp

def transcribe_audio(audio_file_path):
    """
    Transcribe an audio file using Groq's Whisper API.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        str: Transcribed text from the audio file
        None: If transcription fails
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize Groq client
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))

        # Open and read the audio file
        with open(audio_file_path, "rb") as file:
            # Create transcription using Groq's API
            transcription = client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3-turbo",  # Fastest multilingual model
                response_format="text",  # Simple text response
                language="en"  # Default to English
            )
            
            return transcription.text

    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return None


if __name__ == "__main__":
    # Example YouTube URL
    url = "https://www.youtube.com/watch?v=_Jn-EHAW_u0"
    
    # Configure yt-dlp to extract audio
    output_file = "temp_audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '16',
        }],
        'outtmpl': output_file,
        'quiet': True
    }

    try:
        # Download and extract audio from YouTube
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        audio_path = f"{output_file}.wav"
        
        # Transcribe the audio
        transcript = transcribe_audio(audio_path)
        
        if transcript:
            print("Transcription successful:")
            print(transcript)
        else:
            print("Transcription failed")

        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    except Exception as e:
        print(f"Failed to process audio: {str(e)}")
        if os.path.exists(f"{output_file}.wav"):
            os.remove(f"{output_file}.wav")
