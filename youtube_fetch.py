from googleapiclient.discovery import build
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# ----------------- CONFIG -----------------
API_KEY = "AIzaSyDoTbivz3ZGF3-H3nV7mKfMmKNsIZTZq4g"
CHANNEL_ID = "UCv-yOn6QFBonsVyotOYmQCw"  # Example: Google Developers channel
# PostgreSQL connection
engine = create_engine("postgresql+psycopg2://postgres:itsmaygal02@localhost:5432/youtube_dashboard")

# Build YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

# ----------------- STEP 1: Channel Stats -----------------
channel_request = youtube.channels().list(
    part="snippet,statistics",
    id=CHANNEL_ID
)
channel_response = channel_request.execute()

channel_data = channel_response["items"][0]

channel_stats = {
    "channel_name": channel_data["snippet"]["title"],
    "subscribers": int(channel_data["statistics"]["subscriberCount"]),
    "total_views": int(channel_data["statistics"]["viewCount"]),
    "total_videos": int(channel_data["statistics"]["videoCount"]),
    "dislikes": int(channel_data["statistics"].get("dislikeCount", 0))  # 👈 added
}

# Save channel stats to PostgreSQL
df_channel = pd.DataFrame([channel_stats])
df_channel.to_sql("channel_stats", engine, if_exists="append", index=False)
print("✅ Channel stats inserted into PostgreSQL")

# ----------------- STEP 2: Latest 10 Videos -----------------
video_request = youtube.search().list(
    part="snippet",
    channelId=CHANNEL_ID,
    maxResults=10,
    order="date"
)
video_response = video_request.execute()

videos = []

for item in video_response["items"]:
    video_id = item["id"]["videoId"]
    title = item["snippet"]["title"]
    published_at = item["snippet"]["publishedAt"]

    # Get video statistics
    stats_request = youtube.videos().list(
        part="statistics",
        id=video_id
    )
    stats_response = stats_request.execute()
    stats = stats_response["items"][0]["statistics"]

    videos.append({
        "video_id": video_id,
        "title": title,
        "published_at": datetime.fromisoformat(published_at.replace("Z", "+00:00")),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "dislikes": int(stats.get("dislikeCount", 0)),   # 👈 added
        "comments": int(stats.get("commentCount", 0))
    })

# Save video stats to PostgreSQL
df_videos = pd.DataFrame(videos)
df_videos.to_sql("video_stats", engine, if_exists="append", index=False)
print("✅ Video stats inserted into PostgreSQL")
