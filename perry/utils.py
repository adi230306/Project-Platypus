import random
from .models import CelestialProfile, Swipe, Match, ChatThread, Message
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def process_swipe(user, celestial_id, direction):
    celestial = CelestialProfile.objects.get(id=celestial_id)
    
    if Swipe.objects.filter(user=user, celestial=celestial).exists():
        return {'error': 'Already swiped'}
    
    Swipe.objects.create(user=user, celestial=celestial, direction=direction)
    
    celestial_decision = 'R' if random.random() < 0.82 else 'L'
    
    if direction == 'R' and celestial_decision == 'R':
        match = Match.objects.create(
            user=user,
            celestial=celestial,
            celestial_swiped_right=True
        )
        return {'status': 'match', 'match_id': match.id}
    
    return {'status': 'no_match'}

def simulate_celestial_response(thread):
    celestial = thread.celestial
    is_sassy = celestial.temperature > 5000
    response_time = celestial.base_response_delay * random.uniform(0.5, 1.5)
    
    responses = [
        f"My {random.choice(['rings', 'moons', 'atmosphere'])} are tingling!",
        "In my celestial opinion...",
        f"From {celestial.name}'s surface...",
        "The cosmic winds whisper..."
    ]
    
    if is_sassy:
        responses.extend([
            "Ugh, another mortal bothering me?",
            "I've got moons with more interesting things to say",
            f"Tell me something I haven't heard in {celestial.temperature} years"
        ])
    
    response_content = random.choice(responses)
    Message.objects.create(
        thread=thread,
        content=response_content,
        is_celestial=True,
        timestamp=datetime.now() + timedelta(minutes=response_time)
    )
    
    logger.info(f"Scheduled response from {celestial.name}")