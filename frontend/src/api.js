const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }

  const response = await fetch(url, config);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'Something went wrong');
  }

  return data;
}

export const api = {
  // Health
  checkHealth: () => request('/health'),

  // Dashboard Stats
  getDashboardStats: () => request('/dashboard/stats'),

  // Customers
  getCustomers: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/customers?${query}`);
  },
  getCustomerById: (id) => request(`/customers/${id}`),
  generateCustomers: () => request('/customers/generate', { method: 'POST' }),

  // Orders
  getOrders: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/orders?${query}`);
  },

  // Segments
  getSegments: () => request('/segments'),
  createSegment: (segmentData) => request('/segments', {
    method: 'POST',
    body: segmentData,
  }),
  getSegmentCustomers: (id, params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/segments/${id}/customers?${query}`);
  },
  suggestSegments: () => request('/ai/suggest-segments', { method: 'POST' }),

  // Campaigns
  getCampaigns: () => request('/campaigns'),
  createCampaign: (campaignData) => request('/campaigns', {
    method: 'POST',
    body: campaignData,
  }),
  sendCampaign: (id) => request(`/campaigns/${id}/send`, { method: 'POST' }),
  getCampaignStats: (id) => request(`/campaigns/${id}/stats`),

  // AI copywriting
  generateMessage: (payload) => request('/ai/generate-message', {
    method: 'POST',
    body: payload,
  }),
  askAssistant: (message) => request('/ai/campaign-assistant', {
    method: 'POST',
    body: { message },
  }),
};
