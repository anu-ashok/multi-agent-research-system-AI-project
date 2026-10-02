import re

import streamlit as st

st.set_page_config(page_title="Research Assistant", page_icon="🔎", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    :root {
        --bg: #0b1020;
        --surface: #141b2f;
        --surface-2: #1b2440;
        --border: #2a3558;
        --text: #e6edf7;
        --muted: #8b97b1;
        --teal: #2dd4bf;
        --amber: #fbbf24;
        --violet: #8b5cf6;
        --rose: #fb7185;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 80% -10%, #1a2350 0%, var(--bg) 55%);
        color: var(--text);
    }
    .block-container {max-width: 1100px; padding-top: 2rem;}

    /* Hero */
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(45,212,191,.16), rgba(139,92,246,.18));
        border: 1px solid var(--border);
        margin-bottom: 1.4rem;
    }
    .hero h1 {
        margin: 0; padding: 0;
        font-size: 2.2rem;
        background: linear-gradient(90deg, var(--teal), var(--violet) 70%, var(--amber));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {color: var(--muted); margin: .4rem 0 0 0; font-size: 1.02rem;}

    /* Pipeline chips */
    .chips {display: flex; gap: .6rem; flex-wrap: wrap; margin-top: 1rem;}
    .chip {
        padding: .3rem .8rem; border-radius: 999px; font-size: .85rem;
        border: 1px solid var(--border); background: var(--surface);
    }
    .chip.s1 {color: var(--teal); border-color: rgba(45,212,191,.5);}
    .chip.s2 {color: var(--amber); border-color: rgba(251,191,36,.5);}
    .chip.s3 {color: var(--violet); border-color: rgba(139,92,246,.6);}
    .chip.s4 {color: var(--rose); border-color: rgba(251,113,133,.5);}

    /* Form card */
    [data-testid="stForm"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
    }
    .stTextInput input {
        background: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }
    .stTextInput input:focus {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 2px rgba(45,212,191,.25) !important;
    }

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
        border-radius: 10px; font-weight: 600; border: 1px solid var(--border);
        transition: transform .08s ease;
    }
    .stFormSubmitButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primaryFormSubmit"] {
        background: linear-gradient(90deg, var(--teal), var(--violet));
        color: #07101f; border: none;
    }
    .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px); border-color: var(--teal);
    }
    .stDownloadButton > button {background: var(--surface-2); color: var(--teal);}

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] h2 {color: var(--teal);}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {gap: .4rem; border-bottom: 1px solid var(--border);}
    .stTabs [data-baseweb="tab"] {color: var(--muted); padding: .5rem 1rem;}
    .stTabs [aria-selected="true"] {color: var(--teal) !important;}
    .stTabs [data-baseweb="tab-highlight"] {background-color: var(--teal) !important;}

    /* Status box */
    [data-testid="stStatus"] {
        background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    }

    /* Report text */
    .stTabs [data-testid="stMarkdownContainer"] h2 {color: var(--teal);}
    .stTabs [data-testid="stMarkdownContainer"] h3 {color: var(--amber);}
    .stTabs [data-testid="stMarkdownContainer"] a {color: var(--violet);}

    /* Score badge */
    .score {
        display: inline-block; padding: .5rem 1.1rem; border-radius: 12px;
        font-weight: 700; font-size: 1.3rem; margin-bottom: 1rem;
        border: 1px solid currentColor;
    }
    .score.good {color: var(--teal); background: rgba(45,212,191,.12);}
    .score.ok   {color: var(--amber); background: rgba(251,191,36,.12);}
    .score.low  {color: var(--rose); background: rgba(251,113,133,.12);}

    .topic-title {color: var(--text); margin: 1.4rem 0 .6rem 0; font-size: 1.5rem; font-weight: 700;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Multi-Agent Research Assistant</h1>
        <p>Four agents turn a topic into a sourced, reviewed report.</p>
        <div class="chips">
            <span class="chip s1">Search</span>
            <span class="chip s2">Read</span>
            <span class="chip s3">Write</span>
            <span class="chip s4">Review</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("How it works")
    st.markdown(
        "1. **Search agent** finds recent sources\n"
        "2. **Reader agent** scrapes the best URL\n"
        "3. **Writer** drafts the report\n"
        "4. **Critic** scores and reviews it"
    )
    st.divider()
    if st.button("Clear results", use_container_width=True):
        st.session_state.pop("state", None)
        st.session_state.pop("topic", None)
        st.rerun()


# ---------- Pipeline (same steps as pipeline.py, with live progress) ----------
def run_pipeline(topic: str) -> dict:
    from agents import build_search_agent, reader_agent, writer_chain, critic_chain

    state = {}

    with st.status("Running research pipeline...", expanded=True) as status:
        st.write("🔎 Step 1/4: Search agent is finding sources...")
        search_result = build_search_agent().invoke(
            {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
        )
        state["search_results"] = search_result["messages"][-1].content

        st.write("📖 Step 2/4: Reader agent is scraping the top resource...")
        reader_result = reader_agent().invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{state['search_results'][:800]}",
                    )
                ]
            }
        )
        state["scraped_content"] = reader_result["messages"][-1].content

        st.write("✍️ Step 3/4: Writer is drafting the report...")
        research_combined = (
            f"SEARCH RESULTS : \n {state['search_results']} \n\n"
            f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})

        st.write("🧐 Step 4/4: Critic is reviewing the report...")
        state["feedback"] = critic_chain.invoke({"report": state["report"]})

        status.update(label="Research complete", state="complete", expanded=False)

    return state


# ---------- Input ----------
with st.form("topic_form"):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Impact of solid-state batteries on electric vehicles",
    )
    submitted = st.form_submit_button("Start research", type="primary")

if submitted:
    if not topic.strip():
        st.warning("Enter a topic to start.")
    else:
        try:
            st.session_state["state"] = run_pipeline(topic.strip())
            st.session_state["topic"] = topic.strip()
        except Exception as e:
            st.error(f"The pipeline failed: {e}")

# ---------- Results ----------
state = st.session_state.get("state")
if state:
    st.markdown(
        f'<div class="topic-title">{st.session_state.get("topic", "")}</div>',
        unsafe_allow_html=True,
    )

    tab_report, tab_feedback, tab_search, tab_scrape = st.tabs(
        ["Report", "Critic feedback", "Search results", "Scraped content"]
    )

    with tab_report:
        st.markdown(state["report"])
        st.download_button(
            "Download report (.md)",
            data=state["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        match = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", state["feedback"])
        if match:
            score = float(match.group(1))
            level = "good" if score >= 8 else "ok" if score >= 6 else "low"
            st.markdown(
                f'<div class="score {level}">Score {match.group(1)}/10</div>',
                unsafe_allow_html=True,
            )
        st.markdown(state["feedback"])

    with tab_search:
        st.text(state["search_results"])

    with tab_scrape:
        st.text(state["scraped_content"])