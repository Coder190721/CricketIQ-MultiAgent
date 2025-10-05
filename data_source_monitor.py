#!/usr/bin/env python3
"""
Data Source Monitor for Cricket Agent
Track ESPN Cricinfo vs Mock Data usage
"""

import json
import sys
from typing import Dict, List, Any
import argparse
from cricket_mcp_server import scraper

class DataSourceMonitor:
    """Monitor data source usage for cricket agent"""
    
    def __init__(self):
        self.scraper = scraper
    
    def get_data_source_stats(self) -> Dict[str, Any]:
        """Get current data source statistics"""
        return self.scraper.get_data_source_stats()
    
    def show_data_source_status(self):
        """Show current data source status"""
        stats = self.get_data_source_stats()
        
        if "message" in stats:
            print("📊 Data Source Status: No requests made yet")
            return
        
        print("📊 ESPN Cricinfo Data Source Status")
        print("=" * 50)
        print(f"Total Requests: {stats['total_requests']}")
        print(f"ESPN Successful: {stats['espn_successful']} ({stats['espn_success_rate']}%)")
        print(f"ESPN Failed: {stats['espn_failed']}")
        print(f"Mock Data Used: {stats['mock_data_used']} ({stats['mock_data_rate']}%)")
        print(f"Data Source Health: {stats['data_source_health']}")
        
        # Health indicator
        health = stats['data_source_health']
        if health == "Good":
            print("🟢 ESPN Cricinfo is working well!")
        elif health == "Fair":
            print("🟡 ESPN Cricinfo has some issues, but working")
        else:
            print("🔴 ESPN Cricinfo is having problems, using mock data")
    
    def test_espn_connection(self, player_name: str = "Virat Kohli"):
        """Test ESPN connection with a specific player"""
        print(f"🧪 Testing ESPN connection with: {player_name}")
        print("-" * 50)
        
        # Reset stats for clean test
        self.scraper.data_source_stats = {
            'espn_successful': 0,
            'espn_failed': 0,
            'mock_data_used': 0,
            'total_requests': 0
        }
        
        # Test search
        result = self.scraper.search_player(player_name)
        
        if result:
            print(f"✅ Search Result:")
            print(f"   Name: {result.get('name', 'Unknown')}")
            print(f"   URL: {result.get('url', 'Unknown')}")
            print(f"   Data Source: {result.get('data_source', 'Unknown')}")
            
            if result.get('data_source') == 'mock_data':
                print("⚠️  Using mock data - ESPN connection failed")
            else:
                print("✅ Using real ESPN data")
        else:
            print("❌ Search failed completely")
        
        # Show updated stats
        print("\n📊 Updated Statistics:")
        self.show_data_source_status()
    
    def monitor_live_requests(self):
        """Monitor data source in real-time"""
        print("🔴 Live Data Source Monitor (Press Ctrl+C to stop)")
        print("=" * 60)
        
        initial_stats = self.get_data_source_stats()
        last_total = initial_stats.get('total_requests', 0)
        
        try:
            import time
            while True:
                time.sleep(2)  # Check every 2 seconds
                
                current_stats = self.get_data_source_stats()
                current_total = current_stats.get('total_requests', 0)
                
                if current_total > last_total:
                    new_requests = current_total - last_total
                    print(f"📈 {new_requests} new request(s) detected!")
                    
                    # Show latest request details
                    if current_stats.get('total_requests', 0) > 0:
                        espn_success = current_stats.get('espn_successful', 0)
                        mock_used = current_stats.get('mock_data_used', 0)
                        success_rate = current_stats.get('espn_success_rate', 0)
                        
                        print(f"   ESPN Success Rate: {success_rate}%")
                        print(f"   Recent ESPN Success: {espn_success}")
                        print(f"   Recent Mock Data: {mock_used}")
                        
                        if success_rate < 50:
                            print("   ⚠️  Low ESPN success rate - check connection")
                        else:
                            print("   ✅ ESPN working well")
                    
                    last_total = current_total
                    print()
                
        except KeyboardInterrupt:
            print("\n🛑 Live monitoring stopped.")
    
    def show_espn_health_check(self):
        """Perform comprehensive ESPN health check"""
        print("🏥 ESPN Cricinfo Health Check")
        print("=" * 40)
        
        # Test multiple players
        test_players = ["Virat Kohli", "Sachin Tendulkar", "Ricky Ponting"]
        
        print("Testing ESPN connection with multiple players...")
        
        for player in test_players:
            print(f"\n🔍 Testing: {player}")
            result = self.scraper.search_player(player)
            
            if result and result.get('data_source') != 'mock_data':
                print(f"  ✅ ESPN connection successful")
            else:
                print(f"  ❌ ESPN connection failed - using mock data")
        
        # Final statistics
        print(f"\n📊 Final Health Check Results:")
        self.show_data_source_status()
        
        # Recommendations
        stats = self.get_data_source_stats()
        if stats.get('espn_success_rate', 0) < 30:
            print("\n💡 Recommendations:")
            print("   - Check internet connection")
            print("   - ESPN Cricinfo might be blocking requests")
            print("   - Consider using VPN or different network")
            print("   - Check if ESPN Cricinfo is accessible in your region")
        elif stats.get('espn_success_rate', 0) < 70:
            print("\n💡 Recommendations:")
            print("   - ESPN connection is intermittent")
            print("   - Some requests are working, others failing")
            print("   - Consider retrying failed requests")
        else:
            print("\n✅ ESPN Cricinfo connection is healthy!")

def main():
    parser = argparse.ArgumentParser(description="Cricket Agent Data Source Monitor")
    parser.add_argument("--status", "-s", action="store_true", help="Show data source status")
    parser.add_argument("--test", "-t", help="Test ESPN connection with specific player")
    parser.add_argument("--live", "-l", action="store_true", help="Live monitoring")
    parser.add_argument("--health-check", action="store_true", help="Comprehensive health check")
    
    args = parser.parse_args()
    
    monitor = DataSourceMonitor()
    
    if args.status:
        monitor.show_data_source_status()
    elif args.test:
        monitor.test_espn_connection(args.test)
    elif args.live:
        monitor.monitor_live_requests()
    elif args.health_check:
        monitor.show_espn_health_check()
    else:
        # Default: show status
        monitor.show_data_source_status()

if __name__ == "__main__":
    main()
