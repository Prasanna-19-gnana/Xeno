import { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  Send, 
  Bot, 
  User, 
  Bookmark
} from 'lucide-react';
import { api } from '../api';

function AIAssistant({ navigateToTab }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I am **TrendBot**, your TrendWear marketing copilot. I can analyze database stats, suggest target audience segments, write personalized copywriting, or configure whole campaign runs from scratch.\n\nTry asking me something like:\n* *'Create a campaign to win back inactive shoppers.'*\n* *'How can I target shoe buyers in Chennai?'*\n* *'Suggest a segment for accessories frequent buyers.'*",
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [creatingCampaign, setCreatingCampaign] = useState(false);
  
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input;
    setInput('');
    
    // Add user message
    const userMsgId = 'msg_' + Date.now();
    setMessages(prev => [
      ...prev,
      { id: userMsgId, sender: 'user', text: userText }
    ]);
    
    setLoading(true);
    try {
      const response = await api.askAssistant(userText);
      if (response.status === 'success') {
        const aiData = response.data;
        
        // Add assistant message
        setMessages(prev => [
          ...prev,
          { 
            id: 'msg_ai_' + Date.now(), 
            sender: 'assistant', 
            text: aiData.reply,
            suggestedCampaign: aiData.suggested_campaign 
          }
        ]);
      } else {
        setMessages(prev => [
          ...prev,
          { 
            id: 'msg_err_' + Date.now(), 
            sender: 'assistant', 
            text: "I encountered an error trying to process that request: " + response.message 
          }
        ]);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        { 
          id: 'msg_err_' + Date.now(), 
          sender: 'assistant', 
          text: "I couldn't reach the CRM AI server. Please verify the Flask backend is running and GEMINI_API_KEY is configured." 
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Instantiates the campaign and segment in the DB from the suggestion card
  const handleInstantiateCampaign = async (campaign) => {
    setCreatingCampaign(true);
    try {
      // 1. Create the segment first
      const segRes = await api.createSegment({
        name: campaign.segment_name || `${campaign.name} Target Group`,
        rules: campaign.rules || {}
      });
      
      if (segRes.status === 'success') {
        const segmentId = segRes.data._id;
        
        // 2. Create the campaign linked to this segment
        const campRes = await api.createCampaign({
          name: campaign.name,
          segment_id: segmentId,
          channel: campaign.channel,
          message: campaign.message
        });
        
        if (campRes.status === 'success') {
          alert(`Success! Generated segment "${segRes.data.name}" and campaign "${campRes.data.name}" in draft state. Redirecting you to Campaigns to send.`);
          navigateToTab('campaigns');
        }
      }
    } catch (err) {
      alert("Failed to build campaign from suggestion: " + err.message);
    } finally {
      setCreatingCampaign(false);
    }
  };

  // Helper to render markdown bold elements in chat messages
  const renderMessageText = (text) => {
    if (!text) return '';
    
    // Simple bold parse: **text**
    const parts = text.split(/\*\*([^*]+)\*\*/g);
    return parts.map((part, index) => {
      // Every odd element was matched within **
      if (index % 2 === 1) {
        return <strong key={index} style={{ color: '#c084fc' }}>{part}</strong>;
      }
      
      // Simple bullet parsing
      if (part.startsWith('\n* ') || part.startsWith('\n- ')) {
        const items = part.split(/\n[*|-]\s+/).filter(Boolean);
        return (
          <ul key={index} style={{ paddingLeft: '20px', margin: '8px 0' }}>
            {items.map((item, i) => <li key={i} style={{ marginBottom: '4px' }}>{item}</li>)}
          </ul>
        );
      }

      return part;
    });
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Header */}
      <div className="header-actions" style={{ marginBottom: '24px' }}>
        <div>
          <h1 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles size={28} className="text-gradient" />
            <span>AI Copilot</span>
          </h1>
          <p className="section-subtitle">Chat with TrendBot to automate segmentations and copywriting</p>
        </div>
      </div>

      {/* Chat Container */}
      <div className="glass-card chat-container" style={{ padding: '0px' }}>
        
        {/* Chat Window */}
        <div className="chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`chat-message ${msg.sender}`}>
              
              {/* Message Header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', fontSize: '11px', color: 'var(--text-secondary)' }}>
                {msg.sender === 'assistant' ? (
                  <>
                    <Bot size={14} style={{ color: '#8b5cf6' }} />
                    <span style={{ fontWeight: '700' }}>TrendBot</span>
                  </>
                ) : (
                  <>
                    <User size={14} style={{ color: '#ec4899' }} />
                    <span style={{ fontWeight: '700' }}>Marketer</span>
                  </>
                )}
              </div>
              
              {/* Body */}
              <div style={{ fontSize: '14px', whiteSpace: 'pre-line', wordBreak: 'break-word', color: 'var(--text-primary)' }}>
                {renderMessageText(msg.text)}
              </div>
              
              {/* Suggested Campaign Action Card */}
              {msg.suggestedCampaign && (
                <div className="chat-suggested-action">
                  <div className="chat-suggested-info">
                    <span className="chat-suggested-title">
                      {msg.suggestedCampaign.name}
                    </span>
                    <span className="chat-suggested-desc">
                      Targeting: {msg.suggestedCampaign.segment_name} via {msg.suggestedCampaign.channel?.toUpperCase()}
                    </span>
                    <div style={{ background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '6px', fontSize: '11px', fontStyle: 'italic', border: '1px solid var(--border-color)', marginTop: '6px' }}>
                      "{msg.suggestedCampaign.message}"
                    </div>
                  </div>
                  
                  <button 
                    className="btn btn-primary btn-sm" 
                    style={{ flexShrink: 0, padding: '8px 12px', fontSize: '12px' }}
                    onClick={() => handleInstantiateCampaign(msg.suggestedCampaign)}
                    disabled={creatingCampaign}
                  >
                    <Bookmark size={12} />
                    <span>{creatingCampaign ? 'Building...' : 'Create Draft'}</span>
                  </button>
                </div>
              )}

            </div>
          ))}

          {/* Typing Indicator */}
          {loading && (
            <div className="chat-message assistant">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', fontSize: '11px', color: 'var(--text-secondary)' }}>
                <Bot size={14} style={{ color: '#8b5cf6' }} />
                <span style={{ fontWeight: '700' }}>TrendBot</span>
              </div>
              <div style={{ display: 'flex', gap: '4px', padding: '8px' }}>
                <span className="pulse-dot" style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#6b7280', animation: 'spin 1.4s infinite' }}></span>
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Analyzing request...</span>
              </div>
            </div>
          )}
          
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <form onSubmit={handleSend} className="chat-input-area">
          <input 
            type="text" 
            className="form-control" 
            placeholder="Ask AI to suggest segmentations or write copy..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ padding: '12px 20px' }}
            disabled={loading || !input.trim()}
          >
            <Send size={16} />
          </button>
        </form>

      </div>
    </div>
  );
}

export default AIAssistant;
