import asyncio
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse

from backend.config import settings
from backend.models import ResearchRequest, ResearchSession, AnalyzePaperRequest, PaperMetadata
from backend.storage import storage
from backend.agents.orchestrator import ResearchOrchestrator
from backend.agents.llm_provider import LLMProvider
from backend.tools.arxiv_tool import get_paper_by_id, search_arxiv
from backend.tools.pdf_tool import extract_text_from_pdf, download_pdf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ResearchPilot")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Health Check Endpoint
# -------------------------------------------------------------
@app.get("/health")
def health_check():
    has_groq = LLMProvider.is_configured()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "groq_configured": has_groq,
        "default_model": settings.GROQ_MODEL,
        "available_models": settings.AVAILABLE_MODELS
    }

# -------------------------------------------------------------
# Research Task Management
# -------------------------------------------------------------
@app.post("/research", response_model=Dict[str, Any])
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Start a multi-agent research workflow.
    Executes in the background and returns a research_id for polling.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Research query cannot be empty")
        
    session = ResearchOrchestrator.create_session(request)
    
    # Launch async background pipeline
    background_tasks.add_task(
        ResearchOrchestrator.run_research_pipeline,
        session.research_id,
        request
    )
    
    return {
        "research_id": session.research_id,
        "status": session.status,
        "query": session.query,
        "max_papers": session.max_papers,
        "message": "Research task successfully initiated"
    }

@app.get("/research/{research_id}", response_model=ResearchSession)
def get_research_status(research_id: str):
    """
    Retrieve research session status, live progress steps, and results.
    """
    session = storage.get_session(research_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research session '{research_id}' not found")
    return session

@app.get("/history")
def list_research_history():
    """
    List past research runs.
    """
    return storage.list_sessions(limit=30)

# -------------------------------------------------------------
# Direct Single Paper Analyzer Endpoint
# -------------------------------------------------------------
@app.post("/papers/analyze")
async def analyze_paper(request: AnalyzePaperRequest):
    """
    Analyze a specific paper by arXiv ID, URL, or raw text.
    """
    text_content = request.text_content or ""
    title = "Direct Paper Analysis"
    arxiv_id = request.arxiv_id or "direct_input"
    authors = ["Uploaded Document / Input Source"]
    abstract = ""
    
    if request.arxiv_id or (request.paper_url and "arxiv.org" in request.paper_url):
        raw_id = request.arxiv_id or request.paper_url
        paper = get_paper_by_id(raw_id)
        if paper:
            title = paper.title
            arxiv_id = paper.arxiv_id
            authors = paper.authors
            abstract = paper.abstract
            if not text_content:
                text_content = paper.abstract

    if not text_content and not abstract:
        raise HTTPException(status_code=400, detail="No content or valid arXiv paper could be found for analysis")

    dummy_meta = PaperMetadata(
        title=title,
        authors=authors,
        abstract=abstract or text_content[:500],
        publication_date="2026",
        arxiv_id=arxiv_id,
        paper_url=request.paper_url or f"https://arxiv.org/abs/{arxiv_id}",
        pdf_url="",
        extracted_text_preview=text_content
    )

    api_key = request.groq_api_key
    model = request.groq_model

    analysis = await ResearchOrchestrator._analyze_paper_methodology(dummy_meta, api_key, model)
    experiment = await ResearchOrchestrator._analyze_paper_experiments(dummy_meta, api_key, model)
    review = await ResearchOrchestrator._analyze_paper_critique(dummy_meta, api_key, model)

    return {
        "paper_id": arxiv_id,
        "title": title,
        "analysis": analysis,
        "experiments": experiment,
        "critical_review": review
    }

@app.post("/papers/upload")
async def upload_and_analyze_pdf(
    file: UploadFile = File(...),
    groq_api_key: Optional[str] = Form(None),
    groq_model: Optional[str] = Form(None)
):
    """
    Upload a research paper PDF directly and analyze it with the multi-agent team.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    content = await file.read()
    extracted_text = extract_text_from_pdf(content, max_pages=6, char_limit=12000)
    
    if not extracted_text:
        raise HTTPException(status_code=400, detail="Failed to extract readable text from PDF")

    paper_meta = PaperMetadata(
        title=file.filename.replace(".pdf", "").replace("_", " ").title(),
        authors=["Author (Uploaded PDF)"],
        abstract=extracted_text[:600],
        publication_date="Uploaded Document",
        arxiv_id="uploaded_pdf",
        paper_url="",
        pdf_url="",
        extracted_text_preview=extracted_text
    )

    analysis = await ResearchOrchestrator._analyze_paper_methodology(paper_meta, groq_api_key, groq_model)
    experiment = await ResearchOrchestrator._analyze_paper_experiments(paper_meta, groq_api_key, groq_model)
    review = await ResearchOrchestrator._analyze_paper_critique(paper_meta, groq_api_key, groq_model)

    return {
        "filename": file.filename,
        "extracted_chars": len(extracted_text),
        "analysis": analysis,
        "experiments": experiment,
        "critical_review": review
    }

# -------------------------------------------------------------
# Export Report Endpoint
# -------------------------------------------------------------
@app.get("/export/{research_id}")
def export_report(research_id: str, format: str = "markdown"):
    """
    Export the generated research report in markdown, json, or html format.
    """
    session = storage.get_session(research_id)
    if not session or not session.report:
        raise HTTPException(status_code=404, detail="Report not found for this session")

    if format.lower() == "json":
        return JSONResponse(content=session.report.model_dump())
    elif format.lower() == "html":
        # Convert markdown to clean HTML
        content = session.report.full_markdown.replace("\n", "<br/>")
        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>ResearchPilot Report - {session.query}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #1e293b; background: #f8fafc; }}
    h1 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
    h2, h3 {{ color: #1e293b; margin-top: 24px; }}
    pre {{ background: #0f172a; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; }}
    code {{ background: #e2e8f0; padding: 2px 6px; border-radius: 4px; }}
  </style>
</head>
<body>
  {content}
</body>
</html>"""
        return HTMLResponse(content=html)
    else:
        # Default Markdown
        return PlainTextResponse(
            content=session.report.full_markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=research_report_{research_id}.md"}
        )
