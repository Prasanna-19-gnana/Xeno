import { useState, useEffect } from 'react';
import { 
  Users, 
  ShoppingBag, 
  TrendingUp, 
  Send, 
  DollarSign, 
  ArrowRight,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { api } from '../api';

function Dashboard({ navigateToTab }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async (showRefreshIndicator = false) => {
    if (showRefreshIndicator) setRefreshing(true);
    else setLoading(true);
    
    try {
      const response = await api.getDashboardStats();
      if (response.status === 'success') {
        setStats(response.data);
        setError(null);
      } else {
        setError(response.message || 'Failed to fetch dashboard statistics.');
      }
    } catch (err) {
      console.error(err);
      setError('Could not connect to backend server. Make sure Flask is running.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="page-loading-wrapper">
        <div className="spinner"></div>
      </div>
    );
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  const recentCampaigns = stats?.recent_campaigns || [];
  
  return (
    <div>
      {/* Header */}
      <div className="header-actions">
        <div>
          <h1 className="section-title">Overview</h1>
          <p className="section-subtitle">Real-time performance metrics for TrendWear</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            className="btn btn-secondary" 
            onClick={() => fetchStats(true)}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spin' : ''} />
            <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => navigateToTab('ai-assistant')}
          >
            <Sparkles size={16} />
            <span>Ask AI Copilot</span>
          </button>
        </div>
      </div>

      {error && (
        <div style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '12px', color: '#f87171', marginBottom: '24px' }}>
          {error}
        </div>
      )}

      {/* AI Command Center */}
      <div className="glass-card" style={{ marginBottom: '24px', border: '1px solid rgba(139,92,246,0.28)', background: 'linear-gradient(135deg, rgba(139,92,246,0.10), rgba(236,72,153,0.06))' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '16px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 10px', borderRadius: '999px', background: 'rgba(139,92,246,0.16)', color: '#e9d5ff', fontSize: '12px', fontWeight: '700', marginBottom: '12px' }}>
              <Sparkles size={14} />
              AI Command Center
            </div>
            <h3 style={{ fontSize: '20px', marginBottom: '8px' }}>Run AI-assisted CRM actions from one place</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', maxWidth: '760px', lineHeight: '1.6' }}>
              Generate campaign copy, suggest high-value segments, and chat with TrendBot to build a campaign draft without leaving the dashboard.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={() => navigateToTab('ai-assistant')}>
              <Sparkles size={16} />
              <span>Open AI Copilot</span>
            </button>
            <button className="btn btn-secondary" onClick={() => navigateToTab('campaigns')}>
              <Send size={16} />
              <span>AI Copywriter</span>
            </button>
            <button className="btn btn-secondary" onClick={() => navigateToTab('segments')}>
              <Users size={16} />
              <span>AI Suggest Segments</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="kpi-grid">
        {/* Card 1: Total Customers */}
        <div className="glass-card kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">TOTAL SHOPPERS</span>
            <div className="kpi-icon-wrapper" style={{ color: '#8b5cf6' }}>
              <Users size={20} />
            </div>
          </div>
          <span className="kpi-value">{stats?.total_customers?.toLocaleString() || 0}</span>
          <div className="kpi-change" style={{ color: '#10b981' }}>
            <TrendingUp size={14} />
            <span>Active Reach</span>
          </div>
        </div>

        {/* Card 2: Total Orders */}
        <div className="glass-card kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">TOTAL ORDERS</span>
            <div className="kpi-icon-wrapper" style={{ color: '#ec4899' }}>
              <ShoppingBag size={20} />
            </div>
          </div>
          <span className="kpi-value">{stats?.total_orders?.toLocaleString() || 0}</span>
          <div className="kpi-change" style={{ color: '#10b981' }}>
            <TrendingUp size={14} />
            <span>Attributed Conversion</span>
          </div>
        </div>

        {/* Card 3: Total Revenue */}
        <div className="glass-card kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">TOTAL REVENUE</span>
            <div className="kpi-icon-wrapper" style={{ color: '#06b6d4' }}>
              <DollarSign size={20} />
            </div>
          </div>
          <span className="kpi-value" style={{ fontSize: '24px' }}>
            {formatCurrency(stats?.total_revenue || 0)}
          </span>
          <div className="kpi-change" style={{ color: '#10b981' }}>
            <TrendingUp size={14} />
            <span>Life-time Gross</span>
          </div>
        </div>

        {/* Card 4: Average Order Value */}
        <div className="glass-card kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">AVG ORDER VALUE</span>
            <div className="kpi-icon-wrapper" style={{ color: '#10b981' }}>
              <TrendingUp size={20} />
            </div>
          </div>
          <span className="kpi-value" style={{ fontSize: '24px' }}>
            {formatCurrency(stats?.average_order_value || 0)}
          </span>
          <div className="kpi-change" style={{ color: '#10b981' }}>
            <span>Per Transaction</span>
          </div>
        </div>

        {/* Card 5: Total Campaigns */}
        <div className="glass-card kpi-card">
          <div className="kpi-header">
            <span className="kpi-label">CAMPAIGNS</span>
            <div className="kpi-icon-wrapper" style={{ color: '#f59e0b' }}>
              <Send size={20} />
            </div>
          </div>
          <span className="kpi-value">{stats?.total_campaigns || 0}</span>
          <div className="kpi-change" style={{ color: '#6b7280' }}>
            <span>Dispatched</span>
          </div>
        </div>
      </div>

      {/* Main Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        
        {/* Campaign Performance Chart Card */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '6px', fontSize: '18px' }}>Campaign Performance</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '24px' }}>
            Funnel conversion metrics (%) of the last 5 campaigns
          </p>
          
          {recentCampaigns.length === 0 ? (
            <div style={{ height: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: '16px' }}>
              <p style={{ color: 'var(--text-muted)' }}>No campaigns sent yet.</p>
              <button 
                className="btn btn-primary btn-sm"
                onClick={() => navigateToTab('campaigns')}
              >
                Create Campaign
              </button>
            </div>
          ) : (
            <div>
              {/* Custom SVG/HTML Bar Chart */}
              <div className="chart-container">
                {recentCampaigns.map((camp) => {
                  const delivered = camp.delivered || 0;
                  // Calculate funnel percentages relative to delivered (standard marketing practice)
                  const openRate = delivered > 0 ? Math.round((camp.opened / delivered) * 100) : 0;
                  const clickRate = delivered > 0 ? Math.round((camp.clicked / delivered) * 100) : 0;
                  const convRate = delivered > 0 ? Math.round((camp.converted / delivered) * 100) : 0;

                  return (
                    <div key={camp.id} className="chart-bar-wrapper">
                      {/* Bar Group container */}
                      <div style={{ display: 'flex', gap: '4px', alignItems: 'flex-end', height: '100%', width: '100%' }}>
                        
                        {/* Open Rate Bar (Indigo) */}
                        <div 
                          className="chart-bar" 
                          style={{ 
                            height: `${openRate}%`, 
                            background: 'linear-gradient(to top, #4f46e5, #818cf8)',
                            opacity: 0.95
                          }}
                          title={`Open Rate: ${openRate}% (${camp.opened}/${delivered})`}
                        >
                          {openRate > 15 && <span className="chart-bar-value">{openRate}%</span>}
                        </div>
                        
                        {/* Click Rate Bar (Cyan) */}
                        <div 
                          className="chart-bar" 
                          style={{ 
                            height: `${clickRate}%`, 
                            background: 'linear-gradient(to top, #0891b2, #22d3ee)',
                            opacity: 0.95
                          }}
                          title={`Click Rate: ${clickRate}% (${camp.clicked}/${delivered})`}
                        >
                          {clickRate > 15 && <span className="chart-bar-value">{clickRate}%</span>}
                        </div>

                        {/* Conversion Rate Bar (Rose) */}
                        <div 
                          className="chart-bar" 
                          style={{ 
                            height: `${convRate}%`, 
                            background: 'linear-gradient(to top, #db2777, #f472b6)',
                            opacity: 0.95
                          }}
                          title={`Conversion Rate: ${convRate}% (${camp.converted}/${delivered})`}
                        >
                          {convRate > 15 && <span className="chart-bar-value">{convRate}%</span>}
                        </div>
                        
                      </div>
                      
                      {/* Campaign Name Label */}
                      <span className="chart-bar-label" title={camp.name}>
                        {camp.name.length > 12 ? `${camp.name.slice(0, 10)}...` : camp.name}
                      </span>
                    </div>
                  );
                })}
              </div>
              
              {/* Chart Legend */}
              <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', marginTop: '24px', fontSize: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#6366f1' }}></div>
                  <span style={{ color: 'var(--text-secondary)' }}>Open Rate</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#06b6d4' }}></div>
                  <span style={{ color: 'var(--text-secondary)' }}>Click Rate</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#ec4899' }}></div>
                  <span style={{ color: 'var(--text-secondary)' }}>Conversion Rate</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Recent Campaigns List Card */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginBottom: '16px', fontSize: '18px' }}>Recent Campaigns</h3>
          
          {recentCampaigns.length === 0 ? (
            <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No campaigns sent yet.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1 }}>
              {recentCampaigns.map((camp) => (
                <div 
                  key={camp.id} 
                  style={{ 
                    display: 'flex', 
                    justifyContent: 'between', 
                    alignItems: 'center', 
                    padding: '12px 16px', 
                    background: 'rgba(255,255,255,0.02)', 
                    borderRadius: '10px',
                    border: '1px solid var(--border-color)',
                    cursor: 'pointer'
                  }}
                  onClick={() => navigateToTab('analytics', camp.id)}
                >
                  <div style={{ flex: 1 }}>
                    <p style={{ fontWeight: '600', fontSize: '14px', marginBottom: '2px' }}>{camp.name}</p>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <span className="status-badge" style={{ fontSize: '10px', padding: '2px 6px' }}>
                        {camp.channel}
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                        Audience: {camp.sent}
                      </span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-primary)' }}>
                    <span style={{ fontSize: '12px', fontWeight: '500' }}>View</span>
                    <ArrowRight size={14} />
                  </div>
                </div>
              ))}
              
              <button 
                className="btn btn-secondary btn-sm" 
                style={{ marginTop: 'auto', width: '100%' }}
                onClick={() => navigateToTab('analytics')}
              >
                View All Analytics
              </button>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default Dashboard;
