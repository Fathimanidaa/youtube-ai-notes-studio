
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


def extract_video_id(youtube_url):
    """Extract the video ID from common YouTube URL formats."""

    parsed_url = urlparse(youtube_url.strip())
    hostname = (parsed_url.hostname or "").lower()
    video_id = None

    if hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.path.startswith(("/embed/", "/shorts/")):
            video_id = parsed_url.path.split("/")[2]

    elif hostname == "youtu.be" or hostname == "www.youtu.be":
        video_id = parsed_url.path.strip("/").split("/")[0]

    if not video_id:
        raise ValueError("Please enter a valid YouTube video URL.")

    return video_id


def get_transcript(youtube_url):
    """Retrieve available captions and combine them into text."""

    video_id = extract_video_id(youtube_url)

    transcript_api = YouTubeTranscriptApi()
    transcript = transcript_api.fetch(video_id)

    transcript_text = " ".join(
        snippet.text for snippet in transcript
    )

    if not transcript_text.strip():
        raise ValueError("The transcript is empty.")

    return transcript_text