#!/usr/bin/env python3
"""
Cricket Statistics Agent Demo
Demonstrates the capabilities of the cricket agent
"""

import asyncio
import os
from cricket_agent import CricketAgent, AgentConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def demo_player_analysis():
    """Demo player analysis functionality"""
    print("📊 Player Analysis Demo")
    print("-" * 40)
    
    agent = CricketAgent()
    
    # Demo 1: Analyze Virat Kohli
    print("Analyzing Virat Kohli's ODI career...")
    analysis = await agent.analyze_player("Virat Kohli", "ODI")
    print(f"Result: {analysis[:300]}...")
    print()
    
    # Demo 2: Analyze Brian Lara
    print("Analyzing Brian Lara's Test career...")
    analysis = await agent.analyze_player("Brian Lara", "Test")
    print(f"Result: {analysis[:300]}...")
    print()

async def demo_player_comparison():
    """Demo player comparison functionality"""
    print("⚖️ Player Comparison Demo")
    print("-" * 40)
    
    agent = CricketAgent()
    
    # Demo: Compare Sachin and Brian Lara
    print("Comparing Sachin Tendulkar and Brian Lara in Test cricket...")
    comparison = await agent.compare_players("Sachin Tendulkar", "Brian Lara", "Test")
    print(f"Result: {comparison[:300]}...")
    print()

async def demo_cricket_insights():
    """Demo cricket insights functionality"""
    print("💡 Cricket Insights Demo")
    print("-" * 40)
    
    agent = CricketAgent()
    
    # Demo 1: Best all-rounders
    print("Getting insights about best all-rounders...")
    insights = await agent.get_cricket_insights("Who are the best all-rounders in cricket history?")
    print(f"Result: {insights[:300]}...")
    print()
    
    # Demo 2: Highest scores
    print("Getting insights about highest individual scores...")
    insights = await agent.get_cricket_insights("What are the highest individual scores in Test cricket?")
    print(f"Result: {insights[:300]}...")
    print()

async def demo_chat_interface():
    """Demo chat interface functionality"""
    print("💬 Chat Interface Demo")
    print("-" * 40)
    
    agent = CricketAgent()
    
    # Demo chat queries
    queries = [
        "Tell me about the greatest bowling performances in cricket",
        "Who has the best strike rate in T20 cricket?",
        "Compare the batting styles of Sachin Tendulkar and Brian Lara"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        response = await agent.chat(query)
        print(f"Response: {response[:200]}...")
        print()

def demo_mcp_server():
    """Demo MCP server functionality"""
    print("🔧 MCP Server Demo")
    print("-" * 40)
    
    try:
        from cricket_mcp_server import CricketDataScraper
        
        scraper = CricketDataScraper()
        
        # Demo player search
        print("Searching for players...")
        players = ["Virat Kohli", "Sachin Tendulkar", "Brian Lara"]
        
        for player in players:
            print(f"Searching for {player}...")
            result = scraper.search_player(player)
            if result:
                print(f"  ✅ Found: {result['name']}")
                print(f"  URL: {result['url']}")
            else:
                print(f"  ❌ Not found: {player}")
            print()
        
    except Exception as e:
        print(f"❌ MCP Server demo failed: {e}")

async def main():
    """Main demo function"""
    print("🏏 Cricket Statistics Agent Demo")
    print("=" * 50)
    
    # Check API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        print("Please set your Google API key: export GOOGLE_API_KEY='your-api-key'")
        return
    
    try:
        # Run demos
        await demo_player_analysis()
        await demo_player_comparison()
        await demo_cricket_insights()
        await demo_chat_interface()
        demo_mcp_server()
        
        print("🎉 Demo completed successfully!")
        print("\n📋 Available Features:")
        print("✅ Player Statistics Analysis")
        print("✅ Player Comparison")
        print("✅ Cricket Insights")
        print("✅ Interactive Chat")
        print("✅ MCP Server Integration")
        print("✅ Web Interface (Gradio)")
        print("✅ Command Line Interface")
        
        print("\n🚀 To run the full agent:")
        print("  Web Interface: python cricket_gradio_demo.py")
        print("  Command Line:  python cricket_agent.py")
        print("  MCP Server:    python cricket_mcp_server.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
