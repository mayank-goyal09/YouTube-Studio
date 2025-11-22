import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

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
    .metric-card {{
        background: {'rgba(20, 20, 33, 0.80)' if theme_mode=='Dark' else 'rgba(255,255,255,0.95)'};
        border-radius: 18px;
        box-shadow: 0 4px 16px rgba(60,0,100,{0.16 if theme_mode=='Dark' else 0.10});
        padding: 16px;
        backdrop-filter: blur(6px);
        color: {METRIC_FONT_COLOR};
        margin-bottom: 18px;
    }}
    .metric-chip {{
        display: inline-block;
        background: {METRIC_CHIP_BG};
        color: #19be6c;
        font-weight: 700;
        font-size: 1.05em;
        border-radius: 16px;
        padding: 4px 13px;
        margin-top: 6px;
        margin-bottom: 6px;
    }}
    [data-testid="stSidebar"] {{ background: {'#222237' if theme_mode=='Dark' else '#f9fafc'}; color:{BANNER_FONT_COLOR if theme_mode=='Dark' else METRIC_FONT_COLOR}; }}
    hr {{ border-top: 2px solid #2ba8ea; }}
    </style>
""", unsafe_allow_html=True)

# ---- PostgreSQL Connection ----
import os

# Try to use Streamlit secrets first, fallback to local if running locally
try:
    DATABASE_URL = st.secrets["DATABASE_URL"]
except:
    # Local development fallback
    DATABASE_URL = "postgresql+psycopg2://postgres:itsmaygal02@localhost:5432/youtube_dashboard"

engine = create_engine(DATABASE_URL)


# ---- Page Config & Banners ----
st.set_page_config(page_title="YouTube Analytics • Modern Premium", layout="wide")
st.title("✨ YouTube Channel Analytics Dashboard")

st.markdown(f"""
<h3 style='font-weight:700; color:{BANNER_FONT_COLOR};'>
  Where data meets strategy, and people inspire results.<br>
  <span style='font-size:20px;color:#2ba8ea;'>
    Designed by Mayank Goyal — Empowering decisions, creating growth, leading with purpose.
  </span> 🚀
</h3>
<h3 style='font-weight:700;margin-top:10px; color:{BANNER_FONT_COLOR};'>
  Great data, great decisions! 💡 Keep pushing limits, Mayank! <span style='font-size:24px;'>🦄</span>
</h3>
""", unsafe_allow_html=True)

# ---- Cached Data Load ----
@st.cache_data(ttl=45)
def load_tables():
    channel_latest = pd.read_sql("SELECT * FROM channel_stats ORDER BY fetched_at DESC LIMIT 1", engine)
    channel_history = pd.read_sql("SELECT * FROM channel_stats ORDER BY fetched_at ASC", engine)
    videos = pd.read_sql("SELECT * FROM video_stats ORDER BY fetched_at DESC", engine)
    return channel_latest, channel_history, videos

channel_df, channel_history_df, videos_df = load_tables()

# ---- Date & Sidebar Controls ----
for df, dcol in [(channel_history_df, "fetched_at"), (videos_df, "fetched_at"), (videos_df, "published_at")]:
    if dcol in df.columns:
        df[dcol] = pd.to_datetime(df[dcol])

st.sidebar.header("🔎 Filters & Controls")
st.sidebar.caption("Welcome, legend! Choose your style, set filters & let’s analyze 🎨")

date_col = "published_at" if "published_at" in videos_df.columns else "fetched_at"
min_date = videos_df[date_col].min().date() if date_col in videos_df.columns else None
max_date = videos_df[date_col].max().date() if date_col in videos_df.columns else None
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date) if min_date and max_date else []
start_date, end_date = date_range if len(date_range)==2 else (min_date, max_date)
top_n = st.sidebar.slider("Top N Videos to Show", min_value=5, max_value=30, value=10, step=1)
if st.sidebar.button("🔄 Manual Data Refresh"):
    st.cache_data.clear()
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.caption("Auto-refresh every 60s")

# ---- Data Preparation ----
filtered_videos = videos_df.copy()
if start_date and end_date:
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered_videos = filtered_videos[(filtered_videos[date_col] >= start_ts) & (filtered_videos[date_col] <= end_ts)]
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
        xaxis=dict(color=AXIS_FONT_COLOR, showgrid=False, zeroline=False),
        yaxis=dict(color=AXIS_FONT_COLOR, showgrid=False, zeroline=False)
    )
    return fig

st.subheader("📈 Subscriber Growth")
if not channel_history_df.empty:
    ch = channel_history_df.copy()
    ch["fetched_at"] = pd.to_datetime(ch["fetched_at"])
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

# ---- Auto-refresh ----
count = st_autorefresh(interval=60000, key="refresh")

# ---- Footer Branding ----
st.markdown("---")
st.markdown(f"""
    <center><b>Built with ❤️ by Mayank • Powered by Python, Streamlit & YouTube API! </b><br>
    <i>“Data is clarity; analytics is action. You have both!”</i>
    <br>Auto-refreshes every 60s • <b>Premium UI • Modern Insights • Maximum Engagement</b>
    <br><a href='https://github.com/spacrece'>GitHub</a></center>
""", unsafe_allow_html=True)

