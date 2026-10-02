import requests
import logging
from typing import Dict, Any, Optional, List
from backend.config import settings

logger = logging.getLogger(__name__)

class ResearchPilotAPI:
    def __init__(self, base_url: str = settings.BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"Backend health check failed: {e}")
        return {"status": "unreachable", "groq_configured": False}

    def start_research(
        self,
        query: str,
        max_papers: int = 5,
        groq_api_key: Optional[str] = None,
        groq_model: Optional[str] = None,
        include_web: bool = True,
        download_pdfs: bool = True
    ) -> Dict[str, Any]:
        payload = {
            "query": query,
            "max_papers": max_papers,
            "groq_api_key": groq_api_key or None,
            "groq_model": groq_model or None,
            "include_web": include_web,
            "download_pdfs": download_pdfs
        }
        resp = requests.post(f"{self.base_url}/research", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_research_status(self, research_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/research/{research_id}", timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"Error fetching status for {research_id}: {e}")
        return None

    def list_history(self) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/history", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"Error fetching history: {e}")
        return []

    def analyze_single_paper(
        self,
        arxiv_id: Optional[str] = None,
        paper_url: Optional[str] = None,
        text_content: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        groq_model: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {
            "arxiv_id": arxiv_id,
            "paper_url": paper_url,
            "text_content": text_content,
            "groq_api_key": groq_api_key or None,
            "groq_model": groq_model or None
        }
        resp = requests.post(f"{self.base_url}/papers/analyze", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def upload_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        groq_api_key: Optional[str] = None,
        groq_model: Optional[str] = None
    ) -> Dict[str, Any]:
        files = {"file": (filename, file_bytes, "application/pdf")}
        data = {}
        if groq_api_key:
            data["groq_api_key"] = groq_api_key
        if groq_model:
            data["groq_model"] = groq_model
            
        resp = requests.post(f"{self.base_url}/papers/upload", files=files, data=data, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def get_export_url(self, research_id: str, format: str = "markdown") -> str:
        return f"{self.base_url}/export/{research_id}?format={format}"

api = ResearchPilotAPI()
