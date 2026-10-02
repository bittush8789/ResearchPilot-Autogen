import time
import streamlit as st
from pathlib import Path
from frontend.api_client import api
from frontend.components import (
    render_header,
    render_research_status,
    render_paper_card,
    render_web_card,
    render_comparison_table
)

# Page Configuration
st.set_page_config(
    page_title="ResearchPilot — Multi-Agent Research Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Minimal Product Stylesheet
css_path = Path(__file__).parent / "styles.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session State Initialization
if "active_research_id" not in st.session_state:
    st.session_state.active_research_id = None
if "search_query" not in st.session_state:
    st.session_state.search_query = "Latest approaches for Agentic RAG"

# -------------------------------------------------------------------
# Sidebar: Settings & History
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Settings")
    
    # Backend Status
    health = api.get_health()
    if health.get("status") == "healthy":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:14px;">
          <span style="height:8px; width:8px; background-color:#10b981; border-radius:50%; display:inline-block;"></span>
          <span style="color:#6ee7b7; font-size:0.82rem; font-weight:500;">Backend Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:14px;">
          <span style="height:8px; width:8px; background-color:#f43f5e; border-radius:50%; display:inline-block;"></span>
          <span style="color:#fca5a5; font-size:0.82rem; font-weight:500;">Backend Offline (Port 8000)</span>
        </div>
        """, unsafe_allow_html=True)

    # Active Groq Model: Exclusively GPT-OSS 120B (Medium)
    selected_model = "openai/gpt-oss-120b"
    st.markdown("""
    <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.28); border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
      <div style="font-size: 0.72rem; text-transform: uppercase; color: #a5b4fc; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 3px;">LLM Engine</div>
      <div style="color: #ffffff; font-weight: 600; font-size: 0.92rem; display: flex; align-items: center; gap: 6px;">
        <span>⚡</span> GPT-OSS 120B (Medium)
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    max_papers = st.slider("Max arXiv Papers", min_value=1, max_value=8, value=4)
    include_web = st.checkbox("Search Web (DuckDuckGo)", value=True)
    download_pdfs = st.checkbox("Download & Parse PDFs", value=True)

    # History Archive
    st.markdown("---")
    st.markdown("### Recent Research")
    history = api.list_history()
    if history:
        for h in history[:6]:
            q_label = h.get("query", "Untitled")[:28] + "..." if len(h.get("query", "")) > 28 else h.get("query", "")
            if st.button(f"📄 {q_label}", key=f"hist_{h.get('research_id')}", use_container_width=True):
                st.session_state.active_research_id = h.get("research_id")
                st.session_state.search_query = h.get("query")
                st.rerun()
    else:
        st.caption("No previous research yet.")

# -------------------------------------------------------------------
# Main Research Studio (Product-Focused Flow)
# -------------------------------------------------------------------
render_header()

# Central Prompt: "What do you want to research?"
st.markdown('<div class="search-container">', unsafe_allow_html=True)
st.markdown('<div class="search-label">What do you want to research?</div>', unsafe_allow_html=True)

col_input, col_action = st.columns([5, 1.2])
with col_input:
    user_query = st.text_input(
        "Research Query",
        value=st.session_state.search_query,
        placeholder="Enter research topic, method, or technical question...",
        label_visibility="collapsed"
    )
with col_action:
    start_btn = st.button("Start Research", type="primary", use_container_width=True)

# Quick suggestion chips
suggestions = [
    "Latest approaches for Agentic RAG",
    "Multi-Agent Coordination and Consensus",
    "LLM Evaluation & Benchmarking",
    "GraphRAG vs Dense Retrieval",
    "LLM Security & Jailbreak Defense"
]
chip_cols = st.columns(len(suggestions))
for idx, s in enumerate(suggestions):
    with chip_cols[idx]:
        if st.button(s, key=f"chip_{idx}", use_container_width=True):
            st.session_state.search_query = s
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Start Research Trigger
if start_btn:
    if not user_query.strip():
        st.warning("Please enter a research topic to begin.")
    else:
        try:
            res = api.start_research(
                query=user_query.strip(),
                max_papers=max_papers,
                groq_api_key=None,
                groq_model=selected_model,
                include_web=include_web,
                download_pdfs=download_pdfs
            )
            st.session_state.active_research_id = res.get("research_id")
            st.session_state.search_query = user_query.strip()
            st.rerun()
        except Exception as e:
            st.error(f"Could not initiate research: {e}")

# -------------------------------------------------------------------
# Active Research Execution & Report Presentation
# -------------------------------------------------------------------
if st.session_state.active_research_id:
    session = api.get_research_status(st.session_state.active_research_id)
    if session:
        status = session.get("status")

        # 3-Stage Progress: Researching sources... -> Analyzing papers... -> Research Report
        render_research_status(session)

        # Polling if in progress
        if status in ("queued", "running"):
            time.sleep(1.5)
            st.rerun()

        # Display Final Research Report when complete
        elif status == "completed":
            report = session.get("report")
            papers = session.get("papers", [])
            web = session.get("web_results", [])
            analyses = session.get("analyses", [])
            reviews = session.get("reviews", [])
            comp_table = session.get("comparison_table", [])

            st.markdown(f"## 📋 Research Report: {session.get('query')}")

            # Action bar: Download & Stats
            col_stat, col_btn1, col_btn2 = st.columns([3, 1, 1])
            with col_stat:
                st.markdown(f"**Discovered:** {len(papers)} peer-reviewed papers • {len(web)} web resources • {len(analyses)} architectural analyses")
            with col_btn1:
                if report:
                    st.download_button(
                        "📥 Download Markdown",
                        data=report.get("full_markdown", ""),
                        file_name=f"ResearchReport_{session.get('research_id')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            with col_btn2:
                if report:
                    st.download_button(
                        "📥 Download JSON",
                        data=str(report),
                        file_name=f"ResearchReport_{session.get('research_id')}.json",
                        mime="application/json",
                        use_container_width=True
                    )

            st.markdown("---")

            # Main Result Tabs
            tab_report, tab_sources, tab_web, tab_matrix, tab_critique, tab_direct = st.tabs([
                "📄 Research Report",
                f"📚 Papers ({len(papers)})",
                f"💻 Code & Web ({len(web)})",
                "🔍 Comparison Matrix",
                "⚖️ Critical Review",
                "➕ Analyze Specific PDF"
            ])

            # 1. Full 14-Section Report
            with tab_report:
                if report:
                    st.markdown('<div class="report-paper">', unsafe_allow_html=True)
                    st.markdown(report.get("full_markdown", "Report generated successfully."))
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Report synthesis in progress...")

            # 2. Discovered Papers
            with tab_sources:
                st.markdown("### Discovered Academic Papers (arXiv)")
                for idx, p in enumerate(papers):
                    render_paper_card(p, idx)

            # 3. Codebases & Web Resources
            with tab_web:
                st.markdown("### Practical Implementations & Code Repositories")
                for w in web:
                    render_web_card(w)

            # 4. Comparative Matrix
            with tab_matrix:
                st.markdown("### Cross-Paper Comparative Matrix")
                render_comparison_table(comp_table)

            # 5. Critical Peer Review
            with tab_critique:
                st.markdown("### Critical Review & Open Research Questions")
                for r in reviews:
                    with st.expander(f"⚖️ Review for: {r.get('title', 'Paper')}", expanded=True):
                        st.markdown("**Key Limitations:**")
                        for lim in r.get("limitations", []):
                            st.markdown(f"- ⚠️ {lim}")
                        st.markdown("**Open Questions & Future Work:**")
                        for oq in r.get("open_questions", []):
                            st.markdown(f"- 🔭 {oq}")

            # 6. Direct Paper Analyzer (Single paper / PDF upload)
            with tab_direct:
                st.markdown("### Analyze an Additional Paper or PDF")
                direct_mode = st.radio("Input Type", ["arXiv ID or URL", "Upload PDF"], horizontal=True)
                if direct_mode == "arXiv ID or URL":
                    p_input = st.text_input("arXiv ID or URL", placeholder="e.g. 2401.03428")
                    if st.button("Analyze Paper", type="primary"):
                        if p_input.strip():
                            with st.spinner("Analyzing with multi-agent team..."):
                                try:
                                    res = api.analyze_single_paper(
                                        arxiv_id=p_input.strip(),
                                        groq_api_key=None,
                                        groq_model=selected_model
                                    )
                                    st.success(f"Analyzed: {res.get('title')}")
                                    st.json(res.get("analysis"))
                                except Exception as err:
                                    st.error(f"Analysis failed: {err}")
                else:
                    up_pdf = st.file_uploader("Upload PDF Paper", type=["pdf"])
                    if up_pdf and st.button("Analyze Uploaded PDF", type="primary"):
                        with st.spinner("Extracting text and analyzing..."):
                            try:
                                res = api.upload_pdf(
                                    file_bytes=up_pdf.getvalue(),
                                    filename=up_pdf.name,
                                    groq_api_key=None,
                                    groq_model=selected_model
                                )
                                st.success(f"Analyzed: {res.get('filename')}")
                                st.json(res.get("analysis"))
                            except Exception as err:
                                st.error(f"Analysis failed: {err}")

        elif status == "failed":
            st.error(f"Research pipeline failed: {session.get('error_message')}")
