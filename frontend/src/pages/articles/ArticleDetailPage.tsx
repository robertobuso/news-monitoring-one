import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'; // Added useQueryClient
import {
  ArrowLeftIcon,
  DocumentTextIcon,
  ShareIcon,
  PaperClipIcon,
  CheckIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import api from '../../api/client';
import { Article as ArticleType, RelevantClient } from '../../types';

const ArticleDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedClients, setSelectedClients] = useState<string[]>([]);
  const [showShareModal, setShowShareModal] = useState(false);
  
  // Define useQueryClient instance
  const queryClient = useQueryClient();

  const { data: article, isLoading, error } = useQuery({
    queryKey: ['article', id],
    queryFn: () => api.articles.getById(id as string),
    enabled: !!id
  });

  const { data: relevantClients, isLoading: isLoadingClients, refetch: refetchClients } = useQuery({
    queryKey: ['article-clients', id],
    queryFn: () => api.articles.getRelevantClients(id as string),
    enabled: !!id
  });

  const shareMutation = useMutation({
    mutationFn: (data: { articleId: string; clientIds: string[] }) => {
      // TODO: Replace with actual API call
      console.log('Sharing article with clients:', data);
       // return api.articles.shareWithClients(data.articleId, data.clientIds);
      return Promise.resolve(data);
    },
    onSuccess: () => {
      toast.success('Article shared with selected clients');
      setShowShareModal(false);
    },
    onError: () => {
      toast.error('Failed to share article');
    }
  });

  const analyzeMutation = useMutation({
    mutationFn: (articleId: string) => {
      return api.articles.analyze(articleId);
    },
    onSuccess: (data) => {
      console.log("Analysis results:", data);
      toast.success('Article analysis completed');
      
      // Invalidate relevant queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['article', id] });
      queryClient.invalidateQueries({ queryKey: ['article-clients', id] });
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      
      // Explicitly refetch the relevant clients to update the UI immediately
      refetchClients();
      
      // If any relevance calculations were created/updated, refresh client data too
      if (data.relevance_results?.length > 0) {
        queryClient.invalidateQueries({ queryKey: ['clients'] });
        
        // Get unique client IDs from the relevance results
        const clientIds = [...new Set(data.relevance_results.map(r => r.client_id))];
        
        // Invalidate queries for each affected client
        clientIds.forEach(clientId => {
          queryClient.invalidateQueries({ queryKey: ['client', clientId] });
          queryClient.invalidateQueries({ queryKey: ['clientArticles', clientId] });
          queryClient.invalidateQueries({ queryKey: ['clientReports', clientId] });
        });
      }
    },
    onError: (error: any) => {
      console.error('Failed to analyze article:', error);
      toast.error(error.response?.data?.detail || 'Failed to analyze article');
    }
  });

  const handleShare = () => {
    if (selectedClients.length === 0) {
      toast.error('Please select at least one client');
      return;
    }
    
    shareMutation.mutate({
      articleId: id || '',
      clientIds: selectedClients
    });
  };

  const toggleClientSelection = (clientId: string) => {
    setSelectedClients(prev => 
      prev.includes(clientId)
        ? prev.filter(id => id !== clientId)
        : [...prev, clientId]
    );
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    // Loading state
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>;
  }

  if (error || !article) {
     // Error or not found state
    return <div className="text-center py-12">
      <h3 className="text-lg font-medium text-gray-900">Article not found</h3>
      <p className="mt-2 text-sm text-gray-500">
        The article you're looking for doesn't exist or you don't have access to it.
      </p>
      <div className="mt-6">
        <Link
          to="/articles"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
        >
          <ArrowLeftIcon className="-ml-1 mr-2 h-5 w-5" />
          Back to Articles
        </Link>
      </div>
    </div>;
  }

  // ---- RENDER ----
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center">
          <Link to="/articles" className="mr-4 text-gray-500 hover:text-gray-700">
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 leading-tight">{article.title}</h1>
        </div>
        <div className="mt-3 sm:mt-0 flex space-x-3">
          <button
            onClick={() => article?.id && analyzeMutation.mutate(article.id)} 
            disabled={analyzeMutation.isPending}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <DocumentTextIcon className="-ml-0.5 mr-2 h-4 w-4" />
            Analyze
          </button>
          <button
            onClick={() => setShowShareModal(true)}
            className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ShareIcon className="-ml-0.5 mr-2 h-4 w-4" />
            Share
          </button>
        </div>
      </div>

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
                    <ShareIcon className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Share with Clients</h3>
                    <div className="mt-4">
                      <p className="text-sm text-gray-500 mb-4">
                        Select clients to share this article with:
                      </p>
                      <div className="max-h-60 overflow-y-auto">
                        {isLoadingClients ? (
                          <div className="py-4 text-center">Loading clients...</div>
                        ) : relevantClients && relevantClients.length > 0 ? (
                          <ul className="divide-y divide-gray-200">
                            {relevantClients?.map((client) => (
                              <li key={client.id} className="py-3">
                                <div className="flex items-center">
                                  <input
                                    id={`client-${client.id}`}
                                    name={`client-${client.id}`}
                                    type="checkbox"
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    checked={selectedClients.includes(client.id)}
                                    onChange={() => toggleClientSelection(client.id)}
                                  />
                                  <label htmlFor={`client-${client.id}`} className="ml-3 block text-sm text-gray-700">
                                    {client.name}
                                    <span className={`ml-2 inline-block px-2 py-0.5 text-xs font-medium rounded-full ${
                                      client.relevance_score >= 0.8 ? 'bg-green-100 text-green-800' :
                                      client.relevance_score >= 0.5 ? 'bg-yellow-100 text-yellow-800' :
                                      'bg-gray-100 text-gray-800'
                                    }`}>
                                      {(client.relevance_score * 100).toFixed(0)}% relevant
                                    </span>
                                  </label>
                                </div>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div className="py-4 text-center text-gray-500">No relevant clients found</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={handleShare}
                  disabled={shareMutation.isPending}
                >
                  {shareMutation.isPending ? 'Sharing...' : 'Share'}
                </button>
                <button
                  type="button"
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setShowShareModal(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Article Content */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6">
          <div className="flex flex-wrap items-center text-sm text-gray-500 mb-4">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-3">
              {article.source}
            </span>
            {article.author && (
              <span className="mr-3">By {article.author}</span>
            )}
            <span>Published {formatDate(article.published_at)}</span>
            <span className="ml-auto">
              <a 
                href={article.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800"
              >
                Original Source
              </a>
            </span>
          </div>

          <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: article.content }} />

          {/* Metadata Section */}
          {/* Check if meta_data exists and is an object before accessing properties */}
          {article.meta_data && typeof article.meta_data === 'object' && Object.keys(article.meta_data).length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-500">Article Metadata</h3>
              <dl className="mt-2 grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                {/* Access using meta_data */}
                {article.meta_data.word_count && (
                  <div>
                    <dt className="text-xs text-gray-500">Word Count</dt>
                    <dd className="text-sm text-gray-900">{article.meta_data.word_count} words</dd>
                  </div>
                )}
                {article.meta_data.reading_time_minutes && (
                  <div>
                    <dt className="text-xs text-gray-500">Reading Time</dt>
                    <dd className="text-sm text-gray-900">{article.meta_data.reading_time_minutes} min read</dd>
                  </div>
                )}
                {/* Safely access nested topics */}
                {article.meta_data.entities?.topics && Array.isArray(article.meta_data.entities.topics) && article.meta_data.entities.topics.length > 0 && (
                  <div className="sm:col-span-2">
                    <dt className="text-xs text-gray-500">Topics</dt>
                    <dd className="text-sm text-gray-900">
                      <div className="flex flex-wrap gap-2 mt-1">
                        {article.meta_data.entities.topics.map((topic, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          )}
        </div>
      </div>

      {/* Relevant Clients */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Relevant Clients</h3>
          <button
            onClick={() => setShowShareModal(true)}
            className="text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Share with clients
          </button>
        </div>
        <div className="border-t border-gray-200">
          {isLoadingClients ? (
            <div className="p-4 sm:p-6 text-center">
              <div className="animate-spin inline-block h-8 w-8 border-t-2 border-b-2 border-blue-500 rounded-full"></div>
              <p className="mt-2 text-gray-500">Loading clients...</p>
            </div>
          ) : relevantClients && relevantClients.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {relevantClients
                .sort((a, b) => b.relevance_score - a.relevance_score)
                .map((client) => (
                <li key={client.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <Link to={`/clients/${client.id}`} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <span className="text-blue-600 font-medium text-lg">
                          {client.name.charAt(0)}
                        </span>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-900">{client.name}</p>
                        <div className="mt-1 flex items-center">
                          <div className="flex items-center">
                            <div className="w-24 bg-gray-200 rounded-full h-2.5">
                              <div 
                                className={`h-2.5 rounded-full ${
                                  client.relevance_score >= 0.8 ? 'bg-green-500' :
                                  client.relevance_score >= 0.5 ? 'bg-yellow-500' :
                                  'bg-gray-500'
                                }`}
                                style={{ width: `${client.relevance_score * 100}%` }}
                              ></div>
                            </div>
                            <p className="ml-2 text-xs text-gray-500">
                              {(client.relevance_score * 100).toFixed(0)}% match
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                    {selectedClients.includes(client.id) && (
                      <CheckIcon className="h-5 w-5 text-green-500" />
                    )}
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-center py-6 text-gray-500">
              <p>No relevant clients found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ArticleDetailPage;