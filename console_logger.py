#!/usr/bin/env python3
"""
Console Logger for Cricket Agent
Captures console messages for display in Gradio UI
"""

import sys
import io
from datetime import datetime
from typing import List, Dict, Any
import threading
import queue

class ConsoleLogger:
    """Logger that captures console output for UI display"""
    
    def __init__(self, max_messages: int = 100):
        self.max_messages = max_messages
        self.messages = []
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # Store original stdout and stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Create custom stdout/stderr
        self.stdout_capture = self._create_capture_stream('STDOUT')
        self.stderr_capture = self._create_capture_stream('STDERR')
    
    def _create_capture_stream(self, stream_type: str):
        """Create a custom stream that captures output"""
        class CaptureStream:
            def __init__(self, logger, stream_type):
                self.logger = logger
                self.stream_type = stream_type
                self.original_stream = getattr(sys, stream_type.lower())
            
            def write(self, text):
                if text.strip():  # Only capture non-empty lines
                    self.logger._add_message(text.strip(), self.stream_type)
                return len(text)
            
            def flush(self):
                pass
            
            def __getattr__(self, name):
                return getattr(self.original_stream, name)
        
        return CaptureStream(self, stream_type)
    
    def start_capture(self):
        """Start capturing console output"""
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
    
    def stop_capture(self):
        """Stop capturing console output"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
    
    def _add_message(self, text: str, stream_type: str):
        """Add a message to the log"""
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = {
                'timestamp': timestamp,
                'text': text,
                'stream_type': stream_type,
                'formatted': f"[{timestamp}] {text}"
            }
            
            self.messages.append(message)
            self.message_queue.put(message)
            
            # Keep only the last max_messages
            if len(self.messages) > self.max_messages:
                self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get captured messages"""
        with self.lock:
            if limit:
                return self.messages[-limit:]
            return self.messages.copy()
    
    def get_new_messages(self) -> List[Dict[str, Any]]:
        """Get new messages since last call"""
        new_messages = []
        try:
            while True:
                message = self.message_queue.get_nowait()
                new_messages.append(message)
        except queue.Empty:
            pass
        return new_messages
    
    def clear_messages(self):
        """Clear all captured messages"""
        with self.lock:
            self.messages.clear()
            # Clear the queue
            try:
                while True:
                    self.message_queue.get_nowait()
            except queue.Empty:
                pass
    
    def get_formatted_messages(self, limit: int = None) -> str:
        """Get formatted messages as a single string"""
        messages = self.get_messages(limit)
        return "\n".join([msg['formatted'] for msg in messages])
    
    def get_espn_messages(self) -> List[Dict[str, Any]]:
        """Get messages related to ESPN queries"""
        with self.lock:
            espn_messages = []
            for msg in self.messages:
                text = msg['text'].lower()
                if any(keyword in text for keyword in ['espn', 'cricinfo', 'searching', '📡', '🔍', '✅', '❌', '⚠️']):
                    espn_messages.append(msg)
            return espn_messages
    
    def get_data_source_messages(self) -> List[Dict[str, Any]]:
        """Get messages related to data source"""
        with self.lock:
            data_messages = []
            for msg in self.messages:
                text = msg['text'].lower()
                if any(keyword in text for keyword in ['data source', 'mock data', 'espn', 'cricinfo', '🌐', '📊']):
                    data_messages.append(msg)
            return data_messages

# Global console logger instance
console_logger = ConsoleLogger()

def start_console_capture():
    """Start capturing console output"""
    console_logger.start_capture()

def stop_console_capture():
    """Stop capturing console output"""
    console_logger.stop_capture()

def get_console_messages(limit: int = None) -> List[Dict[str, Any]]:
    """Get console messages"""
    return console_logger.get_messages(limit)

def get_console_text(limit: int = None) -> str:
    """Get console messages as formatted text"""
    return console_logger.get_formatted_messages(limit)

def clear_console():
    """Clear console messages"""
    console_logger.clear_messages()
