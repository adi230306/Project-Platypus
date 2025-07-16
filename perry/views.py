from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Swipe, CelestialProfile, Match, ChatThread, Message
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def home(request):
    return HttpResponse("Welcome to Space Tinder! Visit /admin or /api/swipe/")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def swipe(request):
    try:
        celestial_id = request.data.get('celestial_id')
        direction = request.data.get('direction', '').upper()
        
        if not celestial_id:
            return Response({'error': 'celestial_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if direction not in ('L', 'R'):
            return Response({'error': 'Invalid direction - must be "L" or "R"'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        celestial = CelestialProfile.objects.get(id=celestial_id)
        user = request.user
        
        logger.info(f"User {user.id} swiped {direction} on {celestial.name}")
        
        Swipe.objects.create(
            user=user,
            celestial=celestial,
            direction=direction
        )
        
        if direction == 'R':
            celestial_swiped_right = random.random() < 0.82
            if celestial_swiped_right:
                Match.objects.create(
                    user=user,
                    celestial=celestial,
                    celestial_swiped_right=True
                )
                return Response({
                    'match': True,
                    'celestial': celestial.name,
                    'message': f"You matched with {celestial.name}!"
                }, status=status.HTTP_201_CREATED)
        
        return Response({
            'match': False,
            'message': 'No match this time' if direction == 'R' else 'Swipe recorded'
        }, status=status.HTTP_201_CREATED)
        
    except CelestialProfile.DoesNotExist:
        return Response({'error': 'Celestial not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Swipe error: {str(e)}")
        return Response({'error': 'Internal server error'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_threads(request):
    threads = ChatThread.objects.filter(user=request.user).select_related('celestial')
    
    data = []
    for thread in threads:
        last_message = thread.messages.last()
        unread_count = thread.messages.filter(read=False, is_celestial=True).count()
        
        data.append({
            'id': thread.id,
            'celestial': {
                'id': thread.celestial.id,
                'name': thread.celestial.name,
                'image': thread.celestial.gif.url if thread.celestial.gif else None
            },
            'last_message': {
                'content': last_message.content if last_message else None,
                'timestamp': last_message.timestamp if last_message else None,
                'is_celestial': last_message.is_celestial if last_message else None
            },
            'unread_count': unread_count
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def potential_chats(request):
    matches = Match.objects.filter(
        user=request.user,
        celestial_swiped_right=True
    ).exclude(
        celestial__in=ChatThread.objects.filter(user=request.user).values('celestial')
    ).select_related('celestial')
    
    data = [{
        'match_id': match.id,
        'celestial': {
            'id': match.celestial.id,
            'name': match.celestial.name,
            'type': match.celestial.celestial_type,
            'image': match.celestial.gif.url if match.celestial.gif else None
        },
        'matched_at': match.matched_at
    } for match in matches]
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_messages(request, thread_id):
    try:
        thread = ChatThread.objects.get(id=thread_id, user=request.user)
        messages = thread.messages.all()
        
        thread.messages.filter(is_celestial=True, read=False).update(read=True)
        
        data = [{
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp,
            'is_celestial': msg.is_celestial,
            'read': msg.read
        } for msg in messages]
        
        return Response(data)
    except ChatThread.DoesNotExist:
        return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, thread_id):
    try:
        thread = ChatThread.objects.get(id=thread_id, user=request.user)
        content = request.data.get('content')
        
        if not content:
            return Response({'error': 'Message content required'}, status=status.HTTP_400_BAD_REQUEST)
        
        message = Message.objects.create(
            thread=thread,
            sender=request.user,
            content=content,
            is_celestial=False
        )
        
        # Simulate celestial response
        simulate_celestial_response(thread)
        
        return Response({
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp
        }, status=status.HTTP_201_CREATED)
    except ChatThread.DoesNotExist:
        return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_new_chat(request, match_id):
    try:
        match = Match.objects.get(id=match_id, user=request.user)
        
        thread, created = ChatThread.objects.get_or_create(
            user=request.user,
            celestial=match.celestial
        )
        
        content = request.data.get('content')
        if content:
            Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content,
                is_celestial=False
            )
            simulate_celestial_response(thread)
        
        return Response({
            'thread_id': thread.id,
            'created': created
        }, status=status.HTTP_201_CREATED)
    except Match.DoesNotExist:
        return Response({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)

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