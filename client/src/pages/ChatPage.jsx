import React, { useState, useEffect, useRef } from 'react';
import '../components/Chat/chat.css';


const ChatPage = () => {
  // Dummy data for now, representing matches that would appear after swiping
  const [matches, setMatches] = useState([
    { id: 'star_01', name: 'Star 01', emoji: '⭐' },
    { id: 'planet_01', name: 'Planet 01', emoji: '🪐' },
    { id: 'star_02', name: 'Star 02', emoji: '✨' },
    { id: 'planet_02', name: 'Planet 02', emoji: '🌎' },
  ]);

  const [currentChatPartner, setCurrentChatPartner] = useState(matches[0]);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null); 
  const chatMessagesRef = useRef(null); 
  const [showScrollToTop, setShowScrollToTop] = useState(false); 


  // This is function where the first message is comign from the matched partner
  const getInitialChatMessages = (partnerName) => {
    return [
      { id: 1, sender: partnerName, text: `Hello this is ${partnerName}, ready to connect?` },
    ];
  };

  // This is for when currentChatPartner changes
  useEffect(() => {
    if (currentChatPartner) {
      setMessages(getInitialChatMessages(currentChatPartner.name));
    } else {
      setMessages([]); 
    }
  }, [currentChatPartner]);


  useEffect(() => {
    const handleScroll = () => {
      if (chatMessagesRef.current) {
        // Show button if scrolled down only, otherwise, it's not visible by default
        setShowScrollToTop(chatMessagesRef.current.scrollTop > 200);
      }
    };

    const currentChatDiv = chatMessagesRef.current;
    if (currentChatDiv) {
      currentChatDiv.addEventListener('scroll', handleScroll);
    }

    // Clean up the event listener
    return () => {
      if (currentChatDiv) {
        currentChatDiv.removeEventListener('scroll', handleScroll);
      }
    };
  }, []); 

  // This is so that the screen displays the lastest msg when a new msg is sent/received
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() === '') return;
    const newMsg = {
      id: messages.length + 1,
      sender: 'human',
      text: newMessage,
    };
    setMessages((prevMessages) => [...prevMessages, newMsg]);
    setNewMessage('');
  };

  // Function to scroll to the top of the chat
  const scrollToTop = () => {
    chatMessagesRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // this is about the "About this match" button
  const handleAboutClick = () => {
    alert(`This is information about ${currentChatPartner?.name}:\n\n[Add more details here like interests, personality, etc.]`);
  };

  const handleUnmatch = () => {
      if (window.confirm(`Are you sure you want to unmatch with ${currentChatPartner?.name}? This action cannot be undone.`)) {
          alert(`You have unmatched with ${currentChatPartner?.name}.`);
          // i DID NOT add the logic to actually remove/unmatch since we havent writtern the code to even "match"
          // for NOW this will show an alert msg when the user decided to unmatch, but shud be updated with the correct code later ig
      }
  };


  return (
    <div className="cosmic-chat-wrapper">
      {/*for the video background BUT THERE'S NO VIDEO BACKGROUND ENABLED RN SO THIS FOR JUST INCASE:
      <video autoPlay loop muted playsInline className="background-video">
        <source src="path/for/background.mp4" type="video/mp4" /> 
        Your browser does not support the video tag.\
      </video>
      */}

      <aside className="sidebar">
        <div className="top-section">
            <h1>COSMICMATCH</h1>
            <div className="cosmic-match-line"></div>
            <button className="back-to-swiping-btn">Click here to go back to swiping</button>
        </div>

        <div className="middle-section">
            <h2 className="inbox-heading">Your recent inbox:</h2>

            <div className="user-list">
            {matches.map((match) => (
                <div
                key={match.id}
                className={`user-item ${currentChatPartner.id === match.id ? 'active' : ''}`}
                onClick={() => setCurrentChatPartner(match)}
                >
                <div className="pfp-icon">{match.emoji}</div>
                <span className="user-name">{match.name}</span>
                </div>
            ))}
            </div>
        </div>



      </aside>

      <main className="chat-area">
        <div className="chat-header">
            <h2 className="chat-partner-info">
                {currentChatPartner?.name || 'Select a Match'}
                <button className="info-button" onClick={handleAboutClick}>
                    ⓘ About this match
                </button>
            </h2>
            <button className="unmatch-button" onClick={handleUnmatch}>
                Unmatch
            </button>
        </div>

        <div className="chat-messages" ref={chatMessagesRef}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender === 'human' ? 'sent' : 'received'}`}
            >
              <div className={`message-bubble ${message.sender === 'human' ? 'sent' : 'received'}`}>
                {message.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>


          {/* Scroll to Top Button that is visible only when scrolled down */}
          {showScrollToTop && (
            <button className="scroll-to-top-button" onClick={scrollToTop}>
              ↑ {/*hm might change it to a fontsawesome icon cause this looks mid*/}
            </button>
          )}

        <form className="message-input" onSubmit={handleSendMessage}>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={"Type your msg"}
          />
          <button type="submit">Send</button>
        </form>
      </main>
    </div>
  );
};

//yey 

export default ChatPage;