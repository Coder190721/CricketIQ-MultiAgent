#!/usr/bin/env python3
"""
Event Monitor for Cricket Agent ADK
View and analyze user interactions and events
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Any
import argparse

class EventMonitor:
    """Monitor and analyze cricket agent events"""
    
    def __init__(self, events_file: str = "cricket_events.json"):
        self.events_file = events_file
        self.events = self._load_events()
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load events from JSON file"""
        try:
            with open(self.events_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Events file {self.events_file} not found. No events to display.")
            return []
        except Exception as e:
            print(f"Error loading events: {e}")
            return []
    
    def show_recent_events(self, limit: int = 10):
        """Show recent events"""
        if not self.events:
            print("No events found.")
            return
        
        recent_events = self.events[-limit:]
        print(f"\n📊 Recent Events (Last {len(recent_events)}):")
        print("=" * 60)
        
        for event in recent_events:
            timestamp = event.get('timestamp', 'Unknown')
            event_type = event.get('event_type', 'Unknown')
            success = "✅" if event.get('success', False) else "❌"
            processing_time = event.get('processing_time', 0)
            user_input = event.get('user_input', '')[:50] + "..." if len(event.get('user_input', '')) > 50 else event.get('user_input', '')
            
            # Get data source from metadata
            metadata = event.get('metadata', {})
            data_source = metadata.get('data_source', 'unknown')
            data_source_icon = "🌐" if data_source.startswith('espn') else "📊" if data_source == 'mock_data' else "❓"
            
            print(f"{success} {data_source_icon} [{timestamp}] {event_type.upper()}")
            print(f"   Input: {user_input}")
            print(f"   Data Source: {data_source}")
            print(f"   Processing Time: {processing_time:.2f}s")
            if not event.get('success', True):
                print(f"   Error: {event.get('error_message', 'Unknown error')}")
            print()
    
    def show_event_stats(self):
        """Show event statistics"""
        if not self.events:
            print("No events found.")
            return
        
        total_events = len(self.events)
        successful_events = len([e for e in self.events if e.get('success', False)])
        failed_events = total_events - successful_events
        success_rate = (successful_events / total_events) * 100 if total_events > 0 else 0
        
        # Event types
        event_types = {}
        for event in self.events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Average processing time
        processing_times = [e.get('processing_time', 0) for e in self.events if e.get('processing_time')]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        print("\n📈 Event Statistics:")
        print("=" * 40)
        print(f"Total Events: {total_events}")
        print(f"Successful: {successful_events} ({success_rate:.1f}%)")
        print(f"Failed: {failed_events}")
        print(f"Average Processing Time: {avg_processing_time:.2f}s")
        print(f"\nEvent Types:")
        for event_type, count in event_types.items():
            print(f"  {event_type}: {count}")
    
    def show_events_by_type(self, event_type: str):
        """Show events filtered by type"""
        filtered_events = [e for e in self.events if e.get('event_type') == event_type]
        
        if not filtered_events:
            print(f"No events of type '{event_type}' found.")
            return
        
        print(f"\n🔍 Events of type '{event_type}' ({len(filtered_events)} found):")
        print("=" * 60)
        
        for event in filtered_events:
            timestamp = event.get('timestamp', 'Unknown')
            success = "✅" if event.get('success', False) else "❌"
            user_input = event.get('user_input', '')
            processing_time = event.get('processing_time', 0)
            
            print(f"{success} [{timestamp}]")
            print(f"   Input: {user_input}")
            print(f"   Processing Time: {processing_time:.2f}s")
            if not event.get('success', True):
                print(f"   Error: {event.get('error_message', 'Unknown error')}")
            print()
    
    def show_failed_events(self):
        """Show only failed events"""
        failed_events = [e for e in self.events if not e.get('success', True)]
        
        if not failed_events:
            print("No failed events found. Great! 🎉")
            return
        
        print(f"\n❌ Failed Events ({len(failed_events)} found):")
        print("=" * 60)
        
        for event in failed_events:
            timestamp = event.get('timestamp', 'Unknown')
            event_type = event.get('event_type', 'Unknown')
            user_input = event.get('user_input', '')
            error_message = event.get('error_message', 'Unknown error')
            
            print(f"[{timestamp}] {event_type.upper()}")
            print(f"   Input: {user_input}")
            print(f"   Error: {error_message}")
            print()
    
    def export_events(self, output_file: str):
        """Export events to a file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.events, f, indent=2)
            print(f"Events exported to {output_file}")
        except Exception as e:
            print(f"Error exporting events: {e}")
    
    def live_monitor(self):
        """Monitor events in real-time"""
        print("🔴 Live Event Monitor (Press Ctrl+C to stop)")
        print("=" * 50)
        
        last_count = len(self.events)
        
        try:
            while True:
                import time
                time.sleep(2)  # Check every 2 seconds
                
                # Reload events
                self.events = self._load_events()
                current_count = len(self.events)
                
                if current_count > last_count:
                    new_events = self.events[last_count:]
                    for event in new_events:
                        timestamp = event.get('timestamp', 'Unknown')
                        event_type = event.get('event_type', 'Unknown')
                        success = "✅" if event.get('success', False) else "❌"
                        user_input = event.get('user_input', '')[:50] + "..." if len(event.get('user_input', '')) > 50 else event.get('user_input', '')
                        
                        print(f"{success} [{timestamp}] {event_type.upper()}: {user_input}")
                    
                    last_count = current_count
                
        except KeyboardInterrupt:
            print("\n🛑 Live monitoring stopped.")

def main():
    parser = argparse.ArgumentParser(description="Cricket Agent Event Monitor")
    parser.add_argument("--file", "-f", default="cricket_events.json", help="Events file path")
    parser.add_argument("--recent", "-r", type=int, default=10, help="Show recent N events")
    parser.add_argument("--type", "-t", help="Filter by event type")
    parser.add_argument("--failed", action="store_true", help="Show only failed events")
    parser.add_argument("--stats", "-s", action="store_true", help="Show statistics")
    parser.add_argument("--export", "-e", help="Export events to file")
    parser.add_argument("--live", "-l", action="store_true", help="Live monitoring")
    
    args = parser.parse_args()
    
    monitor = EventMonitor(args.file)
    
    if args.live:
        monitor.live_monitor()
    elif args.stats:
        monitor.show_event_stats()
    elif args.failed:
        monitor.show_failed_events()
    elif args.type:
        monitor.show_events_by_type(args.type)
    elif args.export:
        monitor.export_events(args.export)
    else:
        monitor.show_recent_events(args.recent)

if __name__ == "__main__":
    main()
