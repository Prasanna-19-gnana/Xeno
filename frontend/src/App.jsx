import { useState } from 'react';
import { 
  LayoutDashboard, 
  Users, 
  ShoppingBag, 
  Layers, 
  Send, 
  BarChart3, 
  Sparkles 
} from 'lucide-react';

// Import pages
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import Orders from './pages/Orders';
import Segments from './pages/Segments';
import Campaigns from './pages/Campaigns';
import Analytics from './pages/Analytics';
import AIAssistant from './pages/AIAssistant';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  // Pass dynamic campaign ID to analytics if needed, or open segment drawer
  const [selectedCampaignId, setSelectedCampaignId] = useState(null);

  const navigateToTab = (tab, campaignId = null) => {
    setActiveTab(tab);
    if (campaignId) {
      setSelectedCampaignId(campaignId);
    }
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard navigateToTab={navigateToTab} />;
      case 'customers':
        return <Customers />;
      case 'orders':
        return <Orders />;
      case 'segments':
        return <Segments navigateToTab={navigateToTab} />;
      case 'campaigns':
        return <Campaigns navigateToTab={navigateToTab} />;
      case 'analytics':
        return (
          <Analytics 
            campaignId={selectedCampaignId} 
            setSelectedCampaignId={setSelectedCampaignId} 
            navigateToTab={navigateToTab}
          />
        );
      case 'ai-assistant':
        return <AIAssistant navigateToTab={navigateToTab} />;
      default:
        return <Dashboard navigateToTab={navigateToTab} />;
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'customers', label: 'Customers', icon: Users },
    { id: 'orders', label: 'Orders', icon: ShoppingBag },
    { id: 'segments', label: 'Segments', icon: Layers },
    { id: 'campaigns', label: 'Campaigns', icon: Send },
    { id: 'analytics', label: 'Campaign Analytics', icon: BarChart3 },
    { id: 'ai-assistant', label: 'AI Assistant', icon: Sparkles },
  ];

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand-logo">
          <span className="text-gradient" style={{ fontSize: '26px' }}>TrendWear</span>
          <span style={{ fontSize: '12px', background: 'rgba(139,92,246,0.2)', padding: '2px 8px', borderRadius: '10px', color: '#c084fc' }}>CRM</span>
        </div>
        
        <nav className="nav-links">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li key={item.id}>
                <a 
                  className={`nav-item ${isActive ? 'active' : ''}`}
                  onClick={() => navigateToTab(item.id)}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </a>
              </li>
            );
          })}
        </nav>
        
        <div style={{ marginTop: 'auto', padding: '16px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px solid var(--border-color)', fontSize: '11px', color: 'var(--text-muted)' }}>
          <p>Logged in as Marketer</p>
          <p style={{ marginTop: '4px' }}>System Date: 2026-06-10</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        {renderActivePage()}
      </main>
    </div>
  );
}

export default App;
