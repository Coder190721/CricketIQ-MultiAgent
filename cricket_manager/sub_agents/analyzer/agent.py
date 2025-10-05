#!/usr/bin/env python3
"""
Analyzer Sub-Agent
Handles AI analysis using Gemini with data from all sources
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.generativeai import GenerativeModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AnalyzerAgent:
    """Sub-agent for AI analysis using Gemini"""
    
    def __init__(self):
        self.model = None
        self.setup_gemini()
    
    def setup_gemini(self):
        """Initialize Gemini model"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                print("❌ GOOGLE_API_KEY not found in environment variables")
                return
            
            self.model = GenerativeModel('gemini-2.0-flash-exp')
            print("✅ Gemini model initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Gemini: {e}")
    
    async def analyze_player_data(self, player_name: str, format_type: str, data_results: Dict[str, Any]) -> str:
        """Analyze player data from all sources using Gemini"""
        print(f"🧠 Analyzer: Analyzing {player_name} with {len(data_results)} data sources")
        
        if not self.model:
            return "❌ Gemini model not available for analysis"
        
        try:
            # Prepare data for analysis
            analysis_prompt = self._create_analysis_prompt(player_name, format_type, data_results)
            
            # Get AI analysis
            response = await self._get_gemini_analysis(analysis_prompt)
            
            return response
            
        except Exception as e:
            return f"❌ Error in AI analysis: {str(e)}"
    
    async def compare_players_data(self, player1: str, player2: str, format_type: str, 
                                 player1_data: Dict[str, Any], player2_data: Dict[str, Any]) -> str:
        """Compare two players using data from all sources"""
        print(f"🧠 Analyzer: Comparing {player1} vs {player2}")
        
        if not self.model:
            return "❌ Gemini model not available for comparison"
        
        try:
            # Prepare comparison prompt
            comparison_prompt = self._create_comparison_prompt(
                player1, player2, format_type, player1_data, player2_data
            )
            
            # Get AI comparison
            response = await self._get_gemini_analysis(comparison_prompt)
            
            return response
            
        except Exception as e:
            return f"❌ Error in AI comparison: {str(e)}"
    
    def _create_analysis_prompt(self, player_name: str, format_type: str, data_results: Dict[str, Any]) -> str:
        """Create analysis prompt for Gemini"""
        prompt = f"""
You are a cricket statistics expert. Analyze the following data for {player_name} in {format_type} format.

Data Sources Available: {', '.join(data_results.keys())}

Data from each source:
"""
        
        for source, data in data_results.items():
            prompt += f"\n--- {source.upper()} DATA ---\n"
            if data.get('success'):
                prompt += f"Status: Success\n"
                if 'player_info' in data:
                    prompt += f"Player Info: {json.dumps(data['player_info'], indent=2)}\n"
                if 'stats' in data:
                    prompt += f"Statistics: {json.dumps(data['stats'], indent=2)}\n"
                if 'career_stats' in data:
                    prompt += f"Career Stats: {json.dumps(data['career_stats'], indent=2)}\n"
                if 'biographical_info' in data:
                    prompt += f"Biographical Info: {json.dumps(data['biographical_info'], indent=2)}\n"
            else:
                prompt += f"Status: Failed - {data.get('error', 'Unknown error')}\n"
        
        prompt += f"""

Please provide a comprehensive analysis of {player_name} including:

1. **Player Overview**: Basic information and career summary
2. **Statistical Analysis**: Key performance metrics and achievements
3. **Format Performance**: How they perform in {format_type} cricket
4. **Career Highlights**: Notable achievements and records
5. **Data Quality Assessment**: Reliability of different data sources
6. **Overall Assessment**: Summary and conclusion

Format your response in a clear, structured manner with proper headings and bullet points.
"""
        
        return prompt
    
    def _create_comparison_prompt(self, player1: str, player2: str, format_type: str,
                                player1_data: Dict[str, Any], player2_data: Dict[str, Any]) -> str:
        """Create comparison prompt for Gemini"""
        prompt = f"""
You are a cricket statistics expert. Compare the following two players: {player1} vs {player2} in {format_type} format.

PLAYER 1 DATA ({player1}):
Sources: {', '.join(player1_data.keys())}
"""
        
        for source, data in player1_data.items():
            prompt += f"\n--- {source.upper()} DATA ---\n"
            if data.get('success'):
                prompt += f"Status: Success\n"
                if 'stats' in data:
                    prompt += f"Statistics: {json.dumps(data['stats'], indent=2)}\n"
                if 'player_info' in data:
                    prompt += f"Player Info: {json.dumps(data['player_info'], indent=2)}\n"
            else:
                prompt += f"Status: Failed - {data.get('error', 'Unknown error')}\n"
        
        prompt += f"\nPLAYER 2 DATA ({player2}):\nSources: {', '.join(player2_data.keys())}\n"
        
        for source, data in player2_data.items():
            prompt += f"\n--- {source.upper()} DATA ---\n"
            if data.get('success'):
                prompt += f"Status: Success\n"
                if 'stats' in data:
                    prompt += f"Statistics: {json.dumps(data['stats'], indent=2)}\n"
                if 'player_info' in data:
                    prompt += f"Player Info: {json.dumps(data['player_info'], indent=2)}\n"
            else:
                prompt += f"Status: Failed - {data.get('error', 'Unknown error')}\n"
        
        prompt += f"""

Please provide a comprehensive comparison of {player1} vs {player2} including:

1. **Head-to-Head Comparison**: Direct statistical comparison
2. **Strengths and Weaknesses**: What each player excels at
3. **Format Performance**: How they compare in {format_type} cricket
4. **Career Achievements**: Notable records and milestones
5. **Overall Assessment**: Who is better and why
6. **Data Reliability**: Assessment of data quality from different sources

Format your response in a clear, structured manner with proper headings and bullet points.
"""
        
        return prompt
    
    async def _get_gemini_analysis(self, prompt: str) -> str:
        """Get analysis from Gemini model"""
        try:
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error generating Gemini response: {str(e)}"
    
    async def get_cricket_insights(self, query: str) -> str:
        """Get general cricket insights using Gemini"""
        if not self.model:
            return "❌ Gemini model not available for insights"
        
        try:
            prompt = f"""
You are a cricket statistics expert. Answer the following cricket question:

{query}

Please provide a comprehensive, well-researched answer with:
1. Clear explanation
2. Relevant statistics and examples
3. Historical context if applicable
4. Current trends and insights

Format your response in a clear, structured manner.
"""
            
            response = await self._get_gemini_analysis(prompt)
            return response
            
        except Exception as e:
            return f"❌ Error getting cricket insights: {str(e)}"

# Create the Analyzer agent instance
analyzer_agent_instance = AnalyzerAgent()

# Define the Analyzer agent for ADK
analyzer_agent = Agent(name="Analyzer")
# Create the analyzer agent instance
