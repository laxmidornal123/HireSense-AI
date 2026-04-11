def is_valid_resume(text):
    keywords = ["education", "experience", "skills", "project"]

    count = 0
    for word in keywords:
        if word in text:
            count += 1

    return count >= 2