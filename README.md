<div align="center">

  <img src="https://capsule-render.vercel.app/api?type=waving&color=FF0000&height=300&section=header&text=YouTube%20Analytics%20Pro&fontSize=70&fontColor=ffffff&fontAlign=50&desc=AI-Powered%20•%20Real-Time%20•%20Secure&descAlign=50" alt="YouTube Analytics Header" width="100%"/>

  <br>

  [![Status](https://img.shields.io/badge/Status-Live_Production-success?style=for-the-badge&logo=youtube)](https://youtube-dashboard-appql-w6tacoledpx4fgpmkdtth4.streamlit.app/)
  [![Views](https://img.shields.io/github/languages/top/mayank-goyal09/youtube-analytics-dashboard?style=for-the-badge&color=FF0000)](https://github.com/mayank-goyal09/youtube-analytics-dashboard)
  [![Likes](https://img.shields.io/github/stars/mayank-goyal09/youtube-analytics-dashboard?style=for-the-badge&logo=star&color=FFD700)](https://github.com/mayank-goyal09/youtube-analytics-dashboard/stargazers)
  [![Subscribers](https://img.shields.io/github/followers/mayank-goyal09?style=for-the-badge&logo=github&color=333)](https://github.com/mayank-goyal09)

  <br>
  
  <p align="center">
    <b>Turn Data into Views. Turn Analytics into Action.</b><br>
    <i>A premium, automated dashboard for content creators who treat their channel like a business.</i>
  </p>
  
  <br>
  
  [🎬  **WATCH LIVE DEMO**](https://youtube-dashboard-appql-w6tacoledpx4fgpmkdtth4.streamlit.app/)
  
</div>

---

<div align="center">
  <h2>🔥🔥 TRENDING NOW: FEATURES 🔥🔥</h2>
</div>

> **"This isn't just a dashboard. It's your channel's co-pilot."**

| Feature | Description |
| :--- | :--- |
| **📈 Live Stats Engine** | Real-time tracking of **Subscribers**, **Views**, and **Engagement** automatically fetched from YouTube API. |
| **🧠 AI Advisor** | Built-in logic that grades your videos (A+, B, C) and gives **Actionable Strategy Recommendations**. |
| **🎯 Growth Velocity** | Smart metrics that tell you if your channel momentum is "Exploding", "Steady", or "Stagnant". |
| **🌗 Day/Night Mode** | A stunning UI that adapts to your vibe. **Cyberpunk Dark** for late-night coding, **Clean Light** for presentations. |
| **🔒 Zero-Config Database** | Migrated from cloud PostgreSQL to **local SQLite** for instant, secure, and offline-ready deployment. |

---

## 📽️ **BEHIND THE SCENES: THE ARCHITECTURE**

### **The "Why I Switched" Story**
*From PostgreSQL Enterprise to SQLite Embedded*

Initially, I built this system on **PostgreSQL (Neon DB)** to mirror enterprise standards. It was powerful, but it had a flaw for an open-source tool: **Friction.**

To run it, you needed a cloud account, connection strings, and network whitelisting. That's too much work for a portfolio project.

**My Solution:**
I refactored the entire backend to **SQLite**.
*   ✅ **Instant Setup:** `git clone` -> `run`. No database server required.
*   ✅ **Security:** Your API keys and data stay on YOUR machine.
*   ✅ **Portability:** The entire app lives in one folder.

> *I have the skills to manage complex cloud databases, but the wisdom to choose the simple, elegant solution for the user.*

---

## �️ **PRODUCTION GEAR (TECH STACK)** �️

<div align="center">

| **Core** | **Data & Logic** | **Visuals** | **Infrastructure** |
| :---: | :---: | :---: | :---: |
| ![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white) | ![Pandas](https://img.shields.io/badge/Pandas-Data-150458?style=flat-square&logo=pandas&logoColor=white) | ![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) | ![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) | ![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75?style=flat-square&logo=plotly&logoColor=white) | ![GitHub](https://img.shields.io/badge/GitHub-Version_Control-181717?style=flat-square&logo=github&logoColor=white) |

</div>

---

## 🎬 **GET STARTED (INSTALLATION)**

### **1. Setup Your Studio**
Clone the repo and enter the directory:
```bash
git clone https://github.com/mayank-goyal09/youtube-analytics-dashboard.git
cd youtube-analytics-dashboard
```

### **2. Install Equipment**
Install the necessary Python libraries:
```bash
pip install -r requirements.txt
```

### **3. Go Live! (Running the App)**
**Option A: Instant Demo Mode (No API Key Needed)** 🚀
Just run this command to populate the dashboard with sample data:
```bash
python init_demo_data.py
streamlit run youtube_dashboard.py
```

**Option B: Real-Time Data (Your Channel)** 🔴
1.  Get your **YouTube Data API Key**.
2.  Create a `.env` file:
    ```env
    YOUTUBE_API_KEY=your_key_here
    YOUTUBE_CHANNEL_ID=your_channel_id
    ```
3.  Run the fetcher:
    ```bash
    python youtube_fetch.py
    ```

---

<div align="center">
  <h2>� LIKE, COMMENT & CONNECT �</h2>
  
  <a href="https://github.com/mayank-goyal09">
    <img src="https://img.shields.io/badge/GitHub-Follow_Me-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  </a>
  <a href="https://www.linkedin.com/in/mayank-goyal-mg09/">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
  </a>
  <a href="https://mayank-goyal09.github.io/">
    <img src="https://img.shields.io/badge/Portfolio-Visit_My_Work-00C853?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Portfolio"/>
  </a>
  <a href="http://www.youtube.com/@maygal_memer">
    <img src="https://img.shields.io/badge/YouTube-Subscribe-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube Channel"/>
  </a>

  <br><br>
  
  <img src="https://capsule-render.vercel.app/api?type=waving&color=333&height=100&section=footer&text=Created%20by%20Mayank%20Goyal&fontSize=24&fontColor=ffffff" width="100%"/>
</div>
