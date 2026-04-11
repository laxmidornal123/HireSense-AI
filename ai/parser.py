import re

# 🔥 Extended Skill List (VERY IMPORTANT)
COMMON_SKILLS = [
    "python", "java", "c++", "django", "flask", "react", "node",
    "sql", "mysql", "postgresql", "mongodb", "database",
    "aws", "azure", "gcp",
    "docker", "kubernetes",
    "machine learning", "deep learning", "nlp",
    "html", "css", "javascript", "git"
]

# 🔥 Synonyms Mapping (POWERFUL)
SKILL_SYNONYMS = {
    "sql": ["mysql", "postgresql", "database"],
    "python": ["django", "flask"],
    "javascript": ["react", "node"]
}


def extract_details(text):
    text = text.lower()

    found_skills = set()

    # ✅ Direct skill match
    for skill in COMMON_SKILLS:
        if skill in text:
            found_skills.add(skill)

    # ✅ Synonym match (IMPORTANT)
    for main_skill, variants in SKILL_SYNONYMS.items():
        for v in variants:
            if v in text:
                found_skills.add(main_skill)

    # 🔹 Extract Email
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    emails = re.findall(email_pattern, text)

    resume_email = emails[0] if emails else None

    return {
        "skills": list(found_skills),
        "email": resume_email
    }