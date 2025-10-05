#!/usr/bin/env python3
"""
Cricket Manager - Root Agent
Coordinates all sub-agents and manages the cricket statistics workflow
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from google.adk import Agent
from google.adk.tools import FunctionTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CricketManager:
    """Root agent that coordinates all cricket data collection and analysis"""
    
    def __init__(self):
        self.sub_agents = {}
        self.data_sources = [
            'espn_direct',
            'espn_google', 
            'wikipedia'
        ]
        self.analyzer_agent = None
        self.setup_sub_agents()
    
    def setup_sub_agents(self):
        """Initialize all sub-agents"""
        try:
            # Import sub-agent instances
            from .sub_agents.espn_direct.agent import espn_direct_agent_instance
            from .sub_agents.espn_google.agent import espn_google_agent_instance
            from .sub_agents.wikipedia.agent import wikipedia_agent_instance
            from .sub_agents.analyzer.agent import analyzer_agent_instance
            
            self.sub_agents = {
                'espn_direct': espn_direct_agent_instance,
                'espn_google': espn_google_agent_instance,
                'wikipedia': wikipedia_agent_instance
            }
            self.analyzer_agent = analyzer_agent_instance
            
            print("✅ All sub-agents initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing sub-agents: {e}")
    
    async def collect_data_from_sources(self, player_name: str, format_type: str = "all") -> Dict[str, Any]:
        """Collect data from all available sources concurrently"""
        print(f"🔍 Collecting data for {player_name} ({format_type}) from all sources...")
        
        tasks = []
        results = {}
        
        # Start all data collection tasks concurrently
        for source_name, agent in self.sub_agents.items():
            task = asyncio.create_task(
                self._collect_from_source(agent, player_name, format_type, source_name)
            )
            tasks.append((source_name, task))
        
        # Wait for all tasks to complete
        for source_name, task in tasks:
            try:
                result = await task
                results[source_name] = result
                print(f"✅ {source_name}: {'Success' if result.get('success') else 'Failed'}")
            except Exception as e:
                print(f"❌ {source_name}: Error - {e}")
                results[source_name] = {
                    'success': False,
                    'error': str(e),
                    'data_source': source_name
                }
        
        return results
    
    def _format_data_source_status(self, all_results: Dict[str, Any], successful_results: Dict[str, Any]) -> str:
        """Format data source status for display in UI"""
        status_lines = ["**📊 Data Source Status:**"]
        status_lines.append("")
        
        # Define source display names and emojis
        source_display = {
            'espn_direct': '📺 ESPN Cricinfo Direct',
            'espn_google': '🔍 ESPN via Google',
            'wikipedia': '📚 Wikipedia'
        }
        
        for source_name in ['espn_direct', 'espn_google', 'wikipedia']:
            if source_name in all_results:
                result = all_results[source_name]
                is_successful = result.get('success', False)
                is_fallback = result.get('fallback_data', False)
                
                if is_successful:
                    if is_fallback:
                        status = "✅ Success (Fallback Data)"
                        emoji = "⚠️"
                    else:
                        status = "✅ Success (Live Data)"
                        emoji = "🟢"
                else:
                    status = "❌ Failed"
                    emoji = "🔴"
                
                display_name = source_display.get(source_name, source_name)
                status_lines.append(f"{emoji} **{display_name}**: {status}")
        
        status_lines.append("")
        status_lines.append(f"**Summary:** {len(successful_results)}/{len(all_results)} sources successful")
        
        return "\n".join(status_lines)
    
    async def _collect_from_source(self, agent, player_name: str, format_type: str, source_name: str) -> Dict[str, Any]:
        """Collect data from a specific source"""
        try:
            # Call the sub-agent's search function
            result = await agent.search_player(player_name, format_type)
            result['data_source'] = source_name
            # Don't override success - let the agent determine it
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data_source': source_name
            }
    
    async def analyze_player(self, player_name: str, format_type: str = "all") -> str:
        """Main function to analyze a player using all available sources"""
        start_time = time.time()
        
        try:
            # Step 1: Collect data from all sources
            print(f"🏏 Starting analysis for {player_name} ({format_type})")
            data_results = await self.collect_data_from_sources(player_name, format_type)
            
            # Step 2: Filter successful results
            successful_results = {
                source: data for source, data in data_results.items() 
                if data.get('success', False)
            }
            
            if not successful_results:
                return f"❌ No data sources were successful for {player_name}. All sources failed."
            
            # Step 3: Send to analyzer agent for AI analysis
            print(f"🧠 Sending {len(successful_results)} successful results to analyzer...")
            analysis_result = await self.analyzer_agent.analyze_player_data(
                player_name, 
                format_type, 
                successful_results
            )
            
            # Step 4: Format final response
            execution_time = time.time() - start_time
            
            # Create data source status summary
            data_source_status = self._format_data_source_status(data_results, successful_results)
            
            response = f"""🏏 **Cricket Player Analysis**

**Player:** {player_name}
**Format:** {format_type}
**Analysis Time:** {execution_time:.2f} seconds

{data_source_status}

{analysis_result}

---
*Analysis completed using {len(successful_results)} data source(s)*
"""
            
            return response
            
        except Exception as e:
            return f"❌ Error analyzing player {player_name}: {str(e)}"
    
    async def compare_players(self, player1: str, player2: str, format_type: str = "all") -> str:
        """Compare two players using all available sources"""
        try:
            print(f"⚖️ Starting comparison: {player1} vs {player2} ({format_type})")
            
            # Collect data for both players
            player1_data = await self.collect_data_from_sources(player1, format_type)
            player2_data = await self.collect_data_from_sources(player2, format_type)
            
            # Filter successful results
            player1_successful = {
                source: data for source, data in player1_data.items() 
                if data.get('success', False)
            }
            player2_successful = {
                source: data for source, data in player2_data.items() 
                if data.get('success', False)
            }
            
            if not player1_successful or not player2_successful:
                return f"❌ Insufficient data for comparison. Player1 sources: {len(player1_successful)}, Player2 sources: {len(player2_successful)}"
            
            # Send to analyzer for comparison
            comparison_result = await self.analyzer_agent.compare_players_data(
                player1, player2, format_type, player1_successful, player2_successful
            )
            
            # Add data source status for both players
            player1_status = self._format_data_source_status(player1_data, player1_successful)
            player2_status = self._format_data_source_status(player2_data, player2_successful)
            
            formatted_result = f"""⚖️ **Player Comparison**

**Player 1:** {player1}
{player1_status}

**Player 2:** {player2}
{player2_status}

{comparison_result}

---
*Comparison completed using {len(player1_successful)} sources for {player1} and {len(player2_successful)} sources for {player2}*
"""
            
            return formatted_result
            
        except Exception as e:
            return f"❌ Error comparing players: {str(e)}"

# Create the root agent instance
cricket_manager = CricketManager()

# Define the root agent for ADK
root_agent = Agent(name="CricketManager")
