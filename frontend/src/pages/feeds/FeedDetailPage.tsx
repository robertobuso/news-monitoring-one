import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  ArrowLeftIcon, 
  PencilIcon,
  TrashIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { useFormik } from 'formik';
import * as Yup from 'yup';

const FeedDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Mock feed data until API client is updated
  const mockFeed = {
    id: id || 'feed1',
    name: 'Tech News',
    url: 'https://example.com/rss',
    type: 'rss',
    check_frequency: 60,
    is_active: true,
    health_status: 'healthy',
    last_checked: new Date().toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  const { data: feed, isLoading, error } = useQuery({
    queryKey: ['feed', id],
    queryFn: () => {
      // Mock API call
      console.log('Fetching feed with id:', id);
      return Promise.resolve(mockFeed);
    },
    enabled: !!id
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) => {
      // Mock API call
      console.log('Updating feed with data:', data);
      return Promise.resolve({ ...mockFeed, ...data });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed', id] });
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
      setIsEditing(false);
      toast.success('Feed updated successfully');
    },
    onError: () => {
      toast.error('Failed to update feed');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: () => {
      // Mock API call
      console.log('Deleting feed with id:', id);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
      navigate('/feeds');
      toast.success('Feed deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete feed');
    }
  });

  const processMutation = useMutation({
    mutationFn: () => {
      // Mock API call
      console.log('Processing feed with id:', id);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feed', id] });
      toast.success('Feed processing started');
    },
    onError: () => {
      toast.error('Failed to process feed');
    }
  });

  const formik = useFormik({
    initialValues: {
      name: feed?.name || '',
      url: feed?.url || '',
      type: feed?.type || 'rss',
      check_frequency: feed?.check_frequency || 60,
      is_active: feed?.is_active || true
    },
    enableReinitialize: true,
    validationSchema: Yup.object({
      name: Yup.string().required('Name is required'),
      url: Yup.string()
        .url('Must be a valid URL')
        .required('URL is required'),
      type: Yup.string().required('Type is required'),
      check_frequency: Yup.number()
        .min(5, 'Minimum check frequency is 5 minutes')
        .required('Check frequency is required'),
    }),
    onSubmit: (values) => {
      updateMutation.mutate(values);
    },
  });

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'warning':
      case 'error':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error || !feed) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Feed not found</h3>
        <p className="mt-2 text-sm text-gray-500">
          The feed you're looking for doesn't exist or you don't have access to it.
        </p>
        <div className="mt-6">
          <Link
            to="/feeds"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            <ArrowLeftIcon className="-ml-1 mr-2 h-5 w-5" />
            Back to Feeds
          </Link>
        </div>
      </div>
    );
  }

  const feedTypes = [
    { value: 'rss', label: 'RSS Feed' },
    { value: 'api', label: 'API' },
    { value: 'web', label: 'Web Scraper' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center">
          <Link to="/feeds" className="mr-4 text-gray-500 hover:text-gray-700">
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">{feed.name}</h1>
          <div className="ml-3 flex items-center">
            {getHealthStatusIcon(feed.health_status)}
            <span className={`ml-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getHealthStatusColor(feed.health_status)}`}>
              {feed.health_status}
            </span>
          </div>
        </div>
        <div className="mt-3 sm:mt-0 flex space-x-3">
          {!isEditing && (
            <>
              <button
                onClick={() => processMutation.mutate()}
                disabled={processMutation.isPending}
                className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <ArrowPathIcon className="-ml-0.5 mr-2 h-4 w-4" />
                Process Now
              </button>
              <button
                onClick={() => setIsEditing(true)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PencilIcon className="-ml-0.5 mr-2 h-4 w-4" />
                Edit
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <TrashIcon className="-ml-0.5 mr-2 h-4 w-4" />
                Delete
              </button>
            </>
          )}
          {isEditing && (
            <button
              onClick={() => setIsEditing(false)}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <XMarkIcon className="-ml-0.5 mr-2 h-4 w-4" />
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                    <TrashIcon className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Delete Feed</h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        Are you sure you want to delete this feed? This action cannot be undone.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => deleteMutation.mutate()}
                >
                  Delete
                </button>
                <button
                  type="button"
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setShowDeleteConfirm(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feed Form or Details */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {isEditing ? (
          <div className="p-4 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Edit Feed</h2>
            <form onSubmit={formik.handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Feed Name
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  className={`mt-1 block w-full rounded-md border ${
                    formik.touched.name && formik.errors.name 
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                  } shadow-sm sm:text-sm`}
                  value={formik.values.name}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                />
                {formik.touched.name && formik.errors.name && (
                  <p className="mt-1 text-sm text-red-600">{formik.errors.name}</p>
                )}
              </div>

              <div>
                <label htmlFor="url" className="block text-sm font-medium text-gray-700">
                  Feed URL
                </label>
                <input
                  id="url"
                  name="url"
                  type="text"
                  className={`mt-1 block w-full rounded-md border ${
                    formik.touched.url && formik.errors.url 
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                  } shadow-sm sm:text-sm`}
                  value={formik.values.url}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                />
                {formik.touched.url && formik.errors.url && (
                  <p className="mt-1 text-sm text-red-600">{formik.errors.url}</p>
                )}
              </div>

              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                  Feed Type
                </label>
                <select
                  id="type"
                  name="type"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  value={formik.values.type}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                >
                  {feedTypes.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
                {formik.touched.type && formik.errors.type && (
                  <p className="mt-1 text-sm text-red-600">{formik.errors.type}</p>
                )}
              </div>

              <div>
                <label htmlFor="check_frequency" className="block text-sm font-medium text-gray-700">
                  Check Frequency (minutes)
                </label>
                <input
                  id="check_frequency"
                  name="check_frequency"
                  type="number"
                  min="5"
                  className={`mt-1 block w-full rounded-md border ${
                    formik.touched.check_frequency && formik.errors.check_frequency 
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                  } shadow-sm sm:text-sm`}
                  value={formik.values.check_frequency}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                />
                {formik.touched.check_frequency && formik.errors.check_frequency && (
                  <p className="mt-1 text-sm text-red-600">{formik.errors.check_frequency}</p>
                )}
              </div>

              <div className="flex items-center">
                <input
                  id="is_active"
                  name="is_active"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  checked={formik.values.is_active}
                  onChange={formik.handleChange}
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                  Active
                </label>
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="mr-3 px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateMutation.isPending}
                  className="px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="p-4 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Feed Details</h2>
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Name</dt>
                <dd className="mt-1 text-sm text-gray-900">{feed.name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Type</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {feed.type}
                  </span>
                </dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">URL</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <a href={feed.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">
                    {feed.url}
                  </a>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Check Frequency</dt>
                <dd className="mt-1 text-sm text-gray-900">{feed.check_frequency} minutes</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    feed.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {feed.is_active ? 'Active' : 'Inactive'}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Last Checked</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {feed.last_checked ? new Date(feed.last_checked).toLocaleString() : 'Never'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">{new Date(feed.created_at).toLocaleDateString()}</dd>
              </div>
            </dl>
          </div>
        )}
      </div>

      {/* Recent Articles */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-4 sm:p-6 border-b">
          <h2 className="text-lg font-medium text-gray-900">Recent Articles</h2>
        </div>
        <div className="p-4 sm:p-6 text-center text-gray-500">
          <p>No articles fetched yet.</p>
          <button
            onClick={() => processMutation.mutate()}
            disabled={processMutation.isPending}
            className="mt-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" />
            Process Feed Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedDetailPage;