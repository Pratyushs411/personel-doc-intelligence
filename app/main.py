import os
import json
from parser import split_sections
from ranker import rank_sections
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from pdfminer.high_level import extract_text

# Paths
INPUT_DIR = "input/"
OUTPUT_DIR = "output/"
EMBEDDING_MODEL_PATH = "models/all-MiniLM-L6-v2"
SUMMARY_MODEL_PATH = "models/flan-t5-base"
ranked_output = "../output/"
# Load models
embedding_model = SentenceTransformer(EMBEDDING_MODEL_PATH)
summary_tokenizer = AutoTokenizer.from_pretrained(SUMMARY_MODEL_PATH)
summary_model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARY_MODEL_PATH)
summarizer = pipeline("text2text-generation", model=summary_model, tokenizer=summary_tokenizer)


def extract_text_from_pdf(pdf_path):
    """Extract full plain text from a PDF file using pdfminer.six"""
    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"❌ Error extracting text from {pdf_path}: {e}")
        return ""


def generate_summary(text):
    """Generate a one-line summary from a chunk of text"""
    try:
        text = text[:1000]
        result = summarizer(f"summarize: {text}", max_length=30, do_sample=False)[0]["generated_text"]
        return result
    except Exception as e:
        print(f"❌ Summary error: {e}")
        return "No summary available."


def process_all_pdfs(persona_role, persona_goal):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    documents_metadata = []
    challenge_id = "round_1b_003"
    test_case_name = persona_goal.lower().replace(" ", "_")[:50]
    description = persona_goal.split(".")[0]

    combined_query = f"{persona_role} needs: {persona_goal}"

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            print(f"\n🔍 Processing: {filename}")

            # Extract and summarize
            text = extract_text_from_pdf(pdf_path)
            title = os.path.splitext(filename)[0]
            description_summary = generate_summary(text)

            # Section split and ranking
            sections = split_sections(text)
            ranked_sections = rank_sections(sections, combined_query, embedding_model)

            # Save per-document ranking
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            ranked_result = {
                "pdf_file": filename,
                "persona_role": persona_role,
                "persona_query": persona_goal,
                "ranked_sections": ranked_sections
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(ranked_result, f, indent=2, ensure_ascii=False)

            print(f"✅ Ranked & saved: {output_path}")

            # Add to master doc summary
            documents_metadata.append({
                "filename": filename,
                "title": title,
                "description": description_summary
            })

    # Save master processed file
    master_output = {
        "challenge_info": {
            "challenge_id": challenge_id,
            "test_case_name": test_case_name,
            "description": description
        },
        "documents": documents_metadata,
        "persona": {
            "role": persona_role
        },
        "job_to_be_done": {
            "task": persona_goal
        }
    }

    master_path = os.path.join(ranked_output, "processed_summary.json")
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(master_output, f, indent=2, ensure_ascii=False)
    print(f"\n📁 Master summary saved: {master_path}")


if __name__ == "__main__":
    print("👤 Persona-Driven Document Intelligence")
    persona_role = input("Enter the persona role (e.g. Legal Advisor, HR Manager): ").strip()
    persona_goal = input("Enter the job-to-be-done (what this person wants to achieve): ").strip()
    print("\n⚙️  Starting processing...\n")
    process_all_pdfs(persona_role, persona_goal)
