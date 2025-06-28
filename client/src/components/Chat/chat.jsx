import React, { useState, useEffect, useRef } from 'react';
import './chatpage.css';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'star', text: 'Hey there, Ready to orbit around me?' },
  ]);
  const [newMessage, setNewMessage] = useState('');
  const userType = 'planet'; // Fixed userType — no switching
  const messagesEndRef = useRef(null);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() === '') return;
    const newMsg = {
      id: messages.length + 1,
      sender: userType,
      text: newMessage,
    };
    setMessages([...messages, newMsg]);
    setNewMessage('');
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="cosmic-chat-wrapper">
      <div className="shooting-star"></div>
      <div className="shooting-star"></div>
      <div className="shooting-star"></div>

      <aside className="sidebar">
        <h1>COSMICMATCH</h1>
        <p className="tagline">🌟 Talk to stars. Orbit planets. Find your cosmic match.</p>
        {/* Removed role selector */}
      </aside>

      <main className="chat-area">
        <div className="chat-messages">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.sender === userType ? 'sent' : 'received'}`}
            >
              <div className={`message-bubble ${message.sender}`}>
                {message.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form className="message-input" onSubmit={handleSendMessage}>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={`Message as a ${userType}...`}
          />
          <button type="submit">Send</button>
        </form>
      </main>
    </div>
  );
};

export default ChatPage;


