from youtube_transcript_api import YouTubeTranscriptApi

video_id = "TKfnqBqJyzY"
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("Success!")
    print(transcript[:2])  # Print first two entries
except Exception as e:
    print(f"Error: {type(e)} - {str(e)}")