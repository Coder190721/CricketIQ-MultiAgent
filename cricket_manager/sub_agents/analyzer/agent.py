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
    
    async def analyze_player_data(self, player_name: str, format_type: str, data_results: Dict[str, Any], mode: str = "batting") -> str:
        """Analyze player data from all sources using Gemini"""
        print(f"🧠 Analyzer: Analyzing {player_name} with {len(data_results)} data sources")
        
        if not self.model:
            return "❌ Gemini model not available for analysis"
        
        try:
            # Prepare data for analysis
            analysis_prompt = self._create_analysis_prompt(player_name, format_type, data_results, mode)
            
            # Get AI analysis
            response = await self._get_gemini_analysis(analysis_prompt)
            
            return response
            
        except Exception as e:
            return f"❌ Error in AI analysis: {str(e)}"
    
    async def compare_players_data(self, player1: str, player2: str, format_type: str, 
                                 player1_data: Dict[str, Any], player2_data: Dict[str, Any], mode: str = "batting") -> str:
        """Compare two players using data from all sources"""
        print(f"🧠 Analyzer: Comparing {player1} vs {player2}")
        
        if not self.model:
            return "❌ Gemini model not available for comparison"
        
        try:
            # Prepare comparison prompt
            comparison_prompt = self._create_comparison_prompt(
                player1, player2, format_type, player1_data, player2_data, mode
            )
            
            # Get AI comparison
            response = await self._get_gemini_analysis(comparison_prompt)
            
            return response
            
        except Exception as e:
            return f"❌ Error in AI comparison: {str(e)}"
    
    def _create_analysis_prompt(self, player_name: str, format_type: str, data_results: Dict[str, Any], mode: str = "batting") -> str:
        """Create analysis prompt for Gemini"""
        # Mode-specific analysis focus
        mode_focus = {
            "batting": "batting performance, runs, averages, strike rates, centuries, and batting records",
            "bowling": "bowling performance, wickets, bowling averages, economy rates, strike rates, and bowling records", 
            "fielding": "fielding performance, catches, stumpings, dismissals, and fielding records"
        }
        
        focus_area = mode_focus.get(mode, "overall performance")
        
        prompt = f"""
You are a cricket statistics expert. Analyze the following data for {player_name} in {format_type} format, focusing specifically on {focus_area}.

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
        
        # Mode-specific analysis instructions
        if mode == "batting":
            analysis_instructions = f"""
Please provide a comprehensive BATTING analysis of {player_name} including:

1. **Batting Overview**: Career batting summary and style
2. **Batting Statistics**: Runs, averages, strike rates, centuries, fifties
3. **Format Performance**: How they bat in {format_type} cricket
4. **Batting Records**: Notable batting achievements and records
5. **Batting Strengths**: Key batting strengths and techniques
6. **Batting Assessment**: Overall batting ability and ranking

Focus specifically on batting performance, runs scored, batting averages, strike rates, centuries, and batting records.
"""
        elif mode == "bowling":
            analysis_instructions = f"""
Please provide a comprehensive BOWLING analysis of {player_name} including:

1. **Bowling Overview**: Career bowling summary and style
2. **Bowling Statistics**: Wickets, bowling averages, economy rates, strike rates
3. **Format Performance**: How they bowl in {format_type} cricket
4. **Bowling Records**: Notable bowling achievements and records
5. **Bowling Strengths**: Key bowling strengths and techniques
6. **Bowling Assessment**: Overall bowling ability and ranking

Focus specifically on bowling performance, wickets taken, bowling averages, economy rates, and bowling records.
"""
        elif mode == "fielding":
            analysis_instructions = f"""
Please provide a comprehensive FIELDING analysis of {player_name} including:

1. **Fielding Overview**: Career fielding summary and positions
2. **Fielding Statistics**: Catches, stumpings, dismissals, fielding efficiency
3. **Format Performance**: How they field in {format_type} cricket
4. **Fielding Records**: Notable fielding achievements and records
5. **Fielding Strengths**: Key fielding strengths and techniques
6. **Fielding Assessment**: Overall fielding ability and ranking

Focus specifically on fielding performance, catches, stumpings, dismissals, and fielding records.
"""
        else:
            analysis_instructions = f"""
Please provide a comprehensive analysis of {player_name} including:

1. **Player Overview**: Basic information and career summary
2. **Statistical Analysis**: Key performance metrics and achievements
3. **Format Performance**: How they perform in {format_type} cricket
4. **Career Highlights**: Notable achievements and records
5. **Data Quality Assessment**: Reliability of different data sources
6. **Overall Assessment**: Summary and conclusion
"""

        prompt += analysis_instructions + """

Format your response in a clear, structured manner with proper headings and bullet points.
"""
        
        return prompt
    
    def _create_comparison_prompt(self, player1: str, player2: str, format_type: str,
                                player1_data: Dict[str, Any], player2_data: Dict[str, Any], mode: str = "batting") -> str:
        """Create comparison prompt for Gemini"""
        # Mode-specific comparison focus
        mode_focus = {
            "batting": "batting performance, runs, averages, strike rates, centuries, and batting records",
            "bowling": "bowling performance, wickets, bowling averages, economy rates, strike rates, and bowling records", 
            "fielding": "fielding performance, catches, stumpings, dismissals, and fielding records"
        }
        
        focus_area = mode_focus.get(mode, "overall performance")
        
        prompt = f"""
You are a cricket statistics expert. Compare the following two players: {player1} vs {player2} in {format_type} format, focusing specifically on {focus_area}.

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
        
        # Mode-specific comparison instructions
        if mode == "batting":
            comparison_instructions = f"""
Please provide a comprehensive BATTING comparison of {player1} vs {player2} including:

1. **Batting Head-to-Head**: Direct batting statistical comparison
2. **Batting Strengths**: What each player excels at in batting
3. **Format Batting Performance**: How they compare in {format_type} batting
4. **Batting Achievements**: Notable batting records and milestones
5. **Batting Assessment**: Who is the better batsman and why
6. **Data Reliability**: Assessment of batting data quality from different sources

Focus specifically on batting performance, runs scored, batting averages, strike rates, centuries, and batting records.
"""
        elif mode == "bowling":
            comparison_instructions = f"""
Please provide a comprehensive BOWLING comparison of {player1} vs {player2} including:

1. **Bowling Head-to-Head**: Direct bowling statistical comparison
2. **Bowling Strengths**: What each player excels at in bowling
3. **Format Bowling Performance**: How they compare in {format_type} bowling
4. **Bowling Achievements**: Notable bowling records and milestones
5. **Bowling Assessment**: Who is the better bowler and why
6. **Data Reliability**: Assessment of bowling data quality from different sources

Focus specifically on bowling performance, wickets taken, bowling averages, economy rates, and bowling records.
"""
        elif mode == "fielding":
            comparison_instructions = f"""
Please provide a comprehensive FIELDING comparison of {player1} vs {player2} including:

1. **Fielding Head-to-Head**: Direct fielding statistical comparison
2. **Fielding Strengths**: What each player excels at in fielding
3. **Format Fielding Performance**: How they compare in {format_type} fielding
4. **Fielding Achievements**: Notable fielding records and milestones
5. **Fielding Assessment**: Who is the better fielder and why
6. **Data Reliability**: Assessment of fielding data quality from different sources

Focus specifically on fielding performance, catches, stumpings, dismissals, and fielding records.
"""
        else:
            comparison_instructions = f"""
Please provide a comprehensive comparison of {player1} vs {player2} including:

1. **Head-to-Head Comparison**: Direct statistical comparison
2. **Strengths and Weaknesses**: What each player excels at
3. **Format Performance**: How they compare in {format_type} cricket
4. **Career Achievements**: Notable records and milestones
5. **Overall Assessment**: Who is better and why
6. **Data Reliability**: Assessment of data quality from different sources
"""

        prompt += comparison_instructions + """

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
