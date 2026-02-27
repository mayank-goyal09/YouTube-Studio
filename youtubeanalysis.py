from googleapiclient.discovery import build
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your API Key (set in .env file)
API_KEY = os.getenv("YOUTUBE_API_KEY", "")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

if not API_KEY or not CHANNEL_ID:
    raise ValueError("Missing YOUTUBE_API_KEY or YOUTUBE_CHANNEL_ID in .env file")

# Build YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

# 1. Get channel stats
channel_request = youtube.channels().list(
    part="snippet,contentDetails,statistics",
    id=CHANNEL_ID
)
channel_response = channel_request.execute()

channel_data = channel_response["items"][0]
channel_stats = {
    "channel_name": channel_data["snippet"]["title"],
    "subscribers": channel_data["statistics"]["subscriberCount"],
    "total_views": channel_data["statistics"]["viewCount"],
    "total_videos": channel_data["statistics"]["videoCount"]
}
print("Channel Stats:", channel_stats)

# 2. Get latest videos
playlist_id = channel_data["contentDetails"]["relatedPlaylists"]["uploads"]
videos_request = youtube.playlistItems().list(
    part="snippet",
    playlistId=playlist_id,
    maxResults=5
)
videos_response = videos_request.execute()

videos = []
for item in videos_response["items"]:
    video_title = item["snippet"]["title"]
    video_id = item["snippet"]["resourceId"]["videoId"]

    # Get video statistics
    stats_request = youtube.videos().list(
        part="statistics",
        id=video_id
    )
    stats_response = stats_request.execute()
    stats = stats_response["items"][0]["statistics"]

    videos.append({
        "video_id": video_id,
        "title": video_title,
        "views": stats.get("viewCount", 0),
        "likes": stats.get("likeCount", 0),
        "comments": stats.get("commentCount", 0)
    })

df = pd.DataFrame(videos)
print("\nLatest Videos:\n", df)
