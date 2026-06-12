# =============================================================================
# MOVIE RECAP AI — app.py
# =============================================================================
# requirements.txt (paste into your requirements.txt file):
#   streamlit>=1.35.0
#   google-generativeai>=0.7.0
#   yt-dlp>=2024.5.0
# =============================================================================

import streamlit as st
import google.generativeai as genai
import yt_dlp
import os
import time
import tempfile
import re

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎬 Movie Recap AI",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── MOBILE-FIRST CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Import cinematic font ── */
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600&display=swap');

  /* ── Root tokens ── */
  :root {
    --bg:       #0d0d0f;
    --surface:  #17171c;
    --border:   #2a2a35;
    --accent:   #e5c35b;   /* warm gold — film-reel amber */
    --accent2:  #c0392b;   /* deep-cut red — danger/peak-emotion */
    --text:     #e8e8e8;
    --muted:    #888;
    --radius:   10px;
  }

  /* ── Global resets ── */
  html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    line-height: 1.6;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Tight mobile container ── */
  .block-container {
    padding: 0.75rem 0.85rem 2rem !important;
    max-width: 100% !important;
  }

  /* ── App header ── */
  .app-header {
    text-align: center;
    padding: 1.1rem 0 0.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.9rem;
  }
  .app-header h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.1rem;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin: 0;
  }
  .app-header p {
    font-size: 0.78rem;
    color: var(--muted);
    margin: 0.25rem 0 0;
  }

  /* ── Tabs ── */
  .stTabs [role="tablist"] {
    border-bottom: 1px solid var(--border);
    gap: 0;
    flex-wrap: nowrap;
    overflow-x: auto;
  }
  .stTabs [role="tab"] {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 0.5rem 0.75rem;
    color: var(--muted) !important;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
    background: transparent !important;
  }
  .stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
  }
  .stTabs [role="tabpanel"] { padding-top: 0.8rem; }

  /* ── Inputs ── */
  .stTextInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-size: 0.9rem;
    padding: 0.55rem 0.75rem !important;
  }
  .stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(229,195,91,0.18) !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: var(--accent) !important;
    color: #0d0d0f !important;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.05rem;
    letter-spacing: 0.07em;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 0.55rem 1.4rem !important;
    width: 100%;
    cursor: pointer;
    transition: opacity 0.15s;
  }
  .stButton > button:hover { opacity: 0.85; }

  /* ── Download buttons ── */
  .stDownloadButton > button {
    background: var(--surface) !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    border-radius: var(--radius) !important;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    width: 100%;
  }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text) !important;
    padding: 0.65rem 0.85rem !important;
  }
  .streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius) var(--radius) !important;
    padding: 0.85rem !important;
  }

  /* ── Info / warning / error boxes ── */
  .stAlert {
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    font-size: 0.84rem;
  }

  /* ── Video player ── */
  .stVideo { border-radius: var(--radius); overflow: hidden; }

  /* ── Metric cards ── */
  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.7rem 0.85rem;
    margin-bottom: 0.6rem;
    font-size: 0.82rem;
  }
  .stat-card .label { color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat-card .value { font-family: 'Bebas Neue', sans-serif; font-size: 1.35rem; color: var(--accent); }

  /* ── Genre pill buttons ── */
  .genre-pill {
    display: inline-block;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.3rem 0.75rem;
    margin: 0.2rem;
    font-size: 0.78rem;
    cursor: pointer;
    color: var(--text);
  }

  /* ── Spinner override ── */
  .stSpinner > div { border-top-color: var(--accent) !important; }

  /* ── Selectbox ── */
  .stSelectbox div[data-baseweb="select"] {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: var(--surface) !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─── APP HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>🎬 Movie Recap AI</h1>
  <p>Powered by Gemini 1.5 Flash · Scenes · Timestamps · Voice-Over Scripts</p>
</div>
""", unsafe_allow_html=True)


# ─── SIDEBAR: API KEY ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="Paste your API key here…",
        help="Get a free key at aistudio.google.com"
    )
    st.markdown("""
    <div style='font-size:0.72rem; color:#888; margin-top:0.5rem;'>
    🔒 Your key is used only for this session and never stored.
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("**How it works**")
    st.markdown("""
    <div style='font-size:0.78rem; color:#aaa;'>
    1. Enter a movie title<br>
    2. App fetches real scene clips via yt-dlp<br>
    3. Clip is uploaded to Gemini 1.5 Flash<br>
    4. AI returns timestamps + voice-over script<br>
    5. Temp file is deleted automatically
    </div>
    """, unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def configure_gemini(api_key: str):
    """Configure the Gemini SDK with the provided key."""
    genai.configure(api_key=api_key)


def search_and_download_clip(movie_title: str) -> tuple[str | None, str | None, str | None]:
    """
    Use yt-dlp to:
      1. Search YouTube for best movie scene compilation (not trailers).
      2. Return the YouTube URL of the top result.
      3. Download a low-res version to a temp file.

    Returns: (youtube_url, local_file_path, video_title) or (None, None, None) on failure.
    """
    # Craft query to target scene compilations, not trailers
    search_queries = [
        f"{movie_title} best scenes compilation",
        f"{movie_title} all movie clips",
        f"{movie_title} memorable scenes",
    ]

    ydl_search_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,   # fast metadata-only first pass
        "default_search": "ytsearch5",
    }

    youtube_url = None
    video_title = None

    for query in search_queries:
        try:
            with yt_dlp.YoutubeDL(ydl_search_opts) as ydl:
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                if info and "entries" in info:
                    for entry in info["entries"]:
                        title_lower = (entry.get("title") or "").lower()
                        # Skip obvious trailers, teasers, reviews
                        skip_terms = ["trailer", "teaser", "review", "reaction", "explained"]
                        if any(t in title_lower for t in skip_terms):
                            continue
                        youtube_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        video_title = entry.get("title", movie_title)
                        break
                if youtube_url:
                    break
        except Exception:
            continue

    if not youtube_url:
        return None, None, None

    # Download a compressed, low-quality version for Gemini processing
    tmp_dir = tempfile.gettempdir()
    output_template = os.path.join(tmp_dir, "movie_clip_%(id)s.%(ext)s")

    ydl_download_opts = {
        "quiet": True,
        "no_warnings": True,
        # Low-res to conserve bandwidth / disk on Codespaces
        "format": "worstvideo[ext=mp4]+bestaudio[ext=m4a]/worstvideo/worst[ext=mp4]/worst",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        # Limit download size: max 80 MB
        "max_filesize": 80 * 1024 * 1024,
        # Only first 3 minutes — stream-level chunking (more reliable than postprocessor trim)
        "download_ranges": lambda info, ctx: [{"start_time": 0, "end_time": 180}],
        "force_keyframes_at_cuts": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_download_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            # Find the actual output filename
            video_id = info.get("id", "")
            for fname in os.listdir(tmp_dir):
                if video_id in fname and fname.endswith(".mp4"):
                    local_path = os.path.join(tmp_dir, fname)
                    return youtube_url, local_path, video_title
    except Exception as e:
        st.warning(f"Download note: {e}")

    return youtube_url, None, video_title


def upload_to_gemini(local_path: str) -> object | None:
    """
    Upload a local video file to the Gemini Files API.
    Polls until the file state is ACTIVE.
    Returns the file object or None on failure.
    """
    try:
        video_file = genai.upload_file(path=local_path, mime_type="video/mp4")
        # Polling loop — wait until Gemini finishes processing
        max_wait = 120  # seconds
        elapsed = 0
        while video_file.state.name == "PROCESSING":
            if elapsed >= max_wait:
                st.error("⏱ Gemini video processing timed out. Try a shorter clip.")
                return None
            time.sleep(5)
            elapsed += 5
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            st.error("❌ Gemini rejected the video file.")
            return None

        return video_file
    except Exception as e:
        st.error(f"Gemini upload error: {e}")
        return None


def generate_timestamps(video_file: object, movie_title: str) -> str:
    """
    Ask Gemini to produce emotional cadence timestamps for the video.
    """
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = f"""
You are a professional film analyst watching a video clip compilation from the movie "{movie_title}".

Analyze the video carefully and produce a detailed **Emotional Cadence Timestamp Guide**.

Format each entry exactly like this:
⏱ [MM:SS] — **[Scene Label]** (Tone: ACTION / TENSION / EMOTION / HUMOR / CALM)
→ [2-sentence scene summary describing what happens and why it matters emotionally]

Rules:
- Include at least 10 timestamps evenly spread through the video.
- Accurately identify HIGH-ACTION beats, EMOTIONAL SHIFTS, and NARRATIVE PEAKS.
- Be specific about characters and actions — do not be vague.
- End with a short paragraph: "Narrative Arc Summary:" describing the emotional journey of the full clip.
"""
    try:
        response = model.generate_content([video_file, prompt])
        return response.text
    except Exception as e:
        return f"Error generating timestamps: {e}"


def generate_voiceover_script(video_file: object, movie_title: str) -> str:
    """
    Ask Gemini to write a retention-optimized voice-over recap script.
    """
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = f"""
You are a top-tier YouTube/TikTok movie recap creator known for viral, binge-worthy content.

Watch this video clip compilation from "{movie_title}" and write a **complete voice-over script** for a 60–90 second movie recap video.

Requirements:
1. **Hook (5 sec):** Start with a shocking question or statement that grabs attention instantly.
2. **Setup (10 sec):** Introduce the world, the stakes, and the main character in two punchy sentences.
3. **Rising Action (25 sec):** Walk through key plot beats in a fast-paced, energetic tone. Use present tense. Use short sentences. Build tension.
4. **Climax (15 sec):** Describe the peak emotional moment with maximum drama. This is your loudest, most intense section.
5. **Resolution & Hook-Out (10 sec):** Wrap up the ending, then drop a thought-provoking final line that makes viewers want to watch the full movie.

Style rules:
- Write exactly as the words will be spoken aloud — no headers in the final script.
- Use natural speech rhythm with strategic pauses marked as [PAUSE].
- Include [MUSIC UP], [MUSIC DOWN], and [SFX: description] cues where appropriate.
- Maximum energy. Every sentence must earn its place.

Output format:
---
VOICE-OVER SCRIPT: {movie_title.upper()} RECAP
---
[full script here]
---
ESTIMATED RUNTIME: ~[X] seconds
"""
    try:
        response = model.generate_content([video_file, prompt])
        return response.text
    except Exception as e:
        return f"Error generating script: {e}"


def cleanup_file(local_path: str):
    """Strictly delete the local temp video file after processing."""
    try:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
    except Exception:
        pass  # Silent fail — file may already be gone


def get_youtube_embed_id(url: str) -> str | None:
    """Extract YouTube video ID from a URL."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for pat in patterns:
        match = re.search(pat, url)
        if match:
            return match.group(1)
    return None


# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
for key in ["youtube_url", "video_title", "timestamps", "voiceover", "processing_done"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "processing_done" not in st.session_state:
    st.session_state.processing_done = False


# ─── MAIN TABS ───────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎬 Movie Dashboard", "🎭 Genre Discovery", "🌍 Global Search"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MOVIE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    movie_title = st.text_input(
        "🎥 Movie Title",
        placeholder="e.g.  Interstellar, Inception, The Dark Knight…",
        label_visibility="collapsed",
    )

    run_button = st.button("🔍 Fetch & Analyze Clips", key="run_main")

    if run_button:
        # ── Validation ────────────────────────────────────────────────────
        if not api_key_input.strip():
            st.error("🔑 Please paste your Gemini API Key in the sidebar first.")
            st.stop()
        if not movie_title.strip():
            st.warning("Please enter a movie title.")
            st.stop()

        configure_gemini(api_key_input.strip())

        # ── Step 1: Search + Download ─────────────────────────────────────
        with st.spinner("🔎 Searching YouTube for scene compilations…"):
            yt_url, local_path, vid_title = search_and_download_clip(movie_title.strip())

        if not yt_url:
            st.error("Could not find a matching clip on YouTube. Try a different movie title.")
            st.stop()

        st.session_state.youtube_url = yt_url
        st.session_state.video_title = vid_title or movie_title

        # ── Step 2: Upload to Gemini ──────────────────────────────────────
        timestamps_text = ""
        voiceover_text = ""

        if local_path:
            with st.spinner("📤 Uploading clip to Gemini 1.5 Flash…"):
                video_file = upload_to_gemini(local_path)

            if video_file:
                # ── Step 3: Generate AI outputs ───────────────────────────
                with st.spinner("⏱ Generating emotional cadence timestamps…"):
                    timestamps_text = generate_timestamps(video_file, movie_title.strip())

                with st.spinner("🎙 Writing voice-over recap script…"):
                    voiceover_text = generate_voiceover_script(video_file, movie_title.strip())

                # ── Step 4: Cleanup — local file + Gemini cloud file ──────
                cleanup_file(local_path)
                try:
                    genai.delete_file(video_file.name)
                except Exception:
                    pass
            else:
                cleanup_file(local_path)
                st.warning("⚠️ Gemini processing failed. Showing video only (no AI analysis).")
        else:
            st.info("ℹ️ Video download was skipped (size/format limit). Showing YouTube player only.")

        st.session_state.timestamps = timestamps_text
        st.session_state.voiceover = voiceover_text
        st.session_state.processing_done = True

    # ── Render results ────────────────────────────────────────────────────
    if st.session_state.processing_done and st.session_state.youtube_url:

        st.markdown(f"""
        <div style='background:#17171c; border:1px solid #2a2a35; border-radius:10px;
                    padding:0.6rem 0.85rem; margin-bottom:0.8rem; font-size:0.82rem;'>
          <span style='color:#888; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.05em;'>
            Clip Found
          </span><br>
          <span style='color:#e5c35b; font-weight:600;'>
            {st.session_state.video_title or "Scene Compilation"}
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Video player
        st.video(st.session_state.youtube_url)

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

        # ── Expander 1: Timestamps ────────────────────────────────────────
        with st.expander("⏱ Emotional Cadence Timestamps", expanded=True):
            if st.session_state.timestamps:
                st.markdown(st.session_state.timestamps)
                st.download_button(
                    label="⬇️ Download Timestamps (.txt)",
                    data=st.session_state.timestamps,
                    file_name=f"{(st.session_state.video_title or movie_title).replace(' ','_')}_timestamps.txt",
                    mime="text/plain",
                    key="dl_timestamps",
                )
            else:
                st.info("No timestamp data — Gemini analysis was not completed for this clip.")

        # ── Expander 2: Voice-Over Script ─────────────────────────────────
        with st.expander("🎙 Movie Recap Voice-Over Script", expanded=False):
            if st.session_state.voiceover:
                st.markdown(st.session_state.voiceover)
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        label="⬇️ Download Script (.txt)",
                        data=st.session_state.voiceover,
                        file_name=f"{(st.session_state.video_title or movie_title).replace(' ','_')}_voiceover.txt",
                        mime="text/plain",
                        key="dl_script",
                    )
                with col_b:
                    st.download_button(
                        label="📋 Copy as Markdown",
                        data=f"# Voice-Over Script\n\n{st.session_state.voiceover}",
                        file_name=f"{(st.session_state.video_title or movie_title).replace(' ','_')}_script.md",
                        mime="text/markdown",
                        key="dl_script_md",
                    )
            else:
                st.info("No script generated — Gemini analysis was not completed for this clip.")

    elif not st.session_state.processing_done:
        # Welcome state
        st.markdown("""
        <div style='text-align:center; padding:2.5rem 1rem; color:#555;'>
          <div style='font-size:2.8rem; margin-bottom:0.5rem;'>🎞️</div>
          <div style='font-size:0.88rem;'>Enter a movie title above and tap<br>
          <strong style='color:#e5c35b;'>Fetch & Analyze Clips</strong> to begin.</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GENRE DISCOVERY
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 🎭 Discover Movies by Genre")
    st.markdown("<div style='font-size:0.8rem; color:#888; margin-bottom:0.8rem;'>Select a genre and let Gemini recommend must-watch films with short recaps.</div>", unsafe_allow_html=True)

    GENRES = [
        "Action", "Sci-Fi", "Drama", "Thriller",
        "Horror", "Romance", "Animation", "Crime",
        "Comedy", "Fantasy", "Documentary", "Mystery",
    ]

    selected_genre = st.selectbox("Choose a genre", GENRES, label_visibility="collapsed")

    mood = st.selectbox(
        "Mood filter",
        ["Any mood", "Mind-bending", "Feel-good", "Dark & intense", "Epic & sweeping", "Funny & light"],
        label_visibility="collapsed",
    )

    if st.button("🎲 Generate Recommendations", key="genre_btn"):
        if not api_key_input.strip():
            st.error("🔑 Please add your Gemini API Key in the sidebar.")
        else:
            configure_gemini(api_key_input.strip())
            model = genai.GenerativeModel("gemini-1.5-flash")
            mood_clause = "" if mood == "Any mood" else f" The mood should be: {mood}."
            prompt = f"""
You are a cinephile and expert film curator.

Recommend exactly 5 {selected_genre} movies.{mood_clause}

For each movie, provide:
**[RANK]. [Movie Title] ([Year])**
⭐ [IMDb-style score out of 10]
🎬 *[One punchy tagline sentence]*
📖 [3-sentence plot summary — no spoilers, build intrigue]
💡 **Why watch it:** [One sentence explaining the unique hook]

Separate each entry with a horizontal rule (---).
Keep the energy high and the language vivid.
"""
            with st.spinner(f"Finding the best {selected_genre} films…"):
                try:
                    resp = model.generate_content(prompt)
                    st.markdown(resp.text)
                except Exception as e:
                    st.error(f"Gemini error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — GLOBAL SEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 🌍 Global Movie Search")
    st.markdown("<div style='font-size:0.8rem; color:#888; margin-bottom:0.8rem;'>Ask anything about movies — cast, plot, comparisons, trivia.</div>", unsafe_allow_html=True)

    free_query = st.text_area(
        "Ask anything about movies",
        placeholder="e.g. What are the best Christopher Nolan films ranked by emotional depth?\nOr: Compare the cinematography of Blade Runner 2049 and Dune.",
        height=110,
        label_visibility="collapsed",
    )

    search_mode = st.selectbox(
        "Response style",
        ["Detailed Analysis", "Quick Summary", "Fun Facts", "Critical Breakdown"],
        label_visibility="collapsed",
    )

    if st.button("🔮 Ask Gemini", key="global_search_btn"):
        if not api_key_input.strip():
            st.error("🔑 Please add your Gemini API Key in the sidebar.")
        elif not free_query.strip():
            st.warning("Please enter a question.")
        else:
            configure_gemini(api_key_input.strip())
            model = genai.GenerativeModel("gemini-1.5-flash")

            style_instructions = {
                "Detailed Analysis": "Write a thorough, expert-level analysis with examples and context.",
                "Quick Summary": "Be concise — answer in under 150 words with bullet points.",
                "Fun Facts": "Share surprising, little-known facts in a lively, engaging tone.",
                "Critical Breakdown": "Analyze like a film critic: strengths, weaknesses, cultural impact.",
            }

            full_prompt = f"""
You are a world-class film scholar and entertaining movie analyst.

User question: {free_query.strip()}

Response style: {style_instructions[search_mode]}

Use markdown formatting. Include relevant movie titles in **bold**.
"""
            with st.spinner("🔍 Searching Gemini's film knowledge…"):
                try:
                    resp = model.generate_content(full_prompt)
                    st.markdown(resp.text)
                    st.download_button(
                        label="⬇️ Save Response",
                        data=resp.text,
                        file_name="gemini_movie_search.txt",
                        mime="text/plain",
                        key="dl_search",
                    )
                except Exception as e:
                    st.error(f"Gemini error: {e}")

    # ── Static quick-start prompts ─────────────────────────────────────────
    st.divider()
    st.markdown("<div style='font-size:0.75rem; color:#888; margin-bottom:0.4rem;'>💡 Try asking:</div>", unsafe_allow_html=True)
    quick_prompts = [
        "Top 5 movies with unreliable narrators",
        "Best sci-fi films of the last decade",
        "Movies like Parasite but in English",
        "Explain the ending of Mulholland Drive",
    ]
    for qp in quick_prompts:
        st.markdown(f"<div class='stat-card'><span style='color:#e5c35b;'>›</span> {qp}</div>", unsafe_allow_html=True)
