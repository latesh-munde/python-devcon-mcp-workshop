# 🚀 DevCon MCP Workshop + APS Agent System

A **multi-server MCP (Model Context Protocol) system** with an **AI agent layer**, integrating:

- 🧠 MCP-based tool servers
- ☁️ Autodesk Platform Services (APS)
- 🤖 Gemini-powered agent
- 🔗 Multi-server tool orchestration

---

# 📁 Project Structure

```

devcon-workshop/
│
├── server.py # MCP server (basic tools)
├── aps-server.py # MCP server (APS integration + OAuth)
├── agent.py # AI agent (Gemini + MCP orchestration)
├── client.py # Manual MCP client (optional)
│
├── .env # API keys
├── .vscode/
│ └── mcp.json # VS Code MCP integration
│
└── README.md

```

---

# 🧠 Architecture

```
    User / Agent / VS Code
            │
    ---------------------
    │                   │
Server MCP       APS MCP Server
(port 3000)       (port 3001)
```

---

# ⚙️ Features

## 🔹 MCP Server

- Add numbers
- Greet in multiple languages
- Estimate construction cost
- Fetch weather (Open-Meteo API)

---

## 🔹 APS MCP Server

- List OSS buckets
- Create buckets
- Get Autodesk user profile (OAuth)

---

## 🔹 Agent (AI Layer)

- Uses Gemini model
- Automatically selects tools
- Executes multi-step workflows
- Routes tools across multiple MCP servers

---

# 🧪 Prerequisites

- Python 3.10+
- Autodesk Developer Account
- Gemini API Key

---

# 📦 Installation

## 1. Clone / Navigate

```bash
cd devcon-workshop
```

---

## 2. Create virtual environment

```bash
python -m venv .venv
```

---

## 3. Activate environment

```bash
# Windows
.\.venv\Scripts\activate
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file:

```env
APS_CLIENT_ID=your_aps_client_id
APS_CLIENT_SECRET=your_aps_secret
GEMINI_API_KEY=your_gemini_key
```

---

# ▶️ Running the System

⚠️ This is a **multi-process system** — run in separate terminals.

---

## 🔹 Terminal 1 — Start Workshop MCP Server

```bash
python server.py
```

Expected:

```
http://localhost:3000/mcp
```

---

## 🔹 Terminal 2 — Start APS MCP Server

```bash
python aps-server.py
```

Expected:

```
http://localhost:3001/mcp
```

---

## 🔹 Terminal 3 — Authenticate APS

Open browser:

```
http://localhost:3001/auth/login
```

✔ Login → Close tab

---

## 🔹 Terminal 4 — Run Agent

```bash
python agent.py
```

---

# 💡 Usage

## Example Prompt (Agent)

```
Create a new OSS bucket with a persistent policy in the US region, then list all my US buckets.
```

---

# 🧠 MCP Integration (VS Code)

File: `.vscode/mcp.json`

```json
{
  "servers": {
    "devcon-workshop": {
      "type": "http",
      "url": "http://localhost:3000/mcp"
    },
    "devcon-aps": {
      "type": "http",
      "url": "http://localhost:3001/mcp"
    }
  }
}
```

👉 Enables tool usage directly inside VS Code (Copilot / MCP extensions)

---

# ⚠️ Common Issues

## ❌ `ConnectError`

➡ Servers not running

---

## ❌ `405 Method Not Allowed`

➡ Using GET instead of POST

---

## ❌ `JSONDecodeError`

➡ Client not following MCP protocol correctly

---

## ❌ APS tools not working

➡ You forgot login:

```
http://localhost:3001/auth/login
```

---

## ❌ `No module named fastapi`

```bash
pip install fastapi uvicorn
```

---

# 🔥 Key Concepts

## MCP Transport Modes

| Mode  | Use Case            |
| ----- | ------------------- |
| STDIO | VS Code integration |
| HTTP  | Agents / APIs       |

---

## System Flow

```
User → Agent → MCP → Tools → Response
```

---

# 🚀 Future Improvements

- Add Redis for token storage
- Add retry + circuit breaker
- Parallel tool execution
- Tool ranking & selection
- LangGraph integration
- Dockerize full system

---

# 📌 Notes

- `google.generativeai` is deprecated → migrate to `google.genai`
- APS Python SDK is not available → using REST APIs via httpx

---

# 🙌 Acknowledgements

- Autodesk Platform Services (APS)
- Model Context Protocol (MCP)
- Gemini API

---

# 🏁 Summary

This project demonstrates:

✔ Multi-server MCP architecture

✔ Tool orchestration across services

✔ Agentic AI with real-world APIs

✔ Production-style system design

---
