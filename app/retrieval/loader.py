import re
from pathlib import Path


FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_front_matter(text: str) -> dict:
    """
    Parse simple YAML-like front matter without requiring PyYAML.
    The assignment documents use simple key: value pairs.
    """
    match = FRONT_MATTER_RE.match(text)

    if not match:
        return {}

    metadata = {}

    for line in match.group(1).splitlines():
        line = line.strip()

        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        # Remove surrounding quotes.
        if len(value) >= 2 and value[0] == value[-1]:
            value = value[1:-1]

        # Convert simple booleans.
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False

        metadata[key] = value

    return metadata


def extract_sections(text: str):
    """
    Split markdown into heading-aware sections.

    Each section retains its heading so citations can point to
    the relevant part of the document.
    """
    lines = text.splitlines()

    sections = []
    current_heading = None
    current_lines = []

    for line in lines:
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)

        if heading_match:
            if current_lines:
                content = "\n".join(current_lines).strip()

                if content:
                    sections.append(
                        {
                            "heading": current_heading or "Document",
                            "content": content,
                        }
                    )

            current_heading = heading_match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        content = "\n".join(current_lines).strip()

        if content:
            sections.append(
                {
                    "heading": current_heading or "Document",
                    "content": content,
                }
            )

    return sections


def load_documents(directory="knowledge-base"):
    """
    Load all Markdown knowledge-base documents.

    Returns heading-aware chunks with their original metadata.
    """
    documents = []

    for path in sorted(Path(directory).glob("*.md")):
        text = path.read_text(encoding="utf-8")

        metadata = parse_front_matter(text)
        sections = extract_sections(text)

        for section in sections:
            content = section["content"]

            # Ignore empty sections.
            if not content.strip():
                continue

            document = {
                "filename": path.name,
                "document_id": metadata.get("document_id"),
                "title": metadata.get("title", path.stem),
                "status": metadata.get("status", "unknown"),
                "effective_date": metadata.get("effective_date"),
                "last_reviewed": metadata.get("last_reviewed"),
                "audience": metadata.get("audience"),
                "policy_authority": metadata.get(
                    "policy_authority", "unknown"
                ),
                "customer_answering": metadata.get(
                    "customer_answering", True
                ),
                "supersedes": metadata.get("supersedes"),
                "superseded_by": metadata.get("superseded_by"),
                "heading": section["heading"],
                "content": content,
            }

            documents.append(document)

    return documents
