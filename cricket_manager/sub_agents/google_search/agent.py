#!/usr/bin/env python3
"""
Google Search Sub-Agent
Handles comprehensive Google search using player name, format, and mode
"""

import asyncio
import time
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any
from google.adk import Agent
from google.adk.tools import FunctionTool

class GoogleSearchAgent:
    """Sub-agent for comprehensive Google search using player name, format, and mode"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Enhanced headers for Google search
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'https://www.google.com/'
        })
    
    async def search_player(self, player_name: str, format_type: str = "all", mode: str = "batting") -> Dict[str, Any]:
        """Search for a player using comprehensive Google search with format and mode"""
        print(f"🔍 Google Search: Searching for {player_name} ({format_type}, {mode})")
        
        try:
            # Create comprehensive search query
            search_query = self._create_search_query(player_name, format_type, mode)
            search_url = f"https://www.google.com/search?q={search_query}"
            
            print(f"  📡 Google Search Query: {search_query}")
            await asyncio.sleep(2)  # Rate limiting
            
            response = self.session.get(search_url, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract search results and cricket-related information
                search_results = self._extract_search_results(soup, player_name, format_type, mode)
                
                if search_results:
                    print(f"  ✅ Google Search: Found relevant results for {player_name}")
                    return {
                        'success': True,
                        'name': player_name,
                        'url': f"https://www.google.com/search?q={search_query}",
                        'id': f"google_search_{player_name.lower().replace(' ', '_')}",
                        'data_source': 'google_search',
                        'format_type': format_type,
                        'mode': mode,
                        'timestamp': time.time(),
                        'search_query': search_query,
                        'search_results': search_results
                    }
                else:
                    print(f"  ⚠️ Google Search: No relevant results found, using fallback data")
                    return {
                        'success': True,
                        'name': player_name,
                        'url': f"https://www.google.com/search?q={search_query}",
                        'id': f"google_search_{player_name.lower().replace(' ', '_')}",
                        'data_source': 'google_search_fallback',
                        'format_type': format_type,
                        'mode': mode,
                        'timestamp': time.time(),
                        'fallback_data': True,
                        'search_query': search_query,
                        'player_info': {
                            'name': player_name,
                            'role': self._get_role_from_mode(mode),
                            'team': 'International'
                        },
                        'stats': self._get_fallback_stats(format_type, mode)
                    }
            else:
                print(f"  ❌ Google Search: Failed with status {response.status_code}")
                return {
                    'success': False,
                    'error': f'Google search failed with status {response.status_code}',
                    'data_source': 'google_search',
                    'player_name': player_name
                }
                
        except Exception as e:
            print(f"  ⚠️ Google Search error: {e}, using fallback data")
            return {
                'success': True,
                'name': player_name,
                'url': f"https://www.google.com/search?q={player_name}",
                'id': f"google_search_{player_name.lower().replace(' ', '_')}",
                'data_source': 'google_search_fallback',
                'format_type': format_type,
                'mode': mode,
                'timestamp': time.time(),
                'fallback_data': True,
                'player_info': {
                    'name': player_name,
                    'role': self._get_role_from_mode(mode),
                    'team': 'International'
                },
                'stats': self._get_fallback_stats(format_type, mode)
            }
    
    def _create_search_query(self, player_name: str, format_type: str, mode: str) -> str:
        """Create a comprehensive search query using player name, format, and mode"""
        # Base query with player name
        query_parts = [player_name]
        
        # Add format-specific terms
        format_terms = {
            "test": ["test cricket", "test match", "test statistics"],
            "odi": ["ODI cricket", "one day international", "ODI statistics"],
            "t20": ["T20 cricket", "T20I", "T20 statistics", "T20I statistics"],
            "all": ["cricket statistics", "cricket career", "cricket records"]
        }
        
        if format_type.lower() in format_terms:
            query_parts.extend(format_terms[format_type.lower()])
        
        # Add mode-specific terms
        mode_terms = {
            "batting": ["batting average", "runs scored", "centuries", "batting records", "batting statistics"],
            "bowling": ["bowling average", "wickets taken", "bowling figures", "bowling records", "bowling statistics"],
            "fielding": ["catches", "stumpings", "fielding records", "fielding statistics", "dismissals"]
        }
        
        if mode.lower() in mode_terms:
            query_parts.extend(mode_terms[mode.lower()])
        
        # Add cricket-specific terms
        query_parts.extend(["cricket", "stats", "statistics", "records"])
        
        # Join with spaces and URL encode
        search_query = " ".join(query_parts)
        return search_query.replace(' ', '+')
    
    def _extract_search_results(self, soup: BeautifulSoup, player_name: str, format_type: str, mode: str) -> Dict[str, Any]:
        """Extract relevant information from Google search results"""
        results = {
            'player_name': player_name,
            'format_type': format_type,
            'mode': mode,
            'search_snippets': [],
            'cricket_sites': [],
            'statistics_mentioned': []
        }
        
        # Extract search result snippets
        snippets = soup.find_all('div', class_=re.compile(r'VwiC3b|s3v9rd|BNeawe'))
        for snippet in snippets[:5]:  # Limit to first 5 snippets
            text = snippet.get_text(strip=True)
            if text and len(text) > 20:  # Only meaningful snippets
                results['search_snippets'].append(text)
        
        # Look for cricket-related links
        links = soup.find_all('a', href=True)
        cricket_sites = []
        for link in links:
            href = link.get('href', '')
            if any(site in href.lower() for site in ['espncricinfo', 'cricbuzz', 'cricket', 'stats', 'icc']):
                cricket_sites.append({
                    'url': href,
                    'title': link.get_text(strip=True)
                })
        
        results['cricket_sites'] = cricket_sites[:3]  # Limit to first 3 cricket sites
        
        # Look for statistics in the results
        all_text = soup.get_text().lower()
        stat_keywords = ['average', 'runs', 'wickets', 'centuries', 'matches', 'innings', 'strike rate']
        for keyword in stat_keywords:
            if keyword in all_text:
                results['statistics_mentioned'].append(keyword)
        
        return results
    
    def _get_role_from_mode(self, mode: str) -> str:
        """Get player role based on mode"""
        role_mapping = {
            "batting": "Batsman",
            "bowling": "Bowler", 
            "fielding": "Fielder"
        }
        return role_mapping.get(mode.lower(), "Cricketer")
    
    def _get_fallback_stats(self, format_type: str, mode: str) -> Dict[str, Any]:
        """Get fallback statistics based on format and mode"""
        if format_type.lower() == "test":
            if mode.lower() == "batting":
                return {
                    "Test": {
                        "matches": "0",
                        "innings": "0", 
                        "runs": "0",
                        "highest": "0",
                        "average": "0.00",
                        "strike_rate": "0.00",
                        "centuries": "0",
                        "fifties": "0"
                    }
                }
            elif mode.lower() == "bowling":
                return {
                    "Test": {
                        "matches": "0",
                        "innings": "0",
                        "wickets": "0",
                        "best_figures": "0/0",
                        "average": "0.00",
                        "economy": "0.00",
                        "strike_rate": "0.00"
                    }
                }
            elif mode.lower() == "fielding":
                return {
                    "Test": {
                        "matches": "0",
                        "catches": "0",
                        "stumpings": "0",
                        "dismissals": "0"
                    }
                }
        elif format_type.lower() == "odi":
            if mode.lower() == "batting":
                return {
                    "ODI": {
                        "matches": "0",
                        "innings": "0",
                        "runs": "0",
                        "highest": "0",
                        "average": "0.00",
                        "strike_rate": "0.00",
                        "centuries": "0",
                        "fifties": "0"
                    }
                }
            elif mode.lower() == "bowling":
                return {
                    "ODI": {
                        "matches": "0",
                        "innings": "0",
                        "wickets": "0",
                        "best_figures": "0/0",
                        "average": "0.00",
                        "economy": "0.00",
                        "strike_rate": "0.00"
                    }
                }
            elif mode.lower() == "fielding":
                return {
                    "ODI": {
                        "matches": "0",
                        "catches": "0",
                        "stumpings": "0",
                        "dismissals": "0"
                    }
                }
        elif format_type.lower() == "t20":
            if mode.lower() == "batting":
                return {
                    "T20I": {
                        "matches": "0",
                        "innings": "0",
                        "runs": "0",
                        "highest": "0",
                        "average": "0.00",
                        "strike_rate": "0.00",
                        "centuries": "0",
                        "fifties": "0"
                    }
                }
            elif mode.lower() == "bowling":
                return {
                    "T20I": {
                        "matches": "0",
                        "innings": "0",
                        "wickets": "0",
                        "best_figures": "0/0",
                        "average": "0.00",
                        "economy": "0.00",
                        "strike_rate": "0.00"
                    }
                }
            elif mode.lower() == "fielding":
                return {
                    "T20I": {
                        "matches": "0",
                        "catches": "0",
                        "stumpings": "0",
                        "dismissals": "0"
                    }
                }
        else:  # all formats
            return {
                "Test": {
                    "matches": "0",
                    "innings": "0",
                    "runs": "0" if mode == "batting" else "0",
                    "highest": "0" if mode == "batting" else "0",
                    "average": "0.00",
                    "strike_rate": "0.00",
                    "centuries": "0" if mode == "batting" else "0"
                },
                "ODI": {
                    "matches": "0",
                    "innings": "0",
                    "runs": "0" if mode == "batting" else "0",
                    "highest": "0" if mode == "batting" else "0",
                    "average": "0.00",
                    "strike_rate": "0.00",
                    "centuries": "0" if mode == "batting" else "0"
                },
                "T20I": {
                    "matches": "0",
                    "innings": "0",
                    "runs": "0" if mode == "batting" else "0",
                    "highest": "0" if mode == "batting" else "0",
                    "average": "0.00",
                    "strike_rate": "0.00",
                    "centuries": "0" if mode == "batting" else "0"
                }
            }
        
        # Default fallback
        return {
            "General": {
                "matches": "0",
                "statistics": "No data available"
            }
        }

# Create the Google Search agent instance
google_search_agent_instance = GoogleSearchAgent()

# Define the Google Search agent for ADK
google_search_agent = Agent(name="Google_Search")
