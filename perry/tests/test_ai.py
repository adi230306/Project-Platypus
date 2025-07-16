import os
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from perry.models import CelestialProfile, User, ChatThread, Message
from perry.ai import CelestialAI, generate_celestial_response

class CelestialAITests(TestCase):
    """Comprehensive tests for AI response generation"""
    
    def setUp(self):
        """Create test data that will be used across all tests"""
        # Basic test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Create celestial objects with different traits
        self.cool_planet = CelestialProfile.objects.create(
            name="CoolPlanet",
            celestial_type="planet",
            temperature=300,
            has_rings=True,
            moon_count=5,
            personality_prompt="A cold, distant planet that speaks slowly and deliberately",
            base_response_delay=3
        )
        
        self.hot_star = CelestialProfile.objects.create(
            name="HotStar",
            celestial_type="star",
            temperature=15000,
            has_rings=False,
            moon_count=0,
            personality_prompt="A blazing star with quick wit and sharp tongue",
            base_response_delay=1
        )
        
        # Create chat threads
        self.planet_thread = ChatThread.objects.create(
            user=self.user,
            celestial=self.cool_planet
        )
        
        self.star_thread = ChatThread.objects.create(
            user=self.user,
            celestial=self.hot_star
        )
        
        # Add some test messages
        Message.objects.create(
            thread=self.planet_thread,
            sender=self.user,
            content="Hello cold planet!",
            is_celestial=False
        )
        
        Message.objects.create(
            thread=self.star_thread,
            sender=self.user,
            content="Hey hot star!",
            is_celestial=False
        )
    
    # TEST CASE 1: Simulated Responses
    def test_simulated_response_generation(self):
        """Test fallback responses when no API key is set"""
        # Change this to test different celestial types
        test_thread = self.planet_thread  # Try changing to self.star_thread
        
        # Initialize AI with our test thread
        ai = CelestialAI(test_thread)
        
        # Generate a simulated response (what happens when no API key)
        response = ai._generate_simulated_response()
        
        # Verify the response was created
        self.assertIsNotNone(response)
        self.assertTrue(response.is_celestial)
        
        # Check response contains expected patterns
        # Add more patterns based on your simulated responses
        possible_patterns = [
            "are tingling!",
            "As " + test_thread.celestial.name,
            "cosmic",
            "observe"
        ]
        self.assertTrue(any(pattern in response.content for pattern in possible_patterns))
        
        # Verify delay was applied correctly
        expected_min_delay = timezone.now() + timedelta(
            minutes=test_thread.celestial.base_response_delay * 0.8
        )
        expected_max_delay = timezone.now() + timedelta(
            minutes=test_thread.celestial.base_response_delay * 1.2
        )
        self.assertGreaterEqual(response.timestamp, expected_min_delay)
        self.assertLessEqual(response.timestamp, expected_max_delay)
    
    # TEST CASE 2: AI Response Configuration
    def test_ai_system_prompt_generation(self):
        """Verify the system prompt includes all celestial traits"""
        ai = CelestialAI(self.star_thread)
        prompt = ai._build_system_prompt()
        
        # Check all key traits are included
        required_elements = [
            f"Name: {self.hot_star.name}",
            f"Type: {self.hot_star.get_celestial_type_display()}",
            f"Temperature: {self.hot_star.temperature}K",
            "Rings: No",  # Because has_rings=False
            "Moons: 0",
            self.hot_star.personality_prompt
        ]
        
        for element in required_elements:
            self.assertIn(element, prompt)
    
    # TEST CASE 3: Model Selection Logic
    def test_ai_model_selection(self):
        """Test the rules for selecting AI models"""
        # For hot celestials (>8000K)
        ai = CelestialAI(self.star_thread)
        self.assertEqual(ai._determine_ai_model(), "anthropic/claude-3-opus")
        
        # For cooler celestials
        ai = CelestialAI(self.planet_thread)
        self.assertEqual(ai._determine_ai_model(), settings.DEFAULT_AI_MODEL)
    
    # TEST CASE 4: Error Handling
    def test_fallback_response_generation(self):
        """Test that fallbacks work when all else fails"""
        # Simulate an error scenario
        ai = CelestialAI(self.planet_thread)
        response = ai._generate_fallback_response()
        
        self.assertIn(response.content, settings.CELESTIAL_AI_SETTINGS['fallback_responses'])
    
    # TEST CASE 5: Full Integration Test
    def test_generate_celestial_response_integration(self):
        """Test the main interface function"""
        # First test with API key disabled
        original_key = settings.OPENROUTER_API_KEY
        settings.OPENROUTER_API_KEY = None
        
        response = generate_celestial_response(self.planet_thread.id)
        self.assertIsNotNone(response)
        
        # Now test with mock API (advanced - would need requests-mock)
        # settings.OPENROUTER_API_KEY = "test-key"
        # ... mock API calls here ...
        
        # Restore original key
        settings.OPENROUTER_API_KEY = original_key

    # TEST CASE 6: Response Timing
    def test_response_timing(self):
        """Verify responses respect minimum delay settings"""
        ai = CelestialAI(self.planet_thread)
        response = ai._create_ai_message("Test message")
        
        # Should be at least MIN_RESPONSE_DELAY in future
        min_timestamp = timezone.now() + timedelta(minutes=settings.MIN_RESPONSE_DELAY)
        self.assertGreaterEqual(response.timestamp, min_timestamp)