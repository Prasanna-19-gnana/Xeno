import { useState, useEffect } from 'react';
import { 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  User, 
  ShoppingBag, 
  Send,
  Eye,
  X,
  Plus,
  RefreshCw
} from 'lucide-react';
import { api } from '../api';

const CITIES = ["Chennai", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Kolkata", "Pune", "Ahmedabad"];

function Customers() {
  const [customers, setCustomers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [search, setSearch] = useState('');
  const [city, setCity] = useState('');
  const [gender, setGender] = useState('');
  const [sortBy, setSortBy] = useState('total_spend');
  const [sortOrder, setSortOrder] = useState(-1);
  
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  
  // Drawer states
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [drawerData, setDrawerData] = useState(null);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [drawerTab, setDrawerTab] = useState('orders'); // 'orders' or 'messages'

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const response = await api.getCustomers({
        page,
        limit,
        search,
        city,
        gender,
        sort_by: sortBy,
        sort_order: sortOrder
      });
      if (response.status === 'success') {
        setCustomers(response.data);
        setTotal(response.total);
      }
    } catch (err) {
      console.error('Error fetching customers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, city, gender, sortBy, sortOrder]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchCustomers();
  };

  const handleGenerateCustomers = async () => {
    if (!window.confirm("Are you sure? This will delete all existing data and generate 1,000 customers & 5,000 orders. This might take up to 10-15 seconds.")) {
      return;
    }
    setSeeding(true);
    try {
      const res = await api.generateCustomers();
      alert(res.message || "Seeding complete.");
      setPage(1);
      fetchCustomers();
    } catch (err) {
      alert("Seeding failed: " + err.message);
    } finally {
      setSeeding(false);
    }
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 1 ? -1 : 1);
    } else {
      setSortBy(field);
      setSortOrder(-1);
    }
    setPage(1);
  };

  const handleViewCustomer = async (id) => {
    setSelectedCustomerId(id);
    setDrawerLoading(true);
    setDrawerTab('orders');
    try {
      const res = await api.getCustomerById(id);
      if (res.status === 'success') {
        setDrawerData(res.data);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to load customer profile details.");
      setSelectedCustomerId(null);
    } finally {
      setDrawerLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div>
      {/* Header */}
      <div className="header-actions">
        <div>
          <h1 className="section-title">Customers</h1>
          <p className="section-subtitle">Manage and segment your shoppers ({total.toLocaleString()})</p>
        </div>
        <button 
          className="btn btn-accent" 
          onClick={handleGenerateCustomers}
          disabled={seeding || loading}
        >
          {seeding ? (
            <>
              <RefreshCw size={16} className="spin" />
              <span>Generating (10s)...</span>
            </>
          ) : (
            <>
              <Plus size={16} />
              <span>Generate Sample Customers</span>
            </>
          )}
        </button>
      </div>

      {/* Filters Bar */}
      <div className="glass-card" style={{ padding: '16px', marginBottom: '24px', display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center' }}>
        
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '8px', flex: '1', minWidth: '260px' }}>
          <div style={{ position: 'relative', flex: '1' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
            <input 
              type="text" 
              className="form-control" 
              style={{ paddingLeft: '40px', width: '100%' }}
              placeholder="Search name, email, phone, city..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-secondary">Search</button>
        </form>

        {/* City Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>CITY:</label>
          <select 
            className="form-control" 
            value={city} 
            onChange={(e) => { setCity(e.target.value); setPage(1); }}
            style={{ padding: '8px 12px' }}
          >
            <option value="">All Cities</option>
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {/* Gender Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>GENDER:</label>
          <select 
            className="form-control" 
            value={gender} 
            onChange={(e) => { setGender(e.target.value); setPage(1); }}
            style={{ padding: '8px 12px' }}
          >
            <option value="">All Genders</option>
            <option value="Female">Female</option>
            <option value="Male">Male</option>
            <option value="Non-binary">Non-binary</option>
          </select>
        </div>

      </div>

      {/* Table Section */}
      <div className="glass-card" style={{ padding: '0px' }}>
        {loading ? (
          <div className="page-loading-wrapper">
            <div className="spinner"></div>
          </div>
        ) : customers.length === 0 ? (
          <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No customers found. Try generating sample data.
          </div>
        ) : (
          <div className="table-container">
            <table className="modern-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('name')} style={{ cursor: 'pointer' }}>
                    Name {sortBy === 'name' && (sortOrder === 1 ? '▲' : '▼')}
                  </th>
                  <th>Contact Info</th>
                  <th>City</th>
                  <th onClick={() => handleSort('age')} style={{ cursor: 'pointer' }}>
                    Age {sortBy === 'age' && (sortOrder === 1 ? '▲' : '▼')}
                  </th>
                  <th>Gender</th>
                  <th onClick={() => handleSort('total_spend')} style={{ cursor: 'pointer', textAlign: 'right' }}>
                    Total Spend {sortBy === 'total_spend' && (sortOrder === 1 ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('total_orders')} style={{ cursor: 'pointer', textAlign: 'center' }}>
                    Orders {sortBy === 'total_orders' && (sortOrder === 1 ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('last_order_date')} style={{ cursor: 'pointer' }}>
                    Last Order {sortBy === 'last_order_date' && (sortOrder === 1 ? '▲' : '▼')}
                  </th>
                  <th style={{ textAlign: 'center' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c) => (
                  <tr key={c._id} onClick={() => handleViewCustomer(c._id)}>
                    <td style={{ fontWeight: '600' }}>{c.name}</td>
                    <td>
                      <div style={{ fontSize: '13px' }}>{c.email}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>{c.phone}</div>
                    </td>
                    <td>{c.city}</td>
                    <td>{c.age}</td>
                    <td>
                      <span className={`gender-badge ${c.gender?.toLowerCase()}`}>
                        {c.gender}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: '700' }}>{formatCurrency(c.total_spend || 0)}</td>
                    <td style={{ textAlign: 'center', fontWeight: '600' }}>{c.total_orders || 0}</td>
                    <td>{c.last_order_date || 'N/A'}</td>
                    <td style={{ textAlign: 'center' }} onClick={(e) => e.stopPropagation()}>
                      <button 
                        className="btn btn-secondary btn-sm" 
                        style={{ padding: '6px 10px', borderRadius: '8px' }}
                        onClick={() => handleViewCustomer(c._id)}
                      >
                        <Eye size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Footer */}
      {!loading && customers.length > 0 && (
        <div className="pagination">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Showing Page <strong>{page}</strong> of <strong>{totalPages}</strong> (Total: {total.toLocaleString()} shoppers)
          </span>
          <div className="pagination-buttons">
            <button 
              className="btn btn-secondary btn-sm" 
              onClick={() => setPage(p => Math.max(p - 1, 1))}
              disabled={page === 1}
            >
              <ChevronLeft size={16} />
              <span>Prev</span>
            </button>
            <button 
              className="btn btn-secondary btn-sm" 
              onClick={() => setPage(p => Math.min(p + 1, totalPages))}
              disabled={page === totalPages}
            >
              <span>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Profile Detail Drawer (Slides In from Right) */}
      {selectedCustomerId && (
        <>
          <div className="drawer-backdrop" onClick={() => setSelectedCustomerId(null)}></div>
          <div className="glass-panel drawer">
            
            {/* Drawer Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ padding: '10px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '50%', color: 'var(--color-primary)' }}>
                  <User size={24} />
                </div>
                <div>
                  <h2 style={{ fontSize: '20px' }}>{drawerLoading ? 'Loading Profile...' : drawerData?.customer?.name}</h2>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Customer Profile details</p>
                </div>
              </div>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '8px', borderRadius: '50%' }}
                onClick={() => setSelectedCustomerId(null)}
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
                {/* Customer Snapshot Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', fontSize: '13px' }}>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', marginBottom: '2px' }}>Email Address</div>
                    <div style={{ fontWeight: '500' }}>{drawerData?.customer?.email}</div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', marginBottom: '2px' }}>Phone Number</div>
                    <div style={{ fontWeight: '500' }}>{drawerData?.customer?.phone}</div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', marginBottom: '2px' }}>Location / City</div>
                    <div style={{ fontWeight: '500' }}>{drawerData?.customer?.city}</div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', marginBottom: '2px' }}>Demographics</div>
                    <div style={{ fontWeight: '500' }}>{drawerData?.customer?.gender}, {drawerData?.customer?.age} yrs</div>
                  </div>
                  <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '10px', marginTop: '4px' }}>
                    <div style={{ color: 'var(--text-secondary)', marginBottom: '2px' }}>Total Spend</div>
                    <div style={{ fontWeight: '700', color: '#ec4899', fontSize: '15px' }}>{formatCurrency(drawerData?.customer?.total_spend || 0)}</div>
                  </div>
                  <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '10px', marginTop: '4px' }}>
                    <div style={{ color: 'var(--text-secondary)', marginBottom: '2px' }}>Orders Placed</div>
                    <div style={{ fontWeight: '700', color: '#8b5cf6', fontSize: '15px' }}>{drawerData?.customer?.total_orders || 0} orders</div>
                  </div>
                </div>

                {/* Tab Chooser */}
                <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', paddingBottom: '1px' }}>
                  <button 
                    className={`btn`} 
                    style={{ 
                      background: 'none', 
                      boxShadow: 'none', 
                      borderRadius: '0', 
                      borderBottom: drawerTab === 'orders' ? '2px solid var(--color-primary)' : 'none',
                      color: drawerTab === 'orders' ? 'var(--text-primary)' : 'var(--text-secondary)',
                      flex: '1',
                      padding: '12px'
                    }}
                    onClick={() => setDrawerTab('orders')}
                  >
                    <ShoppingBag size={16} />
                    <span>Orders ({drawerData?.orders?.length || 0})</span>
                  </button>
                  <button 
                    className={`btn`} 
                    style={{ 
                      background: 'none', 
                      boxShadow: 'none', 
                      borderRadius: '0', 
                      borderBottom: drawerTab === 'messages' ? '2px solid var(--color-primary)' : 'none',
                      color: drawerTab === 'messages' ? 'var(--text-primary)' : 'var(--text-secondary)',
                      flex: '1',
                      padding: '12px'
                    }}
                    onClick={() => setDrawerTab('messages')}
                  >
                    <Send size={16} />
                    <span>Campaign Outreach ({drawerData?.communications?.length || 0})</span>
                  </button>
                </div>

                {/* Tab Contents */}
                <div style={{ flex: '1', overflowY: 'auto', maxHeight: '400px', paddingRight: '4px' }}>
                  
                  {/* Orders Tab */}
                  {drawerTab === 'orders' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {drawerData?.orders?.length === 0 ? (
                        <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No orders placed.</p>
                      ) : (
                        drawerData?.orders?.map((ord) => (
                          <div 
                            key={ord._id} 
                            style={{ 
                              display: 'flex', 
                              justifyContent: 'between', 
                              alignItems: 'center', 
                              padding: '12px 16px', 
                              background: 'rgba(255,255,255,0.01)', 
                              border: '1px solid var(--border-color)',
                              borderRadius: '10px'
                            }}
                          >
                            <div>
                              <p style={{ fontWeight: '600', fontSize: '13px' }}>{ord.category}</p>
                              <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                ID: {ord._id} • {ord.order_date}
                              </p>
                            </div>
                            <span style={{ fontWeight: '700', fontSize: '14px', color: '#10b981' }}>
                              {formatCurrency(ord.amount)}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {/* Outreach Tab */}
                  {drawerTab === 'messages' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {drawerData?.communications?.length === 0 ? (
                        <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No messages sent to this customer.</p>
                      ) : (
                        drawerData?.communications?.map((comm) => (
                          <div 
                            key={comm._id} 
                            style={{ 
                              padding: '16px', 
                              background: 'rgba(255,255,255,0.01)', 
                              border: '1px solid var(--border-color)',
                              borderRadius: '10px',
                              fontSize: '13px'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                              <span style={{ textTransform: 'uppercase', fontSize: '10px', fontWeight: '700', color: 'var(--color-primary)' }}>
                                {comm.channel}
                              </span>
                              <span className={`status-badge ${comm.status?.toLowerCase()}`} style={{ fontSize: '10px', padding: '2px 6px' }}>
                                {comm.status}
                              </span>
                            </div>
                            <p style={{ color: 'var(--text-primary)', fontStyle: 'italic', marginBottom: '8px', lineHeight: '1.4' }}>
                              "{comm.message}"
                            </p>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-secondary)' }}>
                              <span>Sent: {comm.created_at}</span>
                              <span>Events: {comm.events?.join(' → ')}</span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}

                </div>
              </>
            )}
            
          </div>
        </>
      )}

    </div>
  );
}

export default Customers;
