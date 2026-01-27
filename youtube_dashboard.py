import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import os

# ---- Page Config (MUST BE FIRST) ----
st.set_page_config(page_title="YouTube Analytics • Modern Premium", layout="wide")

# ---- Sidebar Theme Switcher ----
theme_mode = st.sidebar.radio("🌈 Select Theme", ["Dark", "Light"])

# ---- Theme-Aware Variables ----
if theme_mode == "Dark":
    BANNER_FONT_COLOR = "#fff"
    METRIC_FONT_COLOR = "#fff"
    METRIC_CHIP_BG = "#181f2a"
    PLOTLY_THEME = "plotly_dark"
    PLOTLY_BG = "#28243c"
    AXIS_FONT_COLOR = "#fff"
else:
    BANNER_FONT_COLOR = "#222"
    METRIC_FONT_COLOR = "#27364f"
    METRIC_CHIP_BG = "#f2f3f5"
    PLOTLY_THEME = "plotly_white"
    PLOTLY_BG = "#e7eaf3"
    AXIS_FONT_COLOR = "#2a3356"  # navy for more clarity

# ---- Custom CSS for Premium Cards/Chips ----
st.markdown(f"""
    <style>
    .stApp {{
        background: {'linear-gradient(120deg,#28243c 0%, #2ba8ea 100%)' if theme_mode=='Dark' else 'linear-gradient(120deg,#e7eaf3 0%,#fff 100%)'};
        color: {BANNER_FONT_COLOR};
    }}
    
    /* Force all text colors based on theme */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
        color: {BANNER_FONT_COLOR} !important;
    }}
    
    /* Markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown strong, .stMarkdown b {{
        color: {BANNER_FONT_COLOR} !important;
    }}
    
    /* Headers */
    .stApp [data-testid="stHeader"] {{
        color: {BANNER_FONT_COLOR} !important;
    }}
    
    /* Subheaders and titles */
    .stApp .stSubheader, .stApp [data-testid="stSubheader"] {{
        color: {BANNER_FONT_COLOR} !important;
    }}
    
    /* Regular text elements */
    .element-container, .element-container p, .element-container span {{
        color: {BANNER_FONT_COLOR} !important;
    }}
    
    /* Metric cards */
    .metric-card {{
        background: {'rgba(20, 20, 33, 0.80)' if theme_mode=='Dark' else 'rgba(255,255,255,0.95)'};
        border-radius: 18px;
        box-shadow: 0 4px 16px rgba(60,0,100,{0.16 if theme_mode=='Dark' else 0.10});
        padding: 16px;
        backdrop-filter: blur(6px);
        color: {METRIC_FONT_COLOR} !important;
        margin-bottom: 18px;
    }}
    .metric-card h2, .metric-card span, .metric-card b, .metric-card small {{
        color: {METRIC_FONT_COLOR} !important;
    }}
    .metric-card h2 {{
        color: #2ba8ea !important;
    }}
    
    .metric-chip {{
        display: inline-block;
        background: {METRIC_CHIP_BG};
        color: #19be6c !important;
        font-weight: 700;
        font-size: 1.05em;
        border-radius: 16px;
        padding: 4px 13px;
        margin-top: 6px;
        margin-bottom: 6px;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{ 
        background: {'#222237' if theme_mode=='Dark' else '#f9fafc'}; 
        color: {BANNER_FONT_COLOR if theme_mode=='Dark' else METRIC_FONT_COLOR} !important; 
    }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: {BANNER_FONT_COLOR if theme_mode=='Dark' else METRIC_FONT_COLOR} !important;
    }}
    
    /* Checkbox labels */
    .stCheckbox label span {{
        color: {BANNER_FONT_COLOR} !important;
    }}
    
    /* Metric widget */
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {{
        color: {BANNER_FONT_COLOR} !important;
    }}
    
    /* Table text */
    .stDataFrame, .stDataFrame td, .stDataFrame th {{
        color: {'#fff' if theme_mode=='Dark' else '#222'} !important;
    }}
    
    /* Info boxes */
    .stAlert p {{
        color: #333 !important;
    }}
    
    hr {{ border-top: 2px solid #2ba8ea; }}
    </style>
""", unsafe_allow_html=True)

# ---- SQLite Connection (No password needed!) ----
DB_PATH = os.path.join(os.path.dirname(__file__), "youtube_data.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

# ---- Initialize Tables if Needed ----
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

init_database()

# ---- Page Title & Banners ----
# YouTube Channel Button at Top
st.markdown("""
<div style='text-align: right; margin-bottom: -50px;'>
    <a href='http://www.youtube.com/@maygal_memer' target='_blank' style='text-decoration: none;'>
        <div style='display: inline-flex; align-items: center; background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%); 
                    padding: 10px 20px; border-radius: 50px; box-shadow: 0 4px 15px rgba(255,0,0,0.4);
                    transition: all 0.3s ease; cursor: pointer;'>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
            </svg>
            <span style='color: white; font-weight: 700; font-size: 16px; margin-left: 8px;'>Visit My Channel</span>
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

st.title("✨ YouTube Channel Analytics Dashboard")

st.markdown(f"""
<h3 style='font-weight:700; color:{BANNER_FONT_COLOR};'>
  Where data meets strategy, and people inspire results.<br>
  <span style='font-size:20px;color:#2ba8ea;'>
    Designed by Mayank Goyal — Empowering decisions, creating growth, leading with purpose.
  </span> 🚀
</h3>
""", unsafe_allow_html=True)

# ---- Cached Data Load ----
@st.cache_data(ttl=45)
def load_tables():
    try:
        channel_latest = pd.read_sql("SELECT * FROM channel_stats ORDER BY fetched_at DESC LIMIT 1", engine)
        channel_history = pd.read_sql("SELECT * FROM channel_stats ORDER BY fetched_at ASC", engine)
        videos = pd.read_sql("SELECT * FROM video_stats ORDER BY fetched_at DESC", engine)
        return channel_latest, channel_history, videos
    except Exception as e:
        st.warning(f"Database empty or error: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

channel_df, channel_history_df, videos_df = load_tables()

# ---- Check if we have data ----
if channel_df.empty and videos_df.empty:
    st.error("""
    ### 📊 No Data Found!
    
    Your database is empty. To get started:
    
    **Option 1: Fetch real data** (requires YouTube API key)
    1. Create a `.env` file with: `YOUTUBE_API_KEY=your_api_key_here`
    2. Run: `python youtube_fetch.py`
    
    **Option 2: Use demo data** (for testing)
    ```bash
    python init_demo_data.py
    ```
    
    Then refresh this page! 🔄
    """)
    st.stop()

# ---- Date & Sidebar Controls ----
st.sidebar.header("🔎 Filters & Controls")
st.sidebar.caption("Welcome, legend! Choose your style, set filters & let's analyze 🎨")

# Prepare working copies to avoid modifying cached data
working_videos = videos_df.copy()
working_channel_history = channel_history_df.copy()

# Convert date columns
for df, dcol in [(working_channel_history, "fetched_at"), (working_videos, "fetched_at"), (working_videos, "published_at")]:
    if dcol in df.columns:
        df[dcol] = pd.to_datetime(df[dcol], errors='coerce')

date_col = "published_at" if "published_at" in working_videos.columns else "fetched_at"

# Get date range from data
if date_col in working_videos.columns and not working_videos.empty:
    valid_dates = working_videos[date_col].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
    else:
        min_date, max_date = None, None
else:
    min_date, max_date = None, None

# Date range picker
if min_date and max_date:
    date_range = st.sidebar.date_input(
        "Date Range", 
        value=[min_date, max_date], 
        min_value=min_date, 
        max_value=max_date,
        key="date_filter"
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date
else:
    start_date, end_date = None, None

top_n = st.sidebar.slider("Top N Videos to Show", min_value=5, max_value=30, value=10, step=1, key="top_n_slider")

if st.sidebar.button("🔄 Manual Data Refresh"):
    st.cache_data.clear()
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.caption("Auto-refresh every 60s")

# ---- Data Preparation ----
filtered_videos = working_videos.copy()

# Apply date filter
if start_date and end_date and date_col in filtered_videos.columns:
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    mask = (filtered_videos[date_col] >= start_ts) & (filtered_videos[date_col] <= end_ts)
    filtered_videos = filtered_videos[mask].copy()
for col in ["views", "likes", "dislikes", "comments"]:
    if col not in filtered_videos.columns:
        filtered_videos[col] = 0
    filtered_videos[col] = pd.to_numeric(filtered_videos[col], errors="coerce").fillna(0)
filtered_videos["engagement_rate"] = (
    (filtered_videos["likes"] + filtered_videos["comments"]) /
    filtered_videos["views"].replace({0: pd.NA})
).fillna(0)
df_top_n = filtered_videos.nlargest(top_n, "views").copy()

# ---- Premium Metric Card ----
def metric_card(title, value, icon, submetric=None):
    st.markdown(f"""
    <div class='metric-card'>
        <span style='font-size:20px;'>{icon}</span> 
        <span style='font-weight:650;font-size:1.15em;'>{title}</span>
        <h2 style='margin:0;color:#2ba8ea;font-size:2.1em;'>{value}</h2>
        {"<div class='metric-chip'>" + submetric + "</div>" if submetric else ""}
    </div>
    """, unsafe_allow_html=True)

# ---- KPI Row 1: Channel Overview ----
st.markdown("#### 📌 Channel Overview")
cols_kpi = st.columns(4)
kpi_map = [
    ("Subscribers", channel_df['subscribers'].iloc[0], "👥") if not channel_df.empty else ("Subscribers", "N/A", "👥"),
    ("Total Views", channel_df['total_views'].iloc[0], "👀") if not channel_df.empty else ("Total Views", "N/A", "👀"),
    ("Total Videos", channel_df['total_videos'].iloc[0], "🎞") if not channel_df.empty else ("Total Videos", "N/A", "🎞"),
]
avg_views = (channel_df['total_views'].iloc[0] / max(channel_df['total_videos'].iloc[0], 1) if not channel_df.empty else "N/A")
kpi_map.append(("Avg Views / Video", f"{avg_views:,.0f}" if avg_views!="N/A" else "N/A", "📊"))
for i, (title, val, icon) in enumerate(kpi_map):
    with cols_kpi[i]:
        metric_card(title, f"{int(val):,}" if str(val).isnumeric() else val, icon)

if not channel_df.empty and int(channel_df['subscribers'].iloc[0]) >= 10000:
    st.balloons()

# ---- KPI Row 2: Engagement Metrics ----
st.markdown("#### 📊 Engagement Metrics (Filtered)")
cols_eng = st.columns(5)
metric_map = [
    ("Total Likes", int(filtered_videos["likes"].sum()), "👍"),
    ("Total Dislikes", int(filtered_videos["dislikes"].sum()), "👎"),
    ("Total Comments", int(filtered_videos["comments"].sum()), "💬"),
    ("Filtered Views", int(filtered_videos["views"].sum()), "👀"),
    ("Avg Engagement Rate", f"{filtered_videos['engagement_rate'].mean():.2%}", "📈")
]
for i, (title, val, icon) in enumerate(metric_map):
    with cols_eng[i]:
        metric_card(title, val, icon)

# ---- Top Video Metrics (with theme chips!) ----
st.markdown("#### 🏆 Top Videos (Filtered)")
top_metrics = [
    ("Most Viewed", "views", "🔥", "views"),
    ("Most Liked", "likes", "❤️", "likes"),
    ("Most Disliked", "dislikes", "❌", "dislikes"),
]
for label, key, icon, sm in top_metrics:
    if not filtered_videos.empty:
        mvid = filtered_videos.loc[filtered_videos[key].idxmax()]
        metric_card(
            f"{label}",
            mvid.get("title", "N/A") + " 😁 #meme" if label != "Most Disliked" else mvid.get("title", "N/A") + " 😍 #meme",
            icon,
            submetric=f"↑ {int(mvid.get(key,0)):,} {sm}"
        )
    else:
        metric_card(f"{label}", "N/A", icon)

st.markdown("---")

# ---- Subscriber Growth Charts (with contrast fixes) ----
def fixed_chart_layout(fig):
    fig.update_layout(
        font_color=AXIS_FONT_COLOR,
        plot_bgcolor=PLOTLY_BG,
        paper_bgcolor=PLOTLY_BG,
        xaxis=dict(color=AXIS_FONT_COLOR, showgrid=False, zeroline=False, tickfont=dict(color=AXIS_FONT_COLOR)),
        yaxis=dict(color=AXIS_FONT_COLOR, showgrid=False, zeroline=False, tickfont=dict(color=AXIS_FONT_COLOR)),
        title_font=dict(color=AXIS_FONT_COLOR),
        legend=dict(font=dict(color=AXIS_FONT_COLOR)),
        coloraxis_colorbar=dict(tickfont=dict(color=AXIS_FONT_COLOR), title_font=dict(color=AXIS_FONT_COLOR))
    )
    return fig

st.subheader("📈 Subscriber Growth")
if not working_channel_history.empty:
    ch = working_channel_history.copy()
    ch["fetched_at"] = pd.to_datetime(ch["fetched_at"], errors='coerce')
    fig_daily = px.line(ch, x="fetched_at", y="subscribers", markers=True,
        title="Subscribers Over Time", template=PLOTLY_THEME, color_discrete_sequence=["#2ba8ea"])
    st.plotly_chart(fixed_chart_layout(fig_daily), use_container_width=True)
    ch["month"] = ch["fetched_at"].dt.to_period("M")
    monthly_subs = ch.groupby("month")["subscribers"].last().reset_index()
    monthly_subs["month"] = monthly_subs["month"].dt.to_timestamp()
    fig_monthly = px.line(monthly_subs, x="month", y="subscribers", markers=True,
        title="Monthly Subscriber Growth", template=PLOTLY_THEME, color_discrete_sequence=["#3939c9","#2ba8ea","#e040fb"])
    st.plotly_chart(fixed_chart_layout(fig_monthly), use_container_width=True)
else:
    st.info("No channel history data available.")

# ---- Video Insights / Charts (with contrast fixes) ----
st.subheader("🔥 Top Videos & Engagement")
if not df_top_n.empty:
    fig_top = px.bar(df_top_n, x="title", y="views", text="views", title=f"Top {top_n} Videos by Views",
                     template=PLOTLY_THEME, color="views", color_continuous_scale=px.colors.sequential.Agsunset)
    fig_top.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fixed_chart_layout(fig_top), use_container_width=True)
else:
    st.info("No video rows to show in Top N chart.")

st.markdown("**Top videos by engagement rate**")
top_eng = filtered_videos.sort_values("engagement_rate", ascending=False).head(top_n)
if not top_eng.empty:
    fig_eng = px.bar(top_eng, x="title", y="engagement_rate", text=top_eng["engagement_rate"].map(lambda x: f"{x:.2%}"),
        title=f"Top {min(top_n, len(top_eng))} Videos by Engagement Rate", template=PLOTLY_THEME,
        color="engagement_rate", color_continuous_scale=px.colors.sequential.Magenta)
    st.plotly_chart(fixed_chart_layout(fig_eng), use_container_width=True)
else:
    st.info("No videos to show in engagement chart.")

st.markdown("**Engagement vs Views (bubble = likes)**")
if not filtered_videos.empty:
    fig_scatter = px.scatter(filtered_videos, x="views", y="engagement_rate", size="likes",
        hover_name="title", title="Engagement Rate vs Views", template=PLOTLY_THEME,
        color="likes", color_continuous_scale=px.colors.sequential.PuBuGn)
    st.plotly_chart(fixed_chart_layout(fig_scatter), use_container_width=True)
else:
    st.info("No data for scatter chart.")

st.subheader("Likes Distribution (Top 10)")
top_likes = filtered_videos.nlargest(10, "likes")
if not top_likes.empty:
    fig_likes = px.pie(top_likes, names="title", values="likes", title="Top 10 Videos by Likes", template=PLOTLY_THEME)
    st.plotly_chart(fixed_chart_layout(fig_likes), use_container_width=True)
if filtered_videos["dislikes"].sum() > 0:
    st.subheader("Dislikes Distribution (Top 10)")
    top_dislikes = filtered_videos.nlargest(10, "dislikes")
    fig_dislikes = px.pie(top_dislikes, names="title", values="dislikes", title="Top 10 Videos by Dislikes", template=PLOTLY_THEME)
    st.plotly_chart(fixed_chart_layout(fig_dislikes), use_container_width=True)

# ---- Latest Video Table ----
st.subheader("Latest Video Stats (Filtered)")
table_cols = ["title", "views", "likes", "dislikes", "comments", date_col] if date_col in filtered_videos.columns else ["title", "views", "likes", "dislikes", "comments"]
st.dataframe(filtered_videos[table_cols].reset_index(drop=True), use_container_width=True)

st.markdown("---")

# ===============================================
# 🧠 INSIGHTS & DECISION MAKING SECTION
# ===============================================
st.header("🧠 Smart Insights & Recommendations")

if not filtered_videos.empty:
    
    # ---- Performance Score for Each Video ----
    st.subheader("📊 Video Performance Scores")
    
    scored_videos = filtered_videos.copy()
    
    # Calculate performance score (0-100)
    max_views = scored_videos["views"].max() if scored_videos["views"].max() > 0 else 1
    max_likes = scored_videos["likes"].max() if scored_videos["likes"].max() > 0 else 1
    max_comments = scored_videos["comments"].max() if scored_videos["comments"].max() > 0 else 1
    
    scored_videos["view_score"] = (scored_videos["views"] / max_views) * 40
    scored_videos["like_score"] = (scored_videos["likes"] / max_likes) * 35
    scored_videos["comment_score"] = (scored_videos["comments"] / max_comments) * 25
    scored_videos["performance_score"] = (
        scored_videos["view_score"] + scored_videos["like_score"] + scored_videos["comment_score"]
    ).round(1)
    
    # Performance grade
    def get_grade(score):
        if score >= 80: return "🏆 A+"
        elif score >= 65: return "⭐ A"
        elif score >= 50: return "👍 B"
        elif score >= 35: return "📈 C"
        else: return "💪 D"
    
    scored_videos["grade"] = scored_videos["performance_score"].apply(get_grade)
    
    # Show top performers
    top_performers = scored_videos.nlargest(5, "performance_score")[["title", "views", "likes", "comments", "performance_score", "grade"]]
    st.markdown("**🏆 Top 5 Best Performing Videos**")
    st.dataframe(top_performers.reset_index(drop=True), use_container_width=True)
    
    # ---- Growth Velocity ----
    st.subheader("🚀 Growth Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    avg_views = filtered_videos["views"].mean()
    avg_likes = filtered_videos["likes"].mean()
    avg_engagement = filtered_videos["engagement_rate"].mean() * 100
    
    with col1:
        metric_card("Avg Views/Video", f"{avg_views:,.0f}", "👀", 
                   submetric=f"{'🟢 Good' if avg_views > 100 else '🟡 Growing'}")
    with col2:
        metric_card("Avg Likes/Video", f"{avg_likes:,.0f}", "👍",
                   submetric=f"{'🟢 Great' if avg_likes > 10 else '🟡 Building'}")
    with col3:
        metric_card("Avg Engagement", f"{avg_engagement:.2f}%", "📈",
                   submetric=f"{'🟢 Excellent' if avg_engagement > 5 else '🟡 Normal'}" if avg_engagement > 2 else "🔴 Low")
    
    # ---- Content Strategy Insights ----
    st.subheader("💡 Content Strategy Insights")
    
    # Best performing content analysis
    if len(scored_videos) >= 3:
        best_video = scored_videos.loc[scored_videos["performance_score"].idxmax()]
        worst_video = scored_videos.loc[scored_videos["performance_score"].idxmin()]
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.markdown(f"""
            <div class='metric-card'>
                <span style='font-size:24px;'>🌟</span> <b>Your Best Performer</b><br>
                <span style='color:#2ba8ea;font-size:1.1em;'>{best_video['title'][:50]}...</span><br>
                <span class='metric-chip'>Score: {best_video['performance_score']}/100</span><br>
                <small>💡 Create more content like this!</small>
            </div>
            """, unsafe_allow_html=True)
        
        with insights_col2:
            st.markdown(f"""
            <div class='metric-card'>
                <span style='font-size:24px;'>📊</span> <b>Needs Improvement</b><br>
                <span style='color:#e040fb;font-size:1.1em;'>{worst_video['title'][:50]}...</span><br>
                <span class='metric-chip'>Score: {worst_video['performance_score']}/100</span><br>
                <small>💡 Analyze what could be better</small>
            </div>
            """, unsafe_allow_html=True)
    
    # ---- AI-Powered Recommendations ----
    st.subheader("🤖 Smart Recommendations")
    
    recommendations = []
    
    # Engagement analysis
    if avg_engagement < 2:
        recommendations.append("📢 **Boost Engagement**: Your engagement rate is low. Try asking questions in your videos and encouraging comments!")
    elif avg_engagement < 5:
        recommendations.append("👍 **Good Engagement**: Your audience is responding. Keep interacting with comments to build community!")
    else:
        recommendations.append("🔥 **Amazing Engagement**: Your content resonates well! Consider going live to leverage this connection!")
    
    # View analysis
    if avg_views < 50:
        recommendations.append("🎯 **Increase Visibility**: Focus on SEO - use better titles, descriptions, and tags. Share on social media!")
    elif avg_views < 200:
        recommendations.append("📈 **Growing Views**: You're on track! Consider collaborations to reach new audiences.")
    else:
        recommendations.append("🚀 **Great Reach**: Your content is being discovered. Maintain consistent upload schedule!")
    
    # Like ratio analysis
    like_view_ratio = (filtered_videos["likes"].sum() / max(filtered_videos["views"].sum(), 1)) * 100
    if like_view_ratio < 2:
        recommendations.append("💪 **Improve Like Ratio**: Only {:.1f}% of viewers like your videos. Add a call-to-action reminder!".format(like_view_ratio))
    else:
        recommendations.append("❤️ **Solid Like Ratio**: {:.1f}% like rate is healthy. Your content quality is good!".format(like_view_ratio))
    
    # Comment analysis
    comment_ratio = (filtered_videos["comments"].sum() / max(filtered_videos["views"].sum(), 1)) * 100
    if comment_ratio < 0.5:
        recommendations.append("💬 **Encourage Discussion**: Ask thought-provoking questions to spark conversations!")
    else:
        recommendations.append("🗣️ **Active Community**: Your audience loves to engage. Reply to comments within 1 hour for maximum impact!")
    
    # Content consistency
    if len(filtered_videos) >= 5:
        recommendations.append("📅 **Consistency Tip**: Analyze your {0} videos and find patterns in your top performers.".format(len(filtered_videos)))
    
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    # ---- Quick Action Items ----
    st.subheader("✅ Your Action Items")
    
    action_items = []
    
    if avg_engagement < 3:
        action_items.append("Add 'Like & Subscribe' reminder in your next video")
    if like_view_ratio < 3:
        action_items.append("Create a more compelling thumbnail for your next upload")
    if comment_ratio < 1:
        action_items.append("End your next video with a question to viewers")
    if len(filtered_videos) < 10:
        action_items.append("Upload more consistently - aim for 1-2 videos per week")
    else:
        action_items.append("Maintain your upload schedule - consistency builds audience")
    
    action_items.append("Analyze your best performer and replicate its style")
    action_items.append("Share your next video on 3 social platforms within 24 hours")
    
    for i, item in enumerate(action_items[:5], 1):
        st.checkbox(f"{item}", key=f"action_{i}")

else:
    st.info("Upload some videos to see insights!")

# ---- Channel Health Score ----
st.markdown("---")
st.subheader("🏥 Channel Health Score")

if not channel_df.empty and not filtered_videos.empty:
    subs = int(channel_df['subscribers'].iloc[0])
    total_views = int(channel_df['total_views'].iloc[0])
    total_videos = int(channel_df['total_videos'].iloc[0])
    
    # Calculate health score
    views_per_video = total_views / max(total_videos, 1)
    views_per_sub = total_views / max(subs, 1)
    
    health_score = min(100, (
        min(30, subs / 100 * 30) +  # Subscriber score (max 30)
        min(40, views_per_video / 100 * 40) +  # Views per video (max 40)
        min(30, avg_engagement * 6)  # Engagement score (max 30)
    ))
    
    health_color = "#19be6c" if health_score >= 60 else "#f0a500" if health_score >= 40 else "#e04040"
    
    st.markdown(f"""
    <div style='text-align:center;padding:20px;'>
        <div style='font-size:80px;font-weight:bold;color:{health_color};'>{health_score:.0f}</div>
        <div style='font-size:24px;color:{BANNER_FONT_COLOR};'>out of 100</div>
        <div style='font-size:16px;color:#888;margin-top:10px;'>
            {'🌟 Excellent! Keep up the great work!' if health_score >= 70 else 
             '📈 Good progress! Room to grow!' if health_score >= 50 else 
             '💪 Building momentum! Stay consistent!'}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Health breakdown
    st.markdown("**Score Breakdown:**")
    health_col1, health_col2, health_col3 = st.columns(3)
    with health_col1:
        st.metric("Subscriber Score", f"{min(30, subs / 100 * 30):.0f}/30")
    with health_col2:
        st.metric("Content Score", f"{min(40, views_per_video / 100 * 40):.0f}/40")
    with health_col3:
        st.metric("Engagement Score", f"{min(30, avg_engagement * 6):.0f}/30")

# ---- Auto-refresh ----
count = st_autorefresh(interval=60000, key="refresh")

# ---- Footer Branding ----
st.markdown("---")
st.markdown(f"""
    <center><b>Built with ❤️ by Mayank • Powered by Python, Streamlit & YouTube API! </b><br>
    <i>"Data is clarity; analytics is action. You have both!"</i>
    <br>Auto-refreshes every 60s • <b>Premium UI • Modern Insights • Maximum Engagement</b>
    <br><a href='https://github.com/mayank-goyal09'>GitHub</a> • <a href='http://www.youtube.com/@maygal_memer'>YouTube</a></center>
""", unsafe_allow_html=True)
