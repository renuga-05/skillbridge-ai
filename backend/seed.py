import os
import sys
import json
import random

# Ensure backend folder is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db
from app.rag import index_kb_documents
from app.classifier import train_and_save_classifier

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_DIR = os.path.join(os.path.dirname(BASE_DIR), "data", "knowledge_base")

# 1. Knowledge Base Content
KB_DOCUMENTS = {
    "python.md": """# Python Programming Guide
Python is a versatile, high-level programming language.
Key Topics:
- Core Syntax: Variables, lists, dicts, tuples, sets, comprehensions.
- OOP: Classes, inheritance, magic methods, decorators, and generators.
- Testing: Testing with pytest, mocking dependencies.
- Tooling: Poetry, pip, virtualenv, and requirements.txt.
Learning Resources:
- Official Python Docs: https://docs.python.org/3/
- Real Python tutorials: https://realpython.com/
- Learn Python the Hard Way
""",
    
    "sql.md": """# SQL & Relational Databases
Structured Query Language (SQL) is the standard for managing relational databases.
Key Topics:
- Core Queries: SELECT, WHERE, GROUP BY, HAVING, ORDER BY.
- Joins: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN.
- Advanced: CTEs (Common Table Expressions), Window functions (ROW_NUMBER, DENSE_RANK).
- Optimization: Indexing (B-Tree), query plans, and normalization (1NF, 2NF, 3NF).
Learning Resources:
- W3Schools SQL: https://www.w3schools.com/sql/
- Mode Analytics SQL Tutorial: https://mode.com/sql-tutorial/
- SQLZoo interactive practice: https://sqlzoo.net/
""",
    
    "aws.md": """# AWS Cloud Computing
Amazon Web Services (AWS) is a comprehensive, evolving cloud computing platform.
Key Topics:
- Compute: EC2 virtual machines, ECS container service, Lambda serverless functions.
- Storage: S3 object storage, EBS block volumes, EFS network storage.
- Databases: RDS relational databases (PostgreSQL/MySQL), DynamoDB NoSQL.
- Networking & Security: VPC (Virtual Private Cloud), IAM roles and policies, Route53 DNS.
Learning Resources:
- AWS Skill Builder: https://explore.skillbuilder.aws/
- Stephane Maarek's AWS Solutions Architect courses
- AWS Developer Guide: https://docs.aws.amazon.com/
""",
    
    "docker.md": """# Docker Containerization
Docker allows developers to package applications into standard container images.
Key Topics:
- Core Concepts: Containers vs Virtual Machines, Docker Engine.
- Dockerfile syntax: FROM, RUN, COPY, EXPOSE, ENV, CMD, ENTRYPOINT.
- Commands: docker build, docker run, docker ps, docker logs, docker exec.
- Docker Compose: Multi-container orchestration, docker-compose.yml, environment variables, linking services.
Learning Resources:
- Docker Get Started: https://docs.docker.com/get-started/
- Docker Guide on freeCodeCamp: https://www.freecodecamp.org/
""",
    
    "kubernetes.md": """# Kubernetes Container Orchestration
Kubernetes (K8s) is an open-source system for automating deployment, scaling, and management of containerized applications.
Key Topics:
- Architecture: Control Plane, Worker Nodes, Kubelet, API Server.
- Resources: Pods, Deployments, Services (ClusterIP, NodePort, LoadBalancer), Ingress.
- Config: ConfigMaps, Secrets, PersistentVolumes (PV), PersistentVolumeClaims (PVC).
- Tooling: kubectl CLI, Helm charts package manager.
Learning Resources:
- Kubernetes Basics: https://kubernetes.io/docs/tutorials/kubernetes-basics/
- KodeKloud Interactive Labs
- CNCF Kubernetes Certification Prep (CKAD)
""",
    
    "machine_learning.md": """# Machine Learning Fundamentals
Machine Learning is the study of computer algorithms that improve through experience.
Key Topics:
- Supervised: Linear Regression, Logistic Regression, Decision Trees, Random Forests, SVMs, XGBoost.
- Unsupervised: K-Means Clustering, PCA dimension reduction, Hierarchical Clustering.
- Pipeline: Feature scaling, handling missing values, encoding categorical variables.
- Validation: Train-test split, K-fold Cross Validation, Grid Search hyperparameter tuning.
- Metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC.
Learning Resources:
- Scikit-learn documentation: https://scikit-learn.org/stable/
- Andrew Ng's Machine Learning Specialization (Coursera)
- Kaggle Learn Courses: https://www.kaggle.com/learn
""",
    
    "pytorch.md": """# PyTorch Deep Learning
PyTorch is an open-source machine learning library based on the Torch library.
Key Topics:
- Core: Tensors, autograd automatic differentiation, torch.nn neural network modules.
- Model Training: Forward pass, loss functions, backward pass (optimizer.step), learning rates.
- Data Pipelines: Dataset and DataLoader classes, image transformations (torchvision).
- Custom Architectures: CNNs, RNNs, Transformers, Transfer Learning.
Learning Resources:
- PyTorch Tutorials: https://pytorch.org/tutorials/
- Deep Learning with PyTorch Book (free online)
- Fast.ai Practical Deep Learning for Coders
""",
    
    "system_design.md": """# System Design & Scalability
System design is the process of defining architecture, modules, interfaces, and data for a system to satisfy specified requirements.
Key Topics:
- Vertical vs Horizontal Scaling, Load Balancers (Nginx, HAProxy).
- Caching: Caching tiers, Redis, Memcached, cache eviction policies (LRU, LFU).
- Databases: Sharding, replication, read-replicas, CAP Theorem.
- Microservices: API Gateways, service discovery, message queues (RabbitMQ, Kafka).
Learning Resources:
- System Design Primer (GitHub repository by donnemartin)
- ByteByteGo System Design course by Alex Xu
- Designing Data-Intensive Applications (DDIA) by Martin Kleppmann
""",
    
    "react.md": """# React Frontend Development
React is a free and open-source front-end JavaScript library for building user interfaces based on components.
Key Topics:
- Core: JSX, Components, Props, Rendering.
- Hooks: useState, useEffect, useContext, useRef, useMemo, useCallback.
- State: Redux Toolkit, Context API, Zustand.
- Routing: React Router DOM, dynamic path parameters, protected routes.
- Styling: Tailwind CSS integration, Styled Components.
Learning Resources:
- React Documentation (New docs): https://react.dev/
- Scrimba Frontend Path
- Academind React Complete Guide
""",
    
    "nodejs.md": """# Node.js & Express Backend Development
Node.js is an open-source, cross-platform JavaScript runtime environment.
Key Topics:
- Runtime: Event loop, asynchronous non-blocking I/O, event emitters.
- Express: Router, Middleware (cors, helmet, body-parser), error handling.
- REST APIs: Route design, HTTP status codes, JSON request/response.
- Auth: JWT (JSON Web Tokens), bcrypt hashing, session cookies.
Learning Resources:
- Node.js Official Guides: https://nodejs.org/en/docs/guides
- Express.js guide: https://expressjs.com/
- Full Stack Open course (University of Helsinki)
""",
    
    "git.md": """# Git & Version Control
Git is a distributed version control system to track changes in source code.
Key Topics:
- Workflow: git init, clone, add, commit, push, pull.
- Branching: git branch, checkout, switch, merge strategies.
- Advanced: git rebase, git cherry-pick, git stash, git reflog.
- Collaboration: Pull Requests, resolving merge conflicts, git workflows (GitFlow).
Learning Resources:
- Git Book: https://git-scm.com/book/en/v2
- GitHub Git Cheat Sheet
- Learn Git Branching (interactive game)
""",
    
    "dsa.md": """# Data Structures & Algorithms
DSA is the study of how data is stored and manipulated efficiently.
Key Topics:
- Complexity: Big-O notation, Time complexity, Space complexity.
- Data Structures: Arrays, Linked Lists, Stacks, Queues, Hash Tables, Binary Trees, Graphs.
- Sorting & Searching: Binary Search, Quick Sort, Merge Sort.
- Paradigms: Recursion, Dynamic Programming, Greedy Algorithms, Breadth-First / Depth-First Search.
Learning Resources:
- LeetCode / HackerRank: https://leetcode.com/
- GeeksforGeeks: https://www.geeksforgeeks.org/
- Introduction to Algorithms (CLRS book)
""",
    
    "cicd.md": """# CI/CD & Automation Pipelines
Continuous Integration and Continuous Deployment (CI/CD) automates software build, test, and deployment.
Key Topics:
- Principles: Automated tests, fast feedback loops, trunk-based development.
- GitHub Actions: Workflows, triggers (on push, pull_request), jobs, runners, steps, secrets management.
- Jenkins: Jenkinsfiles, pipelines-as-code, agent executors.
- Deployment: Blue-Green deployment, Canary releases.
Learning Resources:
- GitHub Actions Documentation: https://docs.github.com/en/actions
- CI/CD guide on GitLab: https://docs.gitlab.com/ee/ci/
""",
    
    "terraform.md": """# Terraform Infrastructure as Code
Terraform is an open-source IaC tool developed by HashiCorp.
Key Topics:
- Core HCL: providers, resources, data sources, variables, outputs.
- State: terraform.tfstate, remote backends (S3, Consul), state locking.
- Commands: terraform init, plan, apply, destroy, workspace.
- Modules: Writing reusable infrastructure blueprints.
Learning Resources:
- Terraform Learn Tutorials: https://learn.hashicorp.com/terraform
- Terraform Registry documentation: https://registry.terraform.io/
""",
    
    "fastapi.md": """# FastAPI Backend Development
FastAPI is a modern, fast, web framework for building APIs with Python.
Key Topics:
- Basic routes: API Router, Path parameters, Query parameters.
- Data handling: Pydantic schemas, serialization, JSON validation, settings.
- Features: Dependency injection, OAuth2 security integration, automatic Swagger/OpenAPI generation.
- Concurrency: async/await definitions, background tasks, CORS setup.
Learning Resources:
- FastAPI official docs: https://fastapi.tiangolo.com/
- TestDriven.io FastAPI courses
""",
    
    "prompt_engineering.md": """# Prompt Engineering & LLM Integration
Prompt engineering is the practice of structured prompting to optimize LLM outputs.
Key Topics:
- Prompting: Zero-shot, Few-shot prompting, chain-of-thought, system vs user prompts.
- API Client: Groq API, OpenAI API, token consumption, parameter tuning (temperature, top_p).
- Output Control: Enforcing JSON output, error handling on parsing, fallback structures.
- Frameworks: LangChain, LlamaIndex, simple HTTP endpoints.
Learning Resources:
- DeepLearning.AI Prompt Engineering Course
- OpenAI CookBook: https://github.com/openai/openai-cookbook
""",
    
    "databases.md": """# Database Architectures & Comparison
Selecting and designing databases is critical for backend scale.
Key Topics:
- SQL (PostgreSQL, MySQL): Relational, transactional (ACID), schema design.
- NoSQL (MongoDB, DynamoDB): Document-oriented, scalable, flexible JSON schemas.
- Caching (Redis): Key-value store, in-memory operations, pub-sub messaging.
- Replication & Sharding: Master-slave replica, partition keys.
Learning Resources:
- PostgreSQL Docs: https://www.postgresql.org/docs/
- MongoDB University courses
- Redis University
""",
    
    "cybersecurity.md": """# Application Security & Auth
Securing web applications is essential to protect user credentials and systems.
Key Topics:
- OWASP Top 10: SQL injection, XSS (Cross Site Scripting), CSRF, broken authentication.
- Auth Protocols: JWT (JSON Web Tokens), OAuth 2.0, OpenID Connect.
- Cryptography: Hashing passwords with bcrypt/argon2, SSL/TLS, public-key encryption.
- Headers: CORS config, Content Security Policy, HSTS, Rate Limiting.
Learning Resources:
- OWASP Foundation: https://owasp.org/
- PortSwigger Web Security Academy (free labs)
""",
    
    "mobile_development.md": """# Mobile Application Development
Building applications for mobile devices requires platform-specific or cross-platform code.
Key Topics:
- Native Dev: Swift for iOS, Kotlin/Java for Android, Android Studio, Xcode.
- Cross-Platform: React Native (JS/TS), Flutter (Dart), write-once-run-anywhere.
- Concepts: Mobile state management, navigation stacks, offline storage, push notifications.
- Stores: App Store guidelines, Google Play Console release management.
Learning Resources:
- Android Developers: https://developer.android.com/
- Apple Developer Documentation: https://developer.apple.com/documentation/
- React Native Guides: https://reactnative.dev/
"""
}

# 2. Synthetic classifier data generators
SKILLS_BY_CATEGORY = {
    "Data Science & AI": [
        "python", "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn", "sklearn", "machine learning",
        "deep learning", "nlp", "computer vision", "opencv", "data science", "data analysis", "r language",
        "matplotlib", "seaborn", "tableau", "powerbi", "scipy", "keras", "analytics"
    ],
    "Frontend Web Dev": [
        "html", "css", "javascript", "typescript", "react", "angular", "vue", "tailwind", "tailwindcss",
        "next.js", "nextjs", "sass", "bootstrap", "frontend", "ui/ux", "web design", "jquery", "redx", "zustand"
    ],
    "Backend Web Dev": [
        "python", "django", "flask", "fastapi", "node.js", "nodejs", "express", "postgresql", "mysql", "mongodb",
        "redis", "sqlite", "graphql", "rest api", "java", "spring boot", "springboot", "c#", "asp.net", "golang",
        "apis", "backend", "ruby on rails", "rails"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "ci/cd",
        "cicd", "jenkins", "github actions", "ansible", "linux", "bash", "shell", "devops", "cloud computing",
        "sysadmin", "prometheus", "grafana"
    ],
    "Mobile Development": [
        "kotlin", "swift", "flutter", "react native", "reactnative", "ios", "android", "mobile app",
        "swiftui", "android studio", "xcode", "cocoapods", "gradle", "dart", "mobile development"
    ]
}

def generate_synthetic_data(num_samples=200):
    """Generates ~200 synthetic resume skills profile records for training."""
    data = []
    categories = list(SKILLS_BY_CATEGORY.keys())
    
    samples_per_category = num_samples // len(categories)
    
    for category in categories:
        skills_pool = SKILLS_BY_CATEGORY[category]
        # We also mix in some general/other skills to make it realistic
        general_pool = ["git", "github", "jira", "agile", "scrum", "project management", "data structures", "algorithms"]
        
        for _ in range(samples_per_category):
            # Select 4-8 skills from primary category pool
            num_primary = random.randint(4, 8)
            primary_skills = random.sample(skills_pool, min(num_primary, len(skills_pool)))
            
            # Select 1-3 skills from general pool
            num_general = random.randint(1, 3)
            general_skills = random.sample(general_pool, min(num_general, len(general_pool)))
            
            # 10% chance to mix in a random skill from *another* category (noise)
            noise_skills = []
            if random.random() < 0.2:
                other_categories = [c for c in categories if c != category]
                random_other = random.choice(other_categories)
                noise_skills = random.sample(SKILLS_BY_CATEGORY[random_other], 1)
                
            combined = list(set(primary_skills + general_skills + noise_skills))
            
            # Format skills as a list string
            skills_string = ", ".join(combined)
            data.append({
                "skills": skills_string,
                "category": category
            })
            
    # Shuffle dataset
    random.shuffle(data)
    return data

def write_knowledge_base():
    """Writes the markdown knowledge base documents to the data directory."""
    print(f"Creating knowledge base directories at {KB_DIR}...")
    os.makedirs(KB_DIR, exist_ok=True)
    
    for filename, content in KB_DOCUMENTS.items():
        filepath = os.path.join(KB_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Wrote {filename}")
    print("Knowledge base markdown files populated.")

def main():
    print("=== STARTING DATA SEEDING AND ML MODEL TRAINING ===")
    
    # 1. Setup folders and knowledge base
    write_knowledge_base()
    
    # 2. Setup SQLite schema
    print("\nInitializing SQLite database schemas...")
    init_db()
    
    # 3. Train Classifier
    print("\nGenerating synthetic data and training classifier...")
    synthetic_data = generate_synthetic_data(200)
    metrics = train_and_save_classifier(synthetic_data)
    print(f"Classifier trained. Accuracy: {metrics['accuracy']:.4f}")
    

        
    # 5. Index documents in ChromaDB (requires sentence-transformers)
    print("\nIndexing knowledge base files into ChromaDB...")
    try:
        index_kb_documents(KB_DIR)
        print("ChromaDB vector database seeded successfully.")
    except Exception as e:
        print(f"Error indexing ChromaDB: {e}")
        print("Note: Sentence-transformers and chromadb must be installed to run indexer.")

    print("\n=== SEEDING COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
