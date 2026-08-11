# 🤖 AI Tool-Calling Support Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

**A production-grade AI customer support agent with tool-calling, vector search, session memory, and real-time streaming.**

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [Demo](#-demo-scenarios) · [Deployment](#-production-deployment)

</div>

---

## ✨ Features

- 🧠 **LangGraph Agent** — stateful, multi-step reasoning with tool selection
- 🔧 **Tool-Calling** — OrderLookup, FAQSearch (vector), CreateTicket
- 💬 **Session Memory** — Redis-backed conversation history per user
- 🔍 **Vector FAQ Search** — ChromaDB semantic search for instant answers
- ⚡ **Real-time Streaming** — WebSocket responses streamed to the UI
- 🛡️ **Guardrails** — prompt injection detection + input validation
- 🔐 **JWT Auth** — token-based security, ready to enforce
- 🐳 **One-command Deploy** — full Docker Compose stack

---

## 🏗️ Architecture

```
User → React Chat UI  (port 5173)
          │
          ▼
FastAPI REST / WebSocket  (port 8000)
          │  ← guardrails check
          ▼
    LangGraph Agent
          │
    Tool Selection
    ├── OrderLookup  ──→ PostgreSQL
    ├── FAQSearch    ──→ ChromaDB (vector search)
    └── CreateTicket ──→ PostgreSQL
          │
  LLM Response  (gpt-4o-mini)
          │  ← saved to Redis session memory
          ▼
   Stream back to UI
```

| Layer | Technology |
|-------|-----------|
| AI Agent | LangGraph + LangChain |
| LLM | OpenAI gpt-4o-mini |
| Backend | FastAPI (Python) |
| Frontend | React + Vite + Tailwind CSS |
| Persistence | PostgreSQL 16 |
| Session Memory | Redis 7 |
| Vector Search | ChromaDB |
| Containerization | Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone the repo

```bash
git clone https://github.com/Pradeepkumar160/ai-support-agent.git
cd ai-support-agent
```

### 2. Set your API key

```bash
# Edit server/.env
OPENAI_API_KEY=sk-your-real-key-here
```

### 3. Start everything

```bash
docker compose up --build
```

### 4. Seed the database (first time only)

```bash
docker compose exec api python scripts/init_db.py
```

### 5. Load FAQs into vector store (first time only)

```bash
docker compose exec api python scripts/load_faqs.py
```

### 6. Open the app

| Service | URL |
|---------|-----|
| 💬 Chat UI | http://localhost:5173 |
| 📖 API Docs | http://localhost:8000/docs |
| ❤️ Health Check | http://localhost:8000/health |

---

## 🧪 Demo Scenarios

| Message | Tools Invoked |
|---------|--------------|
| `Track my order #101` | `OrderLookup` |
| `How long do refunds take?` | `FAQSearch` |
| `My package arrived damaged` | `CreateTicket` |
| `Where is order 103 and how long does shipping take?` | `OrderLookup` + `FAQSearch` |

---

## 📁 Project Structure

```
ai-support-agent/
├── server/
│   ├── app/
│   │   ├── agents/
│   │   │   └── support_agent.py      ← LangGraph agent definition
│   │   ├── api/
│   │   │   └── chat.py               ← REST + WebSocket endpoints
│   │   ├── core/                     ← config, security, guardrails
│   │   ├── db/
│   │   │   └── database.py           ← SQLAlchemy engine
│   │   ├── models/
│   │   │   └── all_models.py         ← DB models (orders, tickets)
│   │   ├── tools/
│   │   │   └── implementations.py    ← tool functions
│   │   ├── memory/
│   │   │   └── redis_memory.py       ← Redis session memory
│   │   └── main.py                   ← FastAPI app entry point
│   ├── scripts/
│   │   ├── init_db.py                ← seed database with demo data
│   │   └── load_faqs.py              ← ingest FAQs into ChromaDB
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env                          ← ⚠️ never commit this
├── client/
│   ├── src/
│   │   ├── pages/
│   │   │   └── ChatPage.tsx          ← main chat UI
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI key | **Required** |
| `DATABASE_URL` | PostgreSQL connection string | `postgres@db:5432/support_ai` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `JWT_SECRET` | JWT signing secret | `change-this-in-production` |
| `MODEL_NAME` | OpenAI model to use | `gpt-4o-mini` |

---

## 🛠 Local Development (No Docker)

### Backend

```bash
cd server
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set DATABASE_URL and REDIS_URL in .env to your local instances
uvicorn app.main:app --reload
```

### Frontend

```bash
cd client
npm install
npm run dev
```

---

## 🔒 Security Features

- **Prompt injection detection** via guardrails middleware
- **JWT token support** — ready to enforce on all routes
- **Input length validation** — prevents abuse
- **CORS middleware** — controlled cross-origin access
- **Docker health checks** — services only start when dependencies are ready

---

## 📈 Production Deployment

| Service | Recommended Platform |
|---------|---------------------|
| API (FastAPI) | Railway · Render · AWS ECS · GCP Cloud Run |
| Frontend (React) | Vercel · Netlify |
| Database | Railway PostgreSQL · AWS RDS |
| Redis | Railway Redis · Upstash |

After deploying, update the client's `VITE_API_URL` environment variable to point to your live backend URL.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ by [Pradeep Kumar](https://github.com/Pradeepkumar160)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/07pradeepk)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Pradeepkumar160)

⭐ Star this repo if you found it helpful!

</div>
