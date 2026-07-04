# SkillBridge AI — RAG Resume-to-Career Matching & Upskilling Agent

SkillBridge AI is a RAG-powered career transition counselor and upskilling agent. It parses candidate resumes (PDF/DOCX), predicts their skill category using a scikit-learn classifier, matches them against target job descriptions using sentence embeddings, and queries a vector database (ChromaDB) for resources to generate a detailed 4-week learning roadmap with Groq LLaMA-3.1.

---

## 1. System Architecture

```text
       +-------------------------------------------------------+
       |                  React Frontend (Vite)                |
       +-------+-----------------------+-----------------------+
               |                       ^
        Upload | Resume File           | Structured JSON Profile,
        Paste  | Job Description       | Similarity Score, Missing Skills,
               v                       | 4-week Upskilling Roadmap
       +-------+-----------------------+-----------------------+
       |                  FastAPI Backend Server               |
       +---+---------------+-------+---------------+-------+---+
           |               |       |               |       |
           v               v       v               v       v
     +-----+----+ +--------+-----+ |         +-----+----+ +-----+-----+
     | pdfplumber | | scikit-learn| |         | sentence | |  Groq API  |
     | python-docx| |  Classifier | |         |  transf. | | (LLaMA3.1) |
     +----------+-+ +------+------+ |         +----+-----+ +-----+-----+
                |          |        |              |             ^
                |          |        |              |             | Prompt +
                v          v        v              v             | RAG Context
     +----------+----------+--------+--------------+-------------+----+
     |                        SQLite Database                         |
     |        (Tables: candidates, match_history, chroma_db)          |
     +----------------------------------------------------------------+
```

---

## 2. Tech Stack

- **Backend**: Python (FastAPI), Uvicorn, SQLite
- **Machine Learning**: Scikit-Learn (TF-IDF + Logistic Regression)
- **Vector Database & Embeddings**: ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2`)
- **LLM Reasoning**: Groq API (`llama-3.1-8b-instant`)
- **Frontend**: JavaScript/React (Vite), Tailwind CSS, Recharts, Lucide Icons

---

## 3. Directory Layout

```text
e:/SkillBridge AI/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application server
│   │   ├── parser.py        # Text extractor & parsing logic
│   │   ├── classifier.py    # Sklearn classifier & reports
│   │   ├── matcher.py       # Semantic matching & keyword overlap
│   │   ├── rag.py           # ChromaDB client & vector index
│   │   ├── database.py      # SQLite connection & schema
│   │   └── prompts.py       # Prompt templates & examples
│   ├── static/              # Static evaluations & images
│   ├── seed.py              # Schema setup & seed data loader
│   ├── requirements.txt     # Python pinned dependencies
│   └── render.yaml          # Render cloud configuration
├── data/
│   ├── knowledge_base/      # Curated study resources (19 files)
│   └── samples/             # Sample resumes & JDs
└── frontend/                # React App
```

---

## 4. Getting Started Locally

### Prerequisite
Install [Python 3.12](https://www.python.org/downloads/) and [Node.js (v18+)](https://nodejs.org/).

### Backend Setup
1. Open terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your free Groq API key:
   ```bash
   cp .env.example .env
   ```
   *To get a Groq API key, register for free at [Groq Console](https://console.groq.com/keys).*
5. Run the seeding script to initialize the SQLite database, populate knowledge resources into ChromaDB, and train the skill classifier:
   ```bash
   python seed.py
   ```
6. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API documentation will be available at `http://localhost:8000/docs`.

### Frontend Setup
1. Open a new terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 5. API Documentation

| Method | Endpoint | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/upload-resume` | Form-Data (file: PDF/DOCX) | Extracts resume texts, predicts category, saves candidate to SQLite |
| `POST` | `/match` | `{ "candidate_id": "...", "job_description": "..." }` | Calculates Cosine Similarity & Jaccard overlap, logs result to history |
| `POST` | `/roadmap` | `{ "match_id": "..." }` | Queries ChromaDB for skill resources, calls Groq, saves and returns 4-week roadmap |
| `GET` | `/history` | None | Returns list of past matched assessments, scores, and roadmaps |
| `GET` | `/health` | None | Service check endpoint |

---

## 6. Manual Deployment Instructions

### Backend (Render Free Tier)
1. Register/Login to [Render](https://render.com/).
2. Push your project repository to GitHub.
3. On the Render Dashboard, click **New > Web Service**.
4. Connect your GitHub repository.
5. Set up the following parameters:
   - **Name**: `skillbridge-backend`
   - **Environment**: `Python`
   - **Branch**: `main`
   - **Region**: Select closest to your users.
   - **Build Command**: `pip install -r requirements.txt && python seed.py`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Click **Advanced**, then add the Environment Variable:
   - `GROQ_API_KEY`: *[Your actual Groq API Key]*
   - `CORS_ORIGINS`: `*` (or your Vercel frontend URL)
7. Click **Deploy Web Service**. Note the deployed backend URL (e.g. `https://skillbridge-backend.onrender.com`).

### Frontend (Vercel Free Tier)
1. Register/Login to [Vercel](https://vercel.com/).
2. Click **Add New > Project** and select your GitHub repository.
3. Configure the following project parameters:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add the Environment Variable:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: *[Your Render Deployed Backend URL]* (e.g. `https://skillbridge-backend.onrender.com`)
5. Click **Deploy**. Vercel will build and assign you a live link!
