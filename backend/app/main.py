import os
import uuid
import json
import sqlite3
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Import our custom modules
from app.database import get_db_connection, DB_PATH
from app.parser import parse_resume_to_json
from app.classifier import predict_category
from app.matcher import match_resume_to_jd
from app.rag import retrieve_resources
from app.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# Load environment variables
load_dotenv()

app = FastAPI(
    title="SkillBridge AI - RAG-powered Career Matching & Upskilling Agent",
    description="Backend API for parsing resumes, predicting skill categories, matching with JDs, and generating roadmaps.",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    from app.database import init_db
    init_db()
    # Eagerly load embedding model to prevent endpoint timeouts
    print("Eagerly loading sentence-transformers embedding model...")
    from app.rag import get_embedding_model
    get_embedding_model()
    print("Embedding model loaded successfully.")

# Enable CORS for frontend communication
# Allow config via environment variable, fallback to localhost
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + ["*"], # * added for easy rendering
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static folder for metrics charts if it doesn't exist
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Request Models
class MatchRequest(BaseModel):
    candidate_id: str
    job_description: str

class RoadmapRequest(BaseModel):
    match_id: str

# Helper to clean JSON string from LLM response
def clean_llm_json(response_text: str) -> dict:
    """Cleans backticks, markdown markers, and extracts JSON from LLM output."""
    cleaned = response_text.strip()
    
    # Remove markdown code blocks if present
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
        
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
        
    cleaned = cleaned.strip()
    
    # In case there's text before or after the JSON block
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Find first '{' and last '}'
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1:
            try:
                return json.loads(cleaned[start_idx:end_idx+1])
            except json.JSONDecodeError as e:
                raise ValueError(f"Could not parse LLM output: {e}. Output was: {response_text}")
        else:
            raise ValueError(f"Could not find JSON object in response: {response_text}")

# Mock generator for offline/demo mode when Groq API Key is not configured
def generate_mock_roadmap(candidate_name: str, target_role: str, missing_skills: List[str]) -> dict:
    """Generates a high-quality static roadmap for demo fallback."""
    roadmap = []
    
    if not missing_skills:
        missing_skills = ["Docker", "Kubernetes", "FastAPI"]
        
    for i, skill in enumerate(missing_skills[:4]):
        week = i + 1
        roadmap.append({
            "week": week,
            "theme": f"Fundamentals & Project setup for {skill}",
            "topics": [
                f"Core elements of {skill}",
                f"Advanced routing & integration of {skill}",
                f"Best practices & pattern design with {skill}"
            ],
            "tasks": [
                f"Build a sandbox project implementing {skill}",
                f"Write documentation for your {skill} codebase"
            ],
            "resources": [
                f"Official {skill} Documentation & Reference Guides",
                f"Learn {skill} on freeCodeCamp / YouTube tutorials"
            ]
        })
        
    # If fewer than 4 missing skills, pad it to 4 weeks
    while len(roadmap) < 4:
        week = len(roadmap) + 1
        roadmap.append({
            "week": week,
            "theme": "System Integration & Capstone Project",
            "topics": ["Integration architecture", "Testing frameworks", "Production deployment strategies"],
            "tasks": ["Deploy full stack application", "Optimize code and perform security auditing"],
            "resources": ["Web Scalability and DevOps Playbooks"]
        })
        
    return {
        "candidate_name": candidate_name,
        "target_role": target_role or "Full Stack Developer",
        "missing_skills": missing_skills,
        "roadmap": roadmap,
        "mode": "demo_fallback"
    }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SkillBridge AI API!",
        "database_connected": os.path.exists(DB_PATH),
        "groq_api_configured": bool(os.environ.get("GROQ_API_KEY"))
    }

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Accepts PDF/DOCX file, parses candidate details, runs skill classification,
    stores candidate details in SQLite database, and returns candidate profile.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX or TXT files.")
        
    # Save file temporarily to parse it
    temp_filename = f"temp_{uuid.uuid4()}{ext}"
    temp_filepath = os.path.join(STATIC_DIR, temp_filename)
    
    try:
        with open(temp_filepath, "wb") as f:
            f.write(await file.read())
            
        # Parse resume to structured JSON
        profile = parse_resume_to_json(temp_filepath)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume file: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            
    # Predict category based on extracted skills
    predicted_category = predict_category(profile["skills"])
    profile["category"] = predicted_category
    
    # Generate UUID and store in SQLite
    candidate_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO candidates (id, name, email, phone, education, skills, experience, projects, certifications, resume_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_id,
                profile["name"],
                profile["email"],
                profile["phone"],
                profile["education"],
                json.dumps(profile["skills"]),
                profile["experience"],
                profile["projects"],
                profile["certifications"],
                profile["resume_text"]
            )
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Insertion Error: {str(e)}")
    finally:
        conn.close()
        
    # Return structured response
    profile["id"] = candidate_id
    return profile

@app.post("/match")
def match_profile(request: MatchRequest):
    """
    Loads candidate, matches skills and resume text against Job Description,
    computes Match Score, logs matching metrics, and returns match details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (request.candidate_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    candidate = dict(row)
    conn.close()
    
    # Parse candidate skills
    candidate_skills = json.loads(candidate["skills"])
    
    # Compute Match Score and skill gaps
    match_results = match_resume_to_jd(candidate["resume_text"], candidate_skills, request.job_description)
    
    # Store match in match_history
    match_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO match_history (id, candidate_id, job_description, match_score, matched_skills, missing_skills, roadmap_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id,
                request.candidate_id,
                request.job_description,
                match_results["match_score"],
                json.dumps(match_results["matched_skills"]),
                json.dumps(match_results["missing_skills"]),
                None # Will be generated in /roadmap endpoint
            )
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error logging match history: {str(e)}")
    finally:
        conn.close()
        
    return {
        "match_id": match_id,
        "candidate_id": request.candidate_id,
        "candidate_name": candidate["name"],
        "candidate_category": candidate["education"], # placeholder/fallback
        "match_score": match_results["match_score"],
        "cosine_similarity": match_results["cosine_similarity"],
        "keyword_overlap": match_results["keyword_overlap"],
        "matched_skills": match_results["matched_skills"],
        "missing_skills": match_results["missing_skills"],
        "jd_skills": match_results["jd_skills"]
    }

@app.post("/roadmap")
def generate_roadmap(request: RoadmapRequest):
    """
    Pulls match detail, fetches resources for missing skills from ChromaDB,
    submits prompt to Groq LLaMA, parses JSON roadmap, saves to SQLite, and returns roadmap.
    """
    # 1. Fetch match records
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM match_history WHERE id = ?", (request.match_id,))
    match_row = cursor.fetchone()
    
    if not match_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Match record not found")
        
    match_record = dict(match_row)
    
    # 2. Fetch candidate details
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (match_record["candidate_id"],))
    candidate_row = cursor.fetchone()
    
    if not candidate_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Candidate record not found")
        
    candidate = dict(candidate_row)
    conn.close()
    
    # Parse lists
    missing_skills = json.loads(match_record["missing_skills"])
    
    # Check if roadmap is already generated
    if match_record["roadmap_json"]:
        return json.loads(match_record["roadmap_json"])
        
    # 3. Retrieve RAG documents from ChromaDB
    context_str = ""
    try:
        retrieved_docs = retrieve_resources(missing_skills, top_n=2)
        for skill, docs in retrieved_docs.items():
            context_str += f"\n- Resources for missing skill '{skill}':\n"
            if docs:
                for idx, doc in enumerate(docs):
                    context_str += f"  Guide {idx+1}: {doc.strip()}\n"
            else:
                context_str += "  No specific guide available, suggest standard online reference tutorials.\n"
    except Exception as e:
        print(f"RAG retrieval failed: {e}. Proceeding without vector store context.")
        context_str = "No vector store context available due to lookup failure."

    # Extract target role/title from Job Description (take the first line or guess)
    first_line_jd = match_record["job_description"].split("\n")[0][:100].strip()
    target_role = first_line_jd or "Target Role"

    # 4. Integrate Groq API (fallback to mock if key is missing)
    groq_api_key = os.environ.get("GROQ_API_KEY")
    
    if not groq_api_key:
        print("WARNING: GROQ_API_KEY environment variable is not set. Generating mock roadmap for demo.")
        roadmap_dict = generate_mock_roadmap(candidate["name"], target_role, missing_skills)
    else:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            
            # Formulate user prompt
            user_prompt = USER_PROMPT_TEMPLATE.format(
                name=candidate["name"],
                target_role=target_role,
                missing_skills=json.dumps(missing_skills),
                retrieved_context=context_str
            )
            
            print(f"Sending prompt to Groq (llama-3.1-8b-instant) for {candidate['name']}...")
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            
            response_content = chat_completion.choices[0].message.content
            print("Received response from Groq.")
            roadmap_dict = clean_llm_json(response_content)
            
        except Exception as e:
            print(f"Groq API Error: {e}. Falling back to mock roadmap generator for demo safety.")
            roadmap_dict = generate_mock_roadmap(candidate["name"], target_role, missing_skills)
            
    # 5. Store roadmap back into database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE match_history SET roadmap_json = ? WHERE id = ?",
            (json.dumps(roadmap_dict), request.match_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database Error updating roadmap: {e}")
    finally:
        conn.close()
        
    return roadmap_dict

@app.get("/history")
def get_history():
    """Fetches matching logs and history including candidate detail and scores."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            mh.id as match_id,
            mh.candidate_id,
            c.name as candidate_name,
            mh.job_description,
            mh.match_score,
            mh.matched_skills,
            mh.missing_skills,
            mh.roadmap_json,
            mh.timestamp
        FROM match_history mh
        JOIN candidates c ON mh.candidate_id = c.id
        ORDER BY mh.timestamp DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        item = dict(r)
        # Parse json strings back to list/dict objects
        item["matched_skills"] = json.loads(item["matched_skills"]) if item["matched_skills"] else []
        item["missing_skills"] = json.loads(item["missing_skills"]) if item["missing_skills"] else []
        item["roadmap_json"] = json.loads(item["roadmap_json"]) if item["roadmap_json"] else None
        results.append(item)
        
    return results

@app.get("/health")
def health():
    return {"status": "ok"}
