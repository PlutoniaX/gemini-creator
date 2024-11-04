import yt_dlp
import google.generativeai as genai
import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def download_youtube_audio(url):
    # Configure safety settings
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Configure yt-dlp to extract audio in a Gemini-supported format
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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        audio_file = f"{output_file}.wav"
        uploaded_file = genai.upload_file(audio_file)
        
        os.remove(audio_file)
        
        return uploaded_file, safety_settings
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if os.path.exists(f"{output_file}.wav"):
            os.remove(f"{output_file}.wav")
        return None, None
    

# if __name__ == "__main__":
#     # Example usage
#     url = "https://youtu.be/nxoiColWxKo?feature=shared"
#     audio_buffer = download_youtube_audio(url)
    
#     if audio_buffer:
#         print("Successfully downloaded audio to buffer")
#         # Here you could write the buffer to a file if needed:
#         # with open("output.mp3", "wb") as f:
#         #     f.write(audio_buffer.getvalue())
#     else:
#         print("Failed to download audio")
