import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  ArrowPathIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';

const ArticlesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || '');
  const [showFilters, setShowFilters] = useState(false);
  const clientId = searchParams.get('clientId');
  const source = searchParams.get('source');
  const dateFrom = searchParams.get('dateFrom');
  const dateTo = searchParams.get('dateTo');

  // Mock data for articles
  const mockArticles = [
    {
      id: '1',
      title: 'Introduction to Artificial Intelligence',
      source: 'Tech News',
      author: 'John Smith',
      published_at: '2025-04-28T10:00:00.000Z',
      content: 'AI is transforming industries across the board...',
      url: 'https://example.com/ai-intro'
    },
    {
      id: '2',
      title: 'New Advancements in Machine Learning',
      source: 'AI Weekly',
      author: 'Jane Doe',
      published_at: '2025-04-27T14:30:00.000Z',
      content: 'Machine learning models are becoming increasingly sophisticated...',
      url: 'https://example.com/ml-advancements'
    },
    {
      id: '3',
      title: 'Financial Markets Report Q1 2025',
      source: 'Finance Daily',
      author: 'Robert Johnson',
      published_at: '2025-04-25T09:15:00.000Z',
      content: 'Markets have shown resilience in the first quarter...',
      url: 'https://example.com/finance-q1-2025'
    },
    {
      id: '4',
      title: 'Sustainable Energy Solutions on the Rise',
      source: 'Green Tech',
      author: 'Lisa Chen',
      published_at: '2025-04-23T11:45:00.000Z',
      content: 'Renewable energy adoption is accelerating globally...',
      url: 'https://example.com/sustainable-energy'
    },
    {
      id: '5',
      title: 'The Future of Remote Work',
      source: 'Business Insider',
      author: 'Michael Brown',
      published_at: '2025-04-20T16:20:00.000Z',
      content: 'Companies are adapting to hybrid work models...',
      url: 'https://example.com/future-remote-work'
    }
  ];

  // Mock data for client profiles
  const mockClients = [
    { id: '1', name: 'Tech Company' },
    { id: '2', name: 'Finance Corp' },
    { id: '3', name: 'Green Energy Startup' },
  ];

  // Mock data for sources
  const mockSources = [
    'Tech News',
    'AI Weekly',
    'Finance Daily',
    'Green Tech',
    'Business Insider'
  ];

  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles', searchTerm, clientId, source, dateFrom, dateTo],
    queryFn: () => {
      // Mock API call
      console.log('Fetching articles with filters:', { searchTerm, clientId, source, dateFrom, dateTo });
      
      // Apply filters
      let filteredArticles = [...mockArticles];
      
      if (searchTerm) {
        filteredArticles = filteredArticles.filter(article => 
          article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          article.content.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }
      
      if (source) {
        filteredArticles = filteredArticles.filter(article => 
          article.source === source
        );
      }
      
      if (dateFrom) {
        const fromDate = new Date(dateFrom);
        filteredArticles = filteredArticles.filter(article => 
          new Date(article.published_at) >= fromDate
        );
      }
      
      if (dateTo) {
        const toDate = new Date(dateTo);
        filteredArticles = filteredArticles.filter(article => 
          new Date(article.published_at) <= toDate
        );
      }
      
      if (clientId) {
        // In a real app, we would filter by relevance to client
        // Here we just return a subset for demonstration
        filteredArticles = filteredArticles.slice(0, 3);
      }
      
      return Promise.resolve(filteredArticles);
    }
  });

  // Update URL when filters change
  const applyFilters = () => {
    const params: any = {};
    if (searchTerm) params.search = searchTerm;
    if (clientId) params.clientId = clientId;
    if (source) params.source = source;
    if (dateFrom) params.dateFrom = dateFrom;
    if (dateTo) params.dateTo = dateTo;
    
    setSearchParams(params);
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Articles</h1>
        {clientId && (
          <div className="mt-2 sm:mt-0">
            <span className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              Filtered by client: {mockClients.find(c => c.id === clientId)?.name || 'Unknown Client'}
            </span>
          </div>
        )}
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6 border-b">
          <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
            <div className="relative flex-grow">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Search articles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <AdjustmentsHorizontalIcon className="-ml-1 mr-2 h-5 w-5 text-gray-400" />
              Filters
            </button>
            <button
              onClick={applyFilters}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" />
              Refresh
            </button>
          </div>

          {showFilters && (
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <label htmlFor="client" className="block text-sm font-medium text-gray-700">Client</label>
                <select
                  id="client"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  value={clientId || ''}
                  onChange={(e) => setSearchParams(prev => {
                    const newParams = new URLSearchParams(prev);
                    if (e.target.value) {
                      newParams.set('clientId', e.target.value);
                    } else {
                      newParams.delete('clientId');
                    }
                    return newParams;
                  })}
                >
                  <option value="">All Clients</option>
                  {mockClients.map(client => (
                    <option key={client.id} value={client.id}>{client.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="source" className="block text-sm font-medium text-gray-700">Source</label>
                <select
                  id="source"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  value={source || ''}
                  onChange={(e) => setSearchParams(prev => {
                    const newParams = new URLSearchParams(prev);
                    if (e.target.value) {
                      newParams.set('source', e.target.value);
                    } else {
                      newParams.delete('source');
                    }
                    return newParams;
                  })}
                >
                  <option value="">All Sources</option>
                  {mockSources.map(src => (
                    <option key={src} value={src}>{src}</option>
                  ))}
                </select>
              </div>
              <div className="sm:col-span-1">
                <label htmlFor="date-range" className="block text-sm font-medium text-gray-700">Date Range</label>
                <div className="mt-1 flex space-x-2">
                  <input
                    type="date"
                    id="date-from"
                    className="block w-full shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm border-gray-300 rounded-md"
                    value={dateFrom || ''}
                    onChange={(e) => setSearchParams(prev => {
                      const newParams = new URLSearchParams(prev);
                      if (e.target.value) {
                        newParams.set('dateFrom', e.target.value);
                      } else {
                        newParams.delete('dateFrom');
                      }
                      return newParams;
                    })}
                  />
                  <span className="text-gray-500 self-center">to</span>
                  <input
                    type="date"
                    id="date-to"
                    className="block w-full shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm border-gray-300 rounded-md"
                    value={dateTo || ''}
                    onChange={(e) => setSearchParams(prev => {
                      const newParams = new URLSearchParams(prev);
                      if (e.target.value) {
                        newParams.set('dateTo', e.target.value);
                      } else {
                        newParams.delete('dateTo');
                      }
                      return newParams;
                    })}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {isLoading ? (
          <div className="p-4 sm:p-6">
            <div className="animate-pulse space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-24 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : articles && articles.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {articles.map((article) => (
              <li key={article.id}>
                <Link
                  to={`/articles/${article.id}`}
                  className="block hover:bg-gray-50"
                >
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-medium text-gray-900">{article.title}</h3>
                      <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-gray-500">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {article.source}
                          </span>
                          {article.author && (
                            <span className="ml-2">by {article.author}</span>
                          )}
                        </p>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        <p>{formatDate(article.published_at)}</p>
                      </div>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <div className="p-4 sm:p-6 text-center text-gray-500">
            {searchTerm || clientId || source || dateFrom || dateTo ? (
              <p>No articles found matching your filters.</p>
            ) : (
              <p>No articles available.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ArticlesPage;