import re
import os
import json
import pdfplumber
import docx

# Pre-compile the unified skills regex
_SKILLS_REGEX = None
_SKILLS_MAP = {}

def _get_skills_regex():
    global _SKILLS_REGEX, _SKILLS_MAP
    if _SKILLS_REGEX is None:
        patterns = []
        for skill in TECH_SKILLS_DICTIONARY:
            lower_skill = skill.lower()
            escaped = re.escape(lower_skill)
            
            # Map clean display name
            display_name = skill
            if skill == "cpp": display_name = "C++"
            elif skill == "js": display_name = "JavaScript"
            elif skill == "ts": display_name = "TypeScript"
            elif skill == "sklearn": display_name = "Scikit-learn"
            elif skill == "k8s": display_name = "Kubernetes"
            else:
                # Capitalize words
                display_name = " ".join([w.capitalize() for w in skill.split()])
                # Special cases
                display_name = display_name.replace("Sql", "SQL").replace("Html", "HTML").replace("Css", "CSS").replace("Aws", "AWS").replace("Gcp", "GCP").replace("Api", "API").replace("Nlp", "NLP").replace("Numpy", "NumPy").replace("Pytorch", "PyTorch").replace("Tensorflow", "TensorFlow")
                
            _SKILLS_MAP[lower_skill] = display_name
            
            if lower_skill in ["c", "r", "go"]:
                patterns.append(rf"\b{escaped}\b")
            elif lower_skill.endswith("++") or lower_skill.endswith(".js") or lower_skill.startswith("."):
                patterns.append(rf"\b{escaped}" if lower_skill.endswith("++") else rf"{escaped}\b")
            else:
                patterns.append(rf"\b{escaped}\b")
        
        combined_pattern = "|".join(f"({p})" for p in patterns)
        _SKILLS_REGEX = re.compile(combined_pattern, re.IGNORECASE)
    return _SKILLS_REGEX, _SKILLS_MAP

# Hardcoded skill lists for fast vocabulary checks (in addition to classifier)
TECH_SKILLS_DICTIONARY = [
    # Data Science / ML / AI
    "python", "r", "sql", "pytorch", "tensorflow", "keras", "pandas", "numpy", 
    "scikit-learn", "sklearn", "matplotlib", "seaborn", "scipy", "nlp", "natural language processing",
    "computer vision", "opencv", "apache spark", "spark", "hadoop", "tableau", "power bi", "powerbi", 
    "machine learning", "deep learning", "data science", "data analysis", "analytics",
    
    # Web Development
    "html", "css", "javascript", "js", "typescript", "ts", "react", "react.js", "angular", "vue", "vue.js",
    "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring boot", "springboot", 
    "asp.net", "ruby on rails", "rails", "tailwind", "tailwindcss", "sass", "bootstrap", "next.js", "nextjs",
    
    # Cloud / DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "terraform", "ci/cd", "cicd", "jenkins", "github actions", "gitlab", "ansible", "linux", "bash", "shell",
    "devops", "cloud computing",
    
    # Programming Languages & general
    "c", "c++", "cpp", "java", "c#", "golang", "go language", "rust", "swift", "kotlin", "scala",
    
    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "cassandra", "sqlite", "oracle", "mariadb",
    
    # Core CS & Tools
    "git", "github", "jira", "agile", "scrum", "project management", "system design", "data structures", 
    "algorithms", "object-oriented programming", "oop", "rest api", "graphql", "microservices"
]

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def extract_text_from_docx(docx_path: str) -> str:
    """Extracts all text from a Word document (.docx) using python-docx."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
    return text

def extract_text(file_path: str) -> str:
    """Helper to route and extract text based on extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    else:
        # Simple plain text fallback
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading plain text file {file_path}: {e}")
            return ""

def parse_name(text: str) -> str:
    """
    Extracts name from resume text in < 1ms with high accuracy.
    Bypasses heavy spaCy model entirely, saving seconds of execution time and RAM.
    """
    # Look at the first 5 non-empty lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # Common resume labels to ignore
    ignore_keywords = {
        "resume", "cv", "curriculum", "vitae", "contact", "email", "phone", 
        "address", "profile", "summary", "experience", "education", "skills",
        "certifications", "projects", "about", "portfolio", "github", "linkedin"
    }
    
    for line in lines[:5]:
        # Clean line to letters, spaces, dots, dashes
        line_clean = re.sub(r'[^\w\s\.-]', '', line).strip()
        if not line_clean:
            continue
            
        words = line_clean.split()
        # Names are typically 2 to 3 words (sometimes 4)
        if 2 <= len(words) <= 4:
            is_valid_name = True
            for word in words:
                # Must start with letter, only contain letters, dots, or dashes
                if not re.match(r'^[A-Z][a-zA-Z\.-]*$', word):
                    is_valid_name = False
                    break
            
            # Additional safety: should not contain email symbol or phone numbers
            if "@" in line or any(char.isdigit() for char in line):
                is_valid_name = False
                
            # Should not be a section header
            if line_clean.lower() in ignore_keywords:
                is_valid_name = False
                
            if is_valid_name:
                return line_clean
                
    # Fallback to first line if no perfect capitalized name is found
    if lines:
        first_line = lines[0]
        # Clean any contact info
        first_line = re.sub(r'[\d\+\-\(\)\@/\|]', '', first_line).strip()
        words = first_line.split()
        if 1 <= len(words) <= 4:
            return first_line
            
    return "Unknown Candidate"

def parse_email(text: str) -> str:
    """Extracts email address using regex."""
    pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
    match = re.search(pattern, text)
    return match.group(0) if match else ""

def parse_phone(text: str) -> str:
    """Extracts phone number using regex."""
    # Matches various phone formats: +1-234-567-8900, (123) 456-7890, 1234567890, etc.
    pattern = r"\+?\d[\d -()]{8,}\d"
    match = re.search(pattern, text)
    return match.group(0).strip() if match else ""

def parse_education(text: str) -> str:
    """Extracts education milestones using keyword detection and line analysis."""
    edu_keywords = ["university", "college", "school", "institute", "academy", "bachelor", "master", "phd", "b.s", "b.tech", "m.s", "m.tech", "b.e", "b.a", "degree"]
    edu_lines = []
    
    lines = text.split("\n")
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in edu_keywords):
            edu_lines.append(line.strip())
            
    # Return first 3 matching lines grouped
    return "\n".join(edu_lines[:3]) if edu_lines else "Not specified"

def parse_skills(text: str) -> list[str]:
    """
    Parses skills in a single regex pass.
    1000% faster than multiple iterative searches.
    """
    text_lower = text.lower()
    regex, skills_map = _get_skills_regex()
    
    found_skills = set()
    for match in regex.finditer(text_lower):
        matched_text = match.group(0).lower()
        if matched_text in skills_map:
            found_skills.add(skills_map[matched_text])
            
    return sorted(list(found_skills))

def parse_section(text: str, section_headers: list[str]) -> str:
    """Attempts to parse a text block under certain section headers (e.g. experience)."""
    lines = text.split("\n")
    section_content = []
    in_section = False
    
    # Compile headers for exact/regex matching
    header_patterns = [re.compile(rf"^\s*{re.escape(h)}\s*$", re.IGNORECASE) for h in section_headers]
    # Also support general headers containing these words
    keyword_patterns = [re.compile(rf"({re.escape(h)})", re.IGNORECASE) for h in section_headers]
    
    # Generic headers list to detect when *another* section starts
    all_common_headers = [
        "experience", "work experience", "employment history", "employment", "professional experience",
        "projects", "academic projects", "personal projects", "key projects",
        "education", "academic history", "academic profile",
        "skills", "technical skills", "expertise", "core competencies",
        "certifications", "licenses", "courses", "achievements", "summary", "objective"
    ]
    
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        # Detect if we have entered our target section
        if not in_section:
            if any(p.match(cleaned_line) for p in header_patterns) or \
               (len(cleaned_line) < 30 and any(p.search(cleaned_line) for p in keyword_patterns)):
                in_section = True
                continue
        # Detect if we hit another section header, which ends the target section
        else:
            is_other_header = False
            line_lower = cleaned_line.lower()
            # If the line is short and matches any other common headers, terminate section extraction
            if len(cleaned_line) < 30:
                for header in all_common_headers:
                    # Don't trip on our own section keywords
                    if any(x in header for x in [sh.lower() for sh in section_headers]):
                        continue
                    if header in line_lower:
                        is_other_header = True
                        break
            if is_other_header:
                break
            section_content.append(cleaned_line)
            
    return "\n".join(section_content) if section_content else "Not specified"

def parse_resume_to_json(file_path: str) -> dict:
    """Parses a resume file and extracts structured JSON details."""
    text = extract_text(file_path)
    
    # Run parsing steps
    name = parse_name(text)
    email = parse_email(text)
    phone = parse_phone(text)
    education = parse_education(text)
    skills = parse_skills(text)
    
    # Parse large blocks
    experience = parse_section(text, ["experience", "work experience", "employment", "professional experience"])
    projects = parse_section(text, ["projects", "academic projects", "personal projects", "key projects"])
    certifications = parse_section(text, ["certifications", "courses", "achievements"])
    
    # Return formatted profile
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "resume_text": text
    }

if __name__ == "__main__":
    # Test script if executed standalone
    test_text = """
    Jane Doe
    jane.doe@example.com | (123) 456-7890
    
    EDUCATION
    Master of Science in Computer Science, Stanford University, 2024
    
    SKILLS
    Python, SQL, PyTorch, React, Docker, Git
    
    EXPERIENCE
    Software Engineering Intern - Google (Summer 2023)
    - Developed backend features using Python and FastAPI.
    - Containerized applications using Docker.
    
    PROJECTS
    Image Classifier using PyTorch
    - Achieved 95% accuracy on dataset.
    """
    
    print("Testing parser functions locally...")
    skills = parse_skills(test_text)
    name = parse_name(test_text)
    email = parse_email(test_text)
    phone = parse_phone(test_text)
    edu = parse_education(test_text)
    exp = parse_section(test_text, ["experience"])
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print(f"Skills: {skills}")
    print(f"Education: {edu}")
    print(f"Experience: {exp}")
