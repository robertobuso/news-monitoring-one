import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add token to requests
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      localStorage.removeItem('token');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

const api = {
  auth: {
    // For login, you must use form data not JSON
    login: async (email: string, password: string) => {
      // Create URLSearchParams instead of FormData
      const formData = new URLSearchParams();
      formData.append('username', email); // OAuth2 spec uses 'username'
      formData.append('password', password);
      
      const response = await axiosInstance.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    },
    register: async (userData: any) => {
      const response = await axiosInstance.post('/auth/register', userData);
      return response.data;
    },
    me: async () => {
      const response = await axiosInstance.get('/auth/me');
      return response.data;
    },
    refresh: async (refreshToken: string) => {
      const response = await axiosInstance.post('/auth/refresh', { refresh_token: refreshToken });
      return response.data;
    },
  },
  clientProfiles: {
    getAll: async () => {
      const response = await axiosInstance.get('/clients');
      return response.data;
    },
    getById: async (id: string) => {
      const response = await axiosInstance.get(`/clients/${id}`);
      return response.data;
    },
    create: async (data: any) => {
      const response = await axiosInstance.post('/clients', data);
      return response.data;
    },
    update: async (id: string, data: any) => {
      const response = await axiosInstance.put(`/clients/${id}`, data);
      return response.data;
    },
    delete: async (id: string) => {
      const response = await axiosInstance.delete(`/clients/${id}`);
      return response.data;
    },
  },
  feeds: {
    getAll: async () => {
      const response = await axiosInstance.get('/feeds');
      return response.data;
    },
    getById: async (id: string) => {
      const response = await axiosInstance.get(`/feeds/${id}`);
      return response.data;
    },
    create: async (data: any) => {
      const response = await axiosInstance.post('/feeds', data);
      return response.data;
    },
    update: async (id: string, data: any) => {
      const response = await axiosInstance.put(`/feeds/${id}`, data);
      return response.data;
    },
    delete: async (id: string) => {
      const response = await axiosInstance.delete(`/feeds/${id}`);
      return response.data;
    },
    testConnection: async (url: string, type: string) => {
      const response = await axiosInstance.post('/feeds/test-connection', { url, type });
      return response.data;
    },
    processFeed: async (id: string) => {
      const response = await axiosInstance.post(`/feeds/${id}/process`);
      return response.data;
    },
  },
  articles: {
    getAll: async (params: any = {}) => {
      const response = await axiosInstance.get('/articles', { params });
      return response.data;
    },
    getById: async (id: string) => {
      const response = await axiosInstance.get(`/articles/${id}`);
      return response.data;
    },
    getByClient: async (clientId: string, params: any = {}) => {
      const response = await axiosInstance.get(`/articles/by-client/${clientId}`, { params });
      return response.data;
    },
    getRelevant: async (clientId: string, params: any = {}) => {
      const response = await axiosInstance.get('/articles/relevant', {
        params: { client_id: clientId, ...params },
      });
      return response.data;
    },
    analyze: async (id: string) => {
      const response = await axiosInstance.post(`/articles/${id}/analyze`);
      return response.data;
    },
    getSummary: async (id: string, clientId?: string, maxLength?: number) => {
      const params: any = {};
      if (clientId) params.client_id = clientId;
      if (maxLength) params.max_length = maxLength;
      const response = await axiosInstance.get(`/articles/${id}/summary`, { params });
      return response.data;
    },
  },
  reports: {
    getAll: async (params: any = {}) => {
      const response = await axiosInstance.get('/reports', { params });
      return response.data;
    },
    getById: async (id: string) => {
      const response = await axiosInstance.get(`/reports/${id}`);
      return response.data;
    },
    getByClient: async (clientId: string, params: any = {}) => {
      const response = await axiosInstance.get(`/reports/by-client/${clientId}`, { params });
      return response.data;
    },
    generate: async (clientId: string, reportDate?: string, recipientEmail?: string) => {
      const data: any = { client_id: clientId };
      if (reportDate) data.report_date = reportDate;
      if (recipientEmail) data.recipient_email = recipientEmail;
      const response = await axiosInstance.post('/reports/generate', data);
      return response.data;
    },
    download: async (id: string) => {
      window.open(`${API_BASE_URL}/reports/download/${id}`, '_blank');
    },
    sendEmail: async (id: string, email: string) => {
      const response = await axiosInstance.post(`/reports/${id}/send`, { email });
      return response.data;
    },
  },
};

export default api;