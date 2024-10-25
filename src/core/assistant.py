import os
import json
import tempfile
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor

class Assistant:
    def __init__(self, api_client):
        self.api_client = api_client
        self.conversation_history = []
        self.user_agent = UserAgent()

    def chat(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        """Process a chat message and return the response"""
        self.conversation_history.append({"role": "user", "content": message})
        
        response = self.api_client.chat_completion(
            model=model,
            messages=self.conversation_history
        )
        
        assistant_message = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message

    def internet_search(self, query: str) -> List[Dict]:
        """Perform an internet search and return relevant results"""
        sources = [
            {
                "endpoint": "https://en.wikipedia.org/w/api.php",
                "params": {
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                },
                "handler": self._handle_wikipedia_response
            },
            {
                "endpoint": "https://duckduckgo.com/html/",
                "params": {"q": query},
                "handler": self._handle_duckduckgo_response
            }
        ]

        results = []
        with ThreadPoolExecutor() as executor:
            for source in sources:
                content = self._fetch_url(source["endpoint"], source["params"])
                if content:
                    results.extend(source["handler"](content))

        return results

    def process_with_search(self, query: str, search_results: List[Dict]) -> str:
        """Process a query with search results"""
        context = f"Based on the following search results:\n\n"
        for result in search_results:
            context += f"- {result['title']}: {result['content']}\n"
        
        context += f"\nAnswer the following query: {query}"
        
        return self.chat(context)

    def transcribe_audio(self, file_path: str) -> str:
        """Transcribe an audio file using Whisper API"""
        with open(file_path, "rb") as audio_file:
            transcript = self.api_client.audio_transcription(
                file=audio_file,
                model="whisper-1"
            )
        return transcript

    def generate_notes(self, transcript: str) -> str:
        """Generate structured notes from a transcript"""
        prompt = f"""
        Generate structured notes from this transcript using the following format:
        
        # Summary
        [Brief summary of the content]
        
        # Key Points
        - [Key point 1]
        - [Key point 2]
        
        # Action Items
        - [Action item 1]
        - [Action item 2]
        
        Transcript:
        {transcript}
        """
        
        return self.chat(prompt)

    def analyze_code(self, code: str, language: str) -> str:
        """Analyze code and provide insights"""
        prompt = f"""
        Analyze this {language} code and provide:
        1. A brief explanation of what it does
        2. Potential improvements or issues
        3. Best practices that could be applied
        
        Code:        ```{language}
        {code}        ```
        """
        
        return self.chat(prompt)

    def execute_code(self, code: str, language: str) -> str:
        """Execute code in a safe environment and return the result"""
        if language not in ['python', 'javascript', 'ruby']:
            raise ValueError(f"Execution not supported for {language}")
            
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
            f.write(code)
            temp_file = f.name
            
        try:
            if language == 'python':
                result = self._execute_python(temp_file)
            elif language == 'javascript':
                result = self._execute_javascript(temp_file)
            elif language == 'ruby':
                result = self._execute_ruby(temp_file)
                
            return result
        finally:
            os.unlink(temp_file)

    def _fetch_url(self, url: str, params: Dict) -> Optional[str]:
        """Fetch content from a URL with error handling"""
        headers = {"User-Agent": self.user_agent.random}
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _handle_wikipedia_response(self, content: str) -> List[Dict]:
        """Parse Wikipedia API response"""
        data = json.loads(content)
        results = []
        for item in data.get("query", {}).get("search", [])[:3]:
            results.append({
                "title": item["title"],
                "content": BeautifulSoup(item["snippet"], "html.parser").get_text(),
                "url": f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}"
            })
        return results

    def _handle_duckduckgo_response(self, content: str) -> List[Dict]:
        """Parse DuckDuckGo search results"""
        soup = BeautifulSoup(content, "html.parser")
        results = []
        for result in soup.select(".result__body")[:3]:
            title = result.select_one(".result__title")
            snippet = result.select_one(".result__snippet")
            if title and snippet:
                results.append({
                    "title": title.get_text(),
                    "content": snippet.get_text(),
                    "url": result.select_one("a.result__url")["href"]
                })
        return results

    def _execute_python(self, file_path: str) -> str:
        """Execute Python code in a subprocess"""
        import subprocess
        result = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr

    def _execute_javascript(self, file_path: str) -> str:
        """Execute JavaScript code using Node.js"""
        import subprocess
        result = subprocess.run(
            ["node", file_path],
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr

    def _execute_ruby(self, file_path: str) -> str:
        """Execute Ruby code"""
        import subprocess
        result = subprocess.run(
            ["ruby", file_path],
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr

    def create_document(self) -> str:
        """Interactive document creation workflow"""
        # Get document type
        task_types = ["Document", "Research Report", "Academic Paper", "Creative Writing"]
        task_prompt = "What type of document would you like to create? Options:\n" + \
                     "\n".join(f"{i+1}. {t}" for i, t in enumerate(task_types))
        
        task_type = self.chat(task_prompt)
        
        # Get word count range
        word_count_prompt = "Please specify your desired word count range (e.g., '500-1000'):"
        word_count_response = self.chat(word_count_prompt)
        min_words, max_words = self._parse_word_count(word_count_response)
        
        # Ask about internet search
        search_prompt = "Would you like me to perform an internet search to gather information? (yes/no)"
        search_response = self.chat(search_prompt)
        
        context = ""
        if search_response.lower().strip() in ['yes', 'y']:
            search_query_prompt = "What would you like me to search for?"
            search_query = self.chat(search_query_prompt)
            search_results = self.internet_search(search_query)
            
            context = "Based on the following research:\n\n"
            for result in search_results:
                context += f"- {result['title']}: {result['content']}\n"
        
        # Generate the document
        document_prompt = f"""
        Create a {task_type} with the following specifications:
        - Word count: {min_words}-{max_words} words
        {context}
        
        Please structure the document appropriately for its type, including:
        - A clear introduction
        - Well-organized body sections
        - A conclusion
        - Any necessary citations or references
        """
        
        return self.chat(document_prompt)

    def _parse_word_count(self, word_count_str: str) -> Tuple[int, int]:
        """Parse word count range from string input"""
        try:
            # Remove any non-numeric characters except hyphen
            cleaned = ''.join(c for c in word_count_str if c.isdigit() or c == '-')
            min_words, max_words = map(int, cleaned.split('-'))
            return min_words, max_words
        except ValueError:
            # Default range if parsing fails
            return 500, 1000
