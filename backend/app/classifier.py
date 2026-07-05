import os
import pickle
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "skill_classifier.pkl")
CHART_PATH = os.path.join(BASE_DIR, "static", "classifier_metrics.png")

# Class labels
CATEGORIES = [
    "Data Science & AI",
    "Frontend Web Dev",
    "Backend Web Dev",
    "Cloud & DevOps",
    "Mobile Development"
]

def train_and_save_classifier(data: list[dict]):
    """
    Trains a Logistic Regression classifier on synthetic skill lists.
    Saves model as skill_classifier.pkl and evaluation metrics chart as static/classifier_metrics.png.
    """
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

    import matplotlib
    # Use non-interactive backend for matplotlib to avoid GUI thread errors
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(CHART_PATH), exist_ok=True)
    
    # Extract features and targets
    X = [item["skills"] for item in data]
    y = [item["category"] for item in data]
    
    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Create training pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(token_pattern=r'(?u)\b\w+\b|\b\w+\+\+\b|\b\.\w+\b')), # captures C++ and .js
        ('clf', LogisticRegression(max_iter=1000, C=1.0))
    ])
    
    # Train the pipeline
    pipeline.fit(X_train, y_train)
    
    # Make predictions for evaluation
    y_pred = pipeline.predict(X_test)
    
    # Compute metrics
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    
    print("--- Classifier Evaluation Metrics ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-score:  {f1:.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the trained model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"Model saved successfully to {MODEL_PATH}")
    
    # Plot Confusion Matrix
    unique_labels = sorted(list(set(y_test + list(y_pred))))
    cm = confusion_matrix(y_test, y_pred, labels=unique_labels)
    
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Skill Classifier Confusion Matrix')
    plt.colorbar()
    
    tick_marks = np.arange(len(unique_labels))
    plt.xticks(tick_marks, unique_labels, rotation=45, ha="right")
    plt.yticks(tick_marks, unique_labels)
    
    # Loop over data dimensions and create text annotations
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], 'd'),
                     ha="center", va="center",
                     color="white" if cm[i, j] > thresh else "black")
            
    plt.ylabel('True Class')
    plt.xlabel('Predicted Class')
    plt.tight_layout()
    
    # Save chart
    plt.savefig(CHART_PATH, dpi=150)
    plt.close()
    print(f"Evaluation chart saved successfully to {CHART_PATH}")
    
    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1
    }

def predict_category(skills: list[str]) -> str:
    """
    Predicts the category of a list of skills.
    If the model doesn't exist, returns a default fallback.
    """
    if not skills:
        return "Backend Web Dev"  # default fallback
        
    skills_text = ", ".join(skills)
    
    if not os.path.exists(MODEL_PATH):
        # Local heuristic fallback if model not trained
        skills_lower = [s.lower() for s in skills]
        ds_matches = sum(1 for s in skills_lower if any(x in s for x in ["python", "pytorch", "ml", "sql", "pandas", "data science"]))
        fe_matches = sum(1 for s in skills_lower if any(x in s for x in ["react", "js", "html", "css", "tailwind", "frontend"]))
        devops_matches = sum(1 for s in skills_lower if any(x in s for x in ["aws", "docker", "k8s", "kubernetes", "devops", "terraform"]))
        mobile_matches = sum(1 for s in skills_lower if any(x in s for x in ["kotlin", "swift", "flutter", "ios", "android"]))
        
        counts = {
            "Data Science & AI": ds_matches,
            "Frontend Web Dev": fe_matches,
            "Cloud & DevOps": devops_matches,
            "Mobile Development": mobile_matches,
            "Backend Web Dev": 1  # Base default
        }
        return max(counts, key=counts.get)
        
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        prediction = model.predict([skills_text])[0]
        return prediction
    except Exception as e:
        print(f"Error prediction: {e}")
        return "Backend Web Dev"
