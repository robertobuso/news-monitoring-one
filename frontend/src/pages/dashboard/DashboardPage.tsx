import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  ChartBarIcon, 
  DocumentTextIcon, 
  NewspaperIcon, 
  RssIcon, 
  UsersIcon 
} from '@heroicons/react/24/outline';
import { useAuth } from '../../app/providers/AuthProvider';
import api from '../../api/client';
import { format } from 'date-fns';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  
  const { data: clientsData, isLoading: isLoadingClients } = useQuery({
    queryKey: ['clients'],
    queryFn: () => api.clientProfiles.getAll()
  });
  
  const { data: reportsData, isLoading: isLoadingReports } = useQuery({
    queryKey: ['reports'],
    queryFn: () => api.reports.getAll({ limit: 5 })
  });
  
  const { data: articlesData, isLoading: isLoadingArticles } = useQuery({
    queryKey: ['articles'],
    queryFn: () => api.articles.getAll({ limit: 5 })
  });

  // Chart data for articles by source
  const chartData = {
    labels: ['Source 1', 'Source 2', 'Source 3', 'Source 4', 'Source 5'],
    datasets: [
      {
        label: 'Articles by Source',
        data: [12, 19, 8, 15, 10],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Articles by Source',
      },
    },
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-4 sm:p-6">
        <h2 className="text-lg font-semibold mb-4">Welcome, {user?.first_name}!</h2>
        <p className="text-gray-600">
          Here's an overview of your NewsMonitor activity.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white shadow rounded-lg p-4 sm:p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
              <UsersIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">
                {isLoadingClients ? '...' : clientsData?.length || 0}
              </h3>
              <p className="text-sm text-gray-500">Client Profiles</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white shadow rounded-lg p-4 sm:p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
              <DocumentTextIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">
                {isLoadingReports ? '...' : reportsData?.length || 0}
              </h3>
              <p className="text-sm text-gray-500">Reports Generated</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white shadow rounded-lg p-4 sm:p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
              <NewspaperIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">
                {isLoadingArticles ? '...' : articlesData?.length || 0}
              </h3>
              <p className="text-sm text-gray-500">Recent Articles</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white shadow rounded-lg p-4 sm:p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-purple-100 rounded-md p-3">
              <RssIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">5</h3>
              <p className="text-sm text-gray-500">Active Feeds</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chart and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart */}
        <div className="bg-white shadow rounded-lg p-4 sm:p-6">
          <h3 className="text-lg font-semibold mb-4">Analytics</h3>
          <div className="h-64">
            <Bar data={chartData} options={chartOptions} />
          </div>
        </div>
        
        {/* Recent Reports */}
        <div className="bg-white shadow rounded-lg p-4 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Recent Reports</h3>
            <Link to="/reports" className="text-sm font-medium text-blue-600 hover:text-blue-500">
              View all
            </Link>
          </div>
          
          {isLoadingReports ? (
            <div className="animate-pulse space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-12 bg-gray-200 rounded"></div>
              ))}
            </div>
          ) : reportsData && reportsData.length > 0 ? (
            <div className="space-y-4">
              {reportsData.map((report: any) => (
                <Link 
                  key={report.id} 
                  to={`/reports/${report.id}`}
                  className="block p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex justify-between">
                    <div>
                      <p className="font-medium">{report.client_name || 'Client Report'}</p>
                      <p className="text-sm text-gray-500">
                        {format(new Date(report.report_date), 'MMM d, yyyy')}
                      </p>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      report.status === 'ready' ? 'bg-green-100 text-green-800' :
                      report.status === 'sent' ? 'bg-blue-100 text-blue-800' :
                      report.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {report.status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <DocumentTextIcon className="h-12 w-12 mx-auto text-gray-400" />
              <p className="mt-2">No reports generated yet</p>
              <Link 
                to="/clients" 
                className="mt-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Create a Client Profile
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;