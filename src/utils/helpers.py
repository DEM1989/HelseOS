import json
import os
from rich.console import Console
from rich.table import Table
import requests
from bs4 import BeautifulSoup
import re

console = Console()

def save_conversation(conversation, filename):
    """Save conversation history to a file"""
    with open(filename, 'w') as f:
        json.dump(conversation, f)

def load_conversation(filename):
    """Load conversation history from a file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def display_table(headers, rows):
    """Display data in a formatted table"""
    table = Table()
    
    for header in headers:
        table.add_column(header)
        
    for row in rows:
        table.add_row(*row)
        
    console.print(table)

def format_response(response):
    """Format API response for display"""
    if isinstance(response, str):
        return response
    elif isinstance(response, dict):
        return json.dumps(response, indent=2)
    return str(response)

def extract_text_from_url(url):
    """Fetch and return the text content from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException as e:
        console.print(f"An error occurred while fetching {url}: {e}")
        return None

def extract_relevant_info(objective, large_string, task, client):
    """Extract relevant information from a large string based on the objective and task."""
    if client is None:
        raise Exception("OpenAI client is not initialized.") 
    
    chunk_size = 5000  # Size of each chunk to process
    overlap = 500
    notes = ""
    
    for i in range(0, len(large_string), chunk_size - overlap):
        chunk = large_string[i:i + chunk_size]
        
        messages = [
            {"role": "system", "content": f"Objective: {objective}\nCurrent Task: {task}"},
            {"role": "user", "content": f"Analyze the following text and extract information relevant to our objective and current task. Text to analyze: {chunk}."}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Example modeld
            messages=messages
        )

        if hasattr(response.choices[0].message, 'content'):
            notes += response.choices[0].message.content.strip() + ". "
        else:
            raise AttributeError("The 'message' object does not have a 'content' attribute.")
    
    return notes if notes.strip() else "No relevant information found."
