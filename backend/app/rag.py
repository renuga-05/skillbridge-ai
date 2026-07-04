import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "vector_store.pkl")

# Lazy-loaded embedding model
_model = None

def get_embedding_model():
    """Returns the sentence-transformers model, loading it once."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 150) -> list[str]:
    """Chunks text into smaller parts with a defined overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def index_kb_documents(kb_dir: str):
    """
    Reads all markdown files in kb_dir, chunks them, 
    embeds them with sentence-transformers, and saves to a local pickle index.
    """
    if not os.path.exists(kb_dir):
        print(f"Knowledge base directory {kb_dir} does not exist.")
        return

    model = get_embedding_model()
    indexed_data = []

    doc_counter = 0
    for filename in os.listdir(kb_dir):
        if filename.endswith(".md") or filename.endswith(".txt"):
            filepath = os.path.join(kb_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple metadata extraction: first line as title
            lines = content.split("\n")
            title = filename
            for line in lines:
                if line.startswith("#"):
                    title = line.replace("#", "").strip()
                    break
            
            chunks = chunk_text(content)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename}_chunk_{i}"
                
                # Store text, metadata and prepare list for embeddings
                indexed_data.append({
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": {"source": filename, "title": title, "chunk_index": i}
                })
                doc_counter += 1

    if indexed_data:
        # Generate embeddings in a batch
        print(f"Generating embeddings for {len(indexed_data)} text chunks...")
        texts = [item["text"] for item in indexed_data]
        embeddings = model.encode(texts)
        
        # Attach embeddings to indexed entries
        for idx, entry in enumerate(indexed_data):
            entry["embedding"] = embeddings[idx]
            
        # Save index to local persistent file
        with open(INDEX_PATH, "wb") as f:
            pickle.dump(indexed_data, f)
            
        print(f"Indexed {doc_counter} chunks into local vector store at '{INDEX_PATH}'")
    else:
        print("No documents found in knowledge base to index.")

def retrieve_resources(missing_skills: list[str], top_n: int = 2) -> dict[str, list[str]]:
    """
    Queries the persistent numpy vector database for resources relevant to each missing skill.
    Returns a dictionary mapping missing skill names to lists of relevant text chunks.
    """
    if not missing_skills:
        return {}

    if not os.path.exists(INDEX_PATH):
        print(f"Warning: Vector index file {INDEX_PATH} does not exist. Run seed script first.")
        return {skill: [] for skill in missing_skills}

    # Load persistent vectors
    with open(INDEX_PATH, "rb") as f:
        indexed_data = pickle.load(f)
        
    if not indexed_data:
        return {skill: [] for skill in missing_skills}

    model = get_embedding_model()
    
    # Generate query embeddings for all missing skills in one batch
    query_embeddings = model.encode(missing_skills)
    
    # Extract document embeddings and text
    doc_embeddings = np.array([item["embedding"] for item in indexed_data])
    doc_texts = [item["text"] for item in indexed_data]
    
    results = {}
    for i, skill in enumerate(missing_skills):
        q_emb = query_embeddings[i]
        
        # Calculate cosine similarity manually using numpy: dot(q, d) / (norm(q) * norm(d))
        q_norm = np.linalg.norm(q_emb)
        doc_norms = np.linalg.norm(doc_embeddings, axis=1)
        
        # Avoid division by zero
        doc_norms[doc_norms == 0] = 1e-9
        if q_norm == 0:
            q_norm = 1e-9
            
        similarities = np.dot(doc_embeddings, q_emb) / (doc_norms * q_norm)
        
        # Get top N matches
        top_indices = np.argsort(similarities)[::-1][:top_n]
        
        # Filter results that have non-trivial similarity (> 0.1)
        skill_docs = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                skill_docs.append(doc_texts[idx])
                
        results[skill] = skill_docs
        
    return results
