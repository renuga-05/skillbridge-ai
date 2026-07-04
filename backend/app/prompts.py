# prompts.py
# Contains prompt templates and few-shot examples for the upskilling roadmap generation agent.

SYSTEM_PROMPT = """
You are SkillBridge AI, a professional career transition counselor and upskilling AI agent.
Your goal is to analyze a candidate's profile, identify their skill gaps for a target job description, and use retrieved learning resources to generate a detailed, structured, 4-week upskilling roadmap.

CRITICAL INSTRUCTIONS:
1. You must only suggest realistic, structured learning paths.
2. You must incorporate the provided study guides and learning resources retrieved from the knowledge base for each missing skill.
3. You must output your response as a SINGLE, VALID JSON OBJECT.
4. Do NOT include any markdown code blocks (e.g. ```json ... ```) or conversational preamble or postscript in your response. Return ONLY raw JSON text.
5. If no learning resource is provided for a missing skill, suggest standard high-quality open-source tutorials or documentation (e.g., official docs, MDN, etc.).

Your output JSON must strictly follow this structure:
{
  "candidate_name": "Candidate Name",
  "target_role": "Target Job Title",
  "missing_skills": ["Skill 1", "Skill 2"],
  "roadmap": [
    {
      "week": 1,
      "theme": "Week 1 Theme (e.g., Fundamentals of Python and SQL)",
      "topics": ["Specific Topic 1", "Specific Topic 2"],
      "tasks": ["Hands-on project task 1", "Hands-on project task 2"],
      "resources": ["Resource Name - Link or Description", "Resource Name 2"]
    },
    {
      "week": 2,
      "theme": "Week 2 Theme",
      "topics": ["Specific Topic 3"],
      "tasks": ["Hands-on project task 3"],
      "resources": ["Resource Name - Link or Description"]
    },
    {
      "week": 3,
      "theme": "Week 3 Theme",
      "topics": ["Specific Topic 4"],
      "tasks": ["Hands-on project task 4"],
      "resources": ["Resource Name - Link or Description"]
    },
    {
      "week": 4,
      "theme": "Week 4 Theme",
      "topics": ["Specific Topic 5"],
      "tasks": ["Hands-on project task 5", "Final Integration Project"],
      "resources": ["Resource Name - Link or Description"]
    }
  ]
}
"""

FEW_SHOT_EXAMPLE_INPUT = """
Candidate: Alice Smith
Target Job: Backend Python Engineer
Missing Skills: ["Docker", "FastAPI"]

Retrieved Knowledge Base Resources:
- Docker Guide:
  Docker is a tool that allows you to package an application with all of its dependencies into a standardized unit called a container. Learn Dockerfile syntax, docker-compose commands, and container port mapping. Best resource: Docker Official Documentation (docs.docker.com).
- FastAPI Guide:
  FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. Learn route handlers, dependency injection, and Pydantic validation. Best resource: FastAPI tutorial (fastapi.tiangolo.com).
"""

FEW_SHOT_EXAMPLE_OUTPUT = """{
  "candidate_name": "Alice Smith",
  "target_role": "Backend Python Engineer",
  "missing_skills": ["Docker", "FastAPI"],
  "roadmap": [
    {
      "week": 1,
      "theme": "FastAPI Basics & Routing",
      "topics": ["FastAPI path parameters", "Query parameters", "Pydantic request body validation"],
      "tasks": ["Create a basic CRUD API for a bookstore", "Run the app using uvicorn"],
      "resources": ["FastAPI Tutorial - https://fastapi.tiangolo.com/tutorial/"]
    },
    {
      "week": 2,
      "theme": "Advanced FastAPI & Database Integration",
      "topics": ["FastAPI Dependency Injection", "SQLAlchemy ORM integration", "SQLite DB setup"],
      "tasks": ["Connect bookstore API to SQLite database", "Implement route protections and error handlers"],
      "resources": ["FastAPI Database Guide - https://fastapi.tiangolo.com/tutorial/sql-databases/"]
    },
    {
      "week": 3,
      "theme": "Docker Fundamentals for Python Apps",
      "topics": ["Containers vs VMs", "Writing Dockerfiles for FastAPI apps", "Docker image build commands"],
      "tasks": ["Write a Dockerfile for the bookstore API", "Build and run the container locally, exposing port 8000"],
      "resources": ["Docker official docs - https://docs.docker.com/get-started/"]
    },
    {
      "week": 4,
      "theme": "Docker Compose & Multi-Container Deployment",
      "topics": ["Multi-container setups", "Docker Compose syntax", "Linking FastAPI backend with PostgreSQL container"],
      "tasks": ["Write a docker-compose.yml file combining FastAPI and PostgreSQL", "Spin up both services with a single command and test connectivity", "Prepare production bundle"],
      "resources": ["Docker Compose documentation - https://docs.docker.com/compose/"]
    }
  ]
}"""

USER_PROMPT_TEMPLATE = """
Generate a personalized upskilling roadmap.

Candidate Name: {name}
Target Job/Role: {target_role}
Missing Skills Identified: {missing_skills}

Retrieved Reference Guides from Knowledge Base:
{retrieved_context}

Create the 4-week roadmap strictly following the specified JSON schema. Incorporate the study materials provided above.
"""
