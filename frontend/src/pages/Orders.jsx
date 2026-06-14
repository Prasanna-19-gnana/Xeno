import { useState, useEffect } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  SlidersHorizontal,
  Calendar
} from 'lucide-react';
import { api } from '../api';

const CATEGORIES = ["T-Shirts", "Jeans", "Shoes", "Dresses", "Accessories"];

function Orders() {
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [category, setCategory] = useState('');
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');
  const [sortBy, setSortBy] = useState('order_date');
  const [sortOrder, setSortOrder] = useState(-1);
  
  const [loading, setLoading] = useState(true);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const response = await api.getOrders({
        page,
        limit,
        category,
        min_amount: minAmount,
        max_amount: maxAmount,
        sort_by: sortBy,
        sort_order: sortOrder
      });
      if (response.status === 'success') {
        setOrders(response.data);
        setTotal(response.total);
      }
    } catch (err) {
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, category, sortBy, sortOrder]);

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchOrders();
  };

  const handleClearFilters = () => {
    setCategory('');
    setMinAmount('');
    setMaxAmount('');
    setPage(1);
    // Fetch directly since state updates are asynchronous
    setLoading(true);
    api.getOrders({
      page: 1,
      limit,
      sort_by: sortBy,
      sort_order: sortOrder
    }).then(response => {
      if (response.status === 'success') {
        setOrders(response.data);
        setTotal(response.total);
      }
    }).finally(() => setLoading(false));
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
          <h1 className="section-title">Orders</h1>
          <p className="section-subtitle">Browse and analyze shopper transaction records ({total.toLocaleString()})</p>
        </div>
      </div>

      {/* Filter panel */}
      <div className="glass-card" style={{ padding: '16px', marginBottom: '24px' }}>
        <form onSubmit={handleFilterSubmit} style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <SlidersHorizontal size={16} style={{ color: 'var(--text-secondary)' }} />
            <span style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-secondary)' }}>FILTERS</span>
          </div>

          {/* Category Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>CATEGORY:</label>
            <select 
              className="form-control" 
              value={category} 
              onChange={(e) => { setCategory(e.target.value); setPage(1); }}
              style={{ padding: '8px 12px' }}
            >
              <option value="">All Categories</option>
              {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
          </div>

          {/* Price Range inputs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '600' }}>AMOUNT RANGE:</label>
            <input 
              type="number" 
              className="form-control" 
              style={{ padding: '8px 12px', width: '90px' }}
              placeholder="Min ₹"
              value={minAmount}
              onChange={(e) => setMinAmount(e.target.value)}
            />
            <span style={{ color: 'var(--text-secondary)' }}>to</span>
            <input 
              type="number" 
              className="form-control" 
              style={{ padding: '8px 12px', width: '90px' }}
              placeholder="Max ₹"
              value={maxAmount}
              onChange={(e) => setMaxAmount(e.target.value)}
            />
          </div>

          <button type="submit" className="btn btn-secondary btn-sm" style={{ padding: '8px 16px' }}>
            Apply
          </button>

          <button 
            type="button" 
            className="btn btn-secondary btn-sm" 
            style={{ padding: '8px 16px', background: 'none', border: 'none' }}
            onClick={handleClearFilters}
          >
            Clear Filters
          </button>
        </form>
      </div>

      {/* Table Section */}
      <div className="glass-card" style={{ padding: '0' }}>
        {loading ? (
          <div className="page-loading-wrapper">
            <div className="spinner"></div>
          </div>
        ) : orders.length === 0 ? (
          <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            No transaction records found. Try clearing filters or seeding sample data.
          </div>
        ) : (
          <div className="table-container">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer Name</th>
                  <th onClick={() => handleSort('category')} style={{ cursor: 'pointer' }}>
                    Category {sortBy === 'category' && (sortOrder === 1 ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('amount')} style={{ cursor: 'pointer', textAlign: 'right' }}>
                    Amount {sortBy === 'amount' && (sortOrder === 1 ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('order_date')} style={{ cursor: 'pointer' }}>
                    Order Date {sortBy === 'order_date' && (sortOrder === 1 ? '▲' : '▼')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {orders.map((ord) => (
                  <tr key={ord._id} style={{ cursor: 'default' }}>
                    <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{ord._id}</td>
                    <td style={{ fontWeight: '600' }}>{ord.customer_name}</td>
                    <td>
                      <span style={{ background: 'rgba(255,255,255,0.03)', padding: '4px 10px', borderRadius: '12px', border: '1px solid var(--border-color)', fontSize: '13px' }}>
                        {ord.category}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: '700', color: '#10b981' }}>{formatCurrency(ord.amount)}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Calendar size={14} style={{ color: 'var(--text-secondary)' }} />
                        <span>{ord.order_date}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Footer */}
      {!loading && orders.length > 0 && (
        <div className="pagination">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            Showing Page <strong>{page}</strong> of <strong>{totalPages}</strong> (Total: {total.toLocaleString()} transactions)
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

    </div>
  );
}

export default Orders;
