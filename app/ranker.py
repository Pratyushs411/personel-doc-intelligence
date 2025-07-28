import os
import json
from sentence_transformers import SentenceTransformer, util

MODEL_PATH = "models/all-MiniLM-L6-v2"
print("✅ ranker.py loaded\n")

def rank_sections(sections, persona_query, model):
    # Filter out empty or blank sections
    section_texts = [f"{sec['heading']}\n{sec['content']}".strip() for sec in sections if sec.get("content", "").strip()]
    
    if not section_texts:
        print("⚠️ No valid section content to rank.")
        return []

    # Embed sections and query
    section_embeddings = model.encode(section_texts, convert_to_tensor=True)
    query_embedding = model.encode(persona_query, convert_to_tensor=True)

    # Compute cosine similarity
    scores = util.cos_sim(query_embedding, section_embeddings)[0]

    # Combine and rank sections
    ranked = sorted(zip(section_texts, scores), key=lambda x: x[1], reverse=True)

    # Map back to sections with score
    ranked_output = []
    for (text, score) in ranked:
        heading, _, content = text.partition("\n")
        ranked_output.append({
            "heading": heading.strip(),
            "score": float(score),
            "content": content.strip()
        })

    return ranked_output


def rank_all_outputs(persona_query, input_folder="output/", result_folder="final_output/"):
    os.makedirs(result_folder, exist_ok=True)
    model = SentenceTransformer(MODEL_PATH)

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            sections = data.get("sections", [])
            if not sections:
                print(f"⚠️ Skipping {filename} — no sections found.")
                continue

            ranked_sections = rank_sections(sections, persona_query, model)

            ranked_result = {
                "pdf_file": data.get("pdf_file", filename),
                "persona_query": persona_query,
                "ranked_sections": ranked_sections
            }

            output_path = os.path.join(result_folder, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(ranked_result, f, indent=2, ensure_ascii=False)

            print(f"✅ Ranked: {filename} → {output_path}")

if __name__ == "__main__":
    query = input("👤 Enter persona job-to-be-done or query: ").strip()
    if query:
        rank_all_outputs(query)
    else:
        print("❌ No query provided. Exiting.")
