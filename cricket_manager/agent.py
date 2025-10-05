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
            'wikipedia',
            'google_search'
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
            from .sub_agents.google_search.agent import google_search_agent_instance
            from .sub_agents.analyzer.agent import analyzer_agent_instance
            
            self.sub_agents = {
                'espn_direct': espn_direct_agent_instance,
                'espn_google': espn_google_agent_instance,
                'wikipedia': wikipedia_agent_instance,
                'google_search': google_search_agent_instance
            }
            self.analyzer_agent = analyzer_agent_instance
            
            print("✅ All sub-agents initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing sub-agents: {e}")
    
    async def collect_data_from_sources(self, player_name: str, format_type: str = "all", mode: str = "batting") -> Dict[str, Any]:
        """Collect data from all available sources concurrently"""
        print(f"🔍 Collecting data for {player_name} ({format_type}, {mode}) from all sources...")
        
        tasks = []
        results = {}
        
        # Create tasks for all data sources
        for source_name in self.data_sources:
            if source_name in self.sub_agents:
                agent = self.sub_agents[source_name]
                
                # Create task for this source
                if source_name == 'google_search':
                    # Google Search agent uses mode parameter
                    task = asyncio.create_task(
                        self._collect_from_source(agent, player_name, format_type, mode, source_name)
                    )
                else:
                    # Other agents use standard parameters
                    task = asyncio.create_task(
                        self._collect_from_source(agent, player_name, format_type, source_name)
                    )
                tasks.append((source_name, task))
        
        # Wait for all tasks to complete
        for source_name, task in tasks:
            try:
                result = await task
                results[source_name] = result
            except Exception as e:
                print(f"❌ Error collecting from {source_name}: {e}")
                results[source_name] = {
                    'success': False,
                    'error': str(e),
                    'data_source': source_name
                }
        
        return results
    
    async def _collect_from_source(self, agent, player_name: str, format_type: str, source_name: str, mode: str = None) -> Dict[str, Any]:
        """Collect data from a specific source"""
        try:
            if source_name == 'google_search' and mode:
                # Google Search agent with mode parameter
                result = await agent.search_player(player_name, format_type, mode)
            else:
                # Standard agents
                result = await agent.search_player(player_name, format_type)
            
            if result.get('success'):
                print(f"✅ {source_name}: Success")
                return result
            else:
                print(f"❌ {source_name}: Failed - {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            print(f"❌ {source_name}: Exception - {e}")
            return {
                'success': False,
                'error': str(e),
                'data_source': source_name
            }
    
    async def analyze_player(self, player_name: str, format_type: str = "all", mode: str = "batting") -> str:
        """Main function to analyze a player using all available sources"""
        start_time = time.time()
        
        try:
            # Step 1: Collect data from all sources
            print(f"🏏 Starting analysis for {player_name} ({format_type}, {mode})")
            data_results = await self.collect_data_from_sources(player_name, format_type, mode)
            
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
                successful_results,
                mode
            )
            
            # Step 4: Format final response
            execution_time = time.time() - start_time
            
            # Create data source status summary
            data_source_status = self._format_data_source_status(data_results, successful_results)
            
            response = f"""🏏 **Cricket Player Analysis**

**Player:** {player_name}
**Format:** {format_type}
**Mode:** {mode.title()}
**Analysis Time:** {execution_time:.2f} seconds

{data_source_status}

{analysis_result}

---
*Analysis completed using {len(successful_results)} data source(s)*
"""
            
            return response
            
        except Exception as e:
            return f"❌ Error analyzing player {player_name}: {str(e)}"
    
    async def compare_players(self, player1: str, player2: str, format_type: str = "all", mode: str = "batting") -> str:
        """Compare two players using all available sources"""
        start_time = time.time()
        
        try:
            print(f"⚖️ Starting comparison: {player1} vs {player2} ({format_type}, {mode})")
            
            # Collect data for both players
            player1_data = await self.collect_data_from_sources(player1, format_type, mode)
            player2_data = await self.collect_data_from_sources(player2, format_type, mode)
            
            # Filter successful results for both players
            player1_successful = {
                source: data for source, data in player1_data.items() 
                if data.get('success', False)
            }
            player2_successful = {
                source: data for source, data in player2_data.items() 
                if data.get('success', False)
            }
            
            if not player1_successful:
                return f"❌ No data sources were successful for {player1}. Cannot compare."
            if not player2_successful:
                return f"❌ No data sources were successful for {player2}. Cannot compare."
            
            # Send to analyzer for comparison
            print(f"🧠 Comparing players with {len(player1_successful)} and {len(player2_successful)} successful results...")
            comparison_result = await self.analyzer_agent.compare_players_data(
                player1, player2, format_type, 
                player1_successful, player2_successful, mode
            )
            
            # Format final response
            execution_time = time.time() - start_time
            
            response = f"""⚖️ **Player Comparison**

**Players:** {player1} vs {player2}
**Format:** {format_type}
**Mode:** {mode.title()}
**Comparison Time:** {execution_time:.2f} seconds

{comparison_result}

---
*Comparison completed using {len(player1_successful)} and {len(player2_successful)} data sources*
"""
            
            return response
            
        except Exception as e:
            return f"❌ Error comparing players: {str(e)}"
    
    def _format_data_source_status(self, all_results: Dict, successful_results: Dict) -> str:
        """Format data source status for display"""
        status = "📊 **Data Source Status:**\n"
        
        # Define source display names and emojis
        source_display = {
            'espn_direct': '📺 ESPN Cricinfo Direct',
            'espn_google': '🔍 ESPN via Google',
            'wikipedia': '📚 Wikipedia',
            'google_search': '🔍 Google Search'
        }
        
        for source_name in ['espn_direct', 'espn_google', 'wikipedia', 'google_search']:
            if source_name in all_results:
                result = all_results[source_name]
                is_successful = result.get('success', False)
                is_fallback = result.get('fallback_data', False)
                
                display_name = source_display.get(source_name, source_name.replace('_', ' ').title())
                
                if is_successful:
                    if is_fallback:
                        status += f"  - {display_name}: ✅ Success (Fallback Data)\n"
                    else:
                        status += f"  - {display_name}: ✅ Success (Live Data)\n"
                else:
                    error = result.get('error', 'Unknown error')
                    status += f"  - {display_name}: ❌ Failed ({error})\n"
        
        return status

# Create the root agent instance
cricket_manager = CricketManager()

# Define the root agent for ADK
root_agent = Agent(name="CricketManager")