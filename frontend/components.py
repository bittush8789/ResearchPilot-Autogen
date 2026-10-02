import streamlit as st
from typing import List, Dict, Any

def render_header():
    st.markdown("""
    <div class="app-header">
      <div class="app-brand">⚡ ResearchPilot</div>
      <div class="app-tagline">
        Autonomous Multi-Agent Research Assistant &nbsp;•&nbsp; 
        <span class="badge badge-purple" style="font-size:0.78rem; padding: 2px 8px;">GPT-OSS 120B (Medium)</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_research_status(session: Dict[str, Any]):
    """
    Renders the simplified 3-stage research progress:
    1. Researching sources... (arXiv & DuckDuckGo)
    2. Analyzing papers... (AutoGen multi-agent analysis)
    3. Research Report (Synthesis)
    """
    status = session.get("status", "running")
    steps = session.get("progress_steps", [])
    
    # Map steps to phases
    sources_done = any(s.get("id") in ("step_arxiv", "step_web", "step_pdf") and s.get("status") == "completed" for s in steps)
    analysis_done = any(s.get("id") in ("step_analysis", "step_experiments", "step_review") and s.get("status") == "completed" for s in steps)
    report_done = status == "completed"

    sources_active = not sources_done and status == "running"
    analysis_active = sources_done and not analysis_done and status == "running"
    report_active = analysis_done and not report_done and status == "running"

    st.markdown(f"""
    <div class="state-box">
      <div style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; margin-bottom: 12px;">
        Research Progress (Task #{session.get('research_id')})
      </div>
      <div class="state-phase {'done' if sources_done else ('active' if sources_active else '')}">
        <div style="display:flex; align-items:center; gap:10px;">
          <span>{'✓' if sources_done else ('⟳' if sources_active else '○')}</span>
          <strong>1. Researching sources...</strong>
        </div>
        <span class="badge {'badge-emerald' if sources_done else 'badge-blue'}">
          {'Completed' if sources_done else ('In Progress' if sources_active else 'Queued')}
        </span>
      </div>
      <div class="state-phase {'done' if analysis_done else ('active' if analysis_active else '')}">
        <div style="display:flex; align-items:center; gap:10px;">
          <span>{'✓' if analysis_done else ('⟳' if analysis_active else '○')}</span>
          <strong>2. Analyzing papers...</strong>
        </div>
        <span class="badge {'badge-emerald' if analysis_done else 'badge-blue'}">
          {'Completed' if analysis_done else ('In Progress' if analysis_active else 'Queued')}
        </span>
      </div>
      <div class="state-phase {'done' if report_done else ('active' if report_active else '')}">
        <div style="display:flex; align-items:center; gap:10px;">
          <span>{'✓' if report_done else ('⟳' if report_active else '○')}</span>
          <strong>3. Research Report</strong>
        </div>
        <span class="badge {'badge-emerald' if report_done else 'badge-blue'}">
          {'Ready' if report_done else ('Synthesizing...' if report_active else 'Pending')}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Optional collapsible expander to view granular agent logs
    agent_logs = session.get("agent_logs", [])
    if agent_logs:
        with st.expander("🔍 View AutoGen Agent Activity Stream", expanded=False):
            for log in reversed(agent_logs[-8:]):
                agent = log.get("agent", "Agent")
                msg = log.get("message", "")
                ts = log.get("timestamp", "")[:19].replace("T", " ")
                st.markdown(f"**[{ts}] 🤖 {agent}:** {msg}")

def render_paper_card(paper: Dict[str, Any], index: int):
    title = paper.get("title", "Untitled")
    authors = ", ".join(paper.get("authors", [])[:4])
    pub_date = paper.get("publication_date", "")
    arxiv_id = paper.get("arxiv_id", "")
    abstract = paper.get("abstract", "")
    pdf_url = paper.get("pdf_url", "")
    paper_url = paper.get("paper_url", "")

    st.markdown(f"""
    <div class="paper-item">
      <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
        <span class="badge badge-purple">Paper {index + 1}</span>
        <span class="badge badge-blue">{pub_date}</span>
      </div>
      <div class="paper-item-title">{title}</div>
      <div class="paper-item-meta">
        <span>👥 {authors}</span> • <span>📄 arXiv:{arxiv_id}</span>
      </div>
      <div class="paper-item-desc">{abstract}</div>
      <div style="margin-top: 12px; display: flex; gap: 10px;">
        {f'<a href="{paper_url}" target="_blank" style="text-decoration:none;"><button style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); color: #c7d2fe; border-radius: 6px; padding: 5px 12px; font-size: 0.8rem; cursor: pointer;">arXiv Page ↗</button></a>' if paper_url else ''}
        {f'<a href="{pdf_url}" target="_blank" style="text-decoration:none;"><button style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #a7f3d0; border-radius: 6px; padding: 5px 12px; font-size: 0.8rem; cursor: pointer;">Download PDF 📥</button></a>' if pdf_url else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_web_card(item: Dict[str, Any]):
    title = item.get("title", "")
    url = item.get("url", "")
    snippet = item.get("snippet", "")
    source_type = item.get("source_type", "general")

    type_badge = {
        "github": '<span class="badge badge-purple">GitHub Code</span>',
        "docs": '<span class="badge badge-blue">Docs</span>',
        "blog": '<span class="badge badge-emerald">Blog / Guide</span>',
        "general": '<span class="badge">Web</span>'
    }.get(source_type, '<span class="badge">Web</span>')

    st.markdown(f"""
    <div class="web-item">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <strong><a href="{url}" target="_blank" style="color: #38bdf8; text-decoration: none;">{title} ↗</a></strong>
        {type_badge}
      </div>
      <div style="font-size: 0.86rem; color: #94a3b8; margin-bottom: 4px;">{snippet}</div>
      <div style="font-size: 0.76rem; color: #64748b;" class="mono">{url}</div>
    </div>
    """, unsafe_allow_html=True)

def render_comparison_table(rows: List[Dict[str, Any]]):
    if not rows:
        st.info("Comparison table is not available.")
        return

    import pandas as pd
    df = pd.DataFrame([
        {
            "Paper Title": r.get("paper_title", "")[:45] + "...",
            "arXiv ID": r.get("arxiv_id", ""),
            "Approach": r.get("approach", "")[:60] + "...",
            "Datasets": r.get("benchmark_datasets", ""),
            "Metrics": r.get("primary_metrics", ""),
            "Key Strengths": r.get("key_strengths", ""),
            "Key Limitations": r.get("key_limitations", "")
        }
        for r in rows
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
