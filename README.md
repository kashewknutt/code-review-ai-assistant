# 🧠 Agent-Based Developer Assistant

## 📌 Description

An intelligent agent that helps developers improve code quality via automated code review, bug detection, patch generation, and GitHub pull request automation.

The agent:

- Pulls code from GitHub repos (read-only or authenticated)
- Analyzes code using static analysis and LLM-based reasoning
- Suggests and auto-generates fixes
- Creates Pull Requests via the GitHub API

Designed to be lightweight, modular, and deployable on free-tier services.

---

## 🚀 Features

- LLM-powered static code analyzer
- ReAct agent control using LangChain or LangGraph
- GitHub API integration (pull files, push PRs)
- Patch generation and diff visualization
- Basic frontend UI for developer interaction
- Lightweight, free-tier deployable backend

---

## 🧠 Tech Stack

| Component       | Technology                                  |
| --------------- | ------------------------------------------- |
| Agent Logic     | LangChain / LangGraph (ReAct pattern)       |
| Static Analysis | `pylint`, `flake8`, `ast`, custom heuristics |
| Backend         | Python + FastAPI                            |
| Frontend        | React (Next.js or Vite) + TypeScript        |
| GitHub API      | REST v3 / GraphQL                           |
| Deployment      | Docker, Render, Vercel                      |

---

### Directory Structure

```bash
dev-assistant/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── github/
│   │   ├── analysis/
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── public/
│   └── package.json
├── .env.template
├── docker-compose.yml
├── README.md
└── LICENSE
```


---
## 🛠 Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- GitHub Personal Access Token

### Clone & Setup

```bash
# Clone the repo
git clone https://github.com/kashewknutt/code-review-ai-assistant.git
cd code-review-ai-assistant

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Run Locally

```bash
# Backend 
cd backend 
uvicorn app.main:app --reload 

# Frontend 
cd ../frontend npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

---

## 🧪 Testing

```bash
# From backend/ 
pytest tests/
```

---

## 🌐 Environment Variables (`.env`)


```env
GITHUB_API_TOKEN=your_token
OPENAI_API_KEY=your_key
```


---

### ✅ Project Plan: Agent-Based Developer Assistant

#### 🔧 Phase 1: Core Setup

- [X] Create GitHub repo with MIT license
- [X] Initialize lightweight Python + TypeScript monorepo structure
- [X] Setup FastAPI with minimal routes and static analysis shell
- [X] Integrate GitHub OAuth or token config
- [X] Choose and wire up LangChain or LangGraph (agent control logic)

#### 🧠 Phase 2: Agent + Static Analyzer

- [X] Integrate LangChain ReAct-style agent
- [X] Create GitHub repo parser (basic AST)
- [X] Implement bug-pattern detector (pylint/flake8-based)
- [X] Add suggestion engine (text + patch proposal)
- [X] Generate patches and diff output using `difflib` or `unidiff`

#### 🤖 Phase 3: PR Bot

- [X] GitHub API integration (list repos, branches, files)
- [ ] Authenticate and create PRs with suggestions
- [ ] Add commit message generation
- [ ] Auto-describe PR based on LLM summary

#### 🧪 Phase 4: Testing + Benchmarking

- [ ] Integrate SWE-bench / AgentBench (subset)
- [ ] Write unit + integration tests (pytest + mocks)
- [ ] Add error handling + logging
- [ ] Write benchmark tests with real repos

#### 💻 Phase 5: Frontend

- [ ] Create minimal UI (Next.js or Vite + React)
- [ ] Allow GitHub repo input and trigger analysis
- [ ] Show results (issues, suggestions, patches)
- [ ] Allow user to approve PR generation

#### 🌐 Phase 6: Deployment

- [ ] Dockerize backend + frontend separately
- [ ] Enable deployment on Render/Vercel (backend split if needed)
- [ ] Add .env.template + deployment instructions
- [ ] Enable GitHub webhook (optional)

---

## 🔍 Future Ideas

- Use GitHub Copilot API (if available)
- Fine-tune models for specific repos
- Add frontend review panel with code diff editor
- Support multi-language static analysis
- Enable self-hosted mode for enterprises

---

## 🤝 Contributing

Pull requests and feedback welcome!

---

## 📚 Resources

- LangChain Docs
- [GitHub API Docs](https://docs.github.com/en/rest)
- [SWE-Bench](https://github.com/princeton-nlp/SWE-bench)
- [AgentBench](https://github.com/THUDM/AgentBench)

---

```yaml
## 📦 Lightweight Deployment Tips  
- Use Python slim images (`python:3.10-slim`) 
- Avoid unnecessary libraries (no torch, transformers unless needed) 
- Use `chroma` or `duckdb` for local data needs 
- Use client-side logic in React where possible 
- Deploy backend to Render (free tier) or Railway 
- Deploy frontend to Vercel or Cloudflare Pages
```
