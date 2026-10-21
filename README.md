# AeroMind ✈️

### AI-Powered Aircraft Intelligence Platform

**Explore beyond the surface. Understand aircraft through intelligent, document-grounded AI.**

AeroMind is an AI-powered aircraft intelligence platform designed to make complex aviation documentation easier to explore, understand, and interact with. By combining Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), semantic search, and graph-based retrieval approaches, AeroMind aims to transform technical aircraft manuals into an interactive knowledge experience.

Rather than simply returning matching paragraphs from a PDF, AeroMind is designed to retrieve relevant technical evidence and use an LLM to generate clear, context-aware answers grounded in the available documentation.

> **Project status:** Active development. The core backend and retrieval workflows are under development and integration. Some retrieval methods and frontend features remain experimental.

---

## 📌 Table of Contents

- [Vision](#-vision)
- [Core Features](#-core-features)
- [How It Works](#-how-it-works)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [API Overview](#-api-overview)
- [Retrieval Methods](#-retrieval-methods)
- [Development Roadmap](#-development-roadmap)
- [Team](#-team)
- [Contributing](#-contributing)
- [Disclaimer](#-disclaimer)

---

## 🚀 Vision

Aircraft documentation contains extensive technical information distributed across chapters, tables, diagrams, and structured specifications. Finding the right information can require significant time and familiarity with the documents.

AeroMind aims to bridge this gap by building an intelligent interface between users and aircraft knowledge.

Our long-term vision is to develop an interactive aircraft intelligence environment that combines:

- **Conversational aircraft knowledge** — ask questions in natural language.
- **Evidence-grounded answers** — use relevant passages from technical documentation to support generated responses.
- **Multiple retrieval strategies** — compare conventional RAG with graph-based approaches.
- **Interactive aircraft exploration** — connect technical explanations with visual aircraft experiences.
- **Extensible knowledge infrastructure** — support additional aircraft, manuals, and intelligent features as the platform evolves.

## ✨ Core Features

### 1. Aircraft Question Answering

Ask questions about aircraft specifications, dimensions, systems, and other topics covered by the indexed documentation.

The intended workflow combines document retrieval with LLM-based answer generation, helping users understand technical information instead of manually searching through hundreds of pages.

### 2. Retrieval-Augmented Generation (RAG)

AeroMind uses a document-processing and retrieval pipeline to prepare technical information for semantic search.

The pipeline is designed to include:

- PDF text extraction and cleaning.
- Document structure and concept detection.
- Intelligent text chunking.
- Embedding generation.
- Vector storage and semantic retrieval.
- Context preparation for LLM-based answer generation.

### 3. Multiple Retrieval Approaches

AeroMind explores different ways to retrieve technical knowledge:

- **Standard RAG:** retrieves relevant document chunks using vector-based search and supporting retrieval strategies.
- **GraphRAG:** explores relationships between concepts alongside document retrieval.
- **LightRAG:** investigates graph-oriented indexing and retrieval for connected technical knowledge.

These approaches are developed as distinct retrieval strategies rather than interchangeable names for the same pipeline.

### 4. LLM Integration

AeroMind integrates with language models through OpenRouter. The LLM is intended to synthesize retrieved evidence into readable answers, while the retrieval layer supplies the relevant technical context.

### 5. Interactive Frontend

The web interface provides the user-facing experience for exploring aircraft and interacting with the platform. The frontend is being integrated with the FastAPI backend, with aircraft visualization and additional interactive capabilities under development.

---

## 🧠 How It Works

AeroMind follows a retrieval-and-generation workflow.

```text
                  USER QUESTION
                        |
                        v
                FRONTEND INTERFACE
                        |
                        v
                   FASTAPI API
                        |
                        v
                RETRIEVAL STRATEGY
                 /      |       \
                /       |        \
             RAG     GraphRAG   LightRAG
                \       |        /
                 \      |       /
                        v
               RETRIEVED KNOWLEDGE
                        |
                        v
                 LLM + CONTEXT
                        |
                        v
               GENERATED ANSWER
                        |
                        v
             RESPONSE TO FRONTEND
```

### Knowledge Ingestion

Before documents can support question answering, they must be processed and indexed.

```text
Aircraft PDF
     |
     v
Text Extraction
     |
     v
Text Cleaning
     |
     v
Structure and Concept Detection
     |
     v
Chunking and Metadata Assignment
     |
     v
Embedding Generation
     |
     v
Vector Database / Retrieval Index
```

### Answer Generation

When a user submits a question:

1. The backend receives the question and the selected retrieval method.
2. The retrieval pipeline searches the relevant aircraft knowledge base.
3. Retrieved passages are assembled into context.
4. The LLM generates an answer using the question and available context.
5. The backend returns the response to the frontend.

The goal is to ground answers in technical evidence and reduce unsupported claims. Retrieval quality, answer accuracy, and source attribution remain important areas for testing and improvement.

---

## 🏗️ System Architecture

AeroMind is organized around a modular architecture.

| Layer               | Responsibility                                                 |
| ------------------- | -------------------------------------------------------------- |
| Frontend            | User interface, chat interaction, and aircraft exploration     |
| API layer           | HTTP endpoints and request handling through FastAPI            |
| Retrieval layer     | Finds relevant technical information using the selected method |
| Knowledge ingestion | Extracts, cleans, chunks, and indexes aircraft documentation   |
| Vector storage      | Stores and retrieves document embeddings                       |
| Graph retrieval     | Explores relationships between concepts where supported        |
| LLM integration     | Generates natural-language responses using retrieved context   |

This separation allows individual components to evolve without requiring the entire system to be redesigned.

---

## 🛠️ Technology Stack

| Technology          | Role                                            |
| ------------------- | ----------------------------------------------- |
| Python              | Backend and AI pipeline                         |
| FastAPI             | Backend API framework                           |
| React               | Frontend interface                              |
| Vite                | Frontend development server and build tooling   |
| ChromaDB            | Vector storage and similarity search            |
| Embedding models    | Convert text into vector representations        |
| OpenRouter          | LLM API access                                  |
| RAG                 | Document-grounded question answering            |
| GraphRAG / LightRAG | Alternative graph-oriented retrieval approaches |
| Git and GitHub      | Version control and team collaboration          |

The exact models, packages, and infrastructure may evolve during development.

---

## 📂 Project Structure

The repository is organized around the backend, frontend, and retrieval components. The following is a conceptual overview; individual filenames may differ as the implementation evolves.

```text
AeroMind-Shared/
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── aircraft.py
│   │   └── chat.py
│   └── services/
│       └── lightrag_service.py
│
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── AircraftViewer.jsx
│       └── ModelViewer.jsx
│
├── LighRag/
│   ├── ingest.py
│   └── pdf_to_text.py
│
├── .env                 # Local secrets; do not commit
├── .gitignore
└── README.md
```

The actual repository may contain additional ingestion, retrieval, embedding, GraphRAG, configuration, and testing modules.

---

## ⚙️ Getting Started

### Prerequisites

Install the following software:

- Python 3.10 or a compatible version supported by the project's dependencies.
- Node.js and npm.
- Git.
- An OpenRouter API key for LLM requests.

The frontend and backend run as separate development processes.

### 1. Clone the Repository

```bash
git clone https://github.com/saieddine/AeroMind.git
cd AeroMind
```

If you already have the shared repository locally, open the project root in VS Code instead.

### 2. Set Up the Backend

From the project root, create a Python virtual environment:

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project's dependencies:

```powershell
pip install -r requirements.txt
```

Run this command only if the repository contains a `requirements.txt` at the root. If dependencies are managed in another file or directory, use the project's existing dependency configuration.

### 3. Configure Environment Variables

Create or update the local `.env` file using the variable names expected by the backend.

Example:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_configured_model
```

Replace the example values with your own configuration. Never commit API keys or other secrets to GitHub.

### 4. Start the Backend

From the project root, with the virtual environment activated:

```powershell
python -m uvicorn backend.main:app --reload
```

The API should be available at:

- API base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health endpoint: `http://127.0.0.1:8000/api/health`

The health endpoint is intended to provide a basic indication that the API process is running; it does not by itself verify that every retrieval method or external service is healthy.

### 5. Start the Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite will print the local development URL. With the default configuration, it is typically:

`http://localhost:5173/`

Open that address in your browser.

If Node.js works in normal PowerShell but not in VS Code, check the Node.js installation path and terminal `PATH` configuration before reinstalling Node.js.

---

## 🔐 Configuration

AeroMind requires environment variables for external services and model configuration.

| Variable             | Purpose                               |
| -------------------- | ------------------------------------- |
| `OPENROUTER_API_KEY` | Authenticates requests to OpenRouter  |
| `OPENROUTER_MODEL`   | Selects the configured language model |

Additional settings may be required for vector storage, document locations, retrieval parameters, or graph indexing, depending on the component being used.

**Security practices**

- Keep `.env` files out of version control.
- Never hard-code API keys in frontend code.
- Do not expose secret credentials through API responses or logs.
- Validate user input and configure production CORS origins appropriately.
- Do not treat a development server as a production deployment.

---

## 🔌 API Overview

AeroMind uses FastAPI to expose backend functionality.

### Health Check

```http
GET /api/health
```

Intended to confirm that the backend process is responding.

### Chat

```http
POST /api/chat
Content-Type: application/json
```

The current chat integration uses a request structure similar to:

```json
{
  "aircraft_id": "a320",
  "question": "What are the dimensions of the A320?",
  "conversation_id": "example-session",
  "document_id": "a320_ac_0624",
  "method": "rag"
}
```

| Field             | Description                              |
| ----------------- | ---------------------------------------- |
| `aircraft_id`     | Identifies the aircraft context          |
| `question`        | User's question                          |
| `conversation_id` | Identifies the conversation              |
| `document_id`     | Identifies the relevant indexed document |
| `method`          | Selects the retrieval strategy           |

The example values are illustrative. Valid identifiers, supported methods, response fields, and error behavior should be confirmed against the current backend implementation.

Interactive endpoint documentation is available at `http://127.0.0.1:8000/docs` while the backend is running.

---

## 🔎 Retrieval Methods

### Standard RAG

Standard RAG retrieves relevant document chunks and passes them to the LLM as context for answer generation.

It is the baseline approach for document-grounded question answering in AeroMind.

### GraphRAG

GraphRAG aims to enrich retrieval by incorporating relationships between technical concepts. It may be useful for questions that require connecting information across different sections or concepts.

Its retrieval quality, integration, and evidence attribution should be evaluated against representative aircraft questions.

### LightRAG

LightRAG explores lightweight graph-oriented indexing and retrieval. It is maintained as a separate approach so that its indexing and query behavior can be developed and evaluated without replacing the standard RAG pipeline.

**Development note:** The retrieval methods do not necessarily have the same level of readiness. A method appearing in the interface does not guarantee that its complete ingestion, indexing, retrieval, and answer-generation workflow is operational.

---

## 🗺️ Development Roadmap

AeroMind is being developed incrementally.

- [x] Establish a FastAPI backend and frontend foundation.
- [x] Develop a document ingestion and retrieval pipeline.
- [x] Integrate OpenRouter-based LLM access.
- [x] Establish standard RAG question-answering workflows.
- [x] Complete and validate frontend-to-backend chat integration.
- [x] Improve retrieval evaluation and source attribution.
- [x] Stabilize LightRAG ingestion and query behavior.
- [x] Evaluate GraphRAG against standard RAG on representative questions.
- [ ] Expand support for aircraft documents and knowledge bases.
- [ ] Integrate richer aircraft visualization and interactive exploration.
- [ ] Add automated tests, monitoring, and deployment configuration.

Checklist items should be updated as implementation and testing are completed.

---

## 👥 Team

AeroMind is developed collaboratively, with responsibilities spanning AI retrieval, backend engineering, frontend development, and visualization.

The project has used the following responsibility areas:

- **Backend and RAG:** ingestion, retrieval architecture, API integration, and data management.
- **LightRAG and interface integration:** graph-oriented retrieval development and frontend integration.
- **Visualization and frontend:** user experience, aircraft visualization, and interactive features.

Specific ownership and contributions may evolve as the team develops the project.

---

## 🤝 Contributing

Contributions are welcome as the platform evolves.

For team development:

1. Create or switch to the appropriate feature branch.
2. Make focused changes within the relevant component.
3. Test the affected functionality locally.
4. Keep API contracts and shared interfaces consistent.
5. Open a pull request and describe the change, testing performed, and any remaining limitations.

Avoid committing virtual environments, generated indexes, local datasets, secrets, or other machine-specific artifacts unless they are explicitly required by the project.

---

## ⚠️ Disclaimer

AeroMind is a software development and research project for exploring aircraft documentation and AI-assisted technical understanding.

Generated responses may be incomplete, inaccurate, or unsupported by the available documentation. AeroMind is not a substitute for approved aircraft manuals, official maintenance documentation, certified training, or qualified aviation professionals.

Do not use unverified AI-generated answers to make operational, maintenance, flight-safety, or airworthiness decisions.

---

## 🌌 Explore Beyond the Surface

AeroMind brings together aircraft knowledge, retrieval systems, language models, and interactive exploration to make technical aviation information more accessible.

**Our goal is not merely to find information, but to help people understand how it connects.**
