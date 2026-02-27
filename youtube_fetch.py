from googleapiclient.discovery import build
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ----------------- CONFIG -----------------
API_KEY = os.getenv("YOUTUBE_API_KEY", "")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

# SQLite connection (local file, no password needed!)
DB_PATH = os.path.join(os.path.dirname(__file__), "youtube_data.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

# ----------------- INITIALIZE TABLES -----------------
def init_database():
    """Create tables if they don't exist"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS channel_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT,
                subscribers INTEGER,
                total_views INTEGER,
                total_videos INTEGER,
                dislikes INTEGER DEFAULT 0,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS video_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                title TEXT,
                published_at TIMESTAMP,
                views INTEGER,
                likes INTEGER,
                dislikes INTEGER DEFAULT 0,
                comments INTEGER,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
    print("✅ Database tables initialized")

def fetch_youtube_data():
    """Fetch data from YouTube API and save to SQLite"""
    
    # Initialize database
    init_database()
    
    # Check if API key is configured
    if not API_KEY:
        print("⚠️  No YOUTUBE_API_KEY found in environment variables!")
        print("   Create a .env file with: YOUTUBE_API_KEY=your_api_key_here")
        print("   Or run: python init_demo_data.py to use demo data instead")
        return False

    try:
        # Build YouTube API client
        youtube = build("youtube", "v3", developerKey=API_KEY)

        # ----------------- STEP 1: Channel Stats -----------------
        channel_request = youtube.channels().list(
            part="snippet,statistics",
            id=CHANNEL_ID
        )
        channel_response = channel_request.execute()

        if not channel_response["items"]:
            print(f"❌ Channel ID {CHANNEL_ID} not found.")
            return False

        channel_data = channel_response["items"][0]

        channel_stats = {
            "channel_name": channel_data["snippet"]["title"],
            "subscribers": int(channel_data["statistics"]["subscriberCount"]),
            "total_views": int(channel_data["statistics"]["viewCount"]),
            "total_videos": int(channel_data["statistics"]["videoCount"]),
            "dislikes": int(channel_data["statistics"].get("dislikeCount", 0))
        }

        # Save channel stats to SQLite
        df_channel = pd.DataFrame([channel_stats])
        df_channel.to_sql("channel_stats", engine, if_exists="append", index=False)
        print("✅ Channel stats inserted into SQLite")

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
            # Skip non-video items (like playlists)
            if item["id"].get("kind") != "youtube#video" and "videoId" not in item["id"]:
                continue
            
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            published_at = item["snippet"]["publishedAt"]

            # Get video statistics
            stats_request = youtube.videos().list(
                part="statistics",
                id=video_id
            )
            stats_response = stats_request.execute()
            
            if not stats_response["items"]:
                continue
                
            stats = stats_response["items"][0]["statistics"]

            videos.append({
                "video_id": video_id,
                "title": title,
                "published_at": datetime.fromisoformat(published_at.replace("Z", "+00:00")),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "dislikes": int(stats.get("dislikeCount", 0)),
                "comments": int(stats.get("commentCount", 0))
            })

        # Save video stats to SQLite
        if videos:
            df_videos = pd.DataFrame(videos)
            df_videos.to_sql("video_stats", engine, if_exists="append", index=False)
            print(f"✅ {len(videos)} video stats inserted into SQLite")
        else:
            print("⚠️  No videos found to insert")

        print(f"\n📁 Data saved to: {DB_PATH}")
        return True
        
    except Exception as e:
        print(f"❌ Error fetching YouTube data: {e}")
        return False

if __name__ == "__main__":
    fetch_youtube_data()
