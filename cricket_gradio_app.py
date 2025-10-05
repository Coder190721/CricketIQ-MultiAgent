#!/usr/bin/env python3
"""
Cricket Statistics Agent - Gradio Web Interface
Rebuilt for reliability and simplicity
"""

import gradio as gr
import asyncio
import os
import time
from dotenv import load_dotenv
from cricket_agent import CricketAgent, AgentConfig

# Load environment variables
load_dotenv()

class CricketApp:
    """Main Cricket Statistics App"""
    
    def __init__(self):
        self.agent = None
        self.console_messages = []
        self.setup_agent()
    
    def setup_agent(self):
        """Initialize the cricket agent"""
        try:
            print("🔧 Initializing Cricket Agent...")
            config = AgentConfig()
            self.agent = CricketAgent(config)
            print("✅ Cricket Agent ready")
        except Exception as e:
            print(f"❌ Agent initialization failed: {e}")
            self.agent = None
    
    def log_message(self, message):
        """Log a message to console"""
        timestamp = time.strftime("%H:%M:%S")
        self.console_messages.append(f"[{timestamp}] {message}")
        # Keep only last 50 messages
        if len(self.console_messages) > 50:
            self.console_messages = self.console_messages[-50:]
    
    def analyze_player(self, player_name, format_type):
        """Analyze a cricket player"""
        if not player_name.strip():
            return "❌ Please enter a player name."
        
        if not self.agent:
            return "❌ Agent not initialized. Please check your configuration."
        
        try:
            self.log_message(f"🔍 Analyzing {player_name} ({format_type})")
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.agent.analyze_player(player_name, format_type))
            loop.close()
            
            self.log_message("✅ Analysis completed")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error analyzing player: {e}"
            self.log_message(error_msg)
            return error_msg
    
    def compare_players(self, player1, player2, format_type):
        """Compare two cricket players"""
        if not player1.strip() or not player2.strip():
            return "❌ Please enter both player names."
        
        if not self.agent:
            return "❌ Agent not initialized. Please check your configuration."
        
        try:
            self.log_message(f"⚖️ Comparing {player1} vs {player2} ({format_type})")
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.agent.compare_players(player1, player2, format_type))
            loop.close()
            
            self.log_message("✅ Comparison completed")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error comparing players: {e}"
            self.log_message(error_msg)
            return error_msg
    
    def get_insights(self, query):
        """Get cricket insights"""
        if not query.strip():
            return "❌ Please enter a query."
        
        if not self.agent:
            return "❌ Agent not initialized. Please check your configuration."
        
        try:
            self.log_message(f"💡 Getting insights: {query}")
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.agent.get_cricket_insights(query))
            loop.close()
            
            self.log_message("✅ Insights generated")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error getting insights: {e}"
            self.log_message(error_msg)
            return error_msg
    
    def chat_with_agent(self, message, history):
        """Chat with the cricket agent"""
        if not message.strip():
            return history, ""
        
        if not self.agent:
            return history + [("User", message), ("Agent", "❌ Agent not initialized.")], ""
        
        try:
            self.log_message(f"💬 Chat: {message}")
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.agent.chat(message))
            loop.close()
            
            self.log_message("✅ Chat response generated")
            return history + [("User", message), ("Agent", response)], ""
            
        except Exception as e:
            error_msg = f"❌ Error in chat: {e}"
            self.log_message(error_msg)
            return history + [("User", message), ("Agent", error_msg)], ""
    
    def get_console_messages(self):
        """Get console messages"""
        if not self.console_messages:
            return "No console messages yet. Use the agent to see activity."
        return "\n".join(self.console_messages[-20:])  # Last 20 messages
    
    def clear_console(self):
        """Clear console messages"""
        self.console_messages.clear()
        return "Console cleared."
    
    def get_espn_status(self):
        """Get ESPN connection status"""
        try:
            if not self.agent:
                return "❌ Agent not initialized"
            
            # Get data source stats
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
    app = CricketApp()
    
    # Custom CSS
    css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: auto !important;
    }
    .header {
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
        <div class="header">
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
                            value="Virat Kohli"
                        )
                        format_type = gr.Dropdown(
                            choices=["Test", "ODI", "T20I", "all"],
                            value="Test",
                            label="Format"
                        )
                        analyze_btn = gr.Button("📊 Analyze Player", variant="primary")
                    
                    with gr.Column():
                        analysis_output = gr.Textbox(
                            label="Analysis Result",
                            lines=15,
                            max_lines=20,
                            show_copy_button=True
                        )
                
                analyze_btn.click(
                    fn=app.analyze_player,
                    inputs=[player_name, format_type],
                    outputs=analysis_output
                )
            
            # Cricket Insights Tab
            with gr.Tab("💡 Cricket Insights"):
                gr.Markdown("### Get Cricket Insights and Analysis")
                
                with gr.Row():
                    with gr.Column():
                        insights_query = gr.Textbox(
                            label="Your Query",
                            placeholder="e.g., Who are the best all-rounders in T20 cricket?",
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
                    fn=app.get_insights,
                    inputs=insights_query,
                    outputs=insights_output
                )
            
            # Chat Interface Tab
            with gr.Tab("💬 Chat with Agent"):
                gr.Markdown("### Chat with the Cricket Statistics Agent")
                
                chatbot = gr.Chatbot(
                    label="Cricket Agent Chat",
                    height=400,
                    show_copy_button=True,
                    type="messages"
                )
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="Your Message",
                        placeholder="Ask me anything about cricket statistics...",
                        scale=4
                    )
                    chat_btn = gr.Button("Send", variant="primary", scale=1)
                
                chat_btn.click(
                    fn=app.chat_with_agent,
                    inputs=[chat_input, chatbot],
                    outputs=[chatbot, chat_input]
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
    """Main function"""
    print("🚀 Cricket Statistics Agent - Gradio App")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        print("Please set your Google API key: export GOOGLE_API_KEY='your-api-key'")
        return
    
    print("✅ Environment ready")
    
    try:
        # Create interface
        print("🔧 Creating interface...")
        interface = create_interface()
        print("✅ Interface created")
        
        print("\n🌐 Starting server...")
        print("URL: http://127.0.0.1:7891")
        print("Press Ctrl+C to stop")
        
        # Launch with minimal configuration
        interface.launch(
            server_name="127.0.0.1",
            server_port=7891,  # Changed to avoid port conflict
            share=False,
            inbrowser=True,
            quiet=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
