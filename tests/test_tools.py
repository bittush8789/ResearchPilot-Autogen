import pytest
from backend.tools.arxiv_tool import search_arxiv
from backend.tools.web_search import search_web_resources
from backend.tools.pdf_tool import extract_text_from_pdf, parse_paper_sections
import fitz

def test_arxiv_search():
    papers = search_arxiv("RAG", max_results=2)
    assert len(papers) > 0
    paper = papers[0]
    assert paper.title
    assert paper.arxiv_id
    assert paper.pdf_url.startswith("http")

def test_web_search():
    results = search_web_resources("Agentic RAG github", max_results=2)
    assert len(results) > 0
    assert results[0].url.startswith("http")
    assert results[0].source_type in ["github", "docs", "blog", "general"]

def test_pdf_extraction():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "1. Introduction\nThis is a benchmark for agentic research.\n2. Methodology\nWe propose an innovative architecture.")
    pdf_bytes = doc.tobytes()
    doc.close()

    text = extract_text_from_pdf(pdf_bytes)
    assert "agentic research" in text
    
    sections = parse_paper_sections(text)
    assert "introduction" in sections
