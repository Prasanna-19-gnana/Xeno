import { useState, useEffect } from 'react';
import { 
  Send, 
  Sparkles, 
  Layers, 
  MessageSquare,
  Volume2,
  Calendar,
  AlertCircle,
  Plus
} from 'lucide-react';
import { api } from '../api';

const CHANNELS = ["SMS", "WhatsApp", "Email", "RCS"];

function Campaigns({ navigateToTab }) {
  const [campaigns, setCampaigns] = useState([]);
  const [segments, setSegments] = useState([]);
  
  // Form state
  const [name, setName] = useState('');
  const [selectedSegmentId, setSelectedSegmentId] = useState('');
  const [selectedChannel, setSelectedChannel] = useState('SMS');
  const [message, setMessage] = useState('');
  
  // AI message helper states
  const [aiGoal, setAiGoal] = useState('Bring them back with 20% discount');
  const [showAiHelper, setShowAiHelper] = useState(false);
  const [generatingMessage, setGeneratingMessage] = useState(false);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [sendingStates, setSendingStates] = useState({}); // Track which campaigns are sending
  const [error, setError] = useState(null); // Track UI errors
  const [campaignErrors, setCampaignErrors] = useState({}); // Track per-campaign errors

  const fetchCampaignsAndSegments = async () => {
    setLoading(true);
    try {
      const campRes = await api.getCampaigns();
      const segRes = await api.getSegments();
      
      if (campRes.status === 'success') setCampaigns(campRes.data);
      if (segRes.status === 'success') {
        setSegments(segRes.data);
        if (segRes.data.length > 0) {
          setSelectedSegmentId(segRes.data[0]._id);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCampaignsAndSegments();
  }, []);

  const handleGenerateAIMessage = async () => {
    if (!selectedSegmentId) {
      alert("Please select a target segment first so the AI knows who the message is for.");
      return;
    }
    const targetSegment = segments.find(s => s._id === selectedSegmentId);
    
    setGeneratingMessage(true);
    try {
      const response = await api.generateMessage({
        segment_name: targetSegment?.name || "Shoppers",
        channel: selectedChannel,
        goal: aiGoal
      });
      if (response.status === 'success') {
        setMessage(response.message);
        setShowAiHelper(false);
      }
    } catch (err) {
      alert("Failed to generate message: " + err.message);
    } finally {
      setGeneratingMessage(false);
    }
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    if (!name || !selectedSegmentId || !message) {
      setError("Please fill in all campaign fields.");
      return;
    }

    setSaving(true);
    setError(null); // Clear previous errors
    try {
      const response = await api.createCampaign({
        name,
        segment_id: selectedSegmentId,
        channel: selectedChannel,
        message
      });
      if (response.status === 'success') {
        // Clear fields
        setName('');
        setMessage('');
        await fetchCampaignsAndSegments();
        setError(null);
        alert("Campaign successfully drafted!");
      }
    } catch (err) {
      const errorMsg = err.message || "Failed to create campaign";
      setError(errorMsg);
      console.error("Campaign creation error:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleSendCampaign = async (campaignId) => {
    if (!window.confirm("Send this campaign? This will start delivering simulated receipts to the fake channel service asynchronously.")) {
      return;
    }
    
    setSendingStates(prev => ({ ...prev, [campaignId]: true }));
    setCampaignErrors(prev => ({ ...prev, [campaignId]: null })); // Clear previous errors
    try {
      const response = await api.sendCampaign(campaignId);
      if (response.status === 'success') {
        setError(null); // Clear any general errors
        // Refresh campaigns to show updated status
        await fetchCampaignsAndSegments();
        alert(response.message || "Sending started!");
        // Instantly redirect to analytics page for this campaign
        navigateToTab('analytics', campaignId);
      }
    } catch (err) {
      const errorMsg = err.message || "Failed to send campaign";
      setCampaignErrors(prev => ({ ...prev, [campaignId]: errorMsg }));
      console.error("Campaign send error:", err);
    } finally {
      setSendingStates(prev => ({ ...prev, [campaignId]: false }));
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="header-actions">
        <div>
          <h1 className="section-title">Campaigns</h1>
          <p className="section-subtitle">Draft, personalize, and launch marketing outreach campaigns</p>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div style={{ 
          marginBottom: '24px', 
          padding: '16px', 
          borderRadius: '8px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: '#fca5a5'
        }}>
          <AlertCircle size={18} />
          <div style={{ flex: 1 }}>
            <p style={{ fontWeight: '600', marginBottom: '2px' }}>Error</p>
            <p style={{ fontSize: '13px' }}>{error}</p>
          </div>
          <button 
            onClick={() => setError(null)}
            style={{ background: 'none', border: 'none', color: '#fca5a5', cursor: 'pointer', fontSize: '18px' }}
          >
            ×
          </button>
        </div>
      )}

      {/* AI shortcuts */}
      <div className="glass-card" style={{ marginBottom: '24px', border: '1px solid rgba(139,92,246,0.2)', background: 'rgba(139,92,246,0.03)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '18px', marginBottom: '6px' }}>
              <Sparkles size={18} style={{ color: '#c084fc' }} />
              AI Campaign Workbench
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', maxWidth: '720px', lineHeight: '1.6' }}>
              Draft copy with the AI helper here, or jump straight to the TrendBot copilot to generate a segment + campaign draft in one conversation.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button className="btn btn-secondary" onClick={() => navigateToTab('ai-assistant')}>
              <MessageSquare size={16} />
              <span>Ask TrendBot</span>
            </button>
            <button className="btn btn-secondary" onClick={() => navigateToTab('segments')}>
              <Layers size={16} />
              <span>Find a Segment</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Create form vs. Past campaigns list */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '32px' }}>
        
        {/* Create Campaign Card */}
        <div className="glass-card" style={{ height: 'fit-content' }}>
          <h3 style={{ marginBottom: '16px' }}>New Campaign</h3>
          
          <form onSubmit={handleCreateCampaign}>
            
            {/* Campaign Name */}
            <div className="form-group">
              <label>Campaign Name</label>
              <input 
                type="text" 
                className="form-control" 
                placeholder="e.g. Summer Dress Sale"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            {/* Target Segment */}
            <div className="form-group">
              <label>Target Segment</label>
              {segments.length === 0 ? (
                <div style={{ fontSize: '13px', color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
                  <AlertCircle size={16} />
                  <span>No segments found. Save a segment first!</span>
                </div>
              ) : (
                <select 
                  className="form-control" 
                  value={selectedSegmentId} 
                  onChange={(e) => setSelectedSegmentId(e.target.value)}
                >
                  {segments.map(s => (
                    <option key={s._id} value={s._id}>
                      {s.name} ({s.customer_count} shoppers)
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Outreach Channel */}
            <div className="form-group">
              <label>Outreach Channel</label>
              <select 
                className="form-control" 
                value={selectedChannel} 
                onChange={(e) => setSelectedChannel(e.target.value)}
              >
                {CHANNELS.map(ch => <option key={ch} value={ch}>{ch}</option>)}
              </select>
            </div>

            {/* Copy message with AI Generator */}
            <div className="form-group" style={{ position: 'relative' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <label>Message Content</label>
                <button 
                  type="button"
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '4px 10px', fontSize: '12px', border: '1px solid rgba(139,92,246,0.3)', color: '#c084fc', background: 'rgba(139,92,246,0.05)' }}
                  onClick={() => setShowAiHelper(!showAiHelper)}
                >
                  <Sparkles size={12} />
                  <span>AI Copywriter</span>
                </button>
              </div>

              {/* AI Helper settings expanded */}
              {showAiHelper && (
                <div style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', padding: '12px', borderRadius: '8px', marginBottom: '12px', fontSize: '12px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div>
                      <span style={{ color: 'var(--text-secondary)', fontWeight: '600' }}>Goal of copy:</span>
                      <input 
                        type="text" 
                        className="form-control" 
                        style={{ padding: '6px', fontSize: '12px', width: '100%', marginTop: '4px' }}
                        value={aiGoal}
                        onChange={(e) => setAiGoal(e.target.value)}
                      />
                    </div>
                    <button 
                      type="button" 
                      className="btn btn-primary btn-sm" 
                      style={{ padding: '6px 12px', fontSize: '11px', width: '100%' }}
                      onClick={handleGenerateAIMessage}
                      disabled={generatingMessage}
                    >
                      {generatingMessage ? 'Generating...' : 'Generate Personalized Message'}
                    </button>
                  </div>
                </div>
              )}

              <textarea 
                className="form-control" 
                placeholder="Write message copy. Tip: Use {{name}} to personalize with client names. (e.g. Hi {{name}}!)"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
              />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                Tip: The system automatically replaces `{"{{name}}"}` with the shopper's name when sending.
              </span>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%', gap: '8px', marginTop: '12px' }}
              disabled={saving || segments.length === 0}
            >
              <Plus size={16} />
              <span>{saving ? 'Creating Draft...' : 'Create Campaign'}</span>
            </button>
          </form>
        </div>

        {/* Campaign List */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '16px' }}>Campaign History</h3>
          
          {loading ? (
            <div className="page-loading-wrapper">
              <div className="spinner"></div>
            </div>
          ) : campaigns.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              No campaigns created yet. Draft your first campaign in the form.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {campaigns.map((camp) => (
                <div 
                  key={camp._id} 
                  style={{ 
                    padding: '20px', 
                    borderRadius: '12px', 
                    background: 'rgba(255,255,255,0.02)', 
                    border: '1px solid var(--border-color)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h4 style={{ fontSize: '16px', fontWeight: '700' }}>{camp.name}</h4>
                      <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Calendar size={12} />
                        <span>Created: {camp.created_at}</span>
                      </p>
                    </div>
                    <span className={`status-badge ${camp.status?.toLowerCase()}`}>
                      {camp.status}
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', background: 'rgba(0,0,0,0.1)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '12px' }}>
                    <div>
                      <span style={{ color: 'var(--text-secondary)' }}>Target segment:</span>
                      <p style={{ fontWeight: '600', marginTop: '2px', color: '#c084fc', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Layers size={12} />
                        <span>{camp.segment_name}</span>
                      </p>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-secondary)' }}>Channel:</span>
                      <p style={{ fontWeight: '600', marginTop: '2px', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <MessageSquare size={12} />
                        <span>{camp.channel}</span>
                      </p>
                    </div>
                  </div>

                  <div style={{ background: 'rgba(255,255,255,0.01)', border: '1px dashed var(--border-color)', padding: '12px', borderRadius: '8px', fontSize: '13px' }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '11px', display: 'block', marginBottom: '4px' }}>Message Template:</span>
                    <p style={{ fontStyle: 'italic', lineHeight: '1.4' }}>"{camp.message}"</p>
                  </div>

                  {campaignErrors[camp._id] && (
                    <div style={{ 
                      background: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      padding: '12px',
                      borderRadius: '8px',
                      fontSize: '12px',
                      color: '#fca5a5',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <AlertCircle size={14} />
                      <span>{campaignErrors[camp._id]}</span>
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '12px', marginTop: '4px' }}>
                    {camp.status === 'created' ? (
                      <button 
                        className="btn btn-primary"
                        style={{ padding: '8px 16px', flex: '1' }}
                        onClick={() => handleSendCampaign(camp._id)}
                        disabled={sendingStates[camp._id]}
                      >
                        <Send size={14} />
                        <span>{sendingStates[camp._id] ? 'Sending...' : 'Send Campaign'}</span>
                      </button>
                    ) : (
                      <button 
                        className="btn btn-secondary"
                        style={{ padding: '8px 16px', flex: '1', border: '1px solid rgba(139,92,246,0.3)', color: '#c084fc', background: 'rgba(139,92,246,0.03)' }}
                        onClick={() => navigateToTab('analytics', camp._id)}
                      >
                        <Volume2 size={14} />
                        <span>View Delivery Analytics</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default Campaigns;
