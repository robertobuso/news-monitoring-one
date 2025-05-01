import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  AdjustmentsHorizontalIcon, 
  MagnifyingGlassIcon,
  DocumentTextIcon,
  ChevronRightIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';

const ReportsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [showFilters, setShowFilters] = useState(false);
  const clientId = searchParams.get('clientId');
  const dateFrom = searchParams.get('dateFrom');
  const dateTo = searchParams.get('dateTo');
  const status = searchParams.get('status');

  const statusOptions = [
    { value: 'pending', label: 'Pending' },
    { value: 'generating', label: 'Generating' },
    { value: 'ready', label: 'Ready' },
    { value: 'sent', label: 'Sent' },
    { value: 'error', label: 'Error' }
  ];

  const { data: clients } = useQuery({
    queryKey: ['clients'],
    queryFn: () => api.clientProfiles.getAll()
  });
  
  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports', clientId, dateFrom, dateTo, status],
    queryFn: () => {
      // Build query parameters
      const params: any = {};
      if (clientId) params.client_id = clientId;
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      if (status) params.status = status;
      
      return api.reports.getAll(params);
    }
  });

  // Formatting functions
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'sent':
        return 'bg-green-100 text-green-800';
      case 'ready':
        return 'bg-blue-100 text-blue-800';
      case 'generating':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        {clientId && (
          <div className="mt-2 sm:mt-0">
            <span className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              Client: {clients.find(c => c.id === clientId)?.name || 'Unknown'}
            </span>
          </div>
        )}
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6 border-b">
          <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
            <div className="flex-grow">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <AdjustmentsHorizontalIcon className="-ml-1 mr-2 h-5 w-5 text-gray-400" />
                {showFilters ? 'Hide Filters' : 'Show Filters'}
              </button>
            </div>
            <Link
              to="/reports/generate"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <DocumentTextIcon className="-ml-1 mr-2 h-5 w-5" />
              Generate Report
            </Link>
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
                  {clients.map(client => (
                    <option key={client.id} value={client.id}>{client.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                <select
                  id="status"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  value={status || ''}
                  onChange={(e) => setSearchParams(prev => {
                    const newParams = new URLSearchParams(prev);
                    if (e.target.value) {
                      newParams.set('status', e.target.value);
                    } else {
                      newParams.delete('status');
                    }
                    return newParams;
                  })}
                >
                  <option value="">All Statuses</option>
                  {statusOptions.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>
              <div>
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
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : reports && reports.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {reports.map((report) => (
              <li key={report.id}>
                <div className="block hover:bg-gray-50">
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <Link
                        to={`/reports/${report.id}`}
                        className="text-sm font-medium text-blue-600 hover:text-blue-900"
                      >
                        {report.client_name} Report - {formatDate(report.report_date)}
                      </Link>
                      <div className="ml-2 flex-shrink-0 flex">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(report.status)}`}
                        >
                          {report.status}
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-gray-500">
                          <DocumentTextIcon className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
                          Created on {formatDate(report.created_at)}
                        </p>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        {report.sent_at ? (
                          <p>Sent to {report.recipient_email}</p>
                        ) : (
                          <p>Not sent yet</p>
                        )}
                        
                        <div className="ml-4 flex">
                          <Link
                            to={`/reports/${report.id}`}
                            className="text-blue-600 hover:text-blue-900 mr-4"
                          >
                            <ChevronRightIcon className="h-5 w-5" />
                          </Link>
                          
                          {report.pdf_path && (
                            <a
                              href={`/api/v1/reports/download/${report.id}`}
                              className="text-gray-500 hover:text-gray-700"
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <ArrowDownTrayIcon className="h-5 w-5" />
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="p-4 sm:p-6 text-center text-gray-500">
            {clientId || dateFrom || dateTo || status ? (
              <p>No reports found matching your filters.</p>
            ) : (
              <p>No reports generated yet.</p>
            )}
            <Link
              to="/reports/generate"
              className="mt-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <DocumentTextIcon className="-ml-1 mr-2 h-5 w-5" />
              Generate Report
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;