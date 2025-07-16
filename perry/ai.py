import os
import random
import logging
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import Message, ChatThread, CelestialProfile

logger = logging.getLogger(__name__)

class CelestialAI:
    """Handles all AI-powered celestial communications"""
    
    def __init__(self, thread):
        self.thread = thread
        self.celestial = thread.celestial
        self.user = thread.user
        
    def generate_response(self):
        """Generate either AI or simulated response based on availability"""
        try:
            if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != 'your-api-key-here':
                return self._generate_ai_response()
            return self._generate_simulated_response()
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return self._generate_fallback_response()

    def _generate_ai_response(self):
        """Generate response using OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.ALLOWED_HOSTS[0],
            "Content-Type": "application/json"
        }
        
        last_human_message = self.thread.messages\
            .filter(is_celestial=False)\
            .order_by('-timestamp')\
            .first()
        
        payload = {
            "model": self._determine_ai_model(),
            "messages": [
                {
                    "role": "system",
                    "content": self._build_system_prompt()
                },
                {
                    "role": "user",
                    "content": last_human_message.content if last_human_message else "Greetings!"
                }
            ],
            "temperature": self._get_response_temperature(),
            "max_tokens": settings.MAX_RESPONSE_TOKENS
        }
        
        response = requests.post(
            settings.OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        
        ai_content = response.json()['choices'][0]['message']['content']
        return self._create_ai_message(ai_content)
    
    def _generate_simulated_response(self):
        """Fallback simulated response"""
        responses = [
            f"My {random.choice(['rings', 'moons', 'atmosphere'])} are tingling!",
            f"As {self.celestial.name}, a {self.celestial.celestial_type}, I ponder your words...",
            "The cosmic energies align to say...",
            random.choice(self.celestial.personality_prompt.split('.')[:5]) or "I observe your message."
        ]
        
        if self.celestial.temperature > 5000:  # Hot celestial snark
            responses.extend([
                "Ugh, mortal chatter...",
                f"I've burned hotter than your interest for {self.celestial.temperature} years",
                "Your message barely registers on my radiative scale"
            ])
            
        return self._create_ai_message(random.choice(responses))
    
    def _generate_fallback_response(self):
        """Emergency fallback if both AI and simulation fail"""
        return self._create_ai_message(
            random.choice(settings.CELESTIAL_AI_SETTINGS['fallback_responses'])
        )
    
    def _create_ai_message(self, content):
        """Create and save the message with appropriate delay"""
        delay_minutes = max(
            self.celestial.base_response_delay * random.uniform(0.8, 1.2),
            settings.MIN_RESPONSE_DELAY
        )
        
        return Message.objects.create(
            thread=self.thread,
            content=content,
            is_celestial=True,
            timestamp=timezone.now() + timedelta(minutes=delay_minutes)
        )
    
    def _build_system_prompt(self):
        """Construct the AI's personality prompt"""
        traits = [
            f"Name: {self.celestial.name}",
            f"Type: {self.celestial.get_celestial_type_display()}",
            f"Temperature: {self.celestial.temperature}K",
            f"Rings: {'Yes' if self.celestial.has_rings else 'No'}",
            f"Moons: {self.celestial.moon_count}",
            f"Personality: {self.celestial.personality_prompt}",
            "Response Style: Speak as a celestial entity to a mortal admirer",
            f"Response Length: {settings.MAX_RESPONSE_TOKENS} tokens maximum"
        ]
        return '\n'.join(traits)
    
    def _determine_ai_model(self):
        """Select appropriate AI model based on celestial traits"""
        if self.celestial.temperature > 8000:  # Hot stars get smarter models
            return "anthropic/claude-3-opus"
        return settings.DEFAULT_AI_MODEL
    
    def _get_response_temperature(self):
        """Adjust creativity based on celestial traits"""
        base_temp = settings.CELESTIAL_AI_SETTINGS['temperature']
        # Hotter celestials get more variable responses
        return min(1.0, base_temp * (self.celestial.temperature / 5000))

def generate_celestial_response(thread_id):
    """Primary interface for generating responses"""
    try:
        thread = ChatThread.objects.get(id=thread_id)
        ai = CelestialAI(thread)
        return ai.generate_response()
    except Exception as e:
        logger.error(f"Failed to generate response for thread {thread_id}: {str(e)}")
        return None