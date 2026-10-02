# Business Requirements Document (BRD)
## ResearchPilot — Autonomous Multi-Agent Research Intelligence Platform

**Document Version:** 1.0.0  
**Project Name:** ResearchPilot  
**Status:** Approved / MVP  
**Classification:** Confidential — Enterprise AI Engineering  
**Target Delivery:** Q1 2026  

---

## 1. Executive Summary

Modern AI researchers, software engineers, and technical analysts face information overload due to the exponential growth of peer-reviewed preprints and open-source implementations. Manually discovering, reading, cross-referencing, verifying, and synthesizing research papers into actionable technical intelligence takes tens of hours per topic.

**ResearchPilot** is an autonomous multi-agent research intelligence platform designed to transform this manual process. By orchestrating **7 specialized AI agents** using the **AutoGen** framework and **Groq GPT-OSS 120B (Medium)** high-throughput inference, ResearchPilot automates the complete research lifecycle:
1. Academic literature discovery via the **arXiv API**.
2. Open-source codebase and technical tutorial discovery via **DuckDuckGo**.
3. Deep text and mathematical formulation extraction via **PyMuPDF**.
4. Multi-agent methodological, architectural, empirical, and critical peer review.
5. Publication of a comprehensive, 14-section Research Intelligence Report.

---

## 2. Business Problem & Opportunity

### 2.1 Current Workflow Inefficiencies
Researchers, data scientists, and engineering leadership currently rely on fragmented, highly repetitive manual steps:

```text
Manual Research Workflow:
[Topic Idea] ➔ [arXiv / Google Scholar Search] ➔ [Download 10+ PDFs] ➔ [Skim Abstracts & Math] 
    ➔ [Search GitHub for Repos] ➔ [Evaluate Experimental Claims] ➔ [Identify Weaknesses] ➔ [Draft Summary]
```

### 2.2 Key Pain Points
- **Time Cost:** Conducting a thorough literature review on a novel topic (e.g., "Agentic RAG" or "Multi-Agent Consensus") requires 15–30 hours of senior engineering time.
- **Cognitive Overload:** Sifting through voluminous math, experimental baselines, and ablation studies leads to fatigue and missed nuances.
- **Fragmented Context:** Academic papers often lack direct links to working code, while GitHub codebases lack academic rigour and theoretical depth.
- **Lack of Critical Evaluation:** Rapid reviews frequently accept author claims at face value without identifying missing baselines or benchmark saturation.

### 2.3 Proposed Solution
ResearchPilot transforms this fragmented process into a structured, autonomous pipeline:

```text
Autonomous Multi-Agent Workflow:
[Research Query] ➔ [ResearchPilot Multi-Agent Team] ➔ [14-Section Research Brief + Code + Matrix]
```

---

## 3. Business Objectives

### 3.1 Primary Objectives
1. **Automate Discovery:** Reduce time required to identify and rank relevant academic papers from hours to under 60 seconds.
2. **Bridge Theory and Practice:** Link peer-reviewed academic literature with production GitHub repositories and technical documentation automatically.
3. **Rigorous Analysis:** Extract problem statements, algorithms, architectures, datasets, and quantitative metrics without human manual extraction.
4. **Critical Peer Review:** Provide objective critique identifying limitations, missing information, and open research questions.
5. **Standardized Deliverable:** Generate a publication-grade, 14-section research brief exportable to Markdown, JSON, and HTML.

### 3.2 Key Performance Indicators (KPIs)
| Metric | Baseline (Manual) | Target (ResearchPilot MVP) |
|---|---|---|
| **Research Brief Turnaround Time** | 12–24 Hours | < 90 Seconds |
| **Source Diversity** | Academic Only | Academic (arXiv) + Practical Code (GitHub) |
| **Comparative Coverage** | Ad-hoc / Informal | Standardized 6-Metric Comparison Matrix |
| **Report Completeness** | Variable | 100% adherence to 14 standard sections |
| **Cost per Research Task** | ~$250–$500 in engineering time | < $0.05 in compute/tokens |

---

## 4. Target Users & Stakeholders

| User Persona | Role | Core Need |
|---|---|---|
| **AI/ML Researcher** | Research Scientist | Quickly evaluate prior art, empirical baselines, and open questions in a new subfield. |
| **R&D Engineer** | Systems / ML Engineer | Discover working GitHub implementations and architecture designs to implement in production. |
| **Data Science Lead** | Technical Manager | Compare competing algorithmic approaches across standard benchmark datasets to select architectures. |
| **Technical Analyst** | Product & Market Analyst | Generate executive technical briefs on emerging technological paradigms. |
| **Graduate Student** | Academic Researcher | Accelerate literature reviews and bibliography compilation. |

---

## 5. User Journeys

### 5.1 Primary Journey: Autonomous Topic Research
1. **Query Entry:** The user accesses the Streamlit web dashboard and enters a research topic (e.g., *"Latest approaches for Agentic RAG"*).
2. **Parameters Selection:** The user specifies constraints (e.g., 4 papers, web search enabled, PDF parsing enabled).
3. **Initiation:** The user clicks **[ Start Research ]**.
4. **Live Visibility:** The system displays a calm 3-phase status container:
   - `1. Researching sources...` (Queries arXiv, scrapes DuckDuckGo, downloads and parses PDFs).
   - `2. Analyzing papers...` (AutoGen agents extract architecture, experiments, and limitations).
   - `3. Research Report` (Generates the 14-section research brief).
5. **Consumption & Export:** The user reviews the 14-section report, inspects discovered papers and GitHub repos, views the comparative matrix, and exports to Markdown or JSON.

### 5.2 Secondary Journey: Standalone Paper Deep-Dive
1. **Input:** The user uploads a specific research PDF or provides an arXiv ID.
2. **Extraction:** PyMuPDF parses the document structure.
3. **Agent Review:** The Paper Analysis, Experiment, and Critical Reviewer agents extract methodology, results, and limitations for that single document.
4. **Review:** The user inspects the extracted technical profile in the dashboard.

---

## 6. Functional Requirements (FR)

### FR-1: Research Ingestion & Formulation
- **FR-1.1:** The system shall accept natural language research queries, keywords, or research questions.
- **FR-1.2:** The system shall provide instant 1-click topic suggestions for benchmark topics.
- **FR-1.3:** The Research Manager agent shall formulate a structured research plan and decompose queries into targeted sub-searches.

### FR-2: Academic Literature Retrieval (arXiv)
- **FR-2.1:** The system shall query the arXiv API with relevance sorting.
- **FR-2.2:** The system shall extract metadata: Title, Authors, Abstract, Publication Date, arXiv ID, Paper URL, and direct PDF URL.
- **FR-2.3:** The system shall maintain an HTTP fallback to arXiv XML feeds if the primary client library times out.

### FR-3: Practical Web & Codebase Discovery (DuckDuckGo)
- **FR-3.1:** The system shall perform targeted searches for GitHub repositories and open-source implementations matching the query.
- **FR-3.2:** The system shall categorize discovered URLs into `github`, `docs`, `blog`, or `general`.
- **FR-3.3:** The system shall provide fallback curated references if search engines rate-limit requests.

### FR-4: Full-Text Document Processing (PyMuPDF)
- **FR-4.1:** The system shall download research PDFs asynchronously with custom User-Agent headers.
- **FR-4.2:** The system shall extract clean text using PyMuPDF (`fitz`), caching documents locally in `data/pdfs/`.
- **FR-4.3:** The system shall segment documents into Introduction, Methodology, Experiments, and Conclusion sections.

### FR-5: Multi-Agent Analysis (AutoGen)
- **FR-5.1:** The system shall deploy 7 specialized AutoGen agents.
- **FR-5.2:** **Paper Analysis Agent:** Extract problem statements, motivations, proposed methodologies, architectures, and algorithms.
- **FR-5.3:** **Experiment Agent:** Extract benchmark datasets, experimental setups, metrics, baselines, and ablation results.
- **FR-5.4:** **Critical Reviewer Agent:** Formulate rigorous critiques detailing limitations, missing baselines, threats to validity, and open questions.
- **FR-5.5:** **Comparative Matrix Builder:** Synthesize a side-by-side comparative table across all analyzed papers.
- **FR-5.6:** **Report Generator Agent:** Synthesize a publication-grade, 14-section Research Intelligence Report.

### FR-6: Persistence & Export
- **FR-6.1:** All research sessions shall be persisted to `data/sessions/{research_id}.json`.
- **FR-6.2:** Users shall be able to revisit and reload previous research sessions via the sidebar archive.
- **FR-6.3:** The system shall support 1-click export of research reports in Markdown (`.md`), JSON, and HTML.

---

## 7. Non-Functional Requirements (NFR)

### NFR-1: Performance & Latency
- Literature retrieval and web discovery shall complete in < 15 seconds.
- Total end-to-end research generation for 4 papers shall complete in < 90 seconds under standard Groq API latency.

### NFR-2: Reliability & Fault Tolerance
- System shall gracefully handle network timeouts, rate limits (HTTP 429), and malformed PDFs.
- If Groq API quotas are reached, the system shall seamlessly fall back to internal rule-based multi-agent synthesis so user sessions never abort with uncaught exceptions.

### NFR-3: Security & Secrets Management
- All sensitive credentials (`GROQ_API_KEY`) must reside exclusively in `.env` on the server.
- The web UI shall never prompt or require users to upload or input credentials.
- `.env` and `data/` artifacts must be excluded from Git commits via `.gitignore`.

### NFR-4: Usability & Clean Aesthetics
- The UI shall prioritize product minimalism over framework demonstration clutter.
- The interface shall feature responsive dark-mode styling, clean typography, and zero layout shift.

---

## 8. MVP Definition of Done (DoD)

- [x] Streamlit web application running on port 8501.
- [x] FastAPI backend running on port 8000 with interactive Swagger docs.
- [x] AutoGen 7-agent multi-agent orchestration team fully operational.
- [x] Exclusively locked to Groq GPT-OSS 120B (Medium) (`openai/gpt-oss-120b`).
- [x] Live arXiv paper retrieval with title, author, date, and PDF linking.
- [x] Live DuckDuckGo discovery of GitHub codebases and technical documentation.
- [x] PyMuPDF local PDF downloading, caching, and text sectioning.
- [x] Multi-paper comparative matrix generated automatically.
- [x] Structured 14-section Research Intelligence Report generation.
- [x] Export to Markdown, JSON, and HTML supported.
- [x] Automated test suite passing with 100% pass rate.
