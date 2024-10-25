# API Settings
API_TIMEOUT = 30
MAX_RETRIES = 3
BATCH_SIZE = 20

# Model Settings
CHAT_MODELS = {
    "gpt-3.5-turbo": {
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "gpt-4": {
        "max_tokens": 8192,
        "temperature": 0.7
    }
}

EMBEDDING_MODELS = {
    "text-embedding-ada-002": {
        "dimensions": 1536
    }
}

# File Types
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
SUPPORTED_CODE_LANGUAGES = ['python', 'javascript', 'ruby', 'java', 'cpp', 'csharp', 'php']
SUPPORTED_DOC_FORMATS = ['.txt', '.md', '.pdf', '.docx', '.doc']

# Command Prefixes
COMMAND_PREFIX = '!'
COMMANDS = {
    'exit': 'Exit the application',
    'save': 'Save conversation to file',
    'clear': 'Clear conversation history',
    'web': 'Toggle web search',
    'code': 'Execute code',
    'help': 'Show help message'
}

# Web Search
SEARCH_PROVIDERS = {
    'wikipedia': {
        'endpoint': 'https://en.wikipedia.org/w/api.php',
        'rate_limit': 50  # requests per minute
    },
    'duckduckgo': {
        'endpoint': 'https://duckduckgo.com/html/',
        'rate_limit': 100  # requests per minute
    }
}

# Error Messages
ERROR_MESSAGES = {
    'api_key': 'Invalid API key. Please check your configuration.',
    'rate_limit': 'Rate limit exceeded. Please try again later.',
    'connection': 'Connection error. Please check your internet connection.',
    'timeout': 'Request timed out. Please try again.',
    'invalid_input': 'Invalid input. Please check your input and try again.',
    'unsupported_format': 'Unsupported file format.',
    'file_not_found': 'File not found.',
    'permission_denied': 'Permission denied.',
}

# Success Messages
SUCCESS_MESSAGES = {
    'save': 'Successfully saved to {}',
    'load': 'Successfully loaded from {}',
    'clear': 'Successfully cleared conversation history',
    'execute': 'Successfully executed code',
    'transcribe': 'Successfully transcribed audio',
    'analyze': 'Successfully analyzed code',
}
