export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }
  
  export interface ClientProfile {
    id: string;
    user_id: string;
    name: string;
    description?: string;
    industry: string;
    keywords: string[];
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }
  
  export interface Feed {
    id: string;
    name: string;
    url: string;
    type: 'rss' | 'api' | 'web';
    check_frequency: number;
    is_active: boolean;
    last_checked?: string;
    health_status: 'healthy' | 'warning' | 'error';
    created_at: string;
    updated_at: string;
  }
  
  export interface ArticleMetaData {
    entities?: {
      organizations?: string[];
      locations?: string[];
      people?: string[];
      topics?: string[];
    };
    word_count?: number;
    reading_time_minutes?: number;
    tags?: string[];
    urls?: string[];
    [key: string]: any;
  }
  
  export interface Article {
    id: string;
    feed_id: string;
    title: string;
    url: string;
    source: string;
    published_at: string;
    author?: string;
    content: string;
    meta_data: ArticleMetaData;
    created_at: string;
  }
  
  export interface ArticleRelevance {
    id: string;
    article_id: string;
    client_id: string;
    relevance_score: number;
    summary?: string;
    is_included: boolean;
    created_at: string;
  }
  
  export interface ReportArticle {
    id: string;
    report_id: string;
    article_id: string;
    summary?: string;
    position: number;
  }
  
  export interface Report {
    id: string;
    user_id: string;
    client_id: string;
    client_name?: string; // Sometimes included in responses
    report_date: string;
    pdf_path?: string;
    created_at: string;
    sent_at?: string;
    recipient_email?: string;
    status: 'pending' | 'generating' | 'ready' | 'sent' | 'error';
    report_articles?: ReportArticle[];
    executive_summary?: string;
    articles?: Array<{
      id: string;
      title: string;
      source: string;
      published_at: string;
      relevance_score: number;
      summary?: string;
    }>;
  }
  
  export interface RelevantClient {
    id: string;
    name: string;
    relevance_score: number;
    is_included: boolean;
    summary?: string;
  }
  
  export interface SourceStats {
    source: string;
    count: number;
  }
  
  // Other types can be added as needed