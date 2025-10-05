#!/usr/bin/env python3
"""
Cricbuzz Sub-Agent
Handles Cricbuzz data collection as alternative cricket source
"""

import asyncio
import time
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any
from google.adk import Agent
from google.adk.tools import FunctionTool

class CricbuzzAgent:
    """Sub-agent for Cricbuzz data collection"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.cricbuzz.com"
        
        # Headers for Cricbuzz
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
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.cricbuzz.com'
        })
    
    async def search_player(self, player_name: str, format_type: str = "all") -> Dict[str, Any]:
        """Search for a player on Cricbuzz"""
        print(f"🏏 Cricbuzz: Searching for {player_name}")
        
        try:
            # Cricbuzz search URL
            search_url = f"{self.base_url}/search?q={player_name.replace(' ', '+')}"
            
            print(f"  📡 Trying Cricbuzz search: {search_url}")
            await asyncio.sleep(1)  # Rate limiting
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for player links in Cricbuzz results
                player_links = soup.find_all('a', href=re.compile(r'/profiles/'))
                
                if player_links:
                    player_url = player_links[0]['href']
                    player_id = re.search(r'/profiles/([^/]+)', player_url)
                    
                    if player_id:
                        print(f"  ✅ Cricbuzz: Found {player_name}")
                        return {
                            'success': True,
                            'name': player_name,
                            'url': f"{self.base_url}{player_url}",
                            'id': player_id.group(1),
                            'data_source': 'cricbuzz',
                            'format_type': format_type,
                            'timestamp': time.time()
                        }
                else:
                    print(f"  ❌ Cricbuzz: No player links found")
                    return {
                        'success': False,
                        'error': 'No player links found in Cricbuzz search results',
                        'data_source': 'cricbuzz',
                        'player_name': player_name,
                        'message': f'Cricbuzz source did not produce any data for {player_name}. No player links found in search results.'
                    }
            else:
                print(f"  ❌ Cricbuzz: Search failed with status {response.status_code}")
                return {
                    'success': False,
                    'error': f'Cricbuzz search failed with status {response.status_code}',
                    'data_source': 'cricbuzz',
                    'player_name': player_name,
                    'message': f'Cricbuzz source did not produce any data for {player_name}. Search failed with status {response.status_code}.'
                }
                
        except Exception as e:
            print(f"  ❌ Cricbuzz error: {e}")
            return {
                'success': False,
                'error': str(e),
                'data_source': 'cricbuzz',
                'player_name': player_name,
                'message': f'Cricbuzz source encountered an error: {str(e)}'
            }
    
    async def get_player_stats(self, player_url: str, format_type: str) -> Dict[str, Any]:
        """Get player statistics from Cricbuzz"""
        try:
            print(f"  📊 Cricbuzz: Getting stats from {player_url}")
            
            response = self.session.get(player_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract player information
            player_info = {}
            
            # Get player name
            name_element = soup.find('h1', class_='cb-font-40')
            if not name_element:
                name_element = soup.find('h1')
            if name_element:
                player_info['name'] = name_element.get_text(strip=True)
            
            # Get player role/team info
            role_elements = soup.find_all('div', class_='cb-font-12')
            for element in role_elements:
                text = element.get_text(strip=True)
                if 'batsman' in text.lower() or 'bowler' in text.lower() or 'all-rounder' in text.lower():
                    player_info['role'] = text
                elif 'team' in text.lower() or 'country' in text.lower():
                    player_info['team'] = text
            
            # Extract statistics
            stats = self._extract_cricbuzz_stats(soup, format_type)
            
            return {
                'success': True,
                'player_info': player_info,
                'stats': stats,
                'data_source': 'cricbuzz',
                'url': player_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data_source': 'cricbuzz'
            }
    
    def _extract_cricbuzz_stats(self, soup: BeautifulSoup, format_type: str) -> Dict[str, Any]:
        """Extract player statistics from Cricbuzz page"""
        stats = {}
        
        # Look for statistics sections
        stat_sections = soup.find_all('div', class_=re.compile(r'cb-col|stats'))
        
        for section in stat_sections:
            # Look for batting/bowling stats
            if 'batting' in section.get_text().lower() or 'bowling' in section.get_text().lower():
                rows = section.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value and key not in ['', ' ']:
                            stats[key] = value
        
        # Also look for general player stats
        stat_tables = soup.find_all('table')
        for table in stat_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value and key not in ['', ' ']:
                        stats[key] = value
        
        return stats

# Create the Cricbuzz agent instance
cricbuzz_agent_instance = CricbuzzAgent()

# Define the Cricbuzz agent for ADK
cricbuzz_agent = Agent(name="Cricbuzz")