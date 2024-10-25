import os
from typing import List, Dict, Optional, Any
import openai
from openai import OpenAI
import requests
from requests.exceptions import RequestException
from config.settings import OPENAI_API_KEY, DEFAULT_MODEL, MAX_TOKENS

class APIClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = DEFAULT_MODEL,
        max_tokens: int = MAX_TOKENS
    ) -> Any:
        """Send a chat completion request to OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            return response
        except Exception as e:
            raise Exception(f"Chat completion failed: {str(e)}")

    def audio_transcription(
        self, 
        file: Any,
        model: str = "whisper-1",
        language: Optional[str] = None
    ) -> str:
        """Transcribe audio using OpenAI's Whisper API"""
        try:
            response = self.client.audio.transcriptions.create(
                model=model,
                file=file,
                language=language,
                response_format="text"
            )
            return response
        except Exception as e:
            raise Exception(f"Audio transcription failed: {str(e)}")

    def image_generation(
        self,
        prompt: str,
        model: str = "dall-e-2",
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1
    ) -> List[str]:
        """Generate images using DALL-E API"""
        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            return [image.url for image in response.data]
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

    def embeddings(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> List[float]:
        """Get embeddings for text using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")

    def moderate_content(self, text: str) -> Dict:
        """Check content against OpenAI's moderation endpoint"""
        try:
            response = self.client.moderations.create(input=text)
            return response.results[0]
        except Exception as e:
            raise Exception(f"Content moderation failed: {str(e)}")

    def validate_api_key(self) -> bool:
        """Validate the OpenAI API key"""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            raise Exception(f"Failed to fetch models: {str(e)}")
