from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class PaperMetadata(BaseModel):
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: str
    publication_date: str
    arxiv_id: str
    paper_url: str
    pdf_url: str
    categories: List[str] = Field(default_factory=list)
    primary_category: str = ""
    local_pdf_path: Optional[str] = None
    extracted_text_preview: Optional[str] = None

class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source_type: str = "general" # 'github', 'docs', 'blog', 'benchmark', 'general'

class PaperAnalysisResult(BaseModel):
    paper_id: str
    title: str
    problem_statement: str
    motivation: str
    proposed_solution: str
    methodology: str
    architecture: str
    algorithms: str
    key_innovations: List[str] = Field(default_factory=list)

class ExperimentResult(BaseModel):
    paper_id: str
    title: str
    datasets: List[str] = Field(default_factory=list)
    experimental_setup: str
    metrics: List[str] = Field(default_factory=list)
    baselines: List[str] = Field(default_factory=list)
    results: str
    ablation_studies: str

class CriticalReviewResult(BaseModel):
    paper_id: str
    title: str
    limitations: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    potential_weaknesses: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    areas_for_investigation: List[str] = Field(default_factory=list)

class ComparisonRow(BaseModel):
    paper_title: str
    arxiv_id: str
    approach: str
    benchmark_datasets: str
    primary_metrics: str
    key_strengths: str
    key_limitations: str

class ResearchReport(BaseModel):
    research_topic: str
    executive_summary: str
    problem_statement: str
    research_motivation: str
    existing_approaches: str
    proposed_methodology: str
    architecture: str
    experimental_setup: str
    results: str
    comparison: str
    limitations: str
    open_research_questions: str
    implementation_considerations: str
    references: List[str] = Field(default_factory=list)
    full_markdown: str = ""

class ProgressStep(BaseModel):
    id: str
    name: str
    status: str = "pending" # pending, in_progress, completed, failed
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    details: Optional[str] = None

class ResearchRequest(BaseModel):
    query: str
    max_papers: int = 5
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = None
    include_web: bool = True
    download_pdfs: bool = True

class AnalyzePaperRequest(BaseModel):
    query_context: Optional[str] = None
    paper_url: Optional[str] = None
    arxiv_id: Optional[str] = None
    text_content: Optional[str] = None
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = None

class ResearchSession(BaseModel):
    research_id: str
    query: str
    status: str = "queued" # queued, running, completed, failed
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    max_papers: int = 5
    progress_steps: List[ProgressStep] = Field(default_factory=list)
    papers: List[PaperMetadata] = Field(default_factory=list)
    web_results: List[WebSearchResult] = Field(default_factory=list)
    analyses: List[PaperAnalysisResult] = Field(default_factory=list)
    experiments: List[ExperimentResult] = Field(default_factory=list)
    reviews: List[CriticalReviewResult] = Field(default_factory=list)
    comparison_table: List[ComparisonRow] = Field(default_factory=list)
    report: Optional[ResearchReport] = None
    error_message: Optional[str] = None
    agent_logs: List[Dict[str, Any]] = Field(default_factory=list)
