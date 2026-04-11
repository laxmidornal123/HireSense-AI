COMMON_SKILLS = [
    "python", "java", "c++", "django", "flask", "react", "node",
    "sql", "mysql", "postgresql", "mongodb", "database",
    "aws", "azure", "gcp",
    "docker", "kubernetes",
    "machine learning", "deep learning", "nlp",
    "html", "css", "javascript", "git"
]

def extract_skills(text):
    text = text.lower()
    return [skill for skill in COMMON_SKILLS if skill in text]