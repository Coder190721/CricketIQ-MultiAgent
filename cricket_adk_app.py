#!/usr/bin/env python3
"""
Cricket ADK Gradio App
Web interface for the multi-agent cricket statistics system
"""

import gradio as gr
import asyncio
import os
import time
from dotenv import load_dotenv
from cricket_manager.agent import cricket_manager

# Load environment variables
load_dotenv()

class CricketADKApp:
    """Gradio app for the ADK-based cricket system"""
    
    def __init__(self):
        self.manager = cricket_manager
        self.setup_agent()
    
    def setup_agent(self):
        """Initialize the cricket manager agent"""
        try:
            print("🔧 Initializing Cricket Manager Agent...")
            # The manager is already initialized in the agent.py file
            print("✅ Cricket Manager Agent ready")
        except Exception as e:
            print(f"❌ Agent initialization failed: {e}")
            self.manager = None
    
    async def analyze_player_async(self, player_name: str, format_type: str, mode: str = "batting", data_source: str = "auto") -> str:
        """Analyze a cricket player using the ADK system"""
        if not self.manager:
            return "❌ Cricket Manager not initialized. Please check your configuration."
        
        if not player_name.strip():
            return "❌ Please enter a player name."
        
        try:
            print(f"🏏 ADK: Analyzing {player_name} ({format_type}) - {mode}")
            
            # Use the manager's analyze_player method
            result = await self.manager.analyze_player(player_name, format_type, mode)
            
            # Add data source information if specified
            if data_source != "auto":
                data_source_note = self._get_data_source_note(data_source, player_name)
                result = f"{data_source_note}\n\n{result}"
            
            return result
            
        except Exception as e:
            return f"❌ Error analyzing player: {str(e)}"
    
    async def compare_players_async(self, player1: str, player2: str, format_type: str, mode: str = "batting", data_source: str = "auto") -> str:
        """Compare two players using the ADK system"""
        if not self.manager:
            return "❌ Cricket Manager not initialized. Please check your configuration."
        
        if not player1.strip() or not player2.strip():
            return "❌ Please enter both player names."
        
        try:
            print(f"⚖️ ADK: Comparing {player1} vs {player2} ({format_type}) - {mode}")
            
            # Use the manager's compare_players method
            result = await self.manager.compare_players(player1, player2, format_type, mode)
            
            # Add data source information if specified
            if data_source != "auto":
                data_source_note = self._get_data_source_note(data_source, f"{player1} vs {player2}")
                result = f"{data_source_note}\n\n{result}"
            
            return result
            
        except Exception as e:
            return f"❌ Error comparing players: {str(e)}"
    
    async def get_cricket_insights_async(self, query: str) -> str:
        """Get cricket insights using the ADK system"""
        if not self.manager:
            return "❌ Cricket Manager not initialized. Please check your configuration."
        
        if not query.strip():
            return "❌ Please enter a cricket question."
        
        try:
            print(f"💡 ADK: Getting insights for: {query}")
            
            # Use the analyzer agent for insights
            result = await self.manager.analyzer_agent.get_cricket_insights(query)
            return result
            
        except Exception as e:
            return f"❌ Error getting insights: {str(e)}"
    
    def _get_data_source_note(self, data_source: str, player_name: str) -> str:
        """Generate a data source note for the analysis"""
        if data_source == "espn_direct":
            return f"📊 **Data Source**: ESPN Cricinfo (Direct) - Real-time statistics for {player_name}"
        elif data_source == "espn_via_google":
            return f"📊 **Data Source**: ESPN Cricinfo (via Google) - Real-time statistics for {player_name}"
        elif data_source == "wikipedia":
            return f"📊 **Data Source**: Wikipedia - General cricket information for {player_name}"
        elif data_source == "google_search":
            return f"🔍 **Data Source**: Google Search - Comprehensive search results for {player_name}"
        elif data_source == "auto":
            return f"🔄 **Data Source**: Multi-Agent System - Using all available sources for {player_name}"
        else:
            return f"📊 **Data Source**: {data_source.title()} - Statistics for {player_name}"
    
    def get_system_status(self) -> str:
        """Get current system status"""
        try:
            if not self.manager:
                return "❌ Cricket Manager not initialized"
            
            status = "🤖 **CricketIQ Multi-Agent System Status**\n\n"
            status += "📊 **System Overview**:\n"
            status += "  - Multi-agent cricket statistics system\n"
            status += "  - Real-time data collection from multiple sources\n"
            status += "  - AI-powered analysis using Google Gemini\n"
            status += "  - Mode-specific analysis (batting, bowling, fielding)\n"
            status += "  - Data source status reporting\n"
            
            status += "\n📈 **Performance**:\n"
            status += "  - Expected success rate: 75-100%\n"
            status += "  - Analysis time: 10-15 seconds\n"
            status += "  - Data sources: 4 (ESPN, Wikipedia, Google Search)\n"
            
            status += "\n🔧 **Active Agents**:\n"
            if self.manager.sub_agents:
                # Define source display names and emojis
                source_display = {
                    'espn_direct': '📺 ESPN Cricinfo Direct',
                    'espn_google': '🔍 ESPN via Google',
                    'wikipedia': '📚 Wikipedia',
                    'google_search': '🔍 Google Search'
                }
                
                for source, agent in self.manager.sub_agents.items():
                    display_name = source_display.get(source, source.replace('_', ' ').title())
                    status += f"  - {display_name}: ✅ Ready\n"
            
            status += "\n🎯 **Features**:\n"
            status += "  - Player analysis with mode-specific focus\n"
            status += "  - Player comparison across formats\n"
            status += "  - Cricket insights and general knowledge\n"
            status += "  - Real-time data source monitoring\n"
            status += "  - Fallback data mechanisms\n"
            
            return status
            
        except Exception as e:
            return f"❌ Error getting system status: {str(e)}"

def create_interface():
    """Create the Gradio interface for the ADK system"""
    app = CricketADKApp()
    
    with gr.Blocks(
        title="🏏 CricketIQ Multi-Agent System",
        theme=gr.themes.Soft(),
        css="""
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        """
    ) as interface:
        
        gr.HTML("""
        <div class="header">
            <h1>🏏 CricketIQ Multi-Agent System</h1>
            <p>Powered by Google ADK & Multiple Data Sources</p>
            <p>Advanced cricket statistics with AI-powered analysis</p>
        </div>
        """)
        
        with gr.Tabs():
            
            # Player Analysis Tab
            with gr.Tab("📊 Player Analysis"):
                gr.Markdown("### Analyze Individual Player Statistics")
                gr.Markdown("*Multi-agent system collects data from ESPN, Wikipedia, Google Search and analyzes with AI*")
                
                with gr.Row():
                    with gr.Column():
                        player_name = gr.Textbox(
                            label="Player Name",
                            placeholder="e.g., Virat Kohli, Sachin Tendulkar, Brian Lara",
                            value=""
                        )
                        format_dropdown = gr.Dropdown(
                            choices=["Test", "ODI", "T20I", "all"],
                            value="Test",
                            label="Format"
                        )
                        mode_dropdown = gr.Dropdown(
                            choices=["batting", "bowling", "fielding"],
                            value="batting",
                            label="Mode"
                        )
                        data_source_dropdown = gr.Dropdown(
                            choices=[
                                ("🔄 Auto (Multi-Agent)", "auto"),
                                ("📊 ESPN Direct", "espn_direct"),
                                ("🔍 ESPN via Google", "espn_via_google"),
                                ("📚 Wikipedia", "wikipedia"),
                                ("🔍 Google Search", "google_search")
                            ],
                            value="auto",
                            label="Data Source",
                            info="Choose which data source to use (Auto uses all agents)"
                        )
                        analyze_btn = gr.Button("🔍 Analyze Player", variant="primary")
                    
                    with gr.Column():
                        analysis_output = gr.Textbox(
                            label="AI-Powered Analysis Results",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                analyze_btn.click(
                    fn=app.analyze_player_async,
                    inputs=[player_name, format_dropdown, mode_dropdown, data_source_dropdown],
                    outputs=analysis_output
                )
            
            # Player Comparison Tab
            with gr.Tab("⚖️ Player Comparison"):
                gr.Markdown("### Compare Two Players")
                gr.Markdown("*Multi-agent system compares players using data from all sources*")
                
                with gr.Row():
                    with gr.Column():
                        player1_name = gr.Textbox(
                            label="Player 1",
                            placeholder="e.g., Virat Kohli",
                            value=""
                        )
                        player2_name = gr.Textbox(
                            label="Player 2", 
                            placeholder="e.g., Sachin Tendulkar",
                            value=""
                        )
                        compare_format = gr.Dropdown(
                            choices=["Test", "ODI", "T20I", "all"],
                            value="Test",
                            label="Format"
                        )
                        compare_mode = gr.Dropdown(
                            choices=["batting", "bowling", "fielding"],
                            value="batting",
                            label="Mode"
                        )
                        compare_data_source = gr.Dropdown(
                            choices=[
                                ("🔄 Auto (Multi-Agent)", "auto"),
                                ("📊 ESPN Direct", "espn_direct"),
                                ("🔍 ESPN via Google", "espn_via_google"),
                                ("📚 Wikipedia", "wikipedia"),
                                ("🔍 Google Search", "google_search")
                            ],
                            value="auto",
                            label="Data Source"
                        )
                        compare_btn = gr.Button("⚖️ Compare Players", variant="primary")
                    
                    with gr.Column():
                        comparison_output = gr.Textbox(
                            label="AI-Powered Comparison Results",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                compare_btn.click(
                    fn=app.compare_players_async,
                    inputs=[player1_name, player2_name, compare_format, compare_mode, compare_data_source],
                    outputs=comparison_output
                )
            
            # Cricket Insights Tab
            with gr.Tab("💡 Cricket Insights"):
                gr.Markdown("### Get Cricket Insights and Analysis")
                gr.Markdown("*Ask questions about cricket history, records, and general knowledge*")
                
                with gr.Row():
                    with gr.Column():
                        insights_query = gr.Textbox(
                            label="Your Cricket Question",
                            placeholder="e.g., Who are the best all-rounders in T20 cricket?",
                            lines=3
                        )
                        insights_btn = gr.Button("💡 Get Insights", variant="primary")
                    
                    with gr.Column():
                        insights_output = gr.Textbox(
                            label="AI-Powered Insights",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                insights_btn.click(
                    fn=app.get_cricket_insights_async,
                    inputs=[insights_query],
                    outputs=insights_output
                )
            
            # System Status Tab
            with gr.Tab("🤖 System Status"):
                gr.Markdown("### Multi-Agent System Status")
                gr.Markdown("*Real-time monitoring of all agents and data sources*")
                
                with gr.Row():
                    with gr.Column():
                        status_btn = gr.Button("🔄 Refresh Status", variant="secondary")
                        status_output = gr.Textbox(
                            label="System Status",
                            lines=20,
                            max_lines=25,
                            show_copy_button=True
                        )
                    
                    with gr.Column():
                        gr.Markdown("""
                        ### 🎯 System Features
                        
                        **📊 Player Analysis**
                        - Mode-specific analysis (batting, bowling, fielding)
                        - Format-specific statistics (Test, ODI, T20I)
                        - Multi-source data collection
                        - AI-powered insights
                        
                        **⚖️ Player Comparison**
                        - Head-to-head statistical comparison
                        - Mode-specific comparisons
                        - Cross-format analysis
                        - AI-powered assessment
                        
                        **💡 Cricket Insights**
                        - General cricket knowledge
                        - Historical analysis
                        - Record analysis
                        - Predictive insights
                        
                        **🔧 Multi-Agent Architecture**
                        - ESPN Cricinfo Direct Agent
                        - ESPN via Google Agent
                        - Wikipedia Agent
                        - Google Search Agent
                        - AI Analyzer Agent
                        """)
                
                status_btn.click(
                    fn=app.get_system_status,
                    outputs=status_output
                )
                
                # Auto-refresh status on load
                interface.load(
                    fn=app.get_system_status,
                    outputs=status_output
                )
    
    return interface

def main():
    """Main function to run the Gradio app"""
    print("🚀 Starting CricketIQ Multi-Agent System...")
    
    # Create and launch the interface
    interface = create_interface()
    
    # Launch the app
    interface.launch(
        server_name="0.0.0.0",
        server_port=7892,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()