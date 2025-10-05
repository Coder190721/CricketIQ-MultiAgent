#!/usr/bin/env python3
"""
Cricket Agent Gradio Demo
Interactive web interface for the Cricket Statistics Agent
"""

import gradio as gr
import asyncio
import json
import os
import time
from cricket_agent import CricketAgent, AgentConfig
from dotenv import load_dotenv
from console_logger import console_logger, start_console_capture, get_console_text, clear_console

# Load environment variables
load_dotenv()
print("Yes, loaded")
class CricketGradioDemo:
    """Gradio demo for the Cricket Agent"""
    
    def __init__(self):
        self.agent = None
        self.setup_agent()
        # Start console capture
        start_console_capture()
    
    def setup_agent(self):
        """Initialize the cricket agent"""
        try:
            config = AgentConfig()
            self.agent = CricketAgent(config)
            print("✅ Cricket Agent initialized for Gradio demo")
        except Exception as e:
            print(f"❌ Error initializing agent: {e}")
            self.agent = None
    
    async def analyze_player_async(self, player_name: str, format_type: str) -> str:
        """Async wrapper for player analysis"""
        if not self.agent:
            return "❌ Agent not initialized. Please check your configuration."
        
        try:
            result = await self.agent.analyze_player(player_name, format_type)
            return result
        except Exception as e:
            return f"❌ Error analyzing player: {e}"
    
    async def compare_players_async(self, player1: str, player2: str, format_type: str) -> str:
        """Async wrapper for player comparison"""
        if not self.agent:
            return "❌ Agent not initialized. Please check your configuration."
        
        try:
            result = await self.agent.compare_players(player1, player2, format_type)
            return result
        except Exception as e:
            return f"❌ Error comparing players: {e}"
    
    async def get_insights_async(self, query: str) -> str:
        """Async wrapper for cricket insights"""
        if not self.agent:
            return "❌ Agent not initialized. Please check your configuration."
        
        try:
            result = await self.agent.get_cricket_insights(query)
            return result
        except Exception as e:
            return f"❌ Error getting insights: {e}"
    
    async def chat_async(self, message: str, history: list) -> tuple:
        """Async wrapper for chat functionality"""
        if not self.agent:
            return history + [("User", message), ("Agent", "❌ Agent not initialized. Please check your configuration.")]
        
        try:
            response = await self.agent.chat(message)
            return history + [("User", message), ("Agent", response)]
        except Exception as e:
            return history + [("User", message), ("Agent", f"❌ Error: {e}")]
    
    def analyze_player(self, player_name: str, format_type: str) -> str:
        """Analyze a cricket player"""
        if not player_name.strip():
            return "❌ Please enter a player name."
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.analyze_player_async(player_name, format_type))
            loop.close()
            return result
        except Exception as e:
            return f"❌ Error: {e}"
    
    def compare_players(self, player1: str, player2: str, format_type: str) -> str:
        """Compare two cricket players"""
        if not player1.strip() or not player2.strip():
            return "❌ Please enter both player names."
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.compare_players_async(player1, player2, format_type))
            loop.close()
            return result
        except Exception as e:
            return f"❌ Error: {e}"
    
    def get_insights(self, query: str) -> str:
        """Get cricket insights"""
        if not query.strip():
            return "❌ Please enter a query."
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_insights_async(query))
            loop.close()
            return result
        except Exception as e:
            return f"❌ Error: {e}"
    
    def chat(self, message: str, history: list) -> tuple:
        """Chat with the cricket agent"""
        if not message.strip():
            return history, ""
        
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.chat_async(message, history))
            loop.close()
            return result, ""
        except Exception as e:
            return history + [("User", message), ("Agent", f"❌ Error: {e}")], ""
    
    def get_console_messages(self, limit: int = 50) -> str:
        """Get console messages for display"""
        try:
            messages = get_console_text(limit)
            if not messages:
                return "No console messages yet. Start using the agent to see ESPN queries and data source information."
            return messages
        except Exception as e:
            return f"Error getting console messages: {e}"
    
    def clear_console_messages(self):
        """Clear console messages"""
        try:
            clear_console()
            return "Console messages cleared."
        except Exception as e:
            return f"Error clearing console: {e}"
    
    def get_espn_status(self) -> str:
        """Get ESPN connection status"""
        try:
            if not self.agent:
                return "❌ Agent not initialized"
            
            # Get data source stats from the scraper
            from cricket_mcp_server import scraper
            stats = scraper.get_data_source_stats()
            
            if "message" in stats:
                return "📊 No ESPN requests made yet"
            
            status = f"""📊 ESPN Cricinfo Status
Total Requests: {stats['total_requests']}
ESPN Successful: {stats['espn_successful']} ({stats['espn_success_rate']}%)
ESPN Failed: {stats['espn_failed']}
Mock Data Used: {stats['mock_data_used']} ({stats['mock_data_rate']}%)
Health: {stats['data_source_health']}"""
            
            if stats['data_source_health'] == 'Good':
                status += "\n🟢 ESPN Cricinfo is working well!"
            elif stats['data_source_health'] == 'Fair':
                status += "\n🟡 ESPN Cricinfo has some issues"
            else:
                status += "\n🔴 ESPN Cricinfo is having problems"
            
            return status
        except Exception as e:
            return f"Error getting ESPN status: {e}"

def create_interface():
    """Create the Gradio interface"""
    print("🔧 Creating CricketGradioDemo instance...")
    try:
        demo = CricketGradioDemo()
        print("✅ CricketGradioDemo created successfully")
    except Exception as e:
        print(f"❌ Error creating CricketGradioDemo: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Custom CSS for better styling
    css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: auto !important;
    }
    .cricket-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    """
    
    with gr.Blocks(css=css, title="🏏 Cricket Statistics Agent") as interface:
        
        # Header
        gr.HTML("""
        <div class="cricket-header">
            <h1>🏏 Cricket Statistics Agent</h1>
            <p>Powered by Google ADK & ESPN Cricinfo Data</p>
            <p>Get comprehensive cricket player statistics, comparisons, and insights</p>
        </div>
        """)
        
        with gr.Tabs():
            
            # Player Analysis Tab
            with gr.Tab("📊 Player Analysis"):
                gr.Markdown("### Analyze Individual Player Statistics")
                
                with gr.Row():
                    with gr.Column():
                        player_name = gr.Textbox(
                            label="Player Name",
                            placeholder="e.g., Virat Kohli, Sachin Tendulkar, Brian Lara",
                            value=""
                        )
                        format_dropdown = gr.Dropdown(
                            choices=["all", "Test", "ODI", "T20I"],
                            value="all",
                            label="Format"
                        )
                        analyze_btn = gr.Button("🔍 Analyze Player", variant="primary")
                    
                    with gr.Column():
                        analysis_output = gr.Textbox(
                            label="Analysis Results",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                analyze_btn.click(
                    fn=demo.analyze_player,
                    inputs=[player_name, format_dropdown],
                    outputs=analysis_output
                )
            
            # Player Comparison Tab
            with gr.Tab("⚖️ Player Comparison"):
                gr.Markdown("### Compare Two Players")
                
                with gr.Row():
                    with gr.Column():
                        player1_name = gr.Textbox(
                            label="Player 1",
                            placeholder="e.g., Sachin Tendulkar",
                            value=""
                        )
                        player2_name = gr.Textbox(
                            label="Player 2", 
                            placeholder="e.g., Brian Lara",
                            value=""
                        )
                        compare_format = gr.Dropdown(
                            choices=["all", "Test", "ODI", "T20I"],
                            value="all",
                            label="Format"
                        )
                        compare_btn = gr.Button("⚖️ Compare Players", variant="primary")
                    
                    with gr.Column():
                        comparison_output = gr.Textbox(
                            label="Comparison Results",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                compare_btn.click(
                    fn=demo.compare_players,
                    inputs=[player1_name, player2_name, compare_format],
                    outputs=comparison_output
                )
            
            # Cricket Insights Tab
            with gr.Tab("💡 Cricket Insights"):
                gr.Markdown("### Get Cricket Insights and Analysis")
                
                with gr.Row():
                    with gr.Column():
                        insights_query = gr.Textbox(
                            label="Your Query",
                            placeholder="e.g., Who has the highest Test average? Best all-rounders in cricket?",
                            lines=3
                        )
                        insights_btn = gr.Button("💡 Get Insights", variant="primary")
                    
                    with gr.Column():
                        insights_output = gr.Textbox(
                            label="Insights",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                insights_btn.click(
                    fn=demo.get_insights,
                    inputs=insights_query,
                    outputs=insights_output
                )
            
            # Chat Interface Tab
            with gr.Tab("💬 Chat with Agent"):
                gr.Markdown("### Chat with the Cricket Statistics Agent")
                
                chatbot = gr.Chatbot(
                    label="Cricket Agent Chat",
                    height=400,
                    show_copy_button=True
                )
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="Your Message",
                        placeholder="Ask me anything about cricket statistics...",
                        scale=4
                    )
                    chat_btn = gr.Button("Send", variant="primary", scale=1)
                
                chat_btn.click(
                    fn=demo.chat,
                    inputs=[chat_input, chatbot],
                    outputs=[chatbot, chat_input]
                )
                
                # Example queries
                gr.Markdown("""
                ### Example Queries:
                - "Tell me about Virat Kohli's ODI record"
                - "Compare Sachin Tendulkar and Brian Lara in Test cricket"
                - "Who are the best all-rounders in T20 cricket?"
                - "What are the highest individual scores in Test cricket?"
                """)
            
            # Console Messages Tab
            with gr.Tab("🖥️ Console & ESPN Status"):
                gr.Markdown("### Real-time Console Messages and ESPN Connection Status")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("#### 📺 Console Messages")
                        console_output = gr.Textbox(
                            label="Console Output",
                            lines=20,
                            max_lines=30,
                            show_copy_button=True,
                            interactive=False,
                            placeholder="Console messages will appear here when you use the agent..."
                        )
                        
                        with gr.Row():
                            refresh_console_btn = gr.Button("🔄 Refresh Console", variant="secondary")
                            clear_console_btn = gr.Button("🗑️ Clear Console", variant="secondary")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### 📊 ESPN Status")
                        espn_status = gr.Textbox(
                            label="ESPN Cricinfo Connection Status",
                            lines=10,
                            max_lines=15,
                            show_copy_button=True,
                            interactive=False
                        )
                        
                        refresh_espn_btn = gr.Button("🔄 Refresh ESPN Status", variant="secondary")
                        
                        gr.Markdown("""
                        #### 📋 Console Icons:
                        - 🔍 Searching ESPN Cricinfo
                        - 📡 Making HTTP request
                        - ✅ ESPN connection successful
                        - ❌ ESPN connection failed
                        - ⚠️ Using fallback mock data
                        - 🌐 Real ESPN data
                        - 📊 Mock data
                        """)
                
                # Auto-refresh functionality
                refresh_console_btn.click(
                    fn=demo.get_console_messages,
                    outputs=console_output
                )
                
                clear_console_btn.click(
                    fn=demo.clear_console_messages,
                    outputs=console_output
                )
                
                refresh_espn_btn.click(
                    fn=demo.get_espn_status,
                    outputs=espn_status
                )
                
                # Auto-refresh every 2 seconds
                interface.load(
                    fn=demo.get_console_messages,
                    outputs=console_output,
                    every=2
                )
                
                interface.load(
                    fn=demo.get_espn_status,
                    outputs=espn_status,
                    every=5
                )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 20px; color: #666;">
            <p>🏏 Cricket Statistics Agent | Powered by Google ADK & ESPN Cricinfo</p>
            <p>Data sourced from ESPN Cricinfo and Statsguru</p>
        </div>
        """)
    
    return interface

def main():
    """Main function to run the Gradio demo"""
    print("🚀 Starting main function...")
    
    # Check for required environment variables
    print("🔍 Checking environment variables...")
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        print("Please set your Google API key: export GOOGLE_API_KEY='your-api-key'")
        return
    print("✅ GOOGLE_API_KEY found")
    
    # Create and launch the interface
    print("🔧 Creating interface...")
    try:
        interface = create_interface()
        print("✅ Interface created successfully")
    except Exception as e:
        print(f"❌ Error creating interface: {e}")
        import traceback
        traceback.print_exc()
        return
    print("🚀 Starting Cricket Statistics Agent Demo...")
    print("📊 Features:")
    print("  - Player Statistics Analysis")
    print("  - Player Comparison")
    print("  - Cricket Insights")
    print("  - Interactive Chat")
    print("\n🌐 Opening web interface...")
    
    print("\n" + "="*60)
    print("🚀 CRICKET STATISTICS AGENT - GRADIO DEMO")
    print("="*60)
    print("📊 Features Available:")
    print("  • Player Statistics Analysis")
    print("  • Player Comparison")
    print("  • Cricket Insights")
    print("  • Interactive Chat")
    print("  • Console Messages & ESPN Status")
    print("\n🌐 Web Interface:")
    print("  URL: http://localhost:7890")
    print("  URL: http://127.0.0.1:7890")
    print("\n💡 Tips:")
    print("  • Open your browser and go to the URL above")
    print("  • Check the 'Console & ESPN Status' tab for real-time monitoring")
    print("  • Use Ctrl+C to stop the server")
    print("="*60)
    print("🖥️ Starting server...")
    
    print("🖥️ Launching Gradio interface...")
    try:
        interface.launch(
            server_name="127.0.0.1",  # Changed from 0.0.0.0 to 127.0.0.1
            server_port=7890,
            share=False,
            show_error=True,
            inbrowser=True,
            quiet=False,
            prevent_thread_lock=False
        )
    except Exception as e:
        print(f"❌ Error launching interface: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
