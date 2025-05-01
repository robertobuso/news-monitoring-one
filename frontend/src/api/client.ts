import axios from 'axios';
import { Article, Feed, ClientProfile, Report, User /* Import your types */ } from '../types'; // Adjust path as needed

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
      // Optional: Add state to show a message on the login page
      // sessionStorage.setItem('sessionExpired', 'true');
      window.location.href = '/auth/login'; // Or use react-router navigation
    }
    return Promise.reject(error);
  }
);

// --- Define Params Interface for Type Safety ---
interface ArticleListParams {
  skip?: number;
  limit?: number;
  search?: string;
  feed_id?: string; // Use snake_case to match backend Python query param
  source?: string;
  date_from?: string; // Send dates as ISO strings typically
  date_to?: string;
}

// Define specific types for other function inputs/outputs if desired
// e.g., interface FeedProcessResponse { success: boolean; message: string; articles: Article[] }

const api = {
  auth: {
    // For login, you must use form data not JSON
    login: async (email: string, password: string): Promise<{ access_token: string, token_type: string }> => { // Add return type
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
    register: async (userData: any): Promise<User> => { // Add return type
      const response = await axiosInstance.post('/auth/register', userData);
      return response.data;
    },
    me: async (): Promise<User> => { // Add return type
      const response = await axiosInstance.get('/auth/me');
      return response.data;
    },
    refresh: async (refreshToken: string): Promise<{ access_token: string, token_type: string }> => { // Add return type
      const response = await axiosInstance.post('/auth/refresh', { refresh_token: refreshToken });
      return response.data;
    },
  },
  clientProfiles: {
    getAll: async (): Promise<ClientProfile[]> => { // Add return type
      const response = await axiosInstance.get('/clients');
      return response.data;
    },
    getById: async (id: string): Promise<ClientProfile> => { // Add return type
      const response = await axiosInstance.get(`/clients/${id}`);
      return response.data;
    },
    create: async (data: Partial<ClientProfile>): Promise<ClientProfile> => { // Add types
      const response = await axiosInstance.post('/clients', data);
      return response.data;
    },
    update: async (id: string, data: Partial<ClientProfile>): Promise<ClientProfile> => { // Add types
      const response = await axiosInstance.put(`/clients/${id}`, data);
      return response.data;
    },
    delete: async (id: string): Promise<any> => { // Adjust return type if needed
      const response = await axiosInstance.delete(`/clients/${id}`);
      return response.data;
    },
  },
  feeds: {
    getAll: async (): Promise<Feed[]> => { // Add return type
      const response = await axiosInstance.get('/feeds');
      return response.data;
    },
    getById: async (id: string): Promise<Feed> => { // Add return type
      const response = await axiosInstance.get(`/feeds/${id}`);
      return response.data;
    },
    create: async (data: Partial<Feed>): Promise<Feed> => { // Add types
      const response = await axiosInstance.post('/feeds', data);
      return response.data;
    },
    update: async (id: string, data: Partial<Feed>): Promise<Feed> => { // Add types
      const response = await axiosInstance.put(`/feeds/${id}`, data);
      return response.data;
    },
    delete: async (id: string): Promise<any> => { // Adjust return type if needed
      const response = await axiosInstance.delete(`/feeds/${id}`);
      return response.data;
    },
    testConnection: async (url: string, type: string): Promise<{ success: boolean; message: string }> => { // Add return type
      const response = await axiosInstance.post('/feeds/test-connection', { url, type });
      return response.data;
    },
    processFeed: async (id: string): Promise<{ success: boolean; message: string; articles: Article[] }> => { // Add return type
      const response = await axiosInstance.post(`/feeds/${id}/process`);
      return response.data;
    },
  },
  articles: {
    // Use the defined interface for params and return type
    getAll: async (params?: ArticleListParams): Promise<Article[]> => {
      // Ensure keys in params match backend (e.g., feed_id, date_from, date_to)
      const response = await axiosInstance.get('/articles', { params });
      return response.data;
    },
    getById: async (id: string): Promise<Article> => { // Add return type
      const response = await axiosInstance.get(`/articles/${id}`);
      return response.data;
    },
    // --- REMOVED getByClient ---
    // getByClient: async (clientId: string, params: any = {}) => {
    //   const response = await axiosInstance.get(`/articles/by-client/${clientId}`, { params });
    //   return response.data;
    // },
    getRelevant: async (clientId: string, params: any = {}): Promise<any[]> => { // Adjust return type
      const response = await axiosInstance.get('/articles/relevant', { // Should likely be /relevance endpoint? Check backend route
        params: { client_id: clientId, ...params },
      });
      return response.data;
    },
    analyze: async (id: string): Promise<any> => { // Adjust return type
      const response = await axiosInstance.post(`/articles/${id}/analyze`);
      return response.data;
    },
    getSummary: async (id: string, clientId?: string, maxLength?: number): Promise<{ summary: string }> => { // Add return type
      const params: any = {};
      if (clientId) params.client_id = clientId;
      if (maxLength) params.max_length = maxLength;
      const response = await axiosInstance.get(`/articles/${id}/summary`, { params });
      return response.data;
    },
  },
  reports: {
    getAll: async (params: any = {}): Promise<Report[]> => { // Add return type
      const response = await axiosInstance.get('/reports', { params });
      return response.data;
    },
    getById: async (id: string): Promise<Report> => { // Adjust return type if it includes articles
      const response = await axiosInstance.get(`/reports/${id}`);
      return response.data;
    },
    // --- REMOVED getByClient --- (Handled by getAll with client_id param)
    // getByClient: async (clientId: string, params: any = {}) => {
    //   const response = await axiosInstance.get(`/reports/by-client/${clientId}`, { params });
    //   return response.data;
    // },
    generate: async (clientId: string, reportDate?: string): Promise<{ task_id: string; status: string; message: string }> => { // Add return type
      const data: any = { client_id: clientId }; // Backend expects client_id
      if (reportDate) data.report_date = reportDate;
      // recipientEmail seems to be handled in the /send endpoint now
      const response = await axiosInstance.post('/reports/generate', data);
      return response.data;
    },
    download: (id: string) => { // Changed to void, as it opens a new window
      // Add token handling if download requires authentication
       const token = localStorage.getItem('token');
       // Basic approach, might need more robust handling for auth headers on download
       window.open(`${API_BASE_URL}/reports/download/${id}?token=${token}`, '_blank');
       // Alternative: Use axios with responseType: 'blob' and createObjectURL if auth needed
    },
    sendEmail: async (id: string, email: string): Promise<{ success: boolean; message: string }> => { // Add return type
      const response = await axiosInstance.post(`/reports/${id}/send`, { email });
      return response.data;
    },
  },
  // Add relevance api if needed
  relevance: {
     // Define functions to interact with /api/v1/relevance endpoints
  }
};

export default api;