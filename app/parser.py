import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    return text.strip()

def split_sections(text):
    """
    Enhanced section splitter using regex and heuristics.
    Supports:
      - Numbered headings: '1.', '1.1.2', 'A.', etc.
      - Title-style headings: 'Background', 'Introduction', 'CONCLUSION', etc.
    """
    lines = text.splitlines()
    sections = []
    current_heading = None
    current_content = []

    heading_regex = re.compile(r'^(\d+(\.\d+)*|[A-Z][A-Z]?)\.?\s+[^\d\W].*')  # Matches '1.', '2.1 Intro', 'A. Method'
    all_caps_regex = re.compile(r'^[A-Z\s]{4,}$')  # Matches 'INTRODUCTION', 'BACKGROUND'

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if heading_regex.match(line) or all_caps_regex.match(line):
            if current_heading and current_content:
                sections.append({
                    "heading": current_heading,
                    "content": clean_text("\n".join(current_content))
                })
                current_content = []
            current_heading = line
        else:
            current_content.append(line)

    if current_heading and current_content:
        sections.append({
            "heading": current_heading,
            "content": clean_text("\n".join(current_content))
        })

    return sections
