"""
Model-agnostic vision LLM interface.

Supports: OpenAI (GPT-4V/4o), Anthropic (Claude 3), Google (Gemini Pro Vision)
"""
import os
import base64
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class VisionModel(ABC):
    """Abstract base class for vision models."""
    
    @abstractmethod
    def analyze_image(self, image_path: Path, prompt: str) -> Optional[str]:
        """Analyze image and return text response."""
        pass
    
    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64."""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')


class OpenAIVision(VisionModel):
    """OpenAI GPT-4V/4o vision model."""
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize OpenAI vision model.
        
        Args:
            model: Model name (gpt-4o, gpt-4-turbo, gpt-4-vision-preview)
        """
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def analyze_image(self, image_path: Path, prompt: str) -> Optional[str]:
        """Analyze image using OpenAI vision model."""
        try:
            base64_image = self._encode_image(image_path)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }],
                max_tokens=2000,
                temperature=0  # Deterministic for consistency
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI vision error: {e}")
            return None


class ClaudeVision(VisionModel):
    """Anthropic Claude 3 vision model."""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Claude vision model.
        
        Args:
            model: Model name (claude-3-5-sonnet, claude-3-opus, etc.)
        """
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def analyze_image(self, image_path: Path, prompt: str) -> Optional[str]:
        """Analyze image using Claude vision model."""
        try:
            base64_image = self._encode_image(image_path)
            
            # Detect image type
            suffix = image_path.suffix.lower()
            media_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(suffix, 'image/png')
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Claude vision error: {e}")
            return None


class GeminiVision(VisionModel):
    """Google Gemini Pro Vision model."""
    
    def __init__(self, model: str = "gemini-3-flash-preview"):
        """
        Initialize Gemini vision model.
        
        Args:
            model: Model name (gemini-1.5-pro, gemini-3-flash-preview)
        """
        self.model = model
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    def analyze_image(self, image_path: Path, prompt: str) -> Optional[str]:
        """Analyze image using Gemini vision model."""
        try:
            import PIL.Image
            
            # Gemini requires PIL Image object
            image = PIL.Image.open(image_path)
            
            response = self.client.generate_content(
                [prompt, image],
                generation_config={
                    'temperature': 0,
                    'max_output_tokens': 8000  # Increased for long nutrient lists
                }
            )
            
            # Validate response is not empty
            if not response.text or not response.text.strip():
                logger.warning("Empty response from Gemini")
                return None
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini vision error: {e}")
            return None


class VisionModelFactory:
    """Factory for creating vision model instances."""
    
    @staticmethod
    def create(provider: str = "auto", **kwargs) -> VisionModel:
        """
        Create vision model instance.
        
        Args:
            provider: Model provider ("openai", "claude", "gemini", "auto")
                     "auto" tries providers in order based on available API keys
            **kwargs: Additional arguments passed to model constructor
        
        Returns:
            VisionModel instance
        """
        if provider == "auto":
            # Try providers in order of preference
            for prov in ["openai", "gemini", "claude"]:
                try:
                    return VisionModelFactory.create(prov, **kwargs)
                except ValueError:
                    continue
            raise ValueError("No vision model API key found. Set OPENAI_API_KEY, GOOGLE_API_KEY, or ANTHROPIC_API_KEY")
        
        providers = {
            "openai": OpenAIVision,
            "claude": ClaudeVision,
            "gemini": GeminiVision
        }
        
        if provider not in providers:
            raise ValueError(f"Unknown provider: {provider}. Choose from: {list(providers.keys())}")
        
        return providers[provider](**kwargs)
