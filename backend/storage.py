import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
from backend.models import ResearchSession, ProgressStep
from backend.config import settings

logger = logging.getLogger(__name__)

class SessionStorage:
    def __init__(self):
        self._memory_sessions: Dict[str, ResearchSession] = {}
        self.sessions_dir: Path = settings.SESSIONS_DIR
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._load_from_disk()

    def _load_from_disk(self):
        """Pre-populate memory cache from disk."""
        try:
            for file_path in self.sessions_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        session = ResearchSession.model_validate(data)
                        self._memory_sessions[session.research_id] = session
                except Exception as e:
                    logger.warning(f"Could not load session from {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error accessing sessions directory: {e}")

    def save_session(self, session: ResearchSession):
        """Save session to both in-memory cache and disk."""
        session.updated_at = datetime.utcnow().isoformat()
        self._memory_sessions[session.research_id] = session
        
        file_path = self.sessions_dir / f"{session.research_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(session.model_dump_json(indent=2))
        except Exception as e:
            logger.error(f"Failed to persist session {session.research_id} to disk: {e}")

    def get_session(self, research_id: str) -> Optional[ResearchSession]:
        """Retrieve a session by research_id."""
        if research_id in self._memory_sessions:
            return self._memory_sessions[research_id]
            
        file_path = self.sessions_dir / f"{research_id}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = ResearchSession.model_validate(data)
                    self._memory_sessions[research_id] = session
                    return session
            except Exception as e:
                logger.error(f"Failed reading session file {file_path}: {e}")
        return None

    def update_step(self, research_id: str, step_id: str, status: str, details: Optional[str] = None):
        """Update a specific progress step in the session."""
        session = self.get_session(research_id)
        if not session:
            return
            
        updated = False
        for step in session.progress_steps:
            if step.id == step_id:
                step.status = status
                step.timestamp = datetime.utcnow().isoformat()
                if details:
                    step.details = details
                updated = True
                break
                
        if not updated:
            session.progress_steps.append(
                ProgressStep(
                    id=step_id,
                    name=step_id.replace("_", " ").title(),
                    status=status,
                    details=details
                )
            )
            
        self.save_session(session)

    def list_sessions(self, limit: int = 30) -> List[Dict[str, Any]]:
        """List summary of all sessions sorted by updated_at descending."""
        summaries = []
        for s in self._memory_sessions.values():
            summaries.append({
                "research_id": s.research_id,
                "query": s.query,
                "status": s.status,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "papers_count": len(s.papers),
                "web_results_count": len(s.web_results),
                "has_report": s.report is not None
            })
        summaries.sort(key=lambda x: x["updated_at"], reverse=True)
        return summaries[:limit]

storage = SessionStorage()
