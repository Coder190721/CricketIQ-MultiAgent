"""
Sub-Agents Package
Imports all sub-agents for the cricket manager
"""

# Import all sub-agents
from .espn_direct.agent import espn_direct_agent
from .espn_google.agent import espn_google_agent
from .cricbuzz.agent import cricbuzz_agent
from .wikipedia.agent import wikipedia_agent
from .google_search.agent import google_search_agent
from .analyzer.agent import analyzer_agent

__all__ = [
    'espn_direct_agent',
    'espn_google_agent', 
    'cricbuzz_agent',
    'wikipedia_agent',
    'google_search_agent',
    'analyzer_agent'
]