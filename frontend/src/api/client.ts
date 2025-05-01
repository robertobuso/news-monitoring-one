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
    // Log the error for debugging
    console.error('API Error:', error.response?.status, error.response?.data || error.message);
    
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

interface ArticleEntity {
  organizations: string[];
  locations: string[];
  people: string[];
  topics: string[];
}

interface ArticleRelevanceResult {
  client_id: string;
  client_name: string;
  relevance_id: string;
  relevance_score: number;
  summary: string | null;
  is_included: boolean;
  status: 'new' | 'existing' | 'error';
  error?: string;
}

interface AnalyzeArticleResponse {
  success: boolean;
  article_id: string;
  entities: ArticleEntity;
  relevance_results: ArticleRelevanceResult[];
}

interface ReportGenerateRequest {
  client_id: string;
  report_date?: string;
}

interface ReportGenerateResponse {
  task_id: string;
  status: string;
  message: string;
}

interface RelevantClient {
  id: string;
  name: string;
  relevance_score: number;
  is_included: boolean;
  summary?: string;
}

interface SourceStats {
  source: string;
  count: number;
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
        const response = await axiosInstance.get('/clients', { 
          params: { limit: 100 } // Always use a safe limit
        });
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
        const response = await axiosInstance.get('/feeds', { 
          params: { limit: 100 } // Always use a safe limit
        });
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
          const safeParams = { ...params };
    
          // Enforce server limits
          if (safeParams?.limit && safeParams.limit > 100) {
            safeParams.limit = 100;
          }
          
          const response = await axiosInstance.get('/articles', { params: safeParams });
          return response.data;
        },
        getById: async (id: string): Promise<Article> => { // Add return type
          const response = await axiosInstance.get(`/articles/${id}`);
          return response.data;
        },
        getRelevant: async (clientId: string, params: any = {}): Promise<any[]> => { // Adjust return type
          const response = await axiosInstance.get('/articles/relevant', { // Should likely be /relevance endpoint? Check backend route
            params: { client_id: clientId, ...params },
          });
          return response.data;
        },
        analyze: async (id: string): Promise<AnalyzeArticleResponse> => {
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
        getRelevantClients: async (articleId: string): Promise<RelevantClient[]> => {
          const response = await axiosInstance.get(`/articles/${articleId}/relevance`);
          
          // If the endpoint returns a different structure, map it to what we need
          // This assumes the endpoint returns: { success: true, relevances: [...] }
          return response.data.relevances.map((relevance: any) => ({
            id: relevance.client_id,
            name: relevance.client_name,
            relevance_score: relevance.score,
            is_included: relevance.is_included,
            summary: relevance.summary || undefined
          }));
      }
    },
    articleStats: {
      getSourceCounts: async (): Promise<SourceStats[]> => {
        // Use the dedicated stats endpoint instead of trying to fetch all articles
        const response = await axiosInstance.get('/articles/stats/sources');
        return response.data.sources;
      }
    },
    reports: {
      getAll: async (params: any = {}): Promise<Report[]> => { // Add return type
        const safeParams = { ...params };
    
        // Enforce server limits
        if (safeParams?.limit && safeParams.limit > 100) {
          safeParams.limit = 100;
        }
        
        const response = await axiosInstance.get('/reports', { params: safeParams });
        return response.data;
      },
      getById: async (id: string): Promise<Report> => { // Adjust return type if it includes articles
        const response = await axiosInstance.get(`/reports/${id}`);
        return response.data;
      },
      generate: async (clientId: string, reportDate?: string): Promise<ReportGenerateResponse> => {
        const data: ReportGenerateRequest = { 
          client_id: clientId 
        };
        
        if (reportDate) {
          data.report_date = reportDate;
        }
        
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