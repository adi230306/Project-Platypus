import os
import sys

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from perry.models import CelestialProfile, Swipe, Match

User = get_user_model()

class SwipeTests(TestCase):
    def setUp(self):
        """Create test data that will be used across all tests"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='swiper',
            password='testpass123'
        )
        
        # Create celestial objects
        self.planet = CelestialProfile.objects.create(
            name="TestPlanet",
            celestial_type="planet",
            temperature=300,
            personality_prompt="A test planet"
        )
        
        self.star = CelestialProfile.objects.create(
            name="TestStar",
            celestial_type="star",
            temperature=5000,
            personality_prompt="A test star"
        )
        
        # Authenticate the test client
        self.client.force_authenticate(user=self.user)
    
    def test_swipe_creation(self):
        """Test creating a swipe through the API"""
        url = '/api/swipe/'
        data = {
            'celestial_id': self.planet.id,
            'direction': 'R'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Swipe.objects.count(), 1)
        
        swipe = Swipe.objects.first()
        self.assertEqual(swipe.user, self.user)
        self.assertEqual(swipe.celestial, self.planet)
        self.assertEqual(swipe.direction, 'R')
    
    def test_match_creation(self):
        """Test that matches are created when both parties swipe right"""
        # First swipe (user swipes right)
        self.client.post('/api/swipe/', {
            'celestial_id': self.star.id,
            'direction': 'R'
        }, format='json')
        
        # Verify no match yet
        self.assertEqual(Match.objects.count(), 0)
        
        # Simulate celestial swipe right (82% chance)
        # We'll mock this since celestial swipes are automatic
        from .utils import process_swipe
        result = process_swipe(self.user, self.star.id, 'R')
        
        # Verify match was created
        self.assertEqual(Match.objects.count(), 1)
        match = Match.objects.first()
        self.assertEqual(match.user, self.user)
        self.assertEqual(match.celestial, self.star)
        self.assertTrue(match.celestial_swiped_right)
    
    def test_duplicate_swipe(self):
        """Test that users can't swipe on the same celestial twice"""
        # First swipe
        self.client.post('/api/swipe/', {
            'celestial_id': self.planet.id,
            'direction': 'L'
        }, format='json')
        
        # Second swipe - should fail
        response = self.client.post('/api/swipe/', {
            'celestial_id': self.planet.id,
            'direction': 'R'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already swiped', str(response.data))
    
    def test_invalid_swipe_direction(self):
        """Test that only L/R directions are accepted"""
        response = self.client.post('/api/swipe/', {
            'celestial_id': self.planet.id,
            'direction': 'UP'  # Invalid
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('direction', str(response.data))
    
    def test_nonexistent_celestial(self):
        """Test swiping on non-existent celestial"""
        response = self.client.post('/api/swipe/', {
            'celestial_id': 9999,  # Doesn't exist
            'direction': 'R'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)