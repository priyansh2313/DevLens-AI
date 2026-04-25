<h1 align="center">🧠 DevLens AI</h1>

<p align="center">
  <i>Chat with any GitHub repository like a senior engineer.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-RAG%20System-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Frontend-React-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Embeddings-MiniLM-green?style=for-the-badge" />
</p>

---

## ✨ What is DevLens AI?

DevLens AI is an **AI-powered codebase intelligence assistant** that lets you:

🔍 Understand unfamiliar repositories  
🧠 Ask natural language questions about code  
🐞 Explore architecture & debug faster  
⚡ Get explanations grounded in actual code  

> Think: **Cursor / Greptile — but built from scratch**

---

## 🎥 Demo (Coming Soon)

```diff
+ Chat with any GitHub repo
+ Get real code-backed answers
+ See source references instantly
🧠 How It Works
GitHub Repo
   ↓
Chunking + Embeddings
   ↓
Vector Storage (Supabase)
   ↓
Similarity Search (Cosine)
   ↓
LLM (Gemini)
   ↓
Answer + Sources
⚙️ Tech Stack
🧩 Backend
⚡ FastAPI
🧠 Sentence Transformers (MiniLM)
🗄️ Supabase + pgvector
🔍 Custom Cosine Similarity Engine
🎨 Frontend
⚛️ React + TypeScript
🎨 Tailwind CSS
🤖 AI Layer
🧠 Gemini (google-genai)
📊 RAG Architecture
🚀 Features
🔗 Ingest any public GitHub repo
✂️ Smart code chunking (overlap-based)
🧠 Semantic search using embeddings
🤖 AI-powered explanations
📄 Source attribution (file-level)
⚡ Fast and cost-efficient (local embeddings)
🧪 Example Query
How does routing work in FastAPI?
💡 Output
Explains APIRouter
Mentions Starlette internals
Shows request flow
Provides source files
🏗️ Architecture
Frontend (React)
      ↓
FastAPI Backend
      ↓
Embedding Model (MiniLM)
      ↓
Vector Retrieval
      ↓
Top-K Code Chunks
      ↓
LLM (Gemini)
      ↓
Final Answer
🧠 Key Engineering Decisions
🔥 Manual Similarity (Critical)

Instead of relying on pgvector:
→ Implemented cosine similarity in Python

⚡ Local Embeddings

→ Zero cost
→ Faster iteration
→ No API limits

🔁 Chunk Overlap

→ Better context preservation
→ Improved retrieval quality

🎯 Diversity Filtering

→ Avoids redundant chunks
→ Improves answer quality

🚨 Challenges Solved
❌ Embedding mismatch (768 vs 384)
❌ Supabase RPC vector issues
❌ String → vector conversion bugs
❌ Retrieval returning empty context

Solved using manual ranking + controlled pipeline

📦 Installation
Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
Frontend
cd frontend
npm install
npm run dev
🔗 API Endpoints
Ingest Repo
POST /ingest
Chat with Repo
POST /chat
🚀 Future Improvements
🔄 Multi-hop reasoning (LangGraph)
🎯 Better ranking (rerankers)
💬 Conversation memory
📄 Code highlighting UI
🔐 Private repo support
🧠 Why This Project Matters

This is not a demo.

It demonstrates:

Real-world RAG system design
Handling vector DB limitations
Building LLM-integrated applications
Solving retrieval quality problems
🏁 Final Note

DevLens AI is a step toward making codebases queryable, understandable, and intelligent.
