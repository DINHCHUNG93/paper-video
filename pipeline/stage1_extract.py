"""Stage 1: Content extraction from PDF, arXiv, or plain text."""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
import arxiv

__all__ = ["ExtractedContent", "extract_from_pdf", "extract_from_arxiv", "extract_from_text"]


@dataclass
class ExtractedContent:
    """Structured content extracted from a paper or topic."""

    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    sections: list[dict] = field(default_factory=list)  # [{"heading": ..., "text": ...}]
    equations: list[str] = field(default_factory=list)
    figures: list[str] = field(default_factory=list)  # figure captions
    references: list[str] = field(default_factory=list)
    source_type: str = ""  # "pdf", "arxiv", "text"
    raw_text: str = ""

    def to_prompt_text(self) -> str:
        """Format for LLM consumption."""
        parts = []
        if self.title:
            parts.append(f"# {self.title}")
        if self.authors:
            parts.append(f"Authors: {', '.join(self.authors)}")
        if self.abstract:
            parts.append(f"\n## Abstract\n{self.abstract}")
        for section in self.sections:
            parts.append(f"\n## {section['heading']}\n{section['text']}")
        if self.equations:
            parts.append(f"\n## Key Equations\n" + "\n".join(self.equations))
        return "\n".join(parts)


def extract_from_pdf(pdf_path: str) -> ExtractedContent:
    """Extract content from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    content = ExtractedContent(source_type="pdf")

    full_text = []
    for page in doc:
        full_text.append(page.get_text())

    content.raw_text = "\n".join(full_text)

    # Heuristic title extraction: first large text block
    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]
    max_size = 0
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    if span["size"] > max_size:
                        max_size = span["size"]
                        content.title = span["text"].strip()

    # Section extraction (heuristic: lines starting with common headings)
    current_section = {"heading": "Introduction", "text": ""}
    for line in content.raw_text.split("\n"):
        stripped = line.strip()
        # Detect headings (numbered or all-caps short lines)
        if re.match(r"^\d+\.?\s+[A-Z]", stripped) and len(stripped) < 100:
            if current_section["text"]:
                content.sections.append(current_section)
            current_section = {"heading": stripped, "text": ""}
        elif stripped.isupper() and 3 < len(stripped) < 60:
            if current_section["text"]:
                content.sections.append(current_section)
            current_section = {"heading": stripped, "text": ""}
        else:
            current_section["text"] += stripped + " "

    if current_section["text"]:
        content.sections.append(current_section)

    # Abstract extraction
    abstract_match = re.search(
        r"(?i)abstract[:\s]*(.+?)(?=\n\s*\n|\n\d+\.\s|\nIntroduction|$)",
        content.raw_text,
        re.DOTALL,
    )
    if abstract_match:
        content.abstract = abstract_match.group(1).strip()[:2000]

    doc.close()
    return content


def extract_from_arxiv(arxiv_id: str) -> ExtractedContent:
    """Extract content from an arXiv paper by ID."""
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(search.results())

    content = ExtractedContent(
        title=paper.title,
        authors=[a.name for a in paper.authors],
        abstract=paper.summary,
        source_type="arxiv",
        raw_text=paper.summary,
    )

    # Download PDF for full extraction
    pdf_path = f"/tmp/banim_{arxiv_id.replace('/', '_')}.pdf"
    paper.download_pdf(filename=pdf_path)

    if os.path.exists(pdf_path):
        pdf_content = extract_from_pdf(pdf_path)
        content.sections = pdf_content.sections
        content.equations = pdf_content.equations
        content.raw_text = pdf_content.raw_text
        os.remove(pdf_path)

    return content


def extract_from_text(topic: str) -> ExtractedContent:
    """Create content from a plain text topic description."""
    return ExtractedContent(
        title=topic,
        abstract=topic,
        source_type="text",
        raw_text=topic,
    )


def extract(source: str) -> ExtractedContent:
    """Auto-detect source type and extract content.

    Parameters
    ----------
    source : str
        A file path (PDF), arXiv ID (e.g. "2301.12345"), or plain text topic.
    """
    # arXiv ID pattern
    if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", source):
        return extract_from_arxiv(source)

    # File path
    if os.path.isfile(source) and source.lower().endswith(".pdf"):
        return extract_from_pdf(source)

    # Plain text
    return extract_from_text(source)
