import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  ArrowLeftIcon, 
  ArrowDownTrayIcon,
  EnvelopeIcon,
  DocumentTextIcon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

const ReportDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showSendModal, setShowSendModal] = useState(false);
  const [email, setEmail] = useState('');

  // Mock report data
  const mockReport = {
    id: id || '1',
    client_id: '1',
    client_name: 'Tech Company',
    report_date: '2025-04-30T00:00:00.000Z',
    created_at: '2025-04-30T12:00:00.000Z',
    sent_at: '2025-04-30T12:05:00.000Z',
    status: 'sent',
    recipient_email: 'client@example.com',
    pdf_path: '/reports/tech_report_20250430.pdf',
    executive_summary: `
      This weekly report highlights key developments in the tech industry that may impact your business. 
      There was significant news around AI regulations, with new guidelines proposed by the EU. 
      Several major tech companies announced quarterly earnings that exceeded expectations, 
      indicating strong market performance despite economic concerns. 
      Your competitors have made progress in cloud computing solutions, with announcements of new 
      features that may require strategic response. We recommend focusing on your AI ethics 
      initiatives as a market differentiator given the increasing regulatory scrutiny.
    `,
    articles: [
      {
        id: '1',
        title: 'New AI Regulations Proposed by EU Commission',
        source: 'Tech News',
        published_at: '2025-04-28T10:00:00.000Z',
        relevance_score: 0.92,
        summary: 'The European Commission has proposed new regulations for AI systems, focusing on transparency and ethical use. This could impact global tech companies operating in European markets.'
      },
      {
        id: '2',
        title: 'Tech Giants Report Strong Quarterly Earnings',
        source: 'Finance Daily',
        published_at: '2025-04-27T14:30:00.000Z',
        relevance_score: 0.85,
        summary: 'Major tech companies reported earnings exceeding analyst expectations, with particularly strong performance in cloud services and AI applications.'
      },
      {
        id: '3',
        title: 'Advancements in Quantum Computing Show Promise',
        source: 'Science Today',
        published_at: '2025-04-26T09:15:00.000Z',
        relevance_score: 0.78,
        summary: 'Recent breakthroughs in quantum computing could accelerate development timelines, potentially bringing practical applications to market sooner than expected.'
      },
      {
        id: '4',
        title: 'Competitors Launch New Cloud Features',
        source: 'Business Insider',
        published_at: '2025-04-25T11:45:00.000Z',
        relevance_score: 0.89,
        summary: 'Your key competitors have announced new features for their cloud platforms, focusing on enhanced security and integration capabilities.'
      },
      {
        id: '5',
        title: 'AI Ethics Becoming Key Market Differentiator',
        source: 'Marketing Weekly',
        published_at: '2025-04-24T16:20:00.000Z',
        relevance_score: 0.81,
        summary: 'Companies with strong AI ethics policies are seeing improved customer trust and brand perception, according to a new market research study.'
      }
    ]
  };

  // Mock API calls
  const { data: report, isLoading } = useQuery({
    queryKey: ['report', id],
    queryFn: () => {
      console.log('Fetching report with id:', id);
      return Promise.resolve(mockReport);
    },
    enabled: !!id
  });

  const sendReportMutation = useMutation({
    mutationFn: (data: { reportId: string; email: string }) => {
      console.log('Sending report:', data);
      return Promise.resolve(data);
    },
    onSuccess: () => {
      toast.success('Report sent successfully');
      setShowSendModal(false);
    },
    onError: () => {
      toast.error('Failed to send report');
    }
  });

  const duplicateReportMutation = useMutation({
    mutationFn: (reportId: string) => {
      console.log('Duplicating report:', reportId);
      return Promise.resolve({ id: 'new-report-id' });
    },
    onSuccess: (data) => {
      toast.success('Report duplicated successfully');
      navigate(`/reports/${data.id}`);
    },
    onError: () => {
      toast.error('Failed to duplicate report');
    }
  });

  const handleSendReport = () => {
    if (!email) {
      toast.error('Please enter an email address');
      return;
    }
    
    sendReportMutation.mutate({
      reportId: id || '',
      email: email
    });
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
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

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Report not found</h3>
        <p className="mt-2 text-sm text-gray-500">
          The report you're looking for doesn't exist or you don't have access to it.
        </p>
        <div className="mt-6">
          <Link
            to="/reports"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            <ArrowLeftIcon className="-ml-1 mr-2 h-5 w-5" />
            Back to Reports
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center">
          <Link to="/reports" className="mr-4 text-gray-500 hover:text-gray-700">
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">{report.client_name} Report</h1>
          <span className={`ml-3 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(report.status)}`}>
            {report.status}
          </span>
        </div>
        <div className="mt-3 sm:mt-0 flex space-x-3">
          {report.pdf_path && (
            <a
              href={`/api/v1/reports/download/${report.id}`}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              target="_blank"
              rel="noopener noreferrer"
            >
              <ArrowDownTrayIcon className="-ml-0.5 mr-2 h-4 w-4" />
              Download PDF
            </a>
          )}
          <button
            onClick={() => duplicateReportMutation.mutate(report.id)}
            disabled={duplicateReportMutation.isPending}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <DocumentDuplicateIcon className="-ml-0.5 mr-2 h-4 w-4" />
            Duplicate
          </button>
          {(report.status === 'ready' || report.status === 'sent') && (
            <button
              onClick={() => setShowSendModal(true)}
              className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <EnvelopeIcon className="-ml-0.5 mr-2 h-4 w-4" />
              Send Report
            </button>
          )}
        </div>
      </div>

      {/* Send Email Modal */}
      {showSendModal && (
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
                    <EnvelopeIcon className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Send Report</h3>
                    <div className="mt-4">
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                        Recipient Email
                      </label>
                      <input
                        type="email"
                        name="email"
                        id="email"
                        className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder={report.recipient_email || "client@example.com"}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={handleSendReport}
                  disabled={sendReportMutation.isPending}
                >
                  {sendReportMutation.isPending ? 'Sending...' : 'Send'}
                </button>
                <button
                  type="button"
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setShowSendModal(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Report Details */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6">
          <div className="flex flex-wrap items-center text-sm text-gray-500 mb-4">
            <span className="mr-3">Report Date: {formatDate(report.report_date)}</span>
            <span className="mr-3">Created: {new Date(report.created_at).toLocaleString()}</span>
            {report.sent_at && (
              <span>Sent to: {report.recipient_email} at {new Date(report.sent_at).toLocaleString()}</span>
            )}
          </div>

          <div className="mt-4">
            <h2 className="text-lg font-medium text-gray-900 mb-2">Executive Summary</h2>
            <div className="bg-gray-50 p-4 rounded-md">
              <p className="text-sm text-gray-700 whitespace-pre-line">{report.executive_summary}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Articles in Report */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg font-medium text-gray-900">Articles</h3>
          <p className="mt-1 text-sm text-gray-500">
            Key articles included in this report, sorted by relevance.
          </p>
        </div>
        <div className="border-t border-gray-200">
          <ul className="divide-y divide-gray-200">
            {report.articles.map((article) => (
              <li key={article.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                <Link to={`/articles/${article.id}`} className="block">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-blue-600">{article.title}</p>
                    <div className="ml-2 flex-shrink-0 flex">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        article.relevance_score > 0.8 ? 'bg-green-100 text-green-800' :
                        article.relevance_score > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {(article.relevance_score * 100).toFixed(0)}% relevant
                      </span>
                    </div>
                  </div>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">{article.summary}</p>
                    <div className="mt-2 flex items-center text-xs text-gray-500">
                      <span>{article.source} • {new Date(article.published_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ReportDetailPage;