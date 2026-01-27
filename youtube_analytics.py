from googleapiclient.discovery import build
import pandas as pd

# ----------------- CONFIG -----------------
API_KEY = "AIzaSyDoTbivz3ZGF3-H3nV7mKfMmKNsIZTZq4g"         # Your API Key here
CHANNEL_ID = "UCv-yOn6QFBonsVyotOYmQCw"   # Your Channel ID here
MAX_VIDEOS = 10                  # Number of latest videos to fetch

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
    "total_videos": int(channel_data["statistics"]["videoCount"])
}

print("Channel Stats:")
print(channel_stats)

# ----------------- STEP 2: Fetch Latest Videos -----------------
video_request = youtube.search().list(
    part="snippet",
    channelId=CHANNEL_ID,
    maxResults=MAX_VIDEOS,
    order="date"
)
video_response = video_request.execute()

video_list = []

for item in video_response["items"]:
    video_id = item["id"]["videoId"]
    title = item["snippet"]["title"]
    published_at = item["snippet"]["publishedAt"]

    # ----------------- STEP 3: Fetch Video Stats -----------------
    stats_request = youtube.videos().list(
        part="statistics",
        id=video_id
    )
    stats_response = stats_request.execute()
    stats = stats_response["items"][0]["statistics"]

    video_list.append({
        "video_id": video_id,
        "title": title,
        "published_at": published_at,
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0))
    })

# Convert to DataFrame
df_videos = pd.DataFrame(video_list)

print("\nLatest Video Stats:")
print(df_videos)

# ----------------- STEP 4: Export to CSV -----------------
df_videos.to_csv("youtube_channel_analytics.csv", index=False)
print("\n✅ CSV file 'youtube_channel_analytics.csv' created successfully!")
