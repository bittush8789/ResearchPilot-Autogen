import os
import re
import logging
from pathlib import Path
from typing import Optional, Dict
import httpx
import fitz  # PyMuPDF
from backend.config import settings

logger = logging.getLogger(__name__)

def download_pdf(pdf_url: str, filename: str) -> Optional[Path]:
    """
    Download a PDF file from a URL and save it to the local cache.
    Returns the Path to the downloaded file or None if failed.
    """
    dest_path = settings.PDFS_DIR / filename
    if dest_path.exists() and dest_path.stat().st_size > 1024:
        logger.info(f"Using cached PDF: {dest_path}")
        return dest_path
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(pdf_url)
            if resp.status_code == 200 and resp.content.startswith(b"%PDF"):
                with open(dest_path, "wb") as f:
                    f.write(resp.content)
                logger.info(f"Downloaded PDF to {dest_path} ({len(resp.content)} bytes)")
                return dest_path
            else:
                logger.warning(f"Failed to download PDF from {pdf_url}: status {resp.status_code}")
    except Exception as e:
        logger.error(f"Error downloading PDF from {pdf_url}: {e}")
        
    return None

def extract_text_from_pdf(pdf_path_or_bytes, max_pages: int = 8, char_limit: int = 16000) -> str:
    """
    Extract readable text from a PDF file using PyMuPDF (fitz).
    Limits to the first `max_pages` and caps text to `char_limit`.
    """
    extracted_text = []
    try:
        if isinstance(pdf_path_or_bytes, (str, Path)):
            doc = fitz.open(str(pdf_path_or_bytes))
        else:
            doc = fitz.open(stream=pdf_path_or_bytes, filetype="pdf")
            
        page_count = min(len(doc), max_pages)
        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                extracted_text.append(f"--- PAGE {page_num + 1} ---\n" + text.strip())
                
        doc.close()
    except Exception as e:
        logger.error(f"Error reading PDF with PyMuPDF: {e}")
        return ""
        
    combined = "\n\n".join(extracted_text)
    # Clean excessive whitespace
    combined = re.sub(r"\n{3,}", "\n\n", combined)
    if len(combined) > char_limit:
        combined = combined[:char_limit] + "\n\n[... Text truncated for token efficiency ...]"
    return combined

def parse_paper_sections(full_text: str) -> Dict[str, str]:
    """
    Heuristically segment paper text into key sections for agents:
    - introduction
    - methodology
    - experiments
    - conclusions
    """
    sections = {
        "introduction": "",
        "methodology": "",
        "experiments": "",
        "conclusion": ""
    }
    
    # Common section headers
    lower_text = full_text.lower()
    
    intro_pos = lower_text.find("1. introduction")
    if intro_pos == -1:
        intro_pos = lower_text.find("introduction")
        
    method_pos = -1
    for m_kw in ["methodology", "method", "proposed approach", "system architecture", "model architecture", "3. "]:
        pos = lower_text.find(m_kw)
        if pos != -1 and (intro_pos == -1 or pos > intro_pos):
            method_pos = pos
            break
            
    exp_pos = -1
    for e_kw in ["experiments", "experimental evaluation", "results", "empirical evaluation", "evaluation", "4. "]:
        pos = lower_text.find(e_kw)
        if pos != -1 and (method_pos == -1 or pos > method_pos):
            exp_pos = pos
            break
            
    concl_pos = -1
    for c_kw in ["conclusion", "conclusions", "limitations", "future work", "discussion"]:
        pos = lower_text.find(c_kw)
        if pos != -1 and (exp_pos == -1 or pos > exp_pos):
            concl_pos = pos
            break

    if intro_pos != -1:
        end = method_pos if method_pos != -1 else (exp_pos if exp_pos != -1 else len(full_text))
        sections["introduction"] = full_text[intro_pos:end].strip()[:3000]
        
    if method_pos != -1:
        end = exp_pos if exp_pos != -1 else (concl_pos if concl_pos != -1 else len(full_text))
        sections["methodology"] = full_text[method_pos:end].strip()[:4000]
        
    if exp_pos != -1:
        end = concl_pos if concl_pos != -1 else len(full_text)
        sections["experiments"] = full_text[exp_pos:end].strip()[:4000]
        
    if concl_pos != -1:
        sections["conclusion"] = full_text[concl_pos:].strip()[:3000]
        
    return sections
