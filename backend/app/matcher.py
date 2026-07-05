import numpy as np
from app.parser import parse_skills
from app.rag import get_embedding_model

def calculate_cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """Calculates cosine similarity between two 1D vectors."""
    # SentenceTransformers embeddings are pre-normalized, so dot product is cosine similarity.
    # But we add standard math safety checks just in case.
    dot_product = np.dot(emb1, emb2)
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))

def match_resume_to_jd(resume_text: str, candidate_skills: list[str], jd_text: str) -> dict:
    """
    Matches candidate resume against job description:
    1. Generates sentence embeddings and computes Cosine Similarity.
    2. Identifies skills in JD and computes Jaccard keyword overlap with candidate skills.
    3. Combines both into a Match Score (0 - 100).
    4. Identifies matched skills and missing skills (gaps).
    """
    # 1. Embeddings Cosine Similarity
    model = get_embedding_model()
    embeddings = model.encode([resume_text, jd_text])
    cos_sim = calculate_cosine_similarity(embeddings[0], embeddings[1])
    
    # Bound the similarity between 0 and 1
    cos_sim = max(0.0, min(1.0, cos_sim))
    
    # 2. Skill parsing and overlap
    jd_skills = parse_skills(jd_text)
    
    # Normalize comparison (case-insensitive checks)
    candidate_skills_set = {s.lower() for s in candidate_skills}
    jd_skills_set = {s.lower() for s in jd_skills}
    
    matched_skills = []
    missing_skills = []
    
    # Check overlaps using the actual display names in jd_skills
    for skill in jd_skills:
        if skill.lower() in candidate_skills_set:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    # Compute keyword overlap score
    if len(jd_skills_set) == 0:
        keyword_overlap = 1.0  # If job description lists no skills, default to full overlap
    else:
        keyword_overlap = len(matched_skills) / len(jd_skills_set)
        
    # 3. Combine scores: 70% semantic embedding + 30% exact skill overlap
    combined_score = (0.7 * cos_sim + 0.3 * keyword_overlap) * 100
    
    # Ensure it's between 0 and 100 and round it
    match_score = round(max(0.0, min(100.0, combined_score)), 1)
    
    return {
        "match_score": match_score,
        "cosine_similarity": round(cos_sim * 100, 1),
        "keyword_overlap": round(keyword_overlap * 100, 1),
        "jd_skills": jd_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }
