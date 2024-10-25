import click
import openai
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint
from rich.markdown import Markdown
from rich.syntax import Syntax
import sys
import json
import re
import subprocess


# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    save_conversation, 
    load_conversation,
    display_table,
    format_response,
    extract_text_from_url,  # Ensure this function is defined in helpers.py
    extract_relevant_info
)
from config.settings import *
from core.assistant import Assistant
from utils.api_client import APIClient

# Load environment variables
load_dotenv()

# Initialize console and API client
console = Console()
api_client = APIClient()
assistant = Assistant(api_client)

@click.group()
def cli():
    """Admin Assist CLI - Your AI-powered assistant"""
    pass

@cli.command()
@click.option('--websearch/--no-websearch', default=False, help='Enable/disable web search')
@click.option('--model', default='gpt-3.5-turbo', help='Choose OpenAI model')
@click.option('--save', type=click.Path(), help='Save conversation to file')
def chat(websearch, model, save):
    """Start an interactive chat session"""
    console.print("[bold blue]Starting chat session...[/bold blue]")
    console.print("[bold green]Commands:[/bold green]")
    console.print("  !exit - Exit chat")
    console.print("  !save <filename> - Save conversation")
    console.print("  !clear - Clear conversation")
    console.print("  !web <on/off> - Toggle web search")
    console.print("  !code <language> - Execute code")
    
    conversation = []
    web_search_enabled = websearch
    
    while True:
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
        
        if user_input.startswith("!"):
            handle_command(user_input, conversation, web_search_enabled)
            continue
            
        try:
            # Process message with web search if enabled
            if web_search_enabled and needs_web_search(user_input):
                search_results = assistant.internet_search(user_input)
                response = assistant.process_with_search(user_input, search_results)
            else:
                response = assistant.chat(user_input, model)
                
            # Format and display response
            formatted_response = format_response(response)
            console.print(f"\n[bold green]Assistant:[/bold green] {formatted_response}")
            
            # Save conversation
            conversation.append({
                "role": "user",
                "content": user_input
            })
            conversation.append({
                "role": "assistant",
                "content": response
            })
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['text', 'json', 'markdown']), default='text')
def transcribe(file_path, format):
    """Transcribe an audio file and generate notes"""
    try:
        # Transcribe audio
        transcript = assistant.transcribe_audio(file_path)
        console.print(f"\n[bold green]Transcription complete[/bold green]")
        
        # Generate structured notes
        notes = assistant.generate_notes(transcript)
        
        # Format output
        if format == 'markdown':
            console.print(Markdown(notes))
        elif format == 'json':
            console.print_json(notes)
        else:
            console.print(notes)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@cli.command()
@click.argument('code_file', type=click.Path(exists=True))
@click.option('--language', help='Programming language')
def execute_code(code_file, language):
    """Execute or analyze code"""
    try:
        with open(code_file, 'r') as f:
            code = f.read()
            
        if not language:
            language = detect_language(code_file)
            
        # Display code with syntax highlighting
        syntax = Syntax(code, language, theme="monokai")
        console.print(syntax)
        
        # Analyze code
        analysis = assistant.analyze_code(code, language)
        console.print(f"\n[bold green]Analysis:[/bold green]\n{analysis}")
        
        # Execute code if supported
        if language in ['python', 'javascript', 'ruby']:
            result = assistant.execute_code(code, language)
            console.print(f"\n[bold green]Output:[/bold green]\n{result}")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@cli.command()
@click.argument('task_file', type=click.Path(exists=True))
def run_tasks(task_file):
    """Run a series of tasks from a file"""
    try:
        tasks = load_tasks(task_file)
        task_manager = TaskManager(tasks)
        
        with console.status("[bold green]Running tasks...") as status:
            for task in task_manager.run():
                console.print(f"[bold blue]{task.name}[/bold blue]: {task.status}")
                
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@cli.command()
@click.option('--type', 'doc_type', type=click.Choice(["Document", "Research Report", "Academic Paper", "Creative Writing"]), prompt=True, help='Type of document to create')
@click.option('--objective', prompt=True, help='Objective of the document')
@click.option('--websearch/--no-websearch', default=False, prompt=True, help='Perform web search for background research')
@click.argument('requirements', required=False)
def create_document(doc_type, objective, websearch, requirements):
    """Create a new document with AI assistance"""
    try:
        console.print(f"[bold blue]Creating {doc_type}...[/bold blue]")
        
        # Generate task chain
        task_message = f"Create a task chain to develop a {doc_type} with the following objective: {objective}\n\n{requirements or ''}"
        task_chain = assistant.chat(task_message)
        
        # Review and refine task chain
        review_message = f"""
        Please review the following tasks and determine which sections or components need to be created for this {doc_type}:

        {task_chain}

        Refine the task chain by following these guidelines:
        1. Do not include a general summary at the beginning or introductory remarks.
        2. Generate a new numbered list of tasks, with each task linked to the creation of one specific section or component.
        3. Only include tasks that involve creating content. Omit any tasks that do not require content creation.
        4. For each task, provide the following information:
        - Section or component name (e.g., Introduction, Chapter 1, Methodology)
        - Brief description of the section's or component's purpose or content
        5. At the end of the response, specify the maximum number of sections or components that need to be created using the format: Max = <number>
        6. Only include the listed tasks and the maximum number of sections or components in your response
        """
        
        refined_task_chain = assistant.chat(review_message)
        
        # Extract max items
        max_items_match = re.search(r'Max = (\d+)', refined_task_chain)
        max_items = int(max_items_match.group(1)) if max_items_match else None
        
        if not max_items:
            console.print("[bold red]Error: Could not determine number of sections[/bold red]")
            return
            
        # Split tasks
        tasks = re.split(r'\n\d+\.\s', refined_task_chain)
        tasks = [task.strip() for task in tasks if task.strip()]
        
        # Perform web search if requested
        background_research = ""
        if websearch:
            with console.status("[bold green]Performing background research...") as status:
                search_results = assistant.internet_search(objective)
                background_research = assistant.process_with_search(objective, search_results)
        
        # Generate document content
        content = create_document_content(tasks, max_items, objective, doc_type, background_research)
        
        # Save the document
        output_file = click.prompt('Save document as', type=str, default=f'{doc_type.lower().replace(" ", "_")}.md')
        with open(output_file, 'w') as f:
            f.write(content)
            
        console.print(f"[bold green]Document created successfully and saved to {output_file}[/bold green]")
        
        # Preview the document
        if click.confirm('Would you like to preview the document?'):
            console.print("\n[bold blue]Document Preview:[/bold blue]")
            console.print(Markdown(content))
            
    except Exception as e:
        console.print(f"[bold red]Error creating document: {str(e)}[/bold red]")

def create_document_content(tasks, max_items, objective, doc_type, background_research=""):
    """Generate the document content based on tasks and research"""
    content = f"<h1>{doc_type}</h1>"
    content += f"<h2>Objective: {objective}</h2>"
    
    for task_index, task in enumerate(tasks, start=1):
        if task_index <= max_items:
            section_match = re.search(r'Section: (.+)', task, re.IGNORECASE)
            section_title = section_match.group(1) if section_match else f"Section {task_index}"
            
            # Generate section content
            section_content = assistant.chat(f"Write the '{section_title}' section for a {doc_type} with the objective: {objective}. Based on this task description: {task}. Use this background research if relevant: {background_research}")
            
            # Add section to the document content
            content += f"<h3>{section_title}</h3>"
            content += section_content

    return content

def load_tasks(task_file):
    """Load tasks from a specified file and break them down into steps."""
    with open(task_file, 'r') as f:
        tasks = json.load(f)

    # Break down each task into steps
    all_steps = []
    for task in tasks:
        repo_info = {
            'clone_url': task['clone_url'],
            'repo_name': task['repo_name']
        }
        steps = break_down_task(repo_info)
        all_steps.append(steps)

    return all_steps

def break_down_task(repo_info):
    """Break down complex task into smaller steps"""
    steps = []

    # Step 1: Clone the repository
    clone_step = f"git clone {repo_info['clone_url']}"
    steps.append(clone_step)

    # Step 2: Navigate to the cloned repository directory
    navigate_step = f"cd {repo_info['repo_name']}"
    steps.append(navigate_step)

    # Step 3: Analyze the repository structure and files
    analyze_step = "# Analyze the repository structure and files"
    steps.append(analyze_step)

    # Step 4: Identify the main entry point of the code
    entry_point_step = "# Identify the main entry point of the code"
    steps.append(entry_point_step)

    # Step 5: Set up the necessary dependencies and virtual environment
    setup_step = "# Set up the necessary dependencies and virtual environment"
    steps.append(setup_step)

    # Step 6: Execute the code
    execute_step = "# Execute the code"
    steps.append(execute_step)

    # Step 7: Analyze the output and handle any errors
    analyze_output_step = "# Analyze the output and handle any errors"
    steps.append(analyze_output_step)

    # Step 8: Clean up and remove the cloned repository
    cleanup_step = f"rm -rf {repo_info['repo_name']}"
    steps.append(cleanup_step)

    return steps

def handle_command(cmd, conversation, web_search):
    """Handle special commands"""
    cmd = cmd.lower()
    if cmd == "!exit":
        raise click.Exit()
    elif cmd.startswith("!save"):
        filename = cmd.split()[1] if len(cmd.split()) > 1 else "conversation.json"
        save_conversation(conversation, filename)
        console.print(f"[bold green]Conversation saved to {filename}[/bold green]")
    elif cmd == "!clear":
        conversation.clear()
        console.print("[bold green]Conversation cleared[/bold green]")
    elif cmd.startswith("!web"):
        state = cmd.split()[1] if len(cmd.split()) > 1 else "on"
        web_search = state.lower() == "on"
        console.print(f"[bold green]Web search {'enabled' if web_search else 'disabled'}[/bold green]")
    elif cmd.startswith("!code"):
        handle_code_execution(cmd)

def handle_code_execution(cmd):
    """Handle code execution command"""
    console.print(f"[bold blue]Executing code command: {cmd}[/bold blue]")
    
    # Extract the language and code from the command
    parts = cmd.split(" ", 2)  # Split into command parts
    if len(parts) < 3:
        console.print("[bold red]Error:[/bold red] Invalid command format. Use !code <language> <code>")
        return
    
    language = parts[1]  # The second part is the language
    code = parts[2]  # The rest is the code to execute

    # Validate the language
    if language not in ['python', 'javascript', 'ruby']:
        console.print(f"[bold red]Error:[/bold red] Unsupported language: {language}")
        return

    try:
        if language == 'python':
            # Execute Python code
            exec_globals = {}
            exec(code, exec_globals)
            output = exec_globals.get('result', 'No output variable defined.')
        
        elif language == 'javascript':
            # Execute JavaScript code using Node.js
            process = subprocess.Popen(['node', '-e', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')
        
        elif language == 'ruby':
            # Execute Ruby code using the Ruby interpreter
            process = subprocess.Popen(['ruby', '-e', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')

        console.print(f"\n[bold green]Output:[/bold green]\n{output}")

    except Exception as e:
        console.print(f"[bold red]Error executing code:[/bold red] {str(e)}")
    # Add your code execution logic here

def needs_web_search(text):
    """Check if the input likely needs a web search"""
    search_keywords = [
        'search', 'find', 'look up', 'google', 'recent', 'latest',
        'news', 'information about', 'what is', 'who is'
    ]
    return any(keyword in text.lower() for keyword in search_keywords)

def detect_language(file_path):
    """Detect programming language from file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.rb': 'ruby',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cs': 'csharp',
        '.php': 'php'
    }
    return language_map.get(ext, 'text')

class TaskManager:
    """A simple task manager to handle tasks"""
    def __init__(self, tasks):
        self.tasks = tasks
        self.current_task_index = 0

    def run(self):
        """Run the tasks"""
        while self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index]
            self.current_task_index += 1
            yield task

if __name__ == '__main__':
    cli()

