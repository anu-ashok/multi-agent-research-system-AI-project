# multi-agent-research-system-AI-project



# 🔎 Multi-Agent Research Assistant

A multi-agent research system that turns a single topic into a **sourced, structured and peer-reviewed research report**. Four specialised AI components (Search → Read → Write → Review) work in sequence, each passing its output to the next. It runs either as a **command-line pipeline** or as a **Streamlit web app** with live progress.

---

## ✨ Features

- **Automated web research** using the Tavily search API
- **Deep reading** of the most relevant source via web scraping
- **Structured report generation** (Introduction, Key Findings, Conclusion, Sources)
- **Automated critique** with a score out of 10, strengths, and areas to improve
- **Streamlit UI** with live step-by-step status, tabbed results, score badge and Markdown download
- **CLI mode** for quick terminal runs

---

## 🧠 How It Works

The system is a sequential 4-stage pipeline. Each stage writes its result into a shared `state` dictionary, which is then fed to the next stage.

```
 Topic
   │
   ▼
┌───────────────┐   search_results   ┌───────────────┐   scraped_content   ┌──────────────┐   report   ┌─────────────┐
│ 1. Search     │ ─────────────────▶ │ 2. Reader     │ ──────────────────▶ │ 3. Writer    │ ─────────▶ │ 4. Critic   │
│    Agent      │                    │    Agent      │                     │    Chain     │            │    Chain    │
│ (Tavily tool) │                    │ (scrape tool) │                     │ (LLM prompt) │            │ (LLM prompt)│
└───────────────┘                    └───────────────┘                     └──────────────┘            └─────────────┘
                                                                                                             │
                                                                                                             ▼
                                                                                              feedback (score + review)
```

### Stage 1 — Search Agent
- A LangChain **agent** (`create_agent`) equipped with the `web_search` tool.
- Given the prompt *"Find recent, reliable and detailed information about: {topic}"*, the LLM decides what query to send to **Tavily**.
- The tool returns up to **5 results**, each formatted as `Title`, `URL` and a 300-character `Snippet`.
- The agent's final message is stored as `state["search_results"]`.

### Stage 2 — Reader Agent
- A second LangChain agent equipped with the `scrape_url` tool.
- It receives the first **800 characters** of the search results and is asked to pick the most relevant URL and scrape it.
- `scrape_url` fetches the page with `requests`, parses it with **BeautifulSoup**, strips `script`, `style`, `nav` and `footer` tags, and returns the first **3,000 characters** of clean text. Failures (timeouts, HTTP errors) are caught and returned as a readable message instead of crashing the pipeline.
- The output is stored as `state["scraped_content"]`.

### Stage 3 — Writer Chain
- A plain LangChain chain: `ChatPromptTemplate | LLM | StrOutputParser`.
- The search results and scraped content are combined into one research block and injected, along with the topic, into a prompt that asks the model to produce a report with:
  - Introduction
  - Key Findings (minimum 3 well-explained points)
  - Conclusion
  - Sources (all URLs found in the research)
- The output is stored as `state["report"]`.

### Stage 4 — Critic Chain
- Another `prompt | LLM | StrOutputParser` chain that reviews the report strictly.
- It is forced into a fixed output format:
  ```
  Score: X/10
  Strengths: ...
  Areas to Improve: ...
  One line verdict: ...
  ```
- The output is stored as `state["feedback"]`.
- In the web app, the score is extracted with a regex and shown as a colour-coded badge (**green ≥ 8**, **amber ≥ 6**, **red < 6**).

---

## 🗂️ Project Structure

```
.
├── agents.py        # LLM setup, the two agents, and the writer/critic chains
├── tools.py         # Tools used by agents: web_search (Tavily) and scrape_url (BeautifulSoup)
├── pipeline.py      # CLI version of the 4-step pipeline (prints each step to terminal)
├── app.py           # Streamlit web interface with live progress and tabbed results
├── requirements.txt # Python dependencies
└── .env             # API keys (not committed)
```

| File | Responsibility |
|------|----------------|
| `agents.py` | Creates the `ChatOpenAI` model (`gpt-5-nano`, `temperature=0`), `build_search_agent()`, `reader_agent()`, `writer_chain` and `critic_chain`. |
| `tools.py` | Defines the two `@tool` functions the agents can call. |
| `pipeline.py` | Defines `research_pipeline(topic)` which runs all four stages and prints progress. Run directly for CLI use. |
| `app.py` | Streamlit UI: custom dark theme, topic form, `run_pipeline()` with `st.status` live updates, and result tabs (Report, Critic feedback, Search results, Scraped content). |

---

## 🧰 Tech Stack

| Purpose | Technology |
|---------|------------|
| Agent & chain framework | LangChain (`create_agent`, LCEL), LangGraph |
| LLM | OpenAI `gpt-5-nano` via `langchain-openai` |
| Web search | Tavily |
| Web scraping | `requests` + BeautifulSoup4 |
| Web UI | Streamlit |
| Config | `python-dotenv` |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
pip install streamlit rich
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 4. Run it

**Web app**
```bash
streamlit run app.py
```

**Command line**
```bash
python pipeline.py
```
You'll be prompted to enter a research topic.

---

## 🖥️ Using the Web App

1. Enter a research topic (e.g. *"Impact of solid-state batteries on electric vehicles"*).
2. Click **Start research** and watch the four steps run live.
3. Explore the results in the tabs:
   - **Report** — the final report, with a download button (`.md`)
   - **Critic feedback** — score badge plus detailed review
   - **Search results** — the raw sources found by the Search agent
   - **Scraped content** — the text extracted by the Reader agent
4. Use **Clear results** in the sidebar to reset.

---

## 🔧 Design Notes

- **Agents vs. chains:** Search and Reader are *agents* because they need to decide when and how to call tools. Writer and Critic are simple *chains* because they only transform text, which keeps them fast and predictable.
- **Deterministic output:** the model is configured with `temperature=0` for consistent results.
- **Graceful failure:** scraping errors are returned as text, and the Streamlit app wraps the whole pipeline in a `try/except` that shows a friendly error.
- **Context control:** snippets (300 chars), search text passed to the reader (800 chars) and scraped text (3,000 chars) are all truncated to keep prompts small and cheap.



## 📄 License

Add your license here (e.g. MIT).
