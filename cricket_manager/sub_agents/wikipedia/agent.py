#!/usr/bin/env python3
"""
Wikipedia Sub-Agent
Handles Wikipedia data collection for cricket players
"""

import asyncio
import time
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any
from google.adk import Agent
from google.adk.tools import FunctionTool

class WikipediaAgent:
    """Sub-agent for Wikipedia data collection"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://en.wikipedia.org"
        
        # Headers for Wikipedia
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
            'Origin': 'https://en.wikipedia.org'
        })
    
    async def search_player(self, player_name: str, format_type: str = "all") -> Dict[str, Any]:
        """Search for a cricket player on Wikipedia"""
        print(f"📚 Wikipedia: Searching for {player_name}")
        
        try:
            # Create Wikipedia URL
            wiki_url = f"{self.base_url}/wiki/{player_name.replace(' ', '_')}"
            
            print(f"  📡 Trying Wikipedia: {wiki_url}")
            await asyncio.sleep(1)  # Rate limiting
            
            response = self.session.get(wiki_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check if it's a cricket player page
                page_text = soup.get_text().lower()
                if 'cricket' in page_text or 'cricketer' in page_text:
                    print(f"  ✅ Wikipedia: Found cricket player {player_name}")
                    return {
                        'success': True,
                        'name': player_name,
                        'url': wiki_url,
                        'id': player_name.replace(' ', '_').lower(),
                        'data_source': 'wikipedia',
                        'format_type': format_type,
                        'timestamp': time.time()
                    }
                else:
                    print(f"  ❌ Wikipedia: Page exists but not cricket-related")
                    return {
                        'success': False,
                        'error': 'Wikipedia page exists but is not cricket-related',
                        'data_source': 'wikipedia',
                        'player_name': player_name
                    }
            elif response.status_code == 404:
                print(f"  ❌ Wikipedia: No page found for {player_name}")
                return {
                    'success': False,
                    'error': 'No Wikipedia page found for this player',
                    'data_source': 'wikipedia',
                    'player_name': player_name
                }
            else:
                print(f"  ❌ Wikipedia: Failed with status {response.status_code}")
                return {
                    'success': False,
                    'error': f'Wikipedia request failed with status {response.status_code}',
                    'data_source': 'wikipedia',
                    'player_name': player_name
                }
                
        except Exception as e:
            print(f"  ❌ Wikipedia error: {e}")
            return {
                'success': False,
                'error': str(e),
                'data_source': 'wikipedia',
                'player_name': player_name
            }
    
    async def get_player_stats(self, player_url: str, format_type: str) -> Dict[str, Any]:
        """Get player information from Wikipedia"""
        try:
            print(f"  📊 Wikipedia: Getting info from {player_url}")
            
            response = self.session.get(player_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract player information
            player_info = {}
            
            # Get player name from title
            title_element = soup.find('h1', class_='firstHeading')
            if title_element:
                player_info['name'] = title_element.get_text(strip=True)
            
            # Extract infobox data
            infobox = soup.find('table', class_='infobox')
            if infobox:
                rows = infobox.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value and key not in ['', ' ']:
                            player_info[key] = value
            
            # Extract career statistics
            career_stats = self._extract_career_stats(soup)
            
            # Extract biographical information
            bio_info = self._extract_biographical_info(soup)
            
            return {
                'success': True,
                'player_info': player_info,
                'career_stats': career_stats,
                'biographical_info': bio_info,
                'data_source': 'wikipedia',
                'url': player_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data_source': 'wikipedia'
            }
    
    def _extract_career_stats(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract career statistics from Wikipedia page"""
        career_stats = {}
        
        # Look for statistics tables
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            # Check if this table contains cricket statistics
            table_text = table.get_text().lower()
            if any(term in table_text for term in ['test', 'odi', 't20', 'runs', 'wickets', 'matches']):
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value and key not in ['', ' ']:
                            career_stats[key] = value
        
        return career_stats
    
    def _extract_biographical_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract biographical information from Wikipedia page"""
        bio_info = {}
        
        # Get the first paragraph for biographical summary
        first_para = soup.find('p')
        if first_para:
            bio_info['summary'] = first_para.get_text(strip=True)
        
        # Look for specific biographical details
        paragraphs = soup.find_all('p')
        for para in paragraphs:
            text = para.get_text()
            if 'born' in text.lower() and 'date' not in bio_info:
                bio_info['birth_info'] = text.strip()
            elif 'debut' in text.lower() and 'debut' not in bio_info:
                bio_info['debut_info'] = text.strip()
            elif 'retired' in text.lower() and 'retirement' not in bio_info:
                bio_info['retirement_info'] = text.strip()
        
        return bio_info

# Create the Wikipedia agent instance
wikipedia_agent_instance = WikipediaAgent()

# Define the Wikipedia agent for ADK
wikipedia_agent = Agent(name="Wikipedia")
