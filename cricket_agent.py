#!/usr/bin/env python3
"""
Cricket Agent using Google ADK (Agent Development Kit)
Integrates with the Cricket MCP Server to provide intelligent cricket statistics analysis
"""

import os
import json
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from google.generativeai import GenerativeModel
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
import sys

# Load environment variables
load_dotenv()

@dataclass
class AgentEvent:
    """Event data structure for tracking user interactions"""
    event_id: str
    timestamp: datetime
    event_type: str  # 'query', 'analysis', 'comparison', 'insight', 'chat'
    user_input: str
    response: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentConfig:
    """Configuration for the Cricket Agent"""
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7
    max_tokens: int = 8192
    mcp_server_path: str = "cricket_mcp_server.py"
    log_level: str = "INFO"
    log_file: str = "cricket_agent.log"
    events_file: str = "cricket_events.json"
    system_prompt: str = """
    You are a specialized Cricket Statistics Agent powered by Google ADK. 
    Your primary function is to provide comprehensive cricket player statistics and analysis.
    
    You have access to:
    1. ESPN Cricinfo data for detailed player statistics
    2. Statsguru integration for advanced analytics
    3. Comprehensive batting, bowling, and fielding records across all formats (Test, ODI, T20)
    
    Always provide accurate, detailed, and well-formatted responses about cricket statistics.
    When comparing players, highlight key differences and provide context.
    """

class CricketAgent:
    """Cricket Agent using Google ADK framework"""
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.model = None
        self.mcp_process = None
        self.events = []
        self._setup_logging()
        self._setup_model()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Configure logging
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('CricketAgent')
        self.logger.info("Cricket Agent logging initialized")
    
    def _log_event(self, event_type: str, user_input: str, response: str, 
                   processing_time: float, success: bool, error_message: str = None, 
                   metadata: Dict[str, Any] = None):
        """Log an event to the events list and file"""
        event_id = f"event_{int(time.time() * 1000)}"
        event = AgentEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            event_type=event_type,
            user_input=user_input,
            response=response,
            processing_time=processing_time,
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        # Add to events list
        self.events.append(event)
        
        # Log to file
        self.logger.info(f"Event {event_id}: {event_type} - {'SUCCESS' if success else 'FAILED'}")
        if error_message:
            self.logger.error(f"Event {event_id} error: {error_message}")
        
        # Save to events file
        self._save_events()
        
        return event
    
    def _save_events(self):
        """Save events to JSON file"""
        try:
            events_data = []
            for event in self.events:
                event_dict = asdict(event)
                event_dict['timestamp'] = event.timestamp.isoformat()
                events_data.append(event_dict)
            
            with open(self.config.events_file, 'w') as f:
                json.dump(events_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save events: {e}")
    
    def get_events(self, event_type: str = None, limit: int = None) -> List[AgentEvent]:
        """Get events, optionally filtered by type"""
        events = self.events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if limit:
            events = events[-limit:]
        return events
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get statistics about events"""
        if not self.events:
            return {"total_events": 0}
        
        total_events = len(self.events)
        successful_events = len([e for e in self.events if e.success])
        failed_events = total_events - successful_events
        
        event_types = {}
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        avg_processing_time = sum(e.processing_time for e in self.events) / total_events
        
        return {
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": (successful_events / total_events) * 100,
            "event_types": event_types,
            "average_processing_time": avg_processing_time
        }
    
    def _setup_model(self):
        """Initialize the Google Generative AI model"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required")
            
            genai.configure(api_key=api_key)
            self.model = GenerativeModel(
                model_name=self.config.model_name,
                generation_config={
                    'temperature': self.config.temperature,
                    'max_output_tokens': self.config.max_tokens,
                }
            )
            print(f"✅ Cricket Agent initialized with {self.config.model_name}")
            
        except Exception as e:
            print(f"❌ Error initializing model: {e}")
            raise
    
    def start_mcp_server(self):
        """Start the MCP server as a subprocess"""
        try:
            self.mcp_process = subprocess.Popen(
                [sys.executable, self.config.mcp_server_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✅ MCP Server started")
            return True
        except Exception as e:
            print(f"❌ Error starting MCP server: {e}")
            return False
    
    def stop_mcp_server(self):
        """Stop the MCP server"""
        if self.mcp_process:
            self.mcp_process.terminate()
            self.mcp_process.wait()
            print("✅ MCP Server stopped")
    
    def get_player_stats(self, player_name: str, format_type: str = "all") -> Dict[str, Any]:
        """Get comprehensive player statistics using MCP server"""
        try:
            # Import the scraper directly and use it
            from cricket_mcp_server import scraper
            
            # Search for player
            player_info = scraper.search_player(player_name)
            if not player_info:
                return {"error": f"Player '{player_name}' not found"}
            
            # Get basic player information
            basic_info = scraper.get_player_basic_info(player_info['url'])
            
            # Get comprehensive statistics
            stats = scraper.get_player_stats(player_info['id'], format_type)
            
            return {
                "player_info": {
                    "name": basic_info.get('name', player_info['name']),
                    "role": basic_info.get('role', ''),
                    "country": basic_info.get('country', ''),
                    "image": basic_info.get('image', ''),
                    "espn_url": player_info['url'],
                    "data_source": player_info.get('data_source', 'unknown')
                },
                "statistics": stats,
                "format_requested": format_type,
                "data_source": player_info.get('data_source', 'unknown')
            }
        except Exception as e:
            return {"error": f"Failed to get player stats: {e}"}
    
    def _call_mcp_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Call MCP server function directly"""
        try:
            from cricket_mcp_server import scraper
            
            if function_name == "compare_players":
                player1 = kwargs.get('player1')
                player2 = kwargs.get('player2')
                format_type = kwargs.get('format_type', 'all')
                
                # Get stats for both players
                stats1 = self.get_player_stats(player1, format_type)
                stats2 = self.get_player_stats(player2, format_type)
                
                if "error" in stats1 or "error" in stats2:
                    return {"error": "Failed to get statistics for one or both players"}
                
                return {
                    "player1": {
                        "name": stats1["player_info"]["name"],
                        "statistics": stats1["statistics"]
                    },
                    "player2": {
                        "name": stats2["player_info"]["name"],
                        "statistics": stats2["statistics"]
                    },
                    "format": format_type
                }
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            return {"error": f"Failed to call MCP function: {e}"}
    
    def _get_data_source_note(self, data_source: str, player_name: str) -> str:
        """Generate a data source note for the analysis"""
        if data_source == "espn_direct":
            return f"📊 **Data Source**: ESPN Cricinfo (Direct) - Real-time statistics for {player_name}"
        elif data_source == "espn_via_google":
            return f"📊 **Data Source**: ESPN Cricinfo (via Google) - Real-time statistics for {player_name}"
        elif data_source == "cricbuzz":
            return f"📊 **Data Source**: Cricbuzz - Alternative cricket statistics for {player_name}"
        elif data_source == "wikipedia":
            return f"📊 **Data Source**: Wikipedia - General cricket information for {player_name}"
        elif data_source == "mock_data":
            return f"⚠️ **Data Source**: Fallback Data - Using realistic mock statistics for {player_name} (ESPN connection unavailable)"
        else:
            return f"📊 **Data Source**: {data_source.title()} - Statistics for {player_name}"
    
    async def analyze_player(self, player_name: str, format_type: str = "all") -> str:
        """Analyze a cricket player using AI"""
        start_time = time.time()
        user_input = f"Analyze player: {player_name} ({format_type})"
        
        try:
            # Get player statistics
            stats = self.get_player_stats(player_name, format_type)
            
            # Create analysis prompt
            prompt = f"""
            Analyze the following cricket player statistics for {player_name}:
            
            Statistics: {json.dumps(stats, indent=2)}
            
            Please provide a comprehensive analysis including:
            1. Key performance metrics
            2. Strengths and areas for improvement
            3. Comparison with typical standards for the format
            4. Career highlights and notable achievements
            5. Format-specific insights (if applicable)
            
            Format your response in a clear, structured manner.
            """
            
            # Generate analysis using Gemini
            response = self.model.generate_content(prompt)
            processing_time = time.time() - start_time
            
            # Add data source note at the top
            data_source = stats.get("data_source", "unknown")
            source_note = self._get_data_source_note(data_source, player_name)
            
            # Combine source note with analysis
            full_response = f"{source_note}\n\n{response.text}"
            
            # Log successful event
            self._log_event(
                event_type="analysis",
                user_input=user_input,
                response=full_response,
                processing_time=processing_time,
                success=True,
                metadata={
                    "player_name": player_name, 
                    "format_type": format_type,
                    "data_source": data_source
                }
            )
            
            return full_response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error analyzing player: {e}"
            
            # Log failed event
            self._log_event(
                event_type="analysis",
                user_input=user_input,
                response=error_msg,
                processing_time=processing_time,
                success=False,
                error_message=str(e),
                metadata={"player_name": player_name, "format_type": format_type}
            )
            
            return error_msg
    
    async def compare_players(self, player1: str, player2: str, format_type: str = "all") -> str:
        """Compare two cricket players using AI"""
        try:
            # Use the MCP server's compare_players function directly
            comparison_data = self._call_mcp_function("compare_players", 
                                                   player1=player1, 
                                                   player2=player2, 
                                                   format_type=format_type)
            
            # Create comparison prompt
            prompt = f"""
            Compare the following two cricket players:
            
            Comparison Data: {json.dumps(comparison_data, indent=2)}
            
            Please provide a detailed comparison including:
            1. Statistical comparison across key metrics
            2. Relative strengths
            3. Format-specific performance differences
            4. Career trajectory analysis
            5. Overall assessment and recommendation
            
            Format your response in a clear, structured manner with specific data points.
            """
            
            # Generate comparison using Gemini
            response = self.model.generate_content(prompt)
            
            # Add data source note at the top
            data_sources = []
            if isinstance(comparison_data, dict):
                if "player1_data" in comparison_data:
                    data_sources.append(comparison_data.get("player1_data_source", "unknown"))
                if "player2_data" in comparison_data:
                    data_sources.append(comparison_data.get("player2_data_source", "unknown"))
            
            # Create source note for comparison
            if data_sources:
                unique_sources = list(set(data_sources))
                if len(unique_sources) == 1:
                    source_note = self._get_data_source_note(unique_sources[0], f"{player1} vs {player2}")
                else:
                    source_note = f"📊 **Data Sources**: {', '.join(unique_sources)} - Statistics for {player1} vs {player2}"
            else:
                source_note = f"📊 **Data Sources**: Multiple sources - Statistics for {player1} vs {player2}"
            
            # Combine source note with comparison
            full_response = f"{source_note}\n\n{response.text}"
            return full_response
            
        except Exception as e:
            return f"Error comparing players: {e}"
    
    async def get_cricket_insights(self, query: str) -> str:
        """Get cricket insights based on user query"""
        try:
            prompt = f"""
            As a cricket statistics expert, provide insights on: {query}
            
            Use your knowledge of cricket statistics, player performance, and historical data to provide:
            1. Relevant statistical analysis
            2. Historical context
            3. Current trends and patterns
            4. Expert recommendations or predictions
            
            Be specific and data-driven in your response.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error getting cricket insights: {e}"
    
    async def chat(self, user_input: str) -> str:
        """Main chat interface for the cricket agent"""
        start_time = time.time()
        
        try:
            # Enhanced system prompt with context
            system_prompt = f"""
            {self.config.system_prompt}
            
            You are currently helping with: {user_input}
            
            Available capabilities:
            - Get detailed player statistics (batting, bowling, fielding)
            - Compare players across different formats
            - Analyze player performance trends
            - Provide cricket insights and predictions
            - Answer questions about cricket statistics and records
            
            Always be helpful, accurate, and provide detailed responses with specific data when available.
            """
            
            response = self.model.generate_content(system_prompt)
            processing_time = time.time() - start_time
            
            # Log successful event
            self._log_event(
                event_type="chat",
                user_input=user_input,
                response=response.text,
                processing_time=processing_time,
                success=True
            )
            
            return response.text
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error in chat: {e}"
            
            # Log failed event
            self._log_event(
                event_type="chat",
                user_input=user_input,
                response=error_msg,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
            
            return error_msg

class CricketAgentManager:
    """Manager class for the Cricket Agent"""
    
    def __init__(self):
        self.agent = None
        self.is_running = False
    
    def initialize(self) -> bool:
        """Initialize the cricket agent"""
        try:
            self.agent = CricketAgent()
            self.is_running = True
            print("✅ Cricket Agent Manager initialized")
            return True
        except Exception as e:
            print(f"❌ Error initializing agent manager: {e}")
            return False
    
    async def start_agent(self):
        """Start the cricket agent"""
        if not self.agent:
            if not self.initialize():
                return False
        
        # Start MCP server
        if not self.agent.start_mcp_server():
            return False
        
        print("🚀 Cricket Agent is now running!")
        print("Available commands:")
        print("- analyze_player(player_name, format)")
        print("- compare_players(player1, player2, format)")
        print("- get_cricket_insights(query)")
        print("- chat(user_input)")
        
        return True
    
    async def stop_agent(self):
        """Stop the cricket agent"""
        if self.agent:
            self.agent.stop_mcp_server()
            self.is_running = False
            print("✅ Cricket Agent stopped")
    
    async def run_interactive_session(self):
        """Run an interactive session with the cricket agent"""
        if not await self.start_agent():
            return
        
        print("\n🏏 Welcome to the Cricket Statistics Agent!")
        print("Type 'quit' to exit, 'help' for available commands\n")
        
        while self.is_running:
            try:
                user_input = input("🏏 Cricket Agent > ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif not user_input:
                    continue
                
                # Process the input
                response = await self.agent.chat(user_input)
                print(f"\n🤖 Agent: {response}\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        await self.stop_agent()
    
    def _show_help(self):
        """Show help information"""
        help_text = """
🏏 Cricket Agent Help:

Available Commands:
- analyze_player <player_name> [format] - Analyze a player's statistics
- compare_players <player1> <player2> [format] - Compare two players
- get_cricket_insights <query> - Get cricket insights and analysis
- chat <message> - General conversation about cricket
- help - Show this help message
- quit/exit/q - Exit the agent

Examples:
- "analyze_player Virat Kohli Test"
- "compare_players Sachin Tendulkar Brian Lara ODI"
- "get_cricket_insights Who has the highest Test average?"
- "chat Tell me about the best all-rounders in cricket"

Formats: Test, ODI, T20I, all (default: all)
        """
        print(help_text)

# Main execution
async def main():
    """Main function to run the cricket agent"""
    manager = CricketAgentManager()
    
    try:
        await manager.run_interactive_session()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        if manager.is_running:
            await manager.stop_agent()

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        print("Please set your Google API key: export GOOGLE_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Run the agent
    asyncio.run(main())
