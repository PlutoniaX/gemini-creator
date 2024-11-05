# Import necessary libraries
import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import streamlit as st

# Load environment variables
load_dotenv()

# Get YouTube API key from environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize YouTube Data API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def create_folder(folder_name):
    """Create a folder if it doesn't exist."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def get_video_ids_and_titles_from_playlist(playlist_id):
    """Retrieve video IDs and titles from a YouTube playlist."""
    video_ids_and_titles = []
    request = youtube.playlistItems().list(
        part='contentDetails,snippet',
        playlistId=playlist_id,
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response['items']:
            video_id = item['contentDetails']['videoId']
            video_title = item['snippet']['title']
            video_ids_and_titles.append((video_id, video_title))
        request = youtube.playlistItems().list_next(request, response)
    return video_ids_and_titles

class TranscriptResult:
    def __init__(self, success, content=None, error_type=None):
        self.success = success
        self.content = content
        self.error_type = error_type

def download_transcript(video_id):
    """Download and return the transcript for a given YouTube video ID."""
    try:
        print(f"DEBUG 1: Getting transcript list for video {video_id}")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        print(f"DEBUG 2: Available transcripts: {transcript_list.manual_generated_transcripts}")
        print(f"DEBUG 2.1: Auto-generated transcripts: {transcript_list.generated_transcripts}")
        
        # Try English first
        try:
            print("DEBUG 3: Attempting to find English transcript")
            transcript = transcript_list.find_transcript(['en'])
            print("DEBUG 4: Found English transcript, fetching...")
            text = '\n'.join([entry['text'] for entry in transcript.fetch()])
            return TranscriptResult(success=True, content=text)
        except NoTranscriptFound as e:
            print(f"DEBUG 5: No English transcript found: {str(e)}")
            # If no English, try any available transcript
            print("DEBUG 6: Trying to find any manual transcript")
            available = transcript_list.find_manually_created_transcript()
            text = '\n'.join([entry['text'] for entry in available.fetch()])
            return TranscriptResult(success=True, content=text)
            
    except TranscriptsDisabled as e:
        print(f"DEBUG 7: TranscriptsDisabled error: {str(e)}")
        return TranscriptResult(success=False, error_type="DISABLED")
    except Exception as e:
        print(f"DEBUG 8: Unexpected error: {type(e)} - {str(e)}")
        return TranscriptResult(success=False, error_type="ERROR")

def get_transcript_from_url(youtube_url):
    """Extract video ID from YouTube URL and get its transcript."""
    try:
        parsed_url = urlparse(youtube_url)
        
        # Handle shortened youtu.be URLs
        if 'youtu.be' in parsed_url.netloc:
            video_id = parsed_url.path.lstrip('/')
            video_id = video_id.split('?')[0]  # Remove query parameters
        else:
            # Handle regular youtube.com URLs
            video_id = parse_qs(parsed_url.query).get('v', [None])[0]
        
        st.write(f"DEBUG: Extracted video ID: {video_id}")
        
        if not video_id:
            return TranscriptResult(success=False, error_type="INVALID_URL")
        
        # Try to get transcript directly without constructing URL
        try:
            st.write("DEBUG: Attempting transcript fetch")
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            
            if transcript:
                st.write("DEBUG: Transcript fetch successful")
                text = '\n'.join([entry['text'] for entry in transcript])
                return TranscriptResult(success=True, content=text)
            else:
                st.write("DEBUG: No transcript returned")
                return TranscriptResult(success=False, error_type="ERROR")
                
        except Exception as e:
            st.write(f"DEBUG: First attempt failed: {type(e)} - {str(e)}")
            
            # Try alternative method with list_transcripts
            try:
                st.write("DEBUG: Attempting alternative transcript fetch")
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                available_transcripts = transcript_list.find_transcript(['en'])
                
                if available_transcripts:
                    text = '\n'.join([entry['text'] for entry in available_transcripts.fetch()])
                    return TranscriptResult(success=True, content=text)
                else:
                    return TranscriptResult(success=False, error_type="ERROR")
                    
            except Exception as e2:
                st.write(f"DEBUG: Alternative attempt failed: {type(e2)} - {str(e2)}")
                return TranscriptResult(success=False, error_type="ERROR")
    
    except Exception as e:
        st.write(f"DEBUG: Unexpected error: {type(e)} - {str(e)}")
        return TranscriptResult(success=False, error_type="ERROR")

# Example usage (commented out)
def main():
    youtube_url = 'https://youtu.be/wmz6Pi2RCCo?feature=shared'  # Replace with your actual YouTube URL
    transcript = get_transcript_from_url(youtube_url)
    print(transcript.content)

if __name__ == '__main__':
    main()
