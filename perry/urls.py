from django.urls import path
from .views import (
    swipe,
    chat_threads,
    potential_chats,
    chat_messages,
    send_message,
    start_new_chat
)

urlpatterns = [
    path('swipe/', swipe, name='swipe'),
    path('chat/threads/', chat_threads, name='chat-threads'),
    path('chat/potential/', potential_chats, name='potential-chats'),
    path('chat/messages/<int:thread_id>/', chat_messages, name='chat-messages'),
    path('chat/send/<int:thread_id>/', send_message, name='send-message'),
    path('chat/start/<int:match_id>/', start_new_chat, name='start-chat'),
]