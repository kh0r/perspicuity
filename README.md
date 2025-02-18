# Perspicuity

An open source alternative to Perplexity AI, built with Python FastAPI, React, and Ollama.

## Features

- 🔍 Real-time web search using DuckDuckGo
- 🤖 Local LLM processing using Ollama with DeepSeek 14B
- 🌐 Modern React frontend with Material-UI
- 🚀 Fast and efficient backend with FastAPI
- 🔄 Context-aware responses combining search results with LLM knowledge

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker and Docker Compose (if using containerized setup)
- Ollama - Install from [ollama.ai](https://ollama.ai)
- Nix package manager (optional)

## Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd perspicuity
```

2. **Install dependencies**

If using Nix:
```bash
# This will set up all required dependencies
direnv allow
```

Otherwise:
```bash
# Install Python dependencies
poetry install

# Install frontend dependencies
cd frontend
npm install
cd ..
```

3. **Set up Ollama**

First, ensure you have Ollama installed on your system. You can download it from [ollama.ai](https://ollama.ai).

You can run Ollama in two ways:

**Option 1: Run locally**
```bash
ollama serve
```
In another terminal:
```bash
ollama pull deepseek-r1:14b
```

**Option 2: Run with Docker**
```bash
docker compose up -d
docker exec $(docker ps -qf "name=ollama") ollama pull deepseek-r1:14b
```

Note: The modern Docker Compose command uses `compose.yaml` as the default configuration file.

## Running the Application

1. **Start the backend server**

```bash
cd backend
poetry run python main.py
```

The API will be available at http://localhost:8000

2. **Start the frontend development server**

```bash
cd frontend
npm run dev
```

The web interface will be available at http://localhost:5173

## Usage

1. Open http://localhost:5173 in your web browser
2. Enter your question in the search box
3. Get AI-powered answers with relevant source links

## How It Works

1. When you submit a query, it's sent to the FastAPI backend
2. The backend performs a web search using DuckDuckGo
3. Search results are formatted and combined with your query
4. The combined context is sent to the local Ollama instance running DeepSeek 14B
5. The LLM generates a response based on the search results and its knowledge
6. The response and sources are returned to the frontend for display

## Development

- Frontend code is in the `frontend/` directory
- Backend code is in the `backend/` directory
- API endpoints are documented at http://localhost:8000/docs

## License

MIT
