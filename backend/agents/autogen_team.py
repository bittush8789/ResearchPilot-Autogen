import logging
from typing import Dict, Any, Optional
import autogen
from backend.agents.prompts import (
    RESEARCH_MANAGER_PROMPT,
    ARXIV_AGENT_PROMPT,
    WEB_RESEARCH_AGENT_PROMPT,
    PAPER_ANALYSIS_AGENT_PROMPT,
    EXPERIMENT_AGENT_PROMPT,
    CRITICAL_REVIEWER_AGENT_PROMPT,
    REPORT_GENERATOR_PROMPT
)
from backend.agents.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

def create_autogen_team(api_key: Optional[str] = None, model: Optional[str] = None) -> Dict[str, autogen.ConversableAgent]:
    """
    Instantiate the 7 specialized AutoGen agents configured with Groq LLM (or mock config).
    """
    has_key = LLMProvider.is_configured(api_key)
    llm_config = LLMProvider.get_autogen_config(api_key, model) if has_key else False

    # 1. Research Manager Agent
    research_manager = autogen.AssistantAgent(
        name="Research_Manager",
        system_message=RESEARCH_MANAGER_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    # 2. arXiv Research Agent
    arxiv_agent = autogen.AssistantAgent(
        name="arXiv_Agent",
        system_message=ARXIV_AGENT_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    # 3. Web Research Agent
    web_research_agent = autogen.AssistantAgent(
        name="Web_Research_Agent",
        system_message=WEB_RESEARCH_AGENT_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    # 4. Paper Analysis Agent
    paper_analysis_agent = autogen.AssistantAgent(
        name="Paper_Analysis_Agent",
        system_message=PAPER_ANALYSIS_AGENT_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    # 5. Experiment Agent
    experiment_agent = autogen.AssistantAgent(
        name="Experiment_Agent",
        system_message=EXPERIMENT_AGENT_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    # 6. Critical Reviewer Agent
    critical_reviewer = autogen.AssistantAgent(
        name="Critical_Reviewer",
        system_message=CRITICAL_REVIEWER_AGENT_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    # 7. Report Generator Agent
    report_generator = autogen.AssistantAgent(
        name="Report_Generator",
        system_message=REPORT_GENERATOR_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER"
    )

    # User Proxy (Coordinator)
    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        max_consecutive_auto_reply=1
    )

    return {
        "user_proxy": user_proxy,
        "research_manager": research_manager,
        "arxiv_agent": arxiv_agent,
        "web_research_agent": web_research_agent,
        "paper_analysis_agent": paper_analysis_agent,
        "experiment_agent": experiment_agent,
        "critical_reviewer": critical_reviewer,
        "report_generator": report_generator
    }
