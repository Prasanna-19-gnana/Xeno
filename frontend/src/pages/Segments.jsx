import { useState, useEffect } from 'react';
import { 
  Layers, 
  Sparkles, 
  User, 
  Eye, 
  Send, 
  Check, 
  X,
  PlusCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { api } from '../api';

const CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Kolkata", "Pune", "Ahmedabad"];
const CATEGORIES = ["T-Shirts", "Jeans", "Shoes", "Dresses", "Accessories"];

function Segments({ navigateToTab }) {
  const [segments, setSegments] = useState([]);
  const [name, setName] = useState('');
  
  // Rule builder form state
  const [rules, setRules] = useState({
    spend: { active: false, val: 5000 },
    orders: { active: false, val: 5 },
    city: { active: false, val: 'Chennai' },
    inactivity: { active: false, val: 30 },
    category: { active: false, val: 'Shoes' }
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // AI Suggestions state
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiExpanded, setAiExpanded] = useState(false);

  // Drawer to view segment customers
  const [activeSegmentId, setActiveSegmentId] = useState(null);
  const [segmentCustomers, setSegmentCustomers] = useState([]);
  const [segmentCustomersTotal, setSegmentCustomersTotal] = useState(0);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [drawerPage, setDrawerPage] = useState(1);
  const [drawerLimit] = useState(10);
  const [activeSegmentName, setActiveSegmentName] = useState('');

  const fetchSegments = async () => {
    setLoading(true);
    try {
      const response = await api.getSegments();
      if (response.status === 'success') {
        setSegments(response.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSegments();
  }, []);

  const handleRuleCheckboxChange = (field) => {
    setRules(prev => ({
      ...prev,
      [field]: { ...prev[field], active: !prev[field].active }
    }));
  };

  const handleRuleValChange = (field, value) => {
    setRules(prev => ({
      ...prev,
      [field]: { ...prev[field], val: value }
    }));
  };

  const compileActiveRules = () => {
    const activeRules = {};
    if (rules.spend.active) activeRules.total_spend_gt = rules.spend.val;
    if (rules.orders.active) activeRules.total_orders_gte = rules.orders.val;
    if (rules.city.active) activeRules.city_eq = rules.city.val;
    if (rules.inactivity.active) activeRules.inactive_days_gt = rules.inactivity.val;
    if (rules.category.active) activeRules.category_bought = rules.category.val;
    return activeRules;
  };

  const handleSaveSegment = async (e) => {
    e.preventDefault();
    if (!name) {
      alert("Please enter a segment name.");
      return;
    }
    const compiledRules = compileActiveRules();
    if (Object.keys(compiledRules).length === 0) {
      alert("Please enable at least one filter rule.");
      return;
    }

    setSaving(true);
    try {
      const res = await api.createSegment({
        name,
        rules: compiledRules
      });
      if (res.status === 'success') {
        // Clear form
        setName('');
        setRules({
          spend: { active: false, val: 5000 },
          orders: { active: false, val: 5 },
          city: { active: false, val: 'Chennai' },
          inactivity: { active: false, val: 30 },
          category: { active: false, val: 'Shoes' }
        });
        fetchSegments();
        alert(`Segment "${res.data.name}" created successfully with ${res.data.customer_count} matching shoppers!`);
      }
    } catch (err) {
      alert("Failed to create segment: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleAISuggestions = async () => {
    setAiLoading(true);
    setAiExpanded(true);
    try {
      const response = await api.suggestSegments();
      if (response.status === 'success') {
        setAiSuggestions(response.data);
      }
    } catch (err) {
      alert("Failed to fetch AI recommendations: " + err.message);
    } finally {
      setAiLoading(false);
    }
  };

  const handleQuickCreateSegment = async (suggestion) => {
    setSaving(true);
    try {
      const res = await api.createSegment({
        name: suggestion.name,
        rules: suggestion.rules
      });
      if (res.status === 'success') {
        fetchSegments();
        alert(`AI segment "${res.data.name}" successfully saved with ${res.data.customer_count} shoppers!`);
        // Remove from suggested list
        setAiSuggestions(prev => prev.filter(item => item.name !== suggestion.name));
      }
    } catch (err) {
      alert("Failed to save segment: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const fetchSegmentCustomers = async (id, pageNum) => {
    setDrawerLoading(true);
    try {
      const res = await api.getSegmentCustomers(id, {
        page: pageNum,
        limit: drawerLimit
      });
      if (res.status === 'success') {
        setSegmentCustomers(res.data);
        setSegmentCustomersTotal(res.total);
        setActiveSegmentName(res.segment_name);
      }
    } catch (err) {
      console.error(err);
      alert("Error loading customers.");
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleViewCustomers = (id) => {
    setActiveSegmentId(id);
    setDrawerPage(1);
    fetchSegmentCustomers(id, 1);
  };

  const handleDrawerPageChange = (direction) => {
    const nextPage = direction === 'next' ? drawerPage + 1 : drawerPage - 1;
    setDrawerPage(nextPage);
    fetchSegmentCustomers(activeSegmentId, nextPage);
  };

  const formatRulesText = (segmentRules) => {
    const textParts = [];
    if (segmentRules.total_spend_gt !== undefined) {
      textParts.push(`Spend > ₹${segmentRules.total_spend_gt}`);
    }
    if (segmentRules.total_orders_gte !== undefined) {
      textParts.push(`Orders ≥ ${segmentRules.total_orders_gte}`);
    }
    if (segmentRules.city_eq !== undefined) {
      textParts.push(`City = ${segmentRules.city_eq}`);
    }
    if (segmentRules.inactive_days_gt !== undefined) {
      textParts.push(`Inactive > ${segmentRules.inactive_days_gt} days`);
    }
    if (segmentRules.category_bought !== undefined) {
      textParts.push(`Bought: ${segmentRules.category_bought}`);
    }
    return textParts.join(' AND ') || 'No filters applied';
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  const drawerTotalPages = Math.ceil(segmentCustomersTotal / drawerLimit) || 1;

  return (
    <div>
      {/* Header */}
      <div className="header-actions">
        <div>
          <h1 className="section-title">Segments</h1>
          <p className="section-subtitle">Target customer groupings using rules or AI suggestions</p>
        </div>
        <button 
          className="btn btn-primary" 
          onClick={handleAISuggestions}
          disabled={aiLoading}
        >
          <Sparkles size={16} />
          <span>AI Suggest Segments</span>
        </button>
      </div>

      {/* AI Segment Suggestions Section (Expandable) */}
      {aiExpanded && (
        <div className="glass-card" style={{ border: '1px solid rgba(139, 92, 246, 0.3)', background: 'rgba(139, 92, 246, 0.03)', marginBottom: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} style={{ color: '#c084fc' }} />
              <span className="text-gradient-purple">Gemini Smart Segments</span>
            </h3>
            <button 
              className="btn btn-secondary" 
              style={{ padding: '6px', borderRadius: '50%' }}
              onClick={() => setAiExpanded(false)}
            >
              <X size={16} />
            </button>
          </div>

          {aiLoading ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', padding: '24px' }}>
              <div className="spinner"></div>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Gemini is analyzing database metrics...</p>
            </div>
          ) : aiSuggestions.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>All suggestions created!</p>
          ) : (
            <div className="ai-suggestions-list">
              {aiSuggestions.map((sug, i) => (
                <div key={i} className="glass-card ai-suggestion-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
                  <div>
                    <h4 style={{ color: '#c084fc', fontSize: '15px', marginBottom: '8px' }}>{sug.name}</h4>
                    <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.4', marginBottom: '16px' }}>
                      {sug.description}
                    </p>
                    <div style={{ background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '11px', fontFamily: 'monospace', marginBottom: '16px' }}>
                      Rules: {JSON.stringify(sug.rules, null, 1)}
                    </div>
                  </div>
                  <button 
                    className="btn btn-primary" 
                    style={{ width: '100%', padding: '8px 12px', fontSize: '12px' }}
                    onClick={() => handleQuickCreateSegment(sug)}
                    disabled={saving}
                  >
                    <Check size={14} />
                    <span>Create This Segment</span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Main Grid: Create form vs. Saved segments list */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '32px' }}>
        
        {/* Visual Rule Builder Card */}
        <div className="glass-card" style={{ height: 'fit-content' }}>
          <h3 style={{ marginBottom: '16px' }}>Rule Builder</h3>
          
          <form onSubmit={handleSaveSegment}>
            <div className="form-group">
              <label>Segment Name</label>
              <input 
                type="text" 
                className="form-control" 
                placeholder="e.g. VIP Chennai Shoppers"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <label style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '10px', display: 'block' }}>
              Target Rules (select & configure)
            </label>
            
            <div className="rules-container">
              
              {/* Rule 1: Total Spend */}
              <div className="rule-row">
                <input 
                  type="checkbox" 
                  checked={rules.spend.active} 
                  onChange={() => handleRuleCheckboxChange('spend')} 
                />
                <span style={{ fontSize: '13px' }}>Spend &gt;</span>
                <input 
                  type="number" 
                  className="form-control" 
                  style={{ padding: '6px' }}
                  value={rules.spend.val}
                  onChange={(e) => handleRuleValChange('spend', e.target.value)}
                  disabled={!rules.spend.active}
                />
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>INR</span>
              </div>

              {/* Rule 2: Total Orders */}
              <div className="rule-row">
                <input 
                  type="checkbox" 
                  checked={rules.orders.active} 
                  onChange={() => handleRuleCheckboxChange('orders')} 
                />
                <span style={{ fontSize: '13px' }}>Orders &ge;</span>
                <input 
                  type="number" 
                  className="form-control" 
                  style={{ padding: '6px' }}
                  value={rules.orders.val}
                  onChange={(e) => handleRuleValChange('orders', e.target.value)}
                  disabled={!rules.orders.active}
                />
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>count</span>
              </div>

              {/* Rule 3: City */}
              <div className="rule-row">
                <input 
                  type="checkbox" 
                  checked={rules.city.active} 
                  onChange={() => handleRuleCheckboxChange('city')} 
                />
                <span style={{ fontSize: '13px' }}>City =</span>
                <select 
                  className="form-control" 
                  style={{ padding: '6px' }}
                  value={rules.city.val}
                  onChange={(e) => handleRuleValChange('city', e.target.value)}
                  disabled={!rules.city.active}
                >
                  {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <span></span>
              </div>

              {/* Rule 4: Inactivity */}
              <div className="rule-row">
                <input 
                  type="checkbox" 
                  checked={rules.inactivity.active} 
                  onChange={() => handleRuleCheckboxChange('inactivity')} 
                />
                <span style={{ fontSize: '13px' }}>Inactive &gt;</span>
                <input 
                  type="number" 
                  className="form-control" 
                  style={{ padding: '6px' }}
                  value={rules.inactivity.val}
                  onChange={(e) => handleRuleValChange('inactivity', e.target.value)}
                  disabled={!rules.inactivity.active}
                />
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>days</span>
              </div>

              {/* Rule 5: Category bought */}
              <div className="rule-row">
                <input 
                  type="checkbox" 
                  checked={rules.category.active} 
                  onChange={() => handleRuleCheckboxChange('category')} 
                />
                <span style={{ fontSize: '13px' }}>Bought:</span>
                <select 
                  className="form-control" 
                  style={{ padding: '6px' }}
                  value={rules.category.val}
                  onChange={(e) => handleRuleValChange('category', e.target.value)}
                  disabled={!rules.category.active}
                >
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <span></span>
              </div>

            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%', gap: '8px' }}
              disabled={saving}
            >
              <PlusCircle size={16} />
              <span>{saving ? 'Saving...' : 'Save Segment'}</span>
            </button>
          </form>
        </div>

        {/* Saved Segments List */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '16px' }}>Saved Segments</h3>
          
          {loading ? (
            <div className="page-loading-wrapper">
              <div className="spinner"></div>
            </div>
          ) : segments.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              No segments saved yet. Build one or run AI segment suggestion.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {segments.map((seg) => (
                <div 
                  key={seg._id} 
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
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ padding: '6px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '6px', color: 'var(--color-primary)' }}>
                        <Layers size={16} />
                      </div>
                      <h4 style={{ fontSize: '16px' }}>{seg.name}</h4>
                    </div>
                    <span style={{ fontSize: '13px', color: '#c084fc', fontWeight: '700', background: 'rgba(139,92,246,0.1)', padding: '2px 8px', borderRadius: '10px' }}>
                      {seg.customer_count?.toLocaleString()} matched
                    </span>
                  </div>

                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', fontFamily: 'monospace', background: 'rgba(0,0,0,0.1)', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                    {formatRulesText(seg.rules)}
                  </p>

                  <div style={{ display: 'flex', gap: '12px', marginTop: '4px' }}>
                    <button 
                      className="btn btn-secondary btn-sm"
                      style={{ padding: '8px 14px', flex: '1' }}
                      onClick={() => handleViewCustomers(seg._id)}
                    >
                      <Eye size={14} />
                      <span>View Shoppers</span>
                    </button>
                    <button 
                      className="btn btn-primary btn-sm"
                      style={{ padding: '8px 14px', flex: '1' }}
                      onClick={() => navigateToTab('campaigns')}
                    >
                      <Send size={14} />
                      <span>Send Campaign</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Segment Customers Viewer Drawer */}
      {activeSegmentId && (
        <>
          <div className="drawer-backdrop" onClick={() => setActiveSegmentId(null)}></div>
          <div className="glass-panel drawer" style={{ width: '600px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ padding: '8px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '50%', color: 'var(--color-primary)' }}>
                  <User size={20} />
                </div>
                <div>
                  <h3 style={{ fontSize: '18px' }}>{activeSegmentName}</h3>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Matched shoppers in segment ({segmentCustomersTotal})</p>
                </div>
              </div>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '8px', borderRadius: '50%' }}
                onClick={() => setActiveSegmentId(null)}
              >
                <X size={18} />
              </button>
            </div>

            {drawerLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: '1' }}>
                <div className="spinner"></div>
              </div>
            ) : (
              <>
                <div style={{ flex: '1', overflowY: 'auto' }}>
                  <div className="table-container" style={{ border: 'none' }}>
                    <table className="modern-table">
                      <thead>
                        <tr>
                          <th>Name</th>
                          <th>Location</th>
                          <th style={{ textAlign: 'right' }}>Total Spend</th>
                          <th style={{ textAlign: 'center' }}>Orders</th>
                        </tr>
                      </thead>
                      <tbody>
                        {segmentCustomers.map(cust => (
                          <tr key={cust._id} style={{ cursor: 'default' }}>
                            <td style={{ fontWeight: '600' }}>{cust.name}</td>
                            <td>{cust.city}</td>
                            <td style={{ textAlign: 'right', fontWeight: '700', color: '#ec4899' }}>
                              {formatCurrency(cust.total_spend || 0)}
                            </td>
                            <td style={{ textAlign: 'center', fontWeight: '600' }}>{cust.total_orders || 0}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Drawer Pagination */}
                <div className="pagination" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    Page {drawerPage} of {drawerTotalPages}
                  </span>
                  <div className="pagination-buttons">
                    <button 
                      className="btn btn-secondary btn-sm" 
                      style={{ padding: '4px 10px', fontSize: '11px' }}
                      onClick={() => handleDrawerPageChange('prev')}
                      disabled={drawerPage === 1}
                    >
                      <ChevronLeft size={14} />
                      <span>Prev</span>
                    </button>
                    <button 
                      className="btn btn-secondary btn-sm" 
                      style={{ padding: '4px 10px', fontSize: '11px' }}
                      onClick={() => handleDrawerPageChange('next')}
                      disabled={drawerPage === drawerTotalPages}
                    >
                      <span>Next</span>
                      <ChevronRight size={14} />
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </>
      )}

    </div>
  );
}

export default Segments;
