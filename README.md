# ByteBaaz — LLM Chatbot with Context Window Management

A full-stack multi-turn chatbot powered by the **Google Gemini API** (using the new `google-genai` SDK) and built with **FastAPI**. It features real-time multi-turn conversation memory, sliding-window context management with automatic running summarization, custom persona prompting, and graceful error handling.

---

## 🎯 Features & Requirements Met

| Requirement | Implementation Details |
|---|---|
| **✅ Real LLM Backend Endpoint** | `POST /api/chat` built with FastAPI, sending requests directly to Gemini LLM (`app/llm.py`). |
| **✅ Multi-turn History per Conversation** | Stateful in-memory session store (`app/conversations.py`) tracked by unique `conversation_id`. The bot references facts from earlier turns. |
| **✅ Context Window Management** | **Hybrid Sliding-Window + Running Summary** (`app/context.py`): Keeps the most recent $N$ turns intact while automatically folding overflow turns into a structured memory summary prepended to system instructions. |
| **✅ Custom System Persona** | **ByteBaaz** (`app/config.py`): A witty, encouraging campus CS lab mentor persona who tailors explanations, provides small code snippets, and avoids raw default assistant behavior. |
| **✅ Robust Error Handling** | Catches rate limits (`429`), timeouts (`504`), connection failures (`502`), and model deprecation errors with clear user-facing messages in the UI instead of broken pages. |
| **✅ Security & Git Hygiene** | API keys are managed purely via `.env` and strictly excluded in `.gitignore`. A `.env.example` template is provided. |
| **✅ Web & CLI Interfaces** | Interactive clean web chat UI (`static/index.html`, `static/style.css`, `static/app.js`) plus a command-line interface (`app/cli.py`). |

---

## 🧠 Context Window Management Architecture

Sending unlimited message history forever exhausts token limits and increases latency. To solve this, ByteBaaz implements a two-tier strategy:

```
+-------------------------------------------------------------+
| System Instructions: Persona (ByteBaaz CS Mentor)           |
+-------------------------------------------------------------+
| System Memory: Running Summary of turns older than N        |  <-- Prevents forgetting
+-------------------------------------------------------------+
| Active Window: Last N turns verbatim (default: 12 messages) |  <-- Preserves exact code
+-------------------------------------------------------------+
```

1. **Sliding Window**: Only the most recent `MAX_RECENT_MESSAGES` (configurable in `.env`) are kept in the immediate turn history.
2. **Running Summary Digest**: When older messages overflow the window, they are compressed into a compact chronological digest and retained as persistent system memory.

---

## 🛠️ Project Structure

```text
1st_project/
├── app/
│   ├── __init__.py
│   ├── cli.py             # Interactive terminal interface
│   ├── config.py          # Environment settings, model fallbacks & system prompt
│   ├── context.py         # Context window sliding & running summary logic
│   ├── conversations.py   # Thread-safe in-memory session manager
│   ├── llm.py             # Google GenAI client, model fallback chain & error handling
│   └── main.py            # FastAPI web server & /api/chat endpoint
├── scripts/
│   ├── demo_context.py    # Test script proving context window truncation & summarization
│   └── ping.py            # 1-second connectivity test script for Gemini API
├── static/
│   ├── app.js             # Frontend API integration & conversation state
│   ├── index.html         # Responsive Chat UI
│   └── style.css          # Minimal modern UI styling
├── .env.example           # Configuration template
├── .gitignore             # Git ignore protecting API keys & virtual environments
├── decision.md            # Technical log, model benchmarks & root cause analysis
└── README.md              # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Google Gemini API Key ([Get one free from Google AI Studio](https://aistudio.google.com/apikey))

### 2. Environment Setup

```powershell
# Navigate into the project folder
cd "1st_project"

# Create a virtual environment (if not already done)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configure API Key

Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```

Open `.env` and set your key:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.1-flash-lite
REQUEST_TIMEOUT_SECONDS=30
MAX_RECENT_MESSAGES=12
```

---

## 💻 Running the Application

### Option A: Web Interface (FastAPI + Uvicorn)

Run the server from `1st_project`:
```powershell
uvicorn app.main:app --reload --port 8000
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

### Option B: Terminal CLI Interface

If you prefer testing inside your terminal:
```powershell
python -m app.cli
```

---

## 🧪 Testing & Verification

### 1. Quick API Connectivity Test
```powershell
python scripts\ping.py
```
*Expected Output:* `Hello, I can hear you loud and clear!`

### 2. Context Window & Truncation Verification
```powershell
python scripts\demo_context.py
```
*Expected Output:* Demonstrates that active turn count stays capped at 12 while older tokens are shifted into the persistent running summary.

### 3. Multi-Turn 5-Turn Memory Test (For Submission)
Try this conversation in the UI to confirm long-term recall:
1. **Turn 1**: *"My name is Rahul and I am building an automated plant watering system using Arduino and C++."*
2. **Turn 2**: *"I want to use a soil moisture sensor and a 5V relay module."*
3. **Turn 3**: *"Which pin should I connect the analog output to?"*
4. **Turn 4**: *"Remind me, what programming language and board did I choose in the beginning?"* $\rightarrow$ *(Bot recalls Arduino and C++)*
5. **Turn 5**: *"What is my name and what is the exact project we are building?"* $\rightarrow$ *(Bot recalls Rahul and the automated plant watering system)*

---

## 📄 License
MIT License. Created for the LLM Multi-Turn Chatbot Assignment.
