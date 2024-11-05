# Import necessary libraries
import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

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
        # Try to get the transcript in the default language
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = '\n'.join([entry['text'] for entry in transcript_list])
        return TranscriptResult(success=True, content=transcript)
    except TranscriptsDisabled:
        return TranscriptResult(success=False, error_type="DISABLED")
    except Exception as e:
        try:
            # If default language fails, try Chinese (simplified)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-CN'])
            transcript = '\n'.join([entry['text'] for entry in transcript_list])
            return TranscriptResult(success=True, content=transcript)
        except Exception as e:
            return TranscriptResult(success=False, error_type="ERROR")

def get_transcript_from_url(youtube_url):
    """Extract video ID from YouTube URL and get its transcript."""
    parsed_url = urlparse(youtube_url)
    
    # Handle shortened youtu.be URLs
    if 'youtu.be' in parsed_url.netloc:
        video_id = parsed_url.path.lstrip('/')
    else:
        # Handle regular youtube.com URLs
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    
    if video_id:
        return download_transcript(video_id)
    else:
        return TranscriptResult(success=False, error_type="INVALID_URL")

# Example usage (commented out)
def main():
    youtube_url = 'https://youtu.be/wmz6Pi2RCCo?feature=shared'  # Replace with your actual YouTube URL
    transcript = get_transcript_from_url(youtube_url)
    print(transcript.content)

if __name__ == '__main__':
    main()
