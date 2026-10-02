import logging
from typing import List, Optional
import xml.etree.ElementTree as ET
import httpx
from backend.models import PaperMetadata

logger = logging.getLogger(__name__)

def search_arxiv(query: str, max_results: int = 5) -> List[PaperMetadata]:
    """
    Search arXiv for research papers matching the query.
    Uses the arxiv python package with a resilient HTTP fallback.
    """
    papers: List[PaperMetadata] = []
    
    # Method 1: Try official arxiv package
    try:
        import arxiv
        client = arxiv.Client(
            page_size=max_results,
            delay_seconds=1.0,
            num_retries=3
        )
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        for r in client.results(search):
            authors = [a.name for a in r.authors]
            pub_date = r.published.strftime("%Y-%m-%d") if hasattr(r.published, "strftime") else str(r.published)[:10]
            clean_title = " ".join(r.title.split())
            clean_abstract = " ".join(r.summary.split())
            arxiv_id = r.entry_id.split("/")[-1]
            
            paper = PaperMetadata(
                title=clean_title,
                authors=authors,
                abstract=clean_abstract,
                publication_date=pub_date,
                arxiv_id=arxiv_id,
                paper_url=r.entry_id,
                pdf_url=r.pdf_url if r.pdf_url else f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                categories=r.categories if hasattr(r, "categories") else [],
                primary_category=r.primary_category if hasattr(r, "primary_category") else ""
            )
            papers.append(paper)
            
        if papers:
            logger.info(f"Retrieved {len(papers)} papers via arxiv library for query '{query}'")
            return papers
    except Exception as e:
        logger.warning(f"arxiv package search error ({e}), falling back to direct arXiv API")

    # Method 2: Resilient Direct arXiv XML API Fallback
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            
        root = ET.fromstring(resp.content)
        # Namespace map for atom feed
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        
        for entry in root.findall("atom:entry", ns):
            title_elem = entry.find("atom:title", ns)
            summary_elem = entry.find("atom:summary", ns)
            id_elem = entry.find("atom:id", ns)
            published_elem = entry.find("atom:published", ns)
            
            title = " ".join(title_elem.text.split()) if title_elem is not None and title_elem.text else "Untitled"
            abstract = " ".join(summary_elem.text.split()) if summary_elem is not None and summary_elem.text else ""
            entry_id_url = id_elem.text if id_elem is not None and id_elem.text else ""
            arxiv_id = entry_id_url.split("/")[-1] if entry_id_url else "unknown"
            pub_date = published_elem.text[:10] if published_elem is not None and published_elem.text else ""
            
            authors = []
            for author_elem in entry.findall("atom:author", ns):
                name_elem = author_elem.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text)
                    
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href", pdf_url)
                    
            paper = PaperMetadata(
                title=title,
                authors=authors,
                abstract=abstract,
                publication_date=pub_date,
                arxiv_id=arxiv_id,
                paper_url=entry_id_url,
                pdf_url=pdf_url,
                categories=[],
                primary_category=""
            )
            papers.append(paper)
            
        logger.info(f"Retrieved {len(papers)} papers via direct arXiv XML API for query '{query}'")
    except Exception as e:
        logger.error(f"Direct arXiv API failed: {e}")
        
    return papers

def get_paper_by_id(arxiv_id: str) -> Optional[PaperMetadata]:
    """Retrieve metadata for a specific arXiv ID."""
    clean_id = arxiv_id.strip()
    if clean_id.startswith("http"):
        clean_id = clean_id.rstrip("/").split("/")[-1].replace(".pdf", "")
        
    papers = search_arxiv(f"id:{clean_id}", max_results=1)
    return papers[0] if papers else None
