import { useState, useEffect, useRef } from 'react';
import { 
  BarChart3, 
  RefreshCw, 
  Send, 
  CheckCircle, 
  Eye, 
  MousePointerClick, 
  Award,
  AlertCircle,
  TrendingUp,
  IndianRupee
} from 'lucide-react';
import { api } from '../api';

function Analytics({ campaignId, setSelectedCampaignId, navigateToTab }) {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedId, setSelectedId] = useState(campaignId || '');
  const [stats, setStats] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  
  const pollTimerRef = useRef(null);

  const fetchStats = async (showIndicator = true) => {
    if (!selectedId) return;
    if (showIndicator) setRefreshing(true);
    
    try {
      const res = await api.getCampaignStats(selectedId);
      if (res.status === 'success') {
        setStats(res);
        setError(null);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch campaign stats.');
    } finally {
      if (showIndicator) setRefreshing(false);
    }
  };

  const stopPolling = () => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  };

  const startPolling = () => {
    stopPolling();
    fetchStats(false);
    
    // Poll every 2 seconds to watch active delivery callbacks flow
    pollTimerRef.current = setInterval(() => {
      fetchStats(false);
    }, 2000);
  };

  // Fetch campaign list on mount
  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const res = await api.getCampaigns();
        if (res.status === 'success') {
          // Filter to show only campaigns that are not draft
          const sentCampaigns = res.data.filter(c => c.status !== 'created');
          setCampaigns(sentCampaigns);
          
          // If we had a campaignId passed in, select it
          if (campaignId) {
            setSelectedId(campaignId);
          } else if (sentCampaigns.length > 0 && !selectedId) {
            setSelectedId(sentCampaigns[0]._id);
          }
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchCampaigns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [campaignId]);

  // Handle selected campaign change
  useEffect(() => {
    if (selectedId) {
      fetchStats(false);
      
      // Start live polling to watch fake channel callbacks arrive
      startPolling();
    } else {
      setStats(null);
      stopPolling();
    }

    return () => stopPolling();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  // Clean up timer on unmount
  useEffect(() => {
    return () => stopPolling();
  }, []);

  const handleCampaignChange = (e) => {
    const newId = e.target.value;
    setSelectedId(newId);
    if (setSelectedCampaignId) {
      setSelectedCampaignId(newId); // Keep App state in sync
    }
  };

  const formatPercent = (count, base) => {
    if (!base) return '0%';
    return `${Math.round((count / base) * 100)}%`;
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  // Calculate funnel stages widths
  const funnel = stats?.funnel;
  const sent = funnel?.sent || 0;
  const attribution = stats?.attribution || {};
  const rates = stats?.rates || {};
  
  // Width percentages relative to sent (audience size) to taper down
  const getWidth = (count) => {
    if (!sent) return '0%';
    return `${(count / sent) * 100}%`;
  };

  return (
    <div>
      {/* Header */}
      <div className="header-actions">
        <div>
          <h1 className="section-title">Campaign Analytics</h1>
          <p className="section-subtitle">Monitor outreach delivery funnels and attributed revenue</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          
          {/* Campaign Selector dropdown */}
          <select 
            className="form-control" 
            value={selectedId} 
            onChange={handleCampaignChange}
            style={{ minWidth: '220px', padding: '10px 16px' }}
          >
            <option value="">-- Select Active Campaign --</option>
            {campaigns.map(c => (
              <option key={c._id} value={c._id}>
                {c.name} ({c.channel})
              </option>
            ))}
          </select>

          <button 
            className="btn btn-secondary" 
            onClick={() => fetchStats(true)}
            disabled={!selectedId || refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spin' : ''} />
            <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '12px', color: '#f87171', marginBottom: '24px' }}>
          {error}
        </div>
      )}

      {!selectedId ? (
        <div className="glass-card" style={{ padding: '80px', textAlignment: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
          <BarChart3 size={48} style={{ color: 'var(--text-muted)' }} />
          <h3 style={{ color: 'var(--text-secondary)' }}>No Active Campaigns Selected</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
            Select an active campaign from the dropdown above, or draft one in the campaigns tab.
          </p>
          <button className="btn btn-primary" onClick={() => navigateToTab('campaigns')}>
            Draft a Campaign
          </button>
        </div>
      ) : !stats ? (
        <div className="page-loading-wrapper">
          <div className="spinner"></div>
        </div>
      ) : (
        <div>
          {/* KPI Strip */}
          <div className="kpi-grid" style={{ marginBottom: '24px' }}>
            <div className="glass-card kpi-card">
              <div className="kpi-header">
                <span className="kpi-label">DELIVERY RATE</span>
                <div className="kpi-icon-wrapper" style={{ color: '#10b981' }}>
                  <TrendingUp size={20} />
                </div>
              </div>
              <span className="kpi-value" style={{ fontSize: '24px' }}>{rates.delivery_rate || 0}%</span>
              <div className="kpi-change" style={{ color: '#10b981' }}>
                <span>{funnel?.delivered || 0}/{funnel?.sent || 0} delivered</span>
              </div>
            </div>
            <div className="glass-card kpi-card">
              <div className="kpi-header">
                <span className="kpi-label">OPEN RATE</span>
                <div className="kpi-icon-wrapper" style={{ color: '#06b6d4' }}>
                  <Eye size={20} />
                </div>
              </div>
              <span className="kpi-value" style={{ fontSize: '24px' }}>{rates.open_rate || 0}%</span>
              <div className="kpi-change" style={{ color: '#10b981' }}>
                <span>Of delivered messages</span>
              </div>
            </div>
            <div className="glass-card kpi-card">
              <div className="kpi-header">
                <span className="kpi-label">CLICK RATE</span>
                <div className="kpi-icon-wrapper" style={{ color: '#8b5cf6' }}>
                  <MousePointerClick size={20} />
                </div>
              </div>
              <span className="kpi-value" style={{ fontSize: '24px' }}>{rates.click_rate || 0}%</span>
              <div className="kpi-change" style={{ color: '#10b981' }}>
                <span>Of opened messages</span>
              </div>
            </div>
            <div className="glass-card kpi-card">
              <div className="kpi-header">
                <span className="kpi-label">ATTRIBUTED REVENUE</span>
                <div className="kpi-icon-wrapper" style={{ color: '#f59e0b' }}>
                  <IndianRupee size={20} />
                </div>
              </div>
              <span className="kpi-value" style={{ fontSize: '24px' }}>{formatCurrency(attribution.revenue || 0)}</span>
              <div className="kpi-change" style={{ color: '#10b981' }}>
                <span>{attribution.orders || 0} attributed orders</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '32px' }}>
          
          {/* Funnel Display Column */}
          <div className="glass-card" style={{ height: 'fit-content' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3>Conversion Funnel</h3>
              <span style={{ fontSize: '11px', background: 'rgba(16, 185, 129, 0.1)', color: '#34d399', border: '1px solid rgba(16,185,129,0.2)', padding: '2px 8px', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span className="pulse-dot" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }}></span>
                Live Polling Active
              </span>
            </div>
            
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
              Outreach funnel for <strong>{stats.campaign_name}</strong> sent via <strong>{stats.channel.toUpperCase()}</strong>.
            </p>

            <div className="funnel-container">
              
              {/* Sent */}
              <div className="funnel-stage">
                <div className="funnel-bar" style={{ width: '100%' }}></div>
                <div className="funnel-stage-content">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Send size={14} />
                    <span>Sent / Targeted</span>
                  </div>
                  <span>{funnel.sent}</span>
                </div>
              </div>

              {/* Delivered */}
              <div className="funnel-stage">
                <div className="funnel-bar" style={{ width: getWidth(funnel.delivered) }}></div>
                <div className="funnel-stage-content">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle size={14} />
                    <span>Delivered</span>
                  </div>
                  <span>
                    {funnel.delivered} <span className="funnel-percent">({formatPercent(funnel.delivered, funnel.sent)})</span>
                  </span>
                </div>
              </div>

              {/* Opened */}
              <div className="funnel-stage">
                <div className="funnel-bar" style={{ width: getWidth(funnel.opened) }}></div>
                <div className="funnel-stage-content">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Eye size={14} />
                    <span>Opened</span>
                  </div>
                  <span>
                    {funnel.opened} <span className="funnel-percent">({formatPercent(funnel.opened, funnel.delivered)} of deliv.)</span>
                  </span>
                </div>
              </div>

              {/* Clicked */}
              <div className="funnel-stage">
                <div className="funnel-bar" style={{ width: getWidth(funnel.clicked) }}></div>
                <div className="funnel-stage-content">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <MousePointerClick size={14} />
                    <span>Clicked</span>
                  </div>
                  <span>
                    {funnel.clicked} <span className="funnel-percent">({formatPercent(funnel.clicked, funnel.opened)} of open)</span>
                  </span>
                </div>
              </div>

              {/* Converted */}
              <div className="funnel-stage converted">
                <div className="funnel-bar" style={{ width: getWidth(funnel.converted) }}></div>
                <div className="funnel-stage-content">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Award size={14} />
                    <span>Attributed Purchases</span>
                  </div>
                  <span style={{ color: '#f472b6' }}>
                    {funnel.converted} <span className="funnel-percent" style={{ color: '#f472b6' }}>({formatPercent(funnel.converted, funnel.clicked)} of click)</span>
                  </span>
                </div>
              </div>

              {/* Failed (Red alert bar) */}
              {funnel.failed > 0 && (
                <div className="funnel-stage failed" style={{ marginTop: '16px' }}>
                  <div className="funnel-bar" style={{ width: getWidth(funnel.failed) }}></div>
                  <div className="funnel-stage-content">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <AlertCircle size={14} />
                      <span>Failed / Undelivered</span>
                    </div>
                    <span style={{ color: '#f87171' }}>
                      {funnel.failed} <span className="funnel-percent" style={{ color: '#f87171' }}>({formatPercent(funnel.failed, funnel.sent)})</span>
                    </span>
                  </div>
                </div>
              )}

            </div>
          </div>

          {/* Granular Outbox Table Column */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ marginBottom: '6px' }}>Granular Delivery Log</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
              Real-time delivery progression status of the latest 50 recipients
            </p>

            <div style={{ flex: '1', overflowY: 'auto', maxHeight: '500px' }}>
              <div className="table-container" style={{ border: 'none', margin: '0' }}>
                <table className="modern-table">
                  <thead>
                    <tr>
                      <th>Recipient</th>
                      <th>Status</th>
                      <th>Lifecycle</th>
                      <th>Outreach Text</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.recent_communications?.length === 0 ? (
                      <tr>
                        <td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                          No logs recorded yet. Sending processes...
                        </td>
                      </tr>
                    ) : (
                      stats.recent_communications?.map((comm) => (
                        <tr key={comm._id} style={{ cursor: 'default' }}>
                          <td>
                            <div style={{ fontWeight: '600', fontSize: '13px' }}>{comm.customer_name}</div>
                            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>{comm.recipient}</div>
                          </td>
                          <td>
                            <span className={`status-badge ${comm.status?.toLowerCase()}`} style={{ fontSize: '10px', padding: '2px 6px' }}>
                              {comm.status}
                            </span>
                          </td>
                          <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                            {comm.events?.join(' → ') || 'sent'}
                          </td>
                          <td style={{ fontSize: '12px', fontStyle: 'italic', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={comm.message}>
                            "{comm.message}"
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

        </div>
        </div>
      )}
    </div>
  );
}

export default Analytics;
