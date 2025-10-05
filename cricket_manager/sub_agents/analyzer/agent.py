#!/usr/bin/env python3
"""
Analyzer Sub-Agent
Handles AI analysis using Gemini model with data from various sources
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.generativeai import GenerativeModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AnalyzerAgent:
    """Sub-agent for AI analysis using Gemini model"""
    
    def __init__(self):
        self.model = None
        self.setup_gemini()
    
    def setup_gemini(self):
        """Initialize Gemini model"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key or api_key == 'your_google_api_key_here':
                print("❌ Google API key not configured")
                return
            
            # Initialize Gemini model
            self.model = GenerativeModel('gemini-1.5-flash')
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
            
            # Print the entire prompt to terminal
            print("\n" + "="*80)
            print("🔍 COMPLETE AI PROMPT BEING SENT TO GEMINI:")
            print("="*80)
            print(analysis_prompt)
            print("="*80)
            print("📤 Sending prompt to Gemini for analysis...")
            print("="*80 + "\n")
            
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
            
            # Print the entire prompt to terminal
            print("\n" + "="*80)
            print("🔍 COMPLETE AI COMPARISON PROMPT BEING SENT TO GEMINI:")
            print("="*80)
            print(comparison_prompt)
            print("="*80)
            print("📤 Sending comparison prompt to Gemini for analysis...")
            print("="*80 + "\n")
            
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

1. **Batting Overview**: Basic batting information and style
2. **Statistical Analysis**: Key batting metrics and achievements
3. **Format Performance**: How they perform in {format_type} cricket batting
4. **Batting Strengths**: Key batting strengths and techniques
5. **Batting Assessment**: Overall batting ability and ranking

Focus specifically on batting performance, runs, averages, strike rates, centuries, and batting records.
"""
        elif mode == "bowling":
            analysis_instructions = f"""
Please provide a comprehensive BOWLING analysis of {player_name} including:

1. **Bowling Overview**: Basic bowling information and style
2. **Statistical Analysis**: Key bowling metrics and achievements
3. **Format Performance**: How they perform in {format_type} cricket bowling
4. **Bowling Strengths**: Key bowling strengths and techniques
5. **Bowling Assessment**: Overall bowling ability and ranking

Focus specifically on bowling performance, wickets, bowling averages, economy rates, strike rates, and bowling records.
"""
        elif mode == "fielding":
            analysis_instructions = f"""
Please provide a comprehensive FIELDING analysis of {player_name} including:

1. **Fielding Overview**: Basic fielding information and style
2. **Statistical Analysis**: Key fielding metrics and achievements
3. **Format Performance**: How they perform in {format_type} cricket fielding
4. **Fielding Strengths**: Key fielding strengths and techniques
5. **Fielding Assessment**: Overall fielding ability and ranking

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
You are a cricket statistics expert. Compare the following two players focusing specifically on {focus_area}:

Player 1: {player1}
Player 2: {player2}
Format: {format_type}
Focus Area: {focus_area}

Data for {player1}:
"""
        
        for source, data in player1_data.items():
            prompt += f"\n--- {source.upper()} DATA FOR {player1.upper()} ---\n"
            if data.get('success'):
                prompt += f"Status: Success\n"
                if 'player_info' in data:
                    prompt += f"Player Info: {json.dumps(data['player_info'], indent=2)}\n"
                if 'stats' in data:
                    prompt += f"Statistics: {json.dumps(data['stats'], indent=2)}\n"
                if 'career_stats' in data:
                    prompt += f"Career Stats: {json.dumps(data['career_stats'], indent=2)}\n"
            else:
                prompt += f"Status: Failed - {data.get('error', 'Unknown error')}\n"
        
        prompt += f"\nData for {player2}:\n"
        
        for source, data in player2_data.items():
            prompt += f"\n--- {source.upper()} DATA FOR {player2.upper()} ---\n"
            if data.get('success'):
                prompt += f"Status: Success\n"
                if 'player_info' in data:
                    prompt += f"Player Info: {json.dumps(data['player_info'], indent=2)}\n"
                if 'stats' in data:
                    prompt += f"Statistics: {json.dumps(data['stats'], indent=2)}\n"
                if 'career_stats' in data:
                    prompt += f"Career Stats: {json.dumps(data['career_stats'], indent=2)}\n"
            else:
                prompt += f"Status: Failed - {data.get('error', 'Unknown error')}\n"
        
        # Mode-specific comparison instructions
        if mode == "batting":
            comparison_instructions = f"""
Please provide a comprehensive BATTING comparison between {player1} and {player2} including:

1. **Batting Overview**: Compare their batting styles and approaches
2. **Statistical Comparison**: Side-by-side batting metrics
3. **Format Performance**: How they compare in {format_type} cricket batting
4. **Batting Strengths**: Compare their batting strengths and techniques
5. **Batting Assessment**: Who is the better batsman and why

Focus specifically on batting performance, runs, averages, strike rates, centuries, and batting records.
"""
        elif mode == "bowling":
            comparison_instructions = f"""
Please provide a comprehensive BOWLING comparison between {player1} and {player2} including:

1. **Bowling Overview**: Compare their bowling styles and approaches
2. **Statistical Comparison**: Side-by-side bowling metrics
3. **Format Performance**: How they compare in {format_type} cricket bowling
4. **Bowling Strengths**: Compare their bowling strengths and techniques
5. **Bowling Assessment**: Who is the better bowler and why

Focus specifically on bowling performance, wickets, bowling averages, economy rates, strike rates, and bowling records.
"""
        elif mode == "fielding":
            comparison_instructions = f"""
Please provide a comprehensive FIELDING comparison between {player1} and {player2} including:

1. **Fielding Overview**: Compare their fielding styles and approaches
2. **Statistical Comparison**: Side-by-side fielding metrics
3. **Format Performance**: How they compare in {format_type} cricket fielding
4. **Fielding Strengths**: Compare their fielding strengths and techniques
5. **Fielding Assessment**: Who is the better fielder and why

Focus specifically on fielding performance, catches, stumpings, dismissals, and fielding records.
"""
        else:
            comparison_instructions = f"""
Please provide a comprehensive comparison between {player1} and {player2} including:

1. **Player Overview**: Compare their basic information and career summaries
2. **Statistical Comparison**: Side-by-side performance metrics
3. **Format Performance**: How they compare in {format_type} cricket
4. **Career Highlights**: Compare their notable achievements and records
5. **Data Quality Assessment**: Reliability of different data sources
6. **Overall Assessment**: Who is the better player and why
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
You are a cricket expert. Please provide comprehensive insights about: {query}

Please include:
1. Historical context and background
2. Statistical analysis and trends
3. Key players and records involved
4. Current developments and future outlook
5. Expert opinions and analysis

Format your response in a clear, structured manner with proper headings and bullet points.
"""
            
            # Print the entire prompt to terminal
            print("\n" + "="*80)
            print("🔍 COMPLETE CRICKET INSIGHTS PROMPT BEING SENT TO GEMINI:")
            print("="*80)
            print(prompt)
            print("="*80)
            print("📤 Sending insights prompt to Gemini for analysis...")
            print("="*80 + "\n")
            
            response = await self._get_gemini_analysis(prompt)
            return response
            
        except Exception as e:
            return f"❌ Error getting cricket insights: {str(e)}"

# Create the Analyzer agent instance
analyzer_agent_instance = AnalyzerAgent()

# Define the Analyzer agent for ADK
analyzer_agent = Agent(name="Analyzer")