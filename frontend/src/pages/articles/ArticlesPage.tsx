import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  ArrowPathIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import api from '../../api/client'; // Import your API client
import { Article as ArticleType } from '../../types'; // Import your Article type/interface

const ArticlesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  // Keep state for input field separate initially if desired, or drive directly from searchParams
  const [localSearchTerm, setLocalSearchTerm] = useState(searchParams.get('search') || '');
  const [showFilters, setShowFilters] = useState(false);

  // Extract filter values from searchParams
  const search = searchParams.get('search') || undefined; // Use undefined if empty for cleaner query keys/params
  const clientId = searchParams.get('clientId') || undefined; // Not directly used by article endpoint? Check backend.
  const source = searchParams.get('source') || undefined;
  const dateFrom = searchParams.get('dateFrom') || undefined;
  const dateTo = searchParams.get('dateTo') || undefined;
  const feedId = searchParams.get('feedId') || undefined; // Add if filtering by feed on this page

  // Fetch real data
  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles', search, feedId, source, dateFrom, dateTo],
    queryFn: () => {
      console.log('Fetching articles with filters:', { search, feedId, source, dateFrom, dateTo });
      const apiParams: any = { limit: 20 }; // Use a reasonable default limit that the server accepts
      if (search) apiParams.search = search;
      if (feedId) apiParams.feed_id = feedId;
      if (source) apiParams.source = source;
      if (dateFrom) apiParams.date_from = dateFrom;
      if (dateTo) apiParams.date_to = dateTo;
  
      return api.articles.getAll(apiParams);
    }
  });

  // Fetch clients and sources if needed for filter dropdowns (replace mocks)
   const { data: clients } = useQuery({
     queryKey: ['clients'],
     queryFn: () => api.clientProfiles.getAll() // Assuming this API exists
   });

   const { data: sources } = useQuery({
    queryKey: ['articleSources'],
    queryFn: async () => {
      // Get the stats which already has the sources information
      const sourceStats = await api.articleStats.getSourceCounts();
      // Extract just the source names
      return sourceStats.map(stat => stat.source);
    }
  });


  // Update URL search parameters when filters change
  const handleFilterChange = (newParams: Record<string, string>) => {
    setSearchParams(prev => {
      const updated = new URLSearchParams(prev);
      Object.entries(newParams).forEach(([key, value]) => {
        if (value) {
          updated.set(key, value);
        } else {
          updated.delete(key); // Remove param if value is empty
        }
      });
      return updated;
    });
  };

  const handleSearch = () => {
     handleFilterChange({ search: localSearchTerm });
  };


  // Format date for display
  const formatDate = (dateString: string | Date) => { // Accept Date object too
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
      {/* Header and Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
         <h1 className="text-2xl font-bold text-gray-900">Articles</h1>
         {/* Display active filters if needed */}
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6 border-b">
          <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
            {/* Search Input */}
            <div className="relative flex-grow">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md ..."
                placeholder="Search articles..."
                value={localSearchTerm}
                onChange={(e) => setLocalSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 ..."
            >
              <AdjustmentsHorizontalIcon className="-ml-1 mr-2 h-5 w-5 text-gray-400" />
              Filters
            </button>
            {/* Apply Search Button */}
             <button
              onClick={handleSearch} // Apply only search term here
              className="inline-flex items-center px-4 py-2 border border-transparent ..."
            >
              Search
            </button>
             {/* Refresh Button */}
             <button
              onClick={() => refetch()} // Use react-query's refetch
              className="inline-flex items-center px-4 py-2 border border-transparent ..."
            >
              <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" />
              Refresh
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
             <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
              {/* Feed Filter (Example - add if needed on this page) */}
               {/* <div>
                  <label htmlFor="feed" className="block text-sm font-medium text-gray-700">Feed</label>
                  <select
                     id="feed"
                     className="..."
                     value={feedId || ''}
                     onChange={(e) => handleFilterChange({ feedId: e.target.value })}
                  >
                     <option value="">All Feeds</option>
                     // Populate with fetched feeds
                  </select>
               </div> */}
               {/* Source Filter */}
                <div>
                  <label htmlFor="source" className="block text-sm font-medium text-gray-700">Source</label>
                  <select
                     id="source"
                     className="mt-1 block w-full pl-3 pr-10 py-2 ..."
                     value={source || ''}
                     onChange={(e) => handleFilterChange({ source: e.target.value })}
                  >
                     <option value="">All Sources</option>
                     {sources?.map(src => ( // Use fetched sources
                        <option key={src} value={src}>{src}</option>
                     ))}
                  </select>
               </div>
               {/* Date Range Filter */}
                <div className="sm:col-span-1">
                  <label htmlFor="date-range" className="block text-sm font-medium text-gray-700">Date Range</label>
                  <div className="mt-1 flex space-x-2">
                     <input
                        type="date"
                        id="date-from"
                        className="block w-full shadow-sm ..."
                        value={dateFrom || ''}
                        onChange={(e) => handleFilterChange({ dateFrom: e.target.value })}
                     />
                     <span className="text-gray-500 self-center">to</span>
                     <input
                        type="date"
                        id="date-to"
                        className="block w-full shadow-sm ..."
                        value={dateTo || ''}
                        onChange={(e) => handleFilterChange({ dateTo: e.target.value })}
                     />
                  </div>
               </div>
             </div>
          )}
        </div>

        {/* Article List */}
        {isLoading ? (
          // Loading Skeleton
          <div className="p-4 sm:p-6">...</div>
        ) : articles && articles.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {articles.map((article) => ( // Use data from useQuery
              <li key={article.id}>
                <Link
                  to={`/articles/${article.id}`}
                  className="block hover:bg-gray-50"
                >
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      {/* Use real data */}
                      <h3 className="text-sm font-medium text-gray-900">{article.title}</h3>
                      <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-gray-500">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {article.source} {/* Use real data */}
                          </span>
                          {article.author && (
                            <span className="ml-2">by {article.author}</span> /* Use real data */
                          )}
                        </p>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        <p>{formatDate(article.published_at)}</p> {/* Use real data */}
                      </div>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <div className="p-4 sm:p-6 text-center text-gray-500">
            {/* Adjusted message */}
            <p>No articles found{search || feedId || source || dateFrom || dateTo ? ' matching your filters' : ''}.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArticlesPage;