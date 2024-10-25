# Admin Assist CLI Usage Guide

Welcome to the Admin Assist CLI! This guide will walk you through the steps to set up and use the Admin Assist CLI after cloning the repository.

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Basic Commands](#basic-commands)
   - [1. Interactive AI Chat](#1-interactive-ai-chat)
   - [2. Transcribe Audio Files](#2-transcribe-audio-files)
   - [3. Execute or Analyze Code](#3-execute-or-analyze-code)
   - [4. Run Tasks from a File](#4-run-tasks-from-a-file)
   - [5. Create Documents](#5-create-documents)
   - [6. Create or Improve Applications](#6-create-or-improve-applications)
3. [Getting Help](#getting-help)

## Initial Setup

Follow these steps to set up the Admin Assist CLI:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/admin-assist-cli.git
   cd admin-assist-cli
   ```

2. **Install dependencies:**
   Make sure you have Python and pip installed. Then, run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key:**
   You need an OpenAI API key to use the AI features. Set it up by running:
   ```bash
   admin-assist config set-key YOUR_API_KEY
   ```

## Basic Commands

### 1. Interactive AI Chat
Start a conversation with the AI assistant. This command allows you to ask questions and receive responses in real-time.

**Usage:**
```bash
python src/cli/main.py chat
```

**Options:**
- `--websearch`: Enable or disable web search for additional information.
- `--model`: Specify the OpenAI model to use (default is `gpt-3.5-turbo`).
- `--save`: Save the conversation to a specified file.

**Example:**
```bash
python src/cli/main.py chat --websearch --model gpt-4 --save conversation.json
```

### 2. Transcribe Audio Files
Transcribe audio files and generate structured notes.

**Usage:**
```bash
admin-assist transcribe <file_path>
```

**Options:**
- `--format`: Specify the output format (text, json, markdown).

**Example:**
```bash
admin-assist transcribe audio_file.mp3 --format markdown
```

### 3. Execute or Analyze Code
Analyze a code file or execute it if supported.

**Usage:**
```bash
admin-assist execute_code <code_file> [--language <language>]
```

**Options:**
- `--language`: Specify the programming language if not detected automatically.

**Example:**
```bash
admin-assist execute_code script.py --language python
```

### 4. Run Tasks from a File
Run a series of predefined tasks from a JSON file.

**Usage:**
```bash
admin-assist run_tasks <task_file>
```

**Example:**
```bash
admin-assist run_tasks tasks.json
```

### 5. Create Documents
Create a new document with AI assistance based on specified objectives.

**Usage:**
```bash
admin-assist create_document
```

**Options:**
- `--type`: Specify the type of document (e.g., Document, Research Report).
- `--objective`: Provide the objective of the document.
- `--websearch`: Perform a web search for background research.

**Example:**
```bash
admin-assist create_document --type "Research Report" --objective "Analyze the impact of AI on education" --websearch
```

### 6. Create or Improve Applications
Create a new application or improve an existing one with AI assistance.

**Usage:**
```bash
admin-assist create_application
```

**Options:**
- `--language`: Specify the programming language (e.g., Python, JavaScript).
- `--objective`: Provide the objective of the application.
- `--mode`: Choose to create a new application or improve an existing one.
- `--project-dir`: Specify the directory for the project.

**Example:**
```bash
admin-assist create_application --language Python --objective "Build a web scraper" --mode Create --project-dir my_scraper
```

## Getting Help

If you need assistance:

1. **Check the documentation:**
   ```bash
   admin-assist docs open
   ```

2. **Get command-specific help:**
   ```bash
   admin-assist COMMAND --help
   ```

3. **Access the interactive help system:**
   ```bash
   admin-assist help interactive
   ```

Remember to check our [official documentation](https://admin-assist-cli.readthedocs.io/) for more detailed information and updates.
