from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_similarity(job_desc, resume_text):
    emb1 = model.encode(job_desc, convert_to_tensor=True)
    emb2 = model.encode(resume_text, convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2)
    return float(score[0][0])